# coding = utf-8
'''Deter users from playing video games'''
import os
import sys
import logging

import aiohttp

import discord
from discord.ext import tasks, commands

API_INSULT = "https://evilinsult.com/generate_insult.php?lang=en&type=json"

class Valo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = None
        self.check_valo_players.start()

    @tasks.loop(seconds=5)
    async def check_valo_players(self):
        for member in self.guild.members:
            for activity in member.activities:
                if activity.name == "VALORANT": #deploy soyus
                    async with aiohttp.request("GET", API_INSULT) as insult:
                        message = f"{(await insult.json())['insult']} Stop playing valorant, go study!"
                        logging.info(f"Valo:'{message}' sent to {str(member)}")
                        await member.send(message)

    @check_valo_players.before_loop
    async def before_check_valo_players(self):
        logging.info("Valo:Waiting for bot...")
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            if guild.id == 711543189693136916: #our guild
                self.guild = guild
