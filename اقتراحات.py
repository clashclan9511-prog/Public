import discord
from discord.ext import commands
import json
import os

CONFIG_FILE = "data/suggestions_config.json"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(data):
    os.makedirs("data", exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class اقتراحات(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        config = load_config()
        guild_id = str(message.guild.id) if message.guild else None
        if not guild_id:
            return

        suggestion_channel_id = config.get(guild_id, {}).get("suggestions_channel")
        if not suggestion_channel_id:
            return
        if message.channel.id != suggestion_channel_id:
            return

        await message.delete()

        embed = discord.Embed(
            title="💡 اقتراح جديد",
            description=message.content,
            color=0x3498db
        )
        embed.set_author(
            name=message.author.display_name,
            icon_url=message.author.display_avatar.url
        )
        embed.set_footer(text=f"🆔 {message.author.id} | اقترح بواسطة {message.author.display_name}")

        sent = await message.channel.send(embed=embed)
        await sent.add_reaction("✅")
        await sent.add_reaction("❌")

    @commands.command(name="روم-اقتراحات")
    @commands.has_permissions(administrator=True)
    async def set_suggestions_channel(self, ctx, قناة: discord.TextChannel = None):
        """تعيين قناة الاقتراحات. مثال: !روم-اقتراحات #اقتراحات"""
        config = load_config()
        guild_id = str(ctx.guild.id)
        if guild_id not in config:
            config[guild_id] = {}

        if قناة:
            config[guild_id]["suggestions_channel"] = قناة.id
            save_config(config)

            embed = discord.Embed(
                title="✅ تم تعيين قناة الاقتراحات",
                description=(
                    f"القناة: {قناة.mention}\n\n"
                    "أي رسالة تُكتب في هذه القناة ستتحول تلقائياً لاقتراح مع ✅ و ❌"
                ),
                color=0x2ecc71
            )
            await ctx.send(embed=embed)
        else:
            config[guild_id].pop("suggestions_channel", None)
            save_config(config)
            await ctx.send("✅ تم إلغاء قناة الاقتراحات.")

    @commands.command(name="قبول-اقتراح")
    @commands.has_permissions(manage_guild=True)
    async def accept_suggestion(self, ctx, message_id: int, *, السبب: str = "تم قبوله من الإدارة"):
        """قبول اقتراح. مثال: !قبول-اقتراح [ID الرسالة] السبب"""
        try:
            msg = await ctx.channel.fetch_message(message_id)
        except Exception:
            await ctx.send("❌ ما وجدت الرسالة في هذه القناة!")
            return

        if not msg.embeds:
            await ctx.send("❌ هذه الرسالة ليست اقتراحاً!")
            return

        old_embed = msg.embeds[0]
        new_embed = discord.Embed(
            title="✅ اقتراح مقبول",
            description=old_embed.description,
            color=0x2ecc71
        )
        if old_embed.author:
            new_embed.set_author(name=old_embed.author.name, icon_url=old_embed.author.icon_url)
        new_embed.add_field(name="📋 قرار الإدارة", value=f"✅ **مقبول** — {السبب}", inline=False)
        new_embed.set_footer(text=f"بواسطة {ctx.author.display_name}")

        await msg.edit(embed=new_embed)
        await ctx.message.delete()

    @commands.command(name="رفض-اقتراح")
    @commands.has_permissions(manage_guild=True)
    async def reject_suggestion(self, ctx, message_id: int, *, السبب: str = "لا يناسب السيرفر حالياً"):
        """رفض اقتراح. مثال: !رفض-اقتراح [ID الرسالة] السبب"""
        try:
            msg = await ctx.channel.fetch_message(message_id)
        except Exception:
            await ctx.send("❌ ما وجدت الرسالة في هذه القناة!")
            return

        if not msg.embeds:
            await ctx.send("❌ هذه الرسالة ليست اقتراحاً!")
            return

        old_embed = msg.embeds[0]
        new_embed = discord.Embed(
            title="❌ اقتراح مرفوض",
            description=old_embed.description,
            color=0xe74c3c
        )
        if old_embed.author:
            new_embed.set_author(name=old_embed.author.name, icon_url=old_embed.author.icon_url)
        new_embed.add_field(name="📋 قرار الإدارة", value=f"❌ **مرفوض** — {السبب}", inline=False)
        new_embed.set_footer(text=f"بواسطة {ctx.author.display_name}")

        await msg.edit(embed=new_embed)
        await ctx.message.delete()

    @commands.command(name="اقتراح-يدوي")
    async def manual_suggestion(self, ctx, *, الاقتراح: str):
        """إرسال اقتراح من أي قناة. مثال: !اقتراح-يدوي أضيفوا بوت موسيقى"""
        config = load_config()
        guild_id = str(ctx.guild.id)
        channel_id = config.get(guild_id, {}).get("suggestions_channel")

        if not channel_id:
            await ctx.send("❌ لم يتم تعيين قناة الاقتراحات بعد! استخدم `!روم-اقتراحات #قناة`")
            return

        channel = ctx.guild.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ قناة الاقتراحات غير موجودة!")
            return

        embed = discord.Embed(
            title="💡 اقتراح جديد",
            description=الاقتراح,
            color=0x3498db
        )
        embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.display_avatar.url
        )
        embed.set_footer(text=f"🆔 {ctx.author.id} | اقترح بواسطة {ctx.author.display_name}")

        sent = await channel.send(embed=embed)
        await sent.add_reaction("✅")
        await sent.add_reaction("❌")

        await ctx.message.delete()
        confirm = await ctx.send(f"✅ تم إرسال اقتراحك إلى {channel.mention}!")
        import asyncio
        await asyncio.sleep(4)
        await confirm.delete()


async def setup(bot):
    await bot.add_cog(اقتراحات(bot))
