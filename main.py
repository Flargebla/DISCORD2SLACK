from discord_client import DiscordClient
from queue import Queue
import time
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

# Run the DiscordClient
t = threading.Thread(target=dc.run, args=(TOKEN,))
t.start()

# Run the SlackClient

#time.sleep(5)
#print("Sending from slack")
#sl2d.put("MSG FROM YABOI")