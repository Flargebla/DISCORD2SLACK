import discord
import threading
import asyncio
import json
import time
import copy
import requests
import random
from emoji import emojize, demojize

class DiscordClient(discord.Client):

    def __init__(self, to_slack, from_slack):
        # Call super
        super().__init__()
        # Store the queues
        self.to_slack = to_slack
        self.from_slack = from_slack
        # Create instance vars
        self.channels = dict()
        self.server = None

    @asyncio.coroutine
    def on_message(self, message):
        # Don't respond to yourself
        if message.author == self.user:
            return
        print(f"Message received from discord: {message.content}")
        # Check for img
        print(f"Message embed: {message.embeds}")
        print(f"Message attachment: {message.attachments}")
        print(f"Message content: {message.content}")
        # Send the message to the Slack
        self.to_slack.put({
            "type": "MSG",
            "sender": "ConnorZapfel",
            "channel": str(message.channel),
            "text": message.content,
            "img": message.attachments[0]["url"]
        })

    @asyncio.coroutine
    def on_reaction_add(self, reaction, user):
        print(f"React received from discord: {reaction}")
        self.to_slack.put({
            "type": "RCT",
            "sender": "ConnorZapfel",
            "channel": reaction.message.channel.name,
            "name": demojize(reaction.emoji),
            "text": reaction.message.content
        })

    @asyncio.coroutine
    def on_ready(self):
        print('------')
        print('Logged in as')
        print("User:\t" + self.user.name)
        print("ID:\t" + self.user.id)
        self.server = [x for x in self.servers][0]
        print("SERVER:\t" + str(self.server))
        print('------')
        # Send CONF
        self.to_slack.put({
            "type": "CONF",
            "discord_user": "ConnorZapfel"
        })
        # Listen for messages forever
        while True:
            # Wait for a message
            if self.from_slack.empty():
                print("Sleeping...")
                yield from asyncio.sleep(1)
                continue
            else:
                print("Reading msg...")
                msg = self.from_slack.get(block=False)
            # Check the message type
            if msg["type"] == "MSG":
                print(f"Received from slack to {msg['channel']}: {msg['text']}")
                print(f"Available Channels: {self.channels.keys()}")
                # Forward it to the discord server
                if msg["channel"] in self.channels.keys() and msg['text'] != "":
                    # Check if msg is part of a thread
                    if len(msg["thread"]) > 0:
                        i = 0
                        msg_str = ""
                        for t in msg["thread"]:
                            msg_str += f"{'|  '*i}{t['text']} ({t['sender']})\n"
                            i += 1
                        msg_str += f"{'| '*i}{msg['text']} ({msg['sender']})"
                        msg_str = f"```{msg_str}```"
                        yield from self.send_message(self.channels[msg["channel"]], msg_str)
                    # Otherwise its just a normal message
                    else:
                        # Check for img
                        if len(message.attachments) > 0:
                            # Grab the remote image
                            rint = str(random.randint(0,9999999))
                            r = requests.get(msg["img"])
                            if r.status_code == 200:
                                with open(f"{rint}.jpg", "wb") as f:
                                    for c in r.iter_content(1024):
                                        f.write(c)
                            yield from self.send_file(msg["channel"], f"{rint}.jpg")
                            yield from asyncio.sleep(1)
                        yield from self.send_message(self.channels[msg["channel"]], f"**{msg['sender']}**")
                        yield from asyncio.sleep(1)
                        m = yield from self.send_message(self.channels[msg["channel"]], f"{msg['text']}")
                else:
                    print(f"ERROR - Channel \"{msg['channel']}\" not found")
            elif msg["type"] == "CONF":
                print(f"Received CONF from Slack: {msg}")
                # Create all the channels
                for ch_name in msg["channels"]:
                    print(f"Creating channel: {ch_name}")
                    yield from self.create_channel(self.server, ch_name)
                    print(f"Created channel: {ch_name}")
                # Store then channel mapping
                time.sleep(10)
                print(f"Discovered channels: {[c for c in self.get_all_channels()]}")
                for ch in [c for c in self.get_all_channels()]:
                    self.channels[ch.name] = ch
            elif msg["type"] == "RCT":
                print(f"Received RCT from Slack: {msg}")
                # Grab a copy of the message deque
                msgs = copy.deepcopy(self.messages)
                for m in msgs:
                    if m.content == msg['text']:
                        print("Found msg! Adding reaction!")
                        uni_emoji = emojize(f":{msg['name']}:", use_aliases=True)
                        yield from self.add_reaction(m, uni_emoji)