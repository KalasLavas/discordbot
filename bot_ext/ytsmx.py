'''Get and torrent movies from yts.mx with Transmission torrent client'''
import logging
import asyncio

import aiohttp
from requests.utils import quote
import transmission_rpc as rpc

import discord
from discord.ext import tasks, commands

WHITELIST_FILE = "whitelist.txt"

NUMBERS = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

RPC = rpc.Client(host='localhost', port=80)
ENDP_SEARCH = "https://yts.mx/api/v2/list_movies.json"
TRACKERS = [
    "udp://glotorrents.pw:6969/announce",
    "udp://open.demonii.com:1337/announce",
    "udp://p4p.arenabg.ch:1337",
    "udp://p4p.arenabg.com:1337",
    "udp://torrent.gresille.org:80/announce",
    "udp://tracker.coppersurfer.tk:6969",
    "udp://tracker.internetwarriors.net:1337",
    "udp://tracker.leechers-paradise.org:6969",
    "udp://tracker.openbittorrent.com:80",
    "udp://tracker.opentrackr.org:1337/announce",
]

QW = {
    "1080p": 10,
    "2160p": 2,
    "720p": 5,
    "3D": 0,
}

RW = {
    "bluray": 2,
    "web": 1,
}

class YTS(commands.Cog):
    data = {}
    whitelist = []
    def __init__(self, bot):
        self.bot = bot
        #load whitelist
        with open(WHITELIST_FILE, 'r') as fwl:
            self.whitelist = [int(i) for i in list(fwl)]
        logging.info(f"init:whitelist loaded [{self.whitelist}]")

    async def yts_search(self, query="", limit=5, sort="download_count", user=0):
        params = {
            "query_term": query,
            "limit": limit,
            "sort_by": sort
        }
        async with aiohttp.request("GET", ENDP_SEARCH, params=params) as r:
            if r.status != 200:
                logging.error(f"ytsmx:search:GET failed [{r.status}]")
                return None

            dt = await r.json()

            if dt["status"] != "ok":
                logging.error(f"ytsmx:search:API error [{dt['status_message']}")
                return None

            self.data[user] = dt["data"]
            resp = []
            for movie in self.data[user]["movies"]:
                mdict = {}
                mdict["title"] = movie["title_long"]
                mdict["rating"] = movie["rating"]
                mdict["summary"] = movie["summary"]
                mdict["image"] = movie["small_cover_image"]
                resp.append(mdict)
            return resp

    async def gen_magnet(self, torrent_hash, title):
        uri = f"magnet:?xt=urn:btih:{torrent_hash}&dn={quote(title)}"
        for tracker in TRACKERS:
            uri += f"&tr={tracker}"
        return uri

    async def yts_download(self, index=1, user=0):
        #pick best option
        logging.debug(f"ytsmx:dload:{user} {index}")
        try:
            movie = self.data[user]["movies"][int(index) - 1]
        except Exception as e:
            logging.error(f"ytsmx:dload:magnet:Invalid index [{index}], size: {len(self.data['movies'])}, user:[{user}], error;[{e}]")
            return -1

        movie["torrents"] = sorted(movie["torrents"], key=lambda tr: QW.get(tr["quality"], 0) + RW.get("type", 0), reverse=True)

        magnet = await self.gen_magnet(movie["torrents"][0]["hash"], f"{movie['title_long']} [{movie['torrents'][0]['quality']}]")

        logging.info(f"ytsmx:dload:Trying to torrent {movie['title_long']}")
        logging.debug(magnet)

        RPC.add_torrent(magnet)

        return (movie["title_long"], movie["small_cover_image"])

    async def torrent_status(self):
        torrents = RPC.get_torrents()
        torrents = sorted(torrents, key=lambda tor: tor.date_added, reverse=True)
        return torrents[:5]

    @classmethod
    def format_size_2(cls, size):
        fsize = rpc.utils.format_size(size)
        return f"{fsize[0]:.2f}{fsize[1]}"

    async def torrent_status_desc(self):
        stats = RPC.session_stats()
        s = f"df: {self.format_size_2(stats.download_dir_free_space)}\n"
        s +=  f"↓{self.format_size_2(stats.cumulative_stats['downloadedBytes'])} | ↑{self.format_size_2(stats.cumulative_stats['uploadedBytes'])}"
        return s

    @commands.Cog.listener()
    async def on_message(self, message):
        pass

    @commands.command()
    async def yts(self, message, *, query: str):
        if message.author.id not in self.whitelist:
            return
        logging.info(query)

        movies = await self.yts_search(query=query, user=message.author.id)
        if len(movies) == 0:
            embed = discord.Embed(title=f"**Nothing was found for {query}**", description="Try to rephrase your query")
            await message.channel.send(embed=embed)
            return

        movie_messages = []
        for i, movie in enumerate(movies):
            embed = discord.Embed(title=f"**{i+1}. {movie['title']}**", description=f"IMDB: **{movie['rating']}**")
            embed.set_thumbnail(url=movie["image"])
            last_message = await message.channel.send(embed=embed)
            movie_messages.append(last_message)

        for i in range(1, len(movies)+1):
            await last_message.add_reaction(NUMBERS[i])

        try:
            def check_reaction_yts(reaction, user):
                return last_message == reaction.message and user == message.author

            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check_reaction_yts)
        except asyncio.TimeoutError:
            for msg in movie_messages:
                await msg.delete()
            embed = discord.Embed(title="**User didn't reply within 60 seconds**", description="Try again")
            await (await message.channel.send(embed=embed)).delete(delay=10)
            return

        for msg in movie_messages:
            await msg.delete()

        try:
            movie_id = NUMBERS.index(reaction.emoji)
            if len(movies) < movie_id:
                raise ValueError
        except ValueError:
            embed = discord.Embed(title="**Invalid emoji**", description="Try again")
            await (await message.channel.send(embed=embed)).delete(delay=10)
            return

        logging.info(movie_id)

        picked_movie = await self.yts_download(index=movie_id, user=user.id)

        logging.info(f"{picked_movie[0]}; {picked_movie[1]}")

        embed = discord.Embed(title=f"Downloading {picked_movie[0]}...", description="")
        embed.set_thumbnail(url=picked_movie[1])
        await message.channel.send(embed=embed)

    @yts.error
    async def yts_error(self, message, error):
        logging.error(error)

    @commands.command()
    async def tstatus(self, message):
        # if message.author.id not in WHITELIST:
        #     return
        torrents = await self.torrent_status() #only top 5
        embed = discord.Embed(title="Status of Transmission", description=await self.torrent_status_desc())
        for torrent in torrents:
            embed.add_field(name=f"{torrent.name}", value=f"{torrent.progress:.1f}% | 1:{torrent.ratio:.2f}", inline=False)
        await message.channel.send(embed=embed)

    @tstatus.error
    async def tstatus_error(self, message, error):
        logging.error(error)
