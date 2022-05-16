# coding = utf-8
'''Uses description of channel as clock with several timezones'''
import os
import sys
import logging

import datetime
import pytz

import discord
from discord.ext import tasks, commands

TZ = {
    "🇰🇷": "Asia/Seoul",
    "🇦🇿": "Asia/Baku",
    "🦫": "US/Eastern",
}



class TimeUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = None
        self.update_time.start()

    @tasks.loop(seconds=360)
    async def update_time(self):
        logging.info(f"TimeUpdater:Updating time with {datetime.datetime.now().strftime('%H:%M:%S')}")
        new_time = ""
        for i in TZ:
            new_time += datetime.datetime.now(pytz.timezone(TZ[i])).strftime(f"{i} %a %H:%M |\n")
        new_time = new_time[:-2] # Remove last " |"

        try:
            await self.guild.system_channel.edit(topic=new_time)
        except Exception as err:
            logging.warning(err)

        logging.info(f"TimeUpdater:Updated on {datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}")

    @update_time.before_loop
    async def before_update_time(self):
        logging.info("TimeUpdater:Waiting for bot...")
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            if guild.id == 711543189693136916: #our guild
                self.guild = guild
