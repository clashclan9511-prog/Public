import discord
from discord.ext import commands
import json
import os

CONFIG_FILE = "data/welcome_config.json"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(data):
    os.makedirs("data", exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class ترحيب(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        config = load_config()
        guild_id = str(member.guild.id)
        if guild_id not in config or not config[guild_id].get("welcome_channel"):
            return
        channel_id = config[guild_id]["welcome_channel"]
        channel = member.guild.get_channel(channel_id)
        if not channel:
            return
        msg = config[guild_id].get("welcome_msg", "مرحباً بك يا {member}!")
        msg = msg.replace("{member}", member.mention).replace("{server}", member.guild.name).replace("{count}", str(member.guild.member_count))
        embed = discord.Embed(
            title="👋 عضو جديد!",
            description=msg,
            color=0x2ecc71
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="👤 الاسم", value=str(member), inline=True)
        embed.add_field(name="🆔 الآيدي", value=member.id, inline=True)
        embed.add_field(name="👥 عدد الأعضاء", value=member.guild.member_count, inline=True)
        embed.set_footer(text=f"📅 {member.created_at.strftime('%Y-%m-%d')}")
        await channel.send(embed=embed)

        auto_role_id = config[guild_id].get("auto_role")
        if auto_role_id:
            role = member.guild.get_role(auto_role_id)
            if role:
                try:
                    await member.add_roles(role)
                except Exception:
                    pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        config = load_config()
        guild_id = str(member.guild.id)
        if guild_id not in config or not config[guild_id].get("goodbye_channel"):
            return
        channel_id = config[guild_id]["goodbye_channel"]
        channel = member.guild.get_channel(channel_id)
        if not channel:
            return
        embed = discord.Embed(
            title="👋 وداعاً!",
            description=f"غادر **{member.display_name}** السيرفر. نتمنى نشوفه مرة ثانية!",
            color=0xe74c3c
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

    @commands.command(name="قناة-ترحيب")
    @commands.has_permissions(administrator=True)
    async def set_welcome(self, ctx, قناة: discord.TextChannel = None):
        """تعيين قناة الترحيب. مثال: !قناة-ترحيب #ترحيب"""
        config = load_config()
        guild_id = str(ctx.guild.id)
        if guild_id not in config:
            config[guild_id] = {}
        if قناة:
            config[guild_id]["welcome_channel"] = قناة.id
            save_config(config)
            await ctx.send(f"✅ تم تعيين {قناة.mention} كقناة الترحيب!")
        else:
            config[guild_id].pop("welcome_channel", None)
            save_config(config)
            await ctx.send("✅ تم إلغاء قناة الترحيب.")

    @commands.command(name="قناة-وداع")
    @commands.has_permissions(administrator=True)
    async def set_goodbye(self, ctx, قناة: discord.TextChannel = None):
        """تعيين قناة الوداع. مثال: !قناة-وداع #وداع"""
        config = load_config()
        guild_id = str(ctx.guild.id)
        if guild_id not in config:
            config[guild_id] = {}
        if قناة:
            config[guild_id]["goodbye_channel"] = قناة.id
            save_config(config)
            await ctx.send(f"✅ تم تعيين {قناة.mention} كقناة الوداع!")
        else:
            config[guild_id].pop("goodbye_channel", None)
            save_config(config)
            await ctx.send("✅ تم إلغاء قناة الوداع.")

    @commands.command(name="رسالة-ترحيب")
    @commands.has_permissions(administrator=True)
    async def set_welcome_msg(self, ctx, *, الرسالة: str):
        """تخصيص رسالة الترحيب. استخدم {member} {server} {count}"""
        config = load_config()
        guild_id = str(ctx.guild.id)
        if guild_id not in config:
            config[guild_id] = {}
        config[guild_id]["welcome_msg"] = الرسالة
        save_config(config)
        preview = الرسالة.replace("{member}", ctx.author.mention).replace("{server}", ctx.guild.name).replace("{count}", str(ctx.guild.member_count))
        embed = discord.Embed(title="✅ تم تعيين رسالة الترحيب", description=f"**معاينة:**\n{preview}", color=0x2ecc71)
        await ctx.send(embed=embed)

    @commands.command(name="رتبة-تلقائية")
    @commands.has_permissions(administrator=True)
    async def auto_role(self, ctx, رتبة: discord.Role = None):
        """تعيين رتبة تلقائية للأعضاء الجدد. مثال: !رتبة-تلقائية @عضو"""
        config = load_config()
        guild_id = str(ctx.guild.id)
        if guild_id not in config:
            config[guild_id] = {}
        if رتبة:
            config[guild_id]["auto_role"] = رتبة.id
            save_config(config)
            await ctx.send(f"✅ سيحصل الأعضاء الجدد على رتبة {رتبة.mention} تلقائياً!")
        else:
            config[guild_id].pop("auto_role", None)
            save_config(config)
            await ctx.send("✅ تم إلغاء الرتبة التلقائية.")

    @commands.command(name="اختبار-ترحيب")
    @commands.has_permissions(administrator=True)
    async def test_welcome(self, ctx):
        """اختبار رسالة الترحيب"""
        await self.on_member_join(ctx.author)
        await ctx.send("✅ تم إرسال رسالة ترحيب تجريبية!")


async def setup(bot):
    await bot.add_cog(ترحيب(bot))
