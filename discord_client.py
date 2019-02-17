import discord
import threading
import asyncio
import json
import time
from emoji import emojize

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
        # Send the message to the Slack
        self.to_slack.put({
            "type": "MSG",
            "sender": "ConnorZapfel",
            "channel": str(message.channel),
            "text": message.content
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
                    if len(msg["thread"]) > 0:
                        # Add threads
                        i = 0
                        for t in msg["thread"]:
                            yield from self.send_message(self.channels[msg["channel"]], f"{'|  '*i}{t['text']} (**{t['sender']}**)")
                            i += 1
                    else:
                        yield from self.send_message(self.channels[msg["channel"]], f"**{msg['sender']}**")
                        m = yield from self.send_message(self.channels[msg["channel"]], f"{msg['text']}")
                        # Add reactions
                        for r in msg['reactions']:
                            for i in range(r['count']):
                                uni_emoji = emojize(f":{r['name']}:", use_aliases=True)
                                print(f"Adding reaction: {uni_emoji}")
                                yield from self.add_reaction(m, uni_emoji)
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
