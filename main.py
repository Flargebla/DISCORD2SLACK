from discord_client import DiscordClient
from slack import SlackBot
from queue import Queue
import time
import json
import os
import threading

# The Discord token
TOKEN = os.environ["DISCORD_API_TOKEN"]

# Create the two messaging Queues
d2sl = Queue()
sl2d = Queue()

# Create the Discord Client
dc = DiscordClient(d2sl, sl2d)

# Create the Slack Client
sc = SlackBot(d2sl, sl2d)

# Run the DiscordClient
t = threading.Thread(target=dc.run, args=(TOKEN,))
t.start()

# Run the SlackClient
#s = threading.Thread(target=sc.run)
#s.start()

#time.sleep(5)
#print("Sending slack conf")
#jm = {
#    "type": "CONF",
#    "channels": ["general","duckhacks2019"]
#}
#sl2d.put(json.dumps(jm))