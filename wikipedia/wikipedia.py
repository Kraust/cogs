""" Wikipedia Search COG """

import string
from pathlib import Path

import aiohttp
import discord
from redbot.core import commands
from redbot.core.utils.menus import menu

SEARCH_BASE = "https://en.wikipedia.org/w/api.php?action=opensearch&search=$search"
SUMMARY_BASE = "https://en.wikipedia.org/api/rest_v1/page/summary/$url"
SEARCH_RESULT = "$extract"
TITLE_FORMAT = "$name"


class Wikipedia(commands.Cog):
    """Wikipedia Cog"""

    def __init__(self, bot):
        """Init"""
        self.bot = bot

    async def urls(self, ctx, session, search):
        """Search Wikipedia Titles"""

        async with session.get(
            string.Template(SEARCH_BASE).safe_substitute(search=search)
        ) as res:
            urls = (await res.json())[3]

        return urls

    async def data(self, ctx, session, urls):
        """Search Wikipedia Summaries"""

        data = []
        for url in urls:
            path = Path(url)
            async with session.get(
                string.Template(SUMMARY_BASE).safe_substitute(url=path.name)
            ) as res:
                data.append(
                    {
                        "url": url,
                        "data": await res.json(),
                    }
                )
        return data

    @commands.command(aliases=["wiki"])
    async def wikipedia(self, ctx, *, search):
        """Wikipedia command"""

        async with aiohttp.ClientSession() as session:
            urls = await self.urls(ctx, session, search)
            data = await self.data(ctx, session, urls)

        embeds = []
        for idx, entry in enumerate(data):
            # print(entry)
            embed = discord.Embed(color=await ctx.embed_color())
            embed.title = string.Template(TITLE_FORMAT).safe_substitute(
                name=entry["data"]["titles"]["normalized"],
            )
            embed.url = entry["url"]
            embed.description = string.Template(SEARCH_RESULT).safe_substitute(
                extract=entry["data"]["extract"],
            )
            embed.set_footer(text=f"Result {idx+1} of {len(data)}")
            embed.set_thumbnail(url=entry["data"]["thumbnail"]["source"])
            embeds.append(embed)

        if len(embeds):
            await menu(ctx, pages=embeds, message=None, page=0, timeout=30)
        else:
            await ctx.send("No results found")
