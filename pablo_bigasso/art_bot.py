from twitchio.ext import commands
from ..requesters import *
from view import *
from ..keats_bot import KeatsBot

import tkinter as tk
import threading
import os

IMAGE = 'image'
SOUND = 'sound'
TIME = 'time'

class ArtBot(KeatsBot):

    def __init__(self):
        super().__init__()

        # add the models in
        self._requests.add_requester(IMAGE, ImageRequester())
        self._requests.add_requester(TIME, TimeRequester())

        self._view = None

    def add_view(self, view):
        self._view = view

    @commands.command(name='request')
    async def request(self, ctx):
        message = ctx.content.split('request', 1)[1].lower().strip() # get request stripped and lowercased.
        self._model.make_request(IMAGE, ctx.author.name, message)

    @commands.command(name='clear')
    async def clear(self, ctx):
        if ctx.author.name != self.OWNER:
            return
        
        self._model.clear_requests()

    @commands.command(name='rate')
    async def rate(self, ctx):
        message = ctx.content.split('rate', 1)[-1].strip() # get request stripped
        model = self._model.get_requester(TIME)
        user = ctx.author.name
        if model.can_request(user) and self._view is not None:
            modifiers = {
                "StinkyCheese": -10,
                "CurseLit": 10
            }
            for key in modifiers:
                if key in message:
                    self._view.change_time(modifiers[key])

            model.request(user, message) # add player to timeout for a little while
    
    @commands.command(name='help')
    async def help(self, ctx):
        response = 'https://docs.google.com/document/d/16SJbn_19oA3_gIh8CC3e2zrfSKOo8S_LztY64qwTHN8/edit?usp=sharing'
        await ctx.send(response)
    

def main():
    
    bot = ArtBot()
    
    view = threading.Thread(target=start_view, args=(bot,))
    view.start()

    bot.run()

def start_view(bot):
    root = tk.Tk()
    root.title('Pablo')

    app = PabloApp(root, bot.get_model())
    bot.add_view(app)

    root.mainloop()

if __name__ == "__main__":
    main()