import discord

TOKEN = "NTQ2NDU0NzU1MDAyNjc5Mjk2.D0od9A.o_ZacumYF9gczEi-Ma0Jym-quIE"

client = discord.Client()

@client.event
async def on_message(message):
    # Don't respond to yourself
    if message.author == client.user:
        return

    # Look for the !join <link> command
    if message.content.startswith('!join'):
        # Grab the slack workspace link
        slack_ws_url = message.content.split(" ")[1]
        print(slack_ws_url)
        #msg = 'Hello {0.author.mention}'.format(message)
        #await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)