import discord
from discord.ext import commands
from datetime import datetime

MOD_ROLE_ID  = 1505181303971250256
HELP_ROLE_ID = 1505174149625151529


def is_staff():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        return any(r.id in (MOD_ROLE_ID, HELP_ROLE_ID) for r in ctx.author.roles)
    return commands.check(predicate)


class معلومات(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── مفتوحة للجميع ────────────────────────────────────────────────────────

    @commands.command(name="سيرفر")
    async def server_info(self, ctx):
        """معلومات عن السيرفر"""
        g = ctx.guild
        embed = discord.Embed(title=f"🏠 معلومات {g.name}", color=0x2ecc71)
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name="👑 المالك",      value=g.owner.mention if g.owner else "غير معروف", inline=True)
        embed.add_field(name="🆔 الآيدي",      value=g.id,                                        inline=True)
        embed.add_field(name="📅 تاريخ الإنشاء",value=g.created_at.strftime("%Y-%m-%d"),           inline=True)
        embed.add_field(name="👥 الأعضاء",     value=g.member_count,                              inline=True)
        embed.add_field(name="💬 القنوات",     value=len(g.channels),                             inline=True)
        embed.add_field(name="🎭 الرتب",       value=len(g.roles),                                inline=True)
        embed.add_field(name="😀 الإيموجي",    value=len(g.emojis),                               inline=True)
        embed.add_field(name="🚀 البوستات",    value=f"{g.premium_subscription_count} | مستوى {g.premium_tier}", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="وقت")
    async def current_time(self, ctx):
        """الوقت والتاريخ الحالي"""
        now = datetime.utcnow()
        embed = discord.Embed(
            title="🕐 الوقت الحالي",
            description=f"**{now.strftime('%Y-%m-%d')}**\n🕐 {now.strftime('%H:%M:%S')} UTC",
            color=0x3498db
        )
        await ctx.send(embed=embed)

    # ── للمشرفين فقط ─────────────────────────────────────────────────────────

    @commands.command(name="بروفايل")
    @is_staff()
    async def profile(self, ctx, عضو: discord.Member = None):
        """عرض بروفايل عضو. مثال: !بروفايل @شخص"""
        عضو = عضو or ctx.author
        roles = [r.mention for r in عضو.roles if r.name != "@everyone"]
        embed = discord.Embed(
            title=f"👤 بروفايل {عضو.display_name}",
            color=عضو.color if عضو.color.value != 0 else 0x3498db
        )
        embed.set_thumbnail(url=عضو.display_avatar.url)
        embed.add_field(name="🏷️ الاسم",        value=str(عضو),                                                inline=True)
        embed.add_field(name="🆔 الآيدي",        value=عضو.id,                                                 inline=True)
        embed.add_field(name="📅 تاريخ الإنشاء", value=عضو.created_at.strftime("%Y-%m-%d"),                    inline=True)
        embed.add_field(name="📥 تاريخ الانضمام",value=عضو.joined_at.strftime("%Y-%m-%d") if عضو.joined_at else "غير معروف", inline=True)
        embed.add_field(name="🤖 بوت؟",          value="نعم" if عضو.bot else "لا",                             inline=True)
        embed.add_field(name=f"🎭 الرتب ({len(roles)})", value=" ".join(roles) if roles else "لا توجد",        inline=False)
        embed.set_footer(text=f"طلب بواسطة {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @commands.command(name="بينق")
    @is_staff()
    async def ping(self, ctx):
        """تحقق من سرعة البوت"""
        latency = round(self.bot.latency * 1000)
        color = 0x2ecc71 if latency < 100 else (0xf39c12 if latency < 200 else 0xe74c3c)
        embed = discord.Embed(
            title="🏓 بينق!",
            description=f"⚡ السرعة: **{latency}ms**",
            color=color
        )
        await ctx.send(embed=embed)

    @commands.command(name="عد")
    @is_staff()
    async def member_count(self, ctx):
        """عد أعضاء السيرفر"""
        g = ctx.guild
        bots   = sum(1 for m in g.members if m.bot)
        humans = g.member_count - bots
        embed = discord.Embed(title="👥 عدد الأعضاء", color=0x9b59b6)
        embed.add_field(name="👤 البشر",    value=humans,        inline=True)
        embed.add_field(name="🤖 البوتات",  value=bots,          inline=True)
        embed.add_field(name="📊 الإجمالي", value=g.member_count, inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="رتبة")
    @is_staff()
    async def role_info(self, ctx, *, اسم_الرتبة: str):
        """معلومات عن رتبة. مثال: !رتبة Admin"""
        role = discord.utils.find(lambda r: r.name.lower() == اسم_الرتبة.lower(), ctx.guild.roles)
        if not role:
            await ctx.send(f"❌ ما وجدت رتبة باسم **{اسم_الرتبة}**")
            return
        embed = discord.Embed(title=f"🎭 رتبة: {role.name}", color=role.color)
        embed.add_field(name="🆔 الآيدي",   value=role.id,                           inline=True)
        embed.add_field(name="👥 الأعضاء",  value=len(role.members),                 inline=True)
        embed.add_field(name="📌 منشن؟",    value="نعم" if role.mentionable else "لا", inline=True)
        embed.add_field(name="🎨 اللون",    value=str(role.color),                   inline=True)
        embed.add_field(name="📅 الإنشاء",  value=role.created_at.strftime("%Y-%m-%d"), inline=True)
        await ctx.send(embed=embed)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(معلومات(bot))
