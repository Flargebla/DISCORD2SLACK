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

        self._username = None;


    def send_channels(self):
      channels = [v for k,v in self.channels.items()]
      self.to_discord.put({
        'type': 'CONF',
        'channels': channels
      })
    

    def start_listeners(self):
      for k, v in self.channels.items():
        threading.Thread(target=self.channel_listener, args=(k,)).start()


    def handle_message(self, message):
      if 'reactions' in message:
          for reaction in message['reactions']:
            for user in reaction['users']:
              rusername = self.userlist.get(user)
              reaction['users'].remove(user)
              reaction['users'].append(rusername)
      thread_parents = {}
      if 'replies' in message:
        thread_parents[message['thread_ts']] = message['text']
      if 'parent_user_id' in message:
        message['parent_text'] = thread_parents[message['thread_ts']]
      m = {
        'type': 'MSG',
        'channel': self.channels[channel],
        'text': message['text'],
        'reactions': message.get('reactions', [])
      }
      if "user" in message:
        m['sender'] = self.userlist[message.get('user')]
        self.to_discord.put(m)
      elif "username" in message and message.get('username') != self._username:
        m['sender'] = message.get('username')
        self.to_discord.put(m)


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
          sorted_ret = sorted(ret['messages'], key=itemgetter('ts'))
          last_ts = sorted_ret[-1]['ts']
          for message in sorted_ret:
            self.handle_message(message)
        else:
          #print("No new messages detected")
          continue


    def receiver(self):
      while(True):
        msg = self.from_discord.get(block=True)
        if msg["type"] == "MSG":
          print(f"Received from discord to {msg['channel']}: {msg['text']}")
          # Forward it to the slack workplace
          print(f"Sending - CHANNEL: {msg['channel']}")
          print(f"Sending - TEXT: {msg['text']}")
          print(f"Sending - SENDER: {msg['sender']}")
          send = self.sc.api_call("chat.postMessage",
                                   channel=msg["channel"],
                                   text=msg["text"],
                                   as_user=False,
                                   username=msg["sender"])
          pprint(send)
        elif msg["type"] == "CONF":
          self._username = msg['discord_user']


    def run(self):
      self.send_channels()
      self.start_listeners()
      threading.Thread(target=self.receiver).start()
