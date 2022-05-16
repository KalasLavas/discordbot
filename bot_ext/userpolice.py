# coding = utf-8
'''Notifies server is specific user becomes online'''
import os
import sys
import logging

import discord
from discord.ext import tasks, commands

TARGET_USER = 677067154570346498 # kalas

class UserPolice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.id != TARGET_USER:
            return
        before_status = 1
        after_status = 1
        
        if before.status == discord.Status.offline:
            before_status = 0
        
        if after.status == discord.Status.offline:
            after_status = 0

        logging.info(f"UserPolice: before {before.status} {before_status} after {after.status} {after_status}")
        if before_status == after_status:
            return

        message = "inner peace <:ibi:838485895472349214>"
        if after_status == 1:
            message = "HE IS HERE, RUN! <:ibi:838485895472349214>"

        await self.bot.get_guild(711543189693136916).system_channel.send(message)

# python3 discordbot-timezone/bot.py