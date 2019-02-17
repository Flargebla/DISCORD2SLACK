import os, time
from operator import itemgetter
from slackclient import SlackClient
from pprint import pprint


class SlackBot:

    def __init__(self, from_discord, to_discord):

        # init client
        self.slack_token = os.environ.get("SLACK_API_TOKEN")
        self.sc = SlackClient(slack_token)

        # Store queues
        self.from_discord = from_discord
        self.to_discord = to_discord
        

    def listener(self):
      last_ts = None
      while(True):
        if (last_ts):
          ret = sc.api_call(
            "channels.history",
            channel="CG8FA1S65",
            oldest=last_ts,
          )
        else:
          ret = sc.api_call(
            "channels.history",
            channel="CG8FA1S65",
          )
        if(len(ret['messages']) > 0):
          print(ret)
          last_ts = sorted(ret['messages'], key=itemgetter('ts'))[-1]['ts']
          for message in ret['messages']:
            self.to_discord.put(message['text'])
        else:
          print("no new messages")
        time.sleep(1)