import discord
from discord.ext import commands
import asyncio

MOD_ROLE_ID = 1505181303971250256


def is_mod():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        return any(r.id == MOD_ROLE_ID for r in ctx.author.roles)
    return commands.check(predicate)


def can_ban():
    async def predicate(ctx):
        if any(r.id == MOD_ROLE_ID for r in ctx.author.roles):
            return False
        return ctx.author.guild_permissions.ban_members or ctx.author.guild_permissions.administrator
    return commands.check(predicate)


async def send_dm(member: discord.Member, embed: discord.Embed):
    try:
        await member.send(embed=embed)
    except Exception:
        pass


class إدارة(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="مسح")
    @is_mod()
    async def clear(self, ctx, العدد: int = 10):
        """مسح رسائل. مثال: !مسح 20"""
        if العدد < 1 or العدد > 100:
            await ctx.send("❌ أدخل رقماً بين 1 و 100!")
            return
        deleted = await ctx.channel.purge(limit=العدد + 1)
        msg = await ctx.send(f"✅ تم مسح **{len(deleted)-1}** رسالة!")
        await asyncio.sleep(3)
        await msg.delete()

    @commands.command(name="كتم")
    @is_mod()
    async def mute(self, ctx, عضو: discord.Member, الدقائق: int = 10, *, السبب: str = "لم يذكر"):
        """كتم عضو. مثال: !كتم @شخص 10 كلام غير لائق"""
        import datetime
        until = discord.utils.utcnow() + datetime.timedelta(minutes=الدقائق)
        await عضو.timeout(until, reason=السبب)

        embed = discord.Embed(title="🔇 تم الكتم", color=0xe74c3c)
        embed.add_field(name="👤 العضو",   value=عضو.mention,              inline=True)
        embed.add_field(name="⏱️ المدة",   value=f"{الدقائق} دقيقة",       inline=True)
        embed.add_field(name="📝 السبب",   value=السبب,                    inline=False)
        embed.add_field(name="👮 المشرف",  value=ctx.author.mention,        inline=True)
        await ctx.send(embed=embed)

        dm = discord.Embed(
            title=f"🔇 تم كتمك في {ctx.guild.name}",
            description=f"📝 **السبب:** {السبب}\n⏱️ **المدة:** {الدقائق} دقيقة\n👮 **بواسطة:** {ctx.author.display_name}",
            color=0xe74c3c
        )
        await send_dm(عضو, dm)

    @commands.command(name="فك-كتم")
    @is_mod()
    async def unmute(self, ctx, عضو: discord.Member):
        """فك كتم عضو. مثال: !فك-كتم @شخص"""
        await عضو.timeout(None)
        embed = discord.Embed(
            title="🔊 تم فك الكتم",
            description=f"{عضو.mention} تم رفع الكتم عنه.",
            color=0x2ecc71
        )
        await ctx.send(embed=embed)

        dm = discord.Embed(
            title=f"🔊 تم فك الكتم عنك في {ctx.guild.name}",
            description=f"👮 **بواسطة:** {ctx.author.display_name}",
            color=0x2ecc71
        )
        await send_dm(عضو, dm)

    @commands.command(name="طرد")
    @is_mod()
    async def kick(self, ctx, عضو: discord.Member, *, السبب: str = "لم يذكر"):
        """طرد عضو. مثال: !طرد @شخص السبب"""
        if عضو.top_role >= ctx.author.top_role and not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ لا تستطيع طرد هذا العضو!")
            return

        dm = discord.Embed(
            title=f"👢 تم طردك من {ctx.guild.name}",
            description=f"📝 **السبب:** {السبب}\n👮 **بواسطة:** {ctx.author.display_name}",
            color=0xe67e22
        )
        await send_dm(عضو, dm)

        await عضو.kick(reason=السبب)
        embed = discord.Embed(title="👢 تم الطرد", color=0xe67e22)
        embed.add_field(name="👤 العضو",  value=str(عضو),          inline=True)
        embed.add_field(name="📝 السبب",  value=السبب,             inline=False)
        embed.add_field(name="👮 المشرف", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="حظر")
    @can_ban()
    async def ban(self, ctx, عضو: discord.Member, *, السبب: str = "لم يذكر"):
        """حظر عضو (أدمن فقط). مثال: !حظر @شخص السبب"""
        if عضو.top_role >= ctx.author.top_role and not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ لا تستطيع حظر هذا العضو!")
            return

        dm = discord.Embed(
            title=f"🔨 تم حظرك من {ctx.guild.name}",
            description=f"📝 **السبب:** {السبب}\n👮 **بواسطة:** {ctx.author.display_name}",
            color=0xe74c3c
        )
        await send_dm(عضو, dm)

        await عضو.ban(reason=السبب)
        embed = discord.Embed(title="🔨 تم الحظر", color=0xe74c3c)
        embed.add_field(name="👤 العضو",  value=str(عضو),          inline=True)
        embed.add_field(name="📝 السبب",  value=السبب,             inline=False)
        embed.add_field(name="👮 المشرف", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="فك-حظر")
    @is_mod()
    async def unban(self, ctx, *, الاسم: str):
        """فك حظر عضو. مثال: !فك-حظر اسم#1234 أو !فك-حظر 123456789"""
        banned = [entry async for entry in ctx.guild.bans()]
        for ban_entry in banned:
            user = ban_entry.user
            if str(user) == الاسم or str(user.id) == الاسم:
                await ctx.guild.unban(user)
                embed = discord.Embed(
                    title="✅ تم فك الحظر",
                    description=f"تم فك حظر **{user}**.\n👮 **بواسطة:** {ctx.author.mention}",
                    color=0x2ecc71
                )
                await ctx.send(embed=embed)
                try:
                    dm = discord.Embed(
                        title=f"✅ تم فك حظرك في {ctx.guild.name}",
                        description=f"👮 **بواسطة:** {ctx.author.display_name}\nيمكنك الانضمام مجدداً.",
                        color=0x2ecc71
                    )
                    await user.send(embed=dm)
                except Exception:
                    pass
                return
        await ctx.send(f"❌ ما وجدت عضواً محظوراً باسم أو ID: **{الاسم}**")

    @commands.command(name="تحذير")
    @is_mod()
    async def warn(self, ctx, عضو: discord.Member, *, السبب: str = "لم يذكر"):
        """إرسال تحذير لعضو. مثال: !تحذير @شخص السبب"""
        embed = discord.Embed(title="⚠️ تحذير", color=0xf39c12)
        embed.add_field(name="👤 العضو",  value=عضو.mention,       inline=True)
        embed.add_field(name="📝 السبب",  value=السبب,            inline=False)
        embed.add_field(name="👮 المشرف", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)

        dm = discord.Embed(
            title=f"⚠️ تلقيت تحذيراً في {ctx.guild.name}",
            description=f"📝 **السبب:** {السبب}\n👮 **بواسطة:** {ctx.author.display_name}",
            color=0xf39c12
        )
        await send_dm(عضو, dm)

    @commands.command(name="قفل")
    @is_mod()
    async def lock(self, ctx):
        """قفل القناة الحالية"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔒 تم قفل القناة!")

    @commands.command(name="فتح")
    @is_mod()
    async def unlock(self, ctx):
        """فتح القناة الحالية"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔓 تم فتح القناة!")

    @commands.command(name="إعلان")
    @is_mod()
    async def announce(self, ctx, *, النص: str):
        """إرسال إعلان مُنسق. مثال: !إعلان مرحباً بالجميع!"""
        embed = discord.Embed(title="📢 إعلان", description=النص, color=0x3498db)
        embed.set_footer(text=f"بواسطة {ctx.author.display_name}")
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command(name="تصويت")
    @is_mod()
    async def poll(self, ctx, *, السؤال: str):
        """إنشاء تصويت. مثال: !تصويت هل تحبون القهوة؟"""
        embed = discord.Embed(title="📊 تصويت", description=السؤال, color=0x9b59b6)
        embed.set_footer(text=f"بواسطة {ctx.author.display_name}")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        await msg.add_reaction("🤷")

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            if ctx.command and ctx.command.name == "حظر":
                await ctx.send("❌ رتبتك لا تملك صلاحية استخدام أمر الحظر!")
            else:
                await ctx.send("❌ ما عندك صلاحية لهذا الأمر!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ ما وجدت هذا العضو!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ ناقص معلومات! تحقق من الأمر وحاول مرة ثانية.")


async def setup(bot):
    await bot.add_cog(إدارة(bot))
