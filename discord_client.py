import discord
import threading
import asyncio

class DiscordClient(discord.Client):

    def __init__(self, to_slack, from_slack):
        # Call super
        super().__init__()
        # Store the queues
        self.to_slack = to_slack
        self.from_slack = from_slack

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
        print('------')
        # Get the channels
        channel = [x for x in self.get_all_channels()][1]
        while True:
            # Wait for a message
            msg = self.from_slack.get(block=True)
            print(f"Received from slack: {msg}")
            # Forward it to the discord server
            yield from self.send_message(channel, msg)