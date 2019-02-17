import os
import time
import threading
from operator import itemgetter
from slackclient import SlackClient
from pprint import pprint


class SlackBot:
    def __init__(self, from_discord, to_discord):
        # init client
        self.slack_token = os.environ.get("SLACK_API_TOKEN")
        self.sc = SlackClient(self.slack_token)

        # Store queues
        self.from_discord = from_discord
        self.to_discord = to_discord

        # establish channel dict from api
        _channels = self.sc.api_call("channels.list")
        self.channels = {channel["id"]: channel["name"] for channel in _channels["channels"]}
        
        # initialize user dict from api
        _users = self.sc.api_call("users.list")
        self.userlist = {user["id"]: user["name"] for user in _users['members']}

        self.bot_username = None;

        self.parents = dict()

        self.history = list()


    def send_channels(self):
      channels = [v for k,v in self.channels.items()]
      self.to_discord.put({
        'type': 'CONF',
        'channels': channels
      })
    

    def start_listeners(self):
      # Start channel listeners
      for k, v in self.channels.items():
        threading.Thread(target=self.channel_listener, args=(k,)).start()
      # Start react listener
      threading.Thread(target=self.react_listener).start()


    def handle_message(self, message, channel):
      if "username" not in message and "user" not in message:
        pprint(message)
        return
      sender = message.get("username") if "username" in message else self.userlist[message.get("user")]
      if 'reactions' in message:
          for reaction in message['reactions']:
            for user in reaction['users']:
              rusername = self.userlist.get(user)
              reaction['users'].remove(user)
              reaction['users'].append(rusername)

      if 'thread_ts' not in message or 'replies' in message:
        self.parents[message['ts']] = [{'sender': sender, 'text': message['text']}]
      else:
        message['thread'] = [obj for obj in self.parents[message['thread_ts']]]
        self.parents[message['thread_ts']].append({'sender': sender, 'text': message['text']})
      
      if 'files' in message:
          #fid = message["files"][0]["id"]
          #ret = self.sc.api_call("files.sharedPublicURL",
          #                        file_id=fid)
          #pprint(ret)
          #message['image'] = ret["url_download"]
          message['image'] = ret['permalink_public']

      if (sender != self.bot_username):
        m = {
          'sender': sender,
          'type': 'MSG',
          'channel': self.channels[channel],
          'text': message['text'],
          'reactions': message.get('reactions', []),
          'thread': message.get('thread', []),
          'img': message.get('image', "")
        }

        self.to_discord.put(m)


    def react_listener(self):
      time.sleep(10)
      last_ts = None
      while(True):
        # Grab the list of reacts
        reacts = self.sc.api_call("reactions.list",
                                  full=True)
        # Send all reacts to Discord
        if last_ts is None and "items" in reacts:
          # Iterate over the reacts
          for i in reacts["items"]:
            for r in i['message']['reactions']:
              self.to_discord.put({
                "type": "RCT",
                "sender": "",
                "name": r['name'],
                "text": i['message']['text']
              })
            # Update last_ts
            if not last_ts or float(i['message']['ts']) > last_ts:
              last_ts = float(i['message']['ts'])
        # Send reacts past last_ts to Discord
        elif "items" in reacts:
          for i in reacts['items']:
            if float(i['message']['ts']) > last_ts:
              for r in i['message']['reactions']:
                self.to_discord.put({
                  "type": "RCT",
                  "sender": "",
                  "name": r['name'],
                  "text": i['message']['text']
                })
              # Update last_ts
              if not last_ts or float(i['message']['ts']) > last_ts:
                last_ts = float(i['message']['ts'])
        time.sleep(3)


    def channel_listener(self, channel):
      last_ts = None
      while(True):
        if (last_ts):
          ret = self.sc.api_call(
            "channels.history",
            channel=channel,
            oldest=last_ts,
          )
        else:
          ret = self.sc.api_call(
            "channels.history",
            channel=channel,
          )
        if(ret.get('messages')):
          self.history = ret.get("messages") + self.history
          sorted_ret = sorted(ret['messages'], key=itemgetter('ts'))
          last_ts = sorted_ret[-1]['ts']
          for message in sorted_ret:
            self.handle_message(message, channel)
        else:
          #print("No new messages detected")
          continue
        time.sleep(3)


    def receiver(self):
      while(True):
        msg = self.from_discord.get(block=True)
        if msg["type"] == "MSG":
          print(f"Received from discord to {msg['channel']}: {msg['text']}")
          if msg["img"] != "":
            #pprint(msg)
            block=[{
              "type": "image",
              "image_url": msg['img'],
              "alt_text": "An image"
            }]
            send = self.sc.api_call(
              "chat.postMessage",
              channel=msg['channel'],
              text=msg["text"],
              as_user=False,
              username=msg['sender'],
              blocks=block)
            pprint(send)
          else:
            send = self.sc.api_call("chat.postMessage",
                                    channel=msg["channel"],
                                    text=msg["text"],
                                    as_user=False,
                                    username=msg["sender"])
        elif msg["type"] == "CONF":
            self.bot_username = msg['discord_user']
        elif msg["type"] == "RCT":
            # Grab channel history
            #history = self.sc.api_call("channels.history", channel=msg['channel'])
            history = [x for x in self.history]
            ts = None
            sorted_hist = sorted(history, key=itemgetter('ts'), reverse=True)
            for m in sorted_hist:
              if m['text'] == msg['text']:
                ts = m['ts']
                break
            # Make sure we found a message 
            if ts is not None:
              print("Found Slack message for:")
              rev_chans = {v:k for k, v in self.channels.items()}
              ret = self.sc.api_call("reactions.add",
                                      name=msg['name'][1:-1],
                                      channel=rev_chans[msg['channel']],
                                      timestamp=ts)
            else:
              pprint(history['messages'])


    def run(self):
      self.send_channels()
      self.start_listeners()
      threading.Thread(target=self.receiver).start()
