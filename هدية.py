import discord
from discord.ext import commands
import asyncio
import random
from datetime import datetime, timedelta

active_giveaways = {}


class هدية(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="هدية")
    @commands.has_permissions(manage_guild=True)
    async def giveaway(self, ctx, المدة: int, الفائزون: int, *, الجائزة: str):
        """إنشاء هدية. مثال: !هدية 60 1 نيترو ديسكورد (المدة بالثواني)"""
        if المدة < 10:
            await ctx.send("❌ المدة يجب أن تكون 10 ثواني على الأقل!")
            return
        if الفائزون < 1 or الفائزون > 10:
            await ctx.send("❌ عدد الفائزين بين 1 و 10!")
            return

        ends_at = datetime.utcnow() + timedelta(seconds=المدة)
        embed = discord.Embed(
            title="🎉 هدية!",
            description=(
                f"**الجائزة:** {الجائزة}\n\n"
                f"تفاعل بـ 🎉 للمشاركة!\n\n"
                f"⏰ تنتهي خلال: **{المدة} ثانية**\n"
                f"🏆 عدد الفائزين: **{الفائزون}**"
            ),
            color=0xf1c40f
        )
        embed.set_footer(text=f"تنتهي: {ends_at.strftime('%H:%M:%S')} UTC")
        embed.set_thumbnail(url="https://i.imgur.com/TP7Opxj.png")

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")
        active_giveaways[msg.id] = True

        await asyncio.sleep(المدة)

        if msg.id not in active_giveaways:
            return

        try:
            msg = await ctx.channel.fetch_message(msg.id)
        except Exception:
            return

        reaction = discord.utils.get(msg.reactions, emoji="🎉")
        if not reaction:
            await ctx.send("❌ لم يشارك أحد في الهدية!")
            del active_giveaways[msg.id]
            return

        users = [u async for u in reaction.users() if not u.bot]

        if not users:
            await ctx.send("❌ لم يشارك أحد في الهدية!")
            del active_giveaways[msg.id]
            return

        winners = random.sample(users, min(الفائزون, len(users)))
        winners_mention = " | ".join([w.mention for w in winners])

        embed = discord.Embed(
            title="🎊 انتهت الهدية!",
            description=f"**الجائزة:** {الجائزة}\n\n🏆 **الفائز/الفائزون:** {winners_mention}",
            color=0x2ecc71
        )
        await msg.edit(embed=embed)
        await ctx.send(f"🎉 مبروك {winners_mention}! فزتم بـ **{الجائزة}**!")
        del active_giveaways[msg.id]

    @commands.command(name="هدية-سريعة")
    async def quick_giveaway(self, ctx, *, الجائزة: str):
        """هدية سريعة 30 ثانية للجميع. مثال: !هدية-سريعة نيترو"""
        embed = discord.Embed(
            title="⚡ هدية سريعة!",
            description=f"**الجائزة:** {الجائزة}\n\nتفاعل بـ 🎉 في 30 ثانية!\n🏆 فائز واحد",
            color=0xe67e22
        )
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")
        active_giveaways[msg.id] = True
        await asyncio.sleep(30)

        try:
            msg = await ctx.channel.fetch_message(msg.id)
        except Exception:
            return

        reaction = discord.utils.get(msg.reactions, emoji="🎉")
        users = [u async for u in reaction.users() if not u.bot] if reaction else []

        if not users:
            await ctx.send("❌ لم يشارك أحد!")
        else:
            winner = random.choice(users)
            await ctx.send(f"🎉 مبروك {winner.mention}! فزت بـ **{الجائزة}**!")

        del active_giveaways[msg.id]

    @commands.command(name="إلغاء-هدية")
    @commands.has_permissions(manage_guild=True)
    async def cancel_giveaway(self, ctx, message_id: int):
        """إلغاء هدية نشطة. مثال: !إلغاء-هدية [id الرسالة]"""
        if message_id in active_giveaways:
            del active_giveaways[message_id]
            await ctx.send("✅ تم إلغاء الهدية!")
        else:
            await ctx.send("❌ ما وجدت هدية بهذا الـ ID!")


async def setup(bot):
    await bot.add_cog(هدية(bot))
