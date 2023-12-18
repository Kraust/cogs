""" Wikipedia Init """

from .wikipedia import Wikipedia


async def setup(bot):
    await bot.add_cog(Wikipedia(bot))
