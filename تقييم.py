import discord
from discord.ext import commands

RATING_CHANNEL_ID = 1505141810115379340
MOD_ROLE_ID       = 1505181303971250256
HELP_ROLE_ID      = 1505174149625151529

STAFF_ROLE_IDS = {MOD_ROLE_ID, HELP_ROLE_ID}


class تقييم(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id != RATING_CHANNEL_ID:
            return
        if not message.mentions:
            return

        for member in message.mentions:
            if member.bot:
                continue
            is_staff = any(r.id in STAFF_ROLE_IDS for r in member.roles)
            if not is_staff:
                continue

            embed = discord.Embed(
                title="⭐ تقييم الإداري",
                description=(
                    f"قيّم أداء {member.mention}\n\n"
                    f"✅ — راضي عن الإداري\n"
                    f"❌ — غير راضي عن الإداري"
                ),
                color=0x3498db
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"طلب بواسطة {message.author.display_name}")

            try:
                await message.delete()
            except Exception:
                pass

            rating_msg = await message.channel.send(embed=embed)
            await rating_msg.add_reaction("✅")
            await rating_msg.add_reaction("❌")


async def setup(bot):
    await bot.add_cog(تقييم(bot))
