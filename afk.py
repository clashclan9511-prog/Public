import discord
from discord.ext import commands
from datetime import datetime

afk_users = {}


class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="afk")
    async def set_afk(self, ctx, *, السبب: str = "غير متاح"):
        """تفعيل وضع AFK. مثال: !afk خارج الخدمة"""
        afk_users[ctx.author.id] = {
            "reason": السبب,
            "time": datetime.utcnow(),
            "guild": ctx.guild.id
        }
        embed = discord.Embed(
            title="💤 وضع AFK مفعّل",
            description=f"{ctx.author.mention} الآن في وضع AFK\n📝 **السبب:** {السبب}",
            color=0x95a5a6
        )
        await ctx.send(embed=embed)
        try:
            old_nick = ctx.author.display_name
            if not old_nick.startswith("[AFK]"):
                await ctx.author.edit(nick=f"[AFK] {old_nick[:25]}")
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # إزالة AFK عند الكتابة
        if message.author.id in afk_users:
            if message.content.startswith("!afk"):
                return
            data = afk_users.pop(message.author.id)
            diff = datetime.utcnow() - data["time"]
            mins = int(diff.total_seconds() // 60)
            duration = f"{mins} دقيقة" if mins > 0 else "أقل من دقيقة"
            embed = discord.Embed(
                title="👋 مرحباً بعودتك!",
                description=f"{message.author.mention} تم إزالة وضع AFK عنك.\n⏱️ كنت غائباً لمدة: **{duration}**",
                color=0x2ecc71
            )
            msg = await message.channel.send(embed=embed)
            try:
                nick = message.author.display_name
                if nick.startswith("[AFK] "):
                    await message.author.edit(nick=nick[6:] or None)
            except Exception:
                pass
            import asyncio
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except Exception:
                pass
            return

        # إشعار عند منشن شخص AFK
        for mentioned in message.mentions:
            if mentioned.id in afk_users and mentioned.id != message.author.id:
                data = afk_users[mentioned.id]
                diff = datetime.utcnow() - data["time"]
                mins = int(diff.total_seconds() // 60)
                duration = f"منذ {mins} دقيقة" if mins > 0 else "منذ لحظات"
                embed = discord.Embed(
                    title="💤 هذا الشخص في وضع AFK",
                    description=(
                        f"**{mentioned.display_name}** غير متاح حالياً\n"
                        f"📝 **السبب:** {data['reason']}\n"
                        f"⏱️ **منذ:** {duration}"
                    ),
                    color=0x95a5a6
                )
                embed.set_thumbnail(url=mentioned.display_avatar.url)
                await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AFK(bot))
