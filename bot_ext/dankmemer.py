# coding = utf-8
'''Dank memer reminder'''
import os
import sys
import logging

from asyncio import sleep

import discord
from discord.ext import tasks, commands

WORK = "pls work"
TIMEOUT = 3600

onTimeout = set(())

class DankMemer(commands.Cog):
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot is True:
            return
        if message.content.lower() == WORK:
            
            if message.author.id in onTimeout:
                return
            onTimeout.add(message.author.id)
            
            logging.info(f"DankMemer: {message.author.name} set work for {TIMEOUT} seconds")
            
            await sleep(TIMEOUT)
            
            onTimeout.discard(message.author.id)
            await message.reply(f"Hey {message.author.mention}, it is time to `{WORK}`")