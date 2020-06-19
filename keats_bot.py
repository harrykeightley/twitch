from twitchio.ext import commands
from requesters import RequestMuxer, SoundRequester

import os

class KeatsBot(commands.Bot):

    OWNER = 'imKeats'
    CHANNELS = ['imkeats']
    TOKEN = os.environ.get('BOT_TOKEN')
    CLIENT_ID = 'keatsbot'
    NICK = 'keatsbot'

    DISCORD = 'https://discord.gg/eBvGYfJ'
    SOUND = 'sound'

    def __init__(self):
        super().__init__(irc_token=self.TOKEN, client_id=self.CLIENT_ID, nick=self.CLIENT_ID, prefix='!',
                         initial_channels=self.CHANNELS)

        # add the models in
        self._requests = RequestMuxer()
        self._requests.add_requester(SOUND, SoundRequester(sound_file='sounds/soundfile', sound_folder='sounds'))

    def get_model(self):
        return self._requests

    # Events don't need decorators when subclassed
    async def event_ready(self):
        print(f'Ready | {self.nick}')

    async def event_message(self, message):
        print(message.content)
        await self.handle_commands(message)

    # Commands use a different decorator
    @commands.command(name='test')
    async def my_command(self, ctx):
        await ctx.send(f'Hello {ctx.author.name}!')

    @commands.command(name='discord')
    async def discord(self, ctx):
        await ctx.send(f'Keats\' discord: {self.DISCORD}')

    @commands.command(name='play')
    async def play(self, ctx):
        message = ctx.content.split('play', 1)[1].lower().strip() # get request stripped and lowercased.
        self._model.make_request(SOUND, ctx.author.name, message)

    @commands.command(name='help')
    async def help(self, ctx):
        response = 'https://docs.google.com/document/d/16SJbn_19oA3_gIh8CC3e2zrfSKOo8S_LztY64qwTHN8/edit?usp=sharing'
        await ctx.send(response)
    