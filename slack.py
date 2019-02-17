import os, time
from operator import itemgetter
from slackclient import SlackClient
from pprint import pprint

slack_token= os.environ.get("SLACK_API_TOKEN")
sc = SlackClient(slack_token)

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
    sorted_ret = sorted(ret['messages'], key=itemgetter('ts'))
    last_ts = sorted_ret[-1]['ts']
    pprint(ret)
  else:
    print("no new messages")
  time.sleep(1)