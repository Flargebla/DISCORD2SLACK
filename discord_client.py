import discord
import threading
import asyncio
import json

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

    @asyncio.coroutine
    def on_ready(self):
        print('------')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print([x for x in self.servers])
        self.server = [x for x in self.servers][0]
        print('------')
        while True:
            # Wait for a message
            msg = self.from_slack.get(block=True)
            # Parse to JSON
            jmsg = json.loads(msg)
            # Check the message type
            if jmsg["type"] == "MSG":
                print(f"Received from slack: {msg}")
                # Forward it to the discord server
                yield from self.send_message(self.channels[jmsg["channel"]], f"{jmsg['sender']}: {jmsg['text']}")
            elif jmsg["type"] == "CONF":
                # Create all the channels
                for ch_name in jmsg["channels"]:
                    yield from self.create_channel(self.server, ch_name)
                # Store then channel mapping
                for ch in [c for c in self.server.get_all_channels()]:
                    self.channels[ch.name] = ch
