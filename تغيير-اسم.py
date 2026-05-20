import discord
from discord.ext import commands
import asyncio


class NicknameButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="✏️ تغيير اسمك",
        style=discord.ButtonStyle.primary,
        custom_id="nickname_ticket_btn",
        emoji="✏️"
    )
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user

        existing = discord.utils.get(guild.text_channels, name=f"اسم-{member.name.lower()[:15]}")
        if existing:
            await interaction.response.send_message(
                f"❌ عندك قناة مفتوحة بالفعل! {existing.mention}",
                ephemeral=True
            )
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
        }

        category = interaction.channel.category
        channel = await guild.create_text_channel(
            name=f"اسم-{member.name[:15]}",
            overwrites=overwrites,
            category=category,
            topic=f"تغيير اسم {member.display_name}"
        )

        embed = discord.Embed(
            title="✏️ تغيير الاسم",
            description=(
                f"مرحباً {member.mention}!\n\n"
                "📝 **اكتب اسمك الجديد** في هذه القناة:\n\n"
                "• الاسم يجب بين **2 و 32 حرف**\n"
                "• القناة ستُغلق تلقائياً بعد الإجابة\n\n"
                "⏰ عندك **60 ثانية** للرد!"
            ),
            color=0x3498db
        )
        embed.set_footer(text="اكتب اسمك الجديد أدناه ⬇️")

        close_view = CloseView()
        msg = await channel.send(content=member.mention, embed=embed, view=close_view)

        await interaction.response.send_message(
            f"✅ تم فتح قناة خاصة لك: {channel.mention}",
            ephemeral=True
        )

        def check(m):
            return m.channel == channel and m.author == member and not m.author.bot

        try:
            reply = await interaction.client.wait_for("message", check=check, timeout=60.0)
            new_name = reply.content.strip()

            if len(new_name) < 2 or len(new_name) > 32:
                await channel.send("❌ الاسم يجب بين 2 و 32 حرف! سيتم إغلاق القناة...")
                await asyncio.sleep(3)
                await channel.delete()
                return

            try:
                await member.edit(nick=new_name)
                embed_done = discord.Embed(
                    title="✅ تم تغيير الاسم!",
                    description=f"اسمك الجديد: **{new_name}**\n\nستُغلق هذه القناة خلال 5 ثواني.",
                    color=0x2ecc71
                )
                await channel.send(embed=embed_done)
            except discord.Forbidden:
                embed_err = discord.Embed(
                    title="❌ تعذّر تغيير الاسم",
                    description="ما أقدر أغير اسمك. تواصل مع الإدارة.\n\nستُغلق هذه القناة خلال 5 ثواني.",
                    color=0xe74c3c
                )
                await channel.send(embed=embed_err)

            await asyncio.sleep(5)
            await channel.delete()

        except asyncio.TimeoutError:
            embed_timeout = discord.Embed(
                title="⏰ انتهى الوقت!",
                description="لم تكتب اسمك في الوقت المحدد. ستُغلق القناة الآن.",
                color=0xe74c3c
            )
            await channel.send(embed=embed_timeout)
            await asyncio.sleep(3)
            await channel.delete()


class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="❌ إغلاق", style=discord.ButtonStyle.danger, custom_id="close_nickname_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("سيتم إغلاق القناة...", ephemeral=True)
        await asyncio.sleep(2)
        await interaction.channel.delete()


class تغيير_اسم(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(NicknameButton())
        bot.add_view(CloseView())

    @commands.command(name="زر-اسم")
    @commands.has_permissions(administrator=True)
    async def send_nickname_panel(self, ctx, *, العنوان: str = "تغيير الاسم"):
        """إرسال لوحة تغيير الاسم. مثال: !زر-اسم"""
        await ctx.message.delete()
        embed = discord.Embed(
            title=f"✏️ {العنوان}",
            description=(
                "اضغط على الزر أدناه لتغيير اسمك في السيرفر!\n\n"
                "🎫 ستُفتح لك قناة خاصة تكتب فيها اسمك الجديد."
            ),
            color=0x3498db
        )
        embed.set_footer(text=ctx.guild.name)
        await ctx.send(embed=embed, view=NicknameButton())

    @commands.command(name="اعادة-اسم")
    @commands.has_permissions(manage_nicknames=True)
    async def reset_nickname(self, ctx, عضو: discord.Member):
        """إعادة تعيين اسم عضو للأصل. مثال: !اعادة-اسم @شخص"""
        await عضو.edit(nick=None)
        await ctx.send(f"✅ تم إعادة اسم {عضو.mention} للاسم الأصلي.")

    @commands.command(name="غير-اسم")
    @commands.has_permissions(manage_nicknames=True)
    async def change_nick(self, ctx, عضو: discord.Member, *, الاسم: str):
        """غيّر اسم عضو يدوياً. مثال: !غير-اسم @شخص الاسم الجديد"""
        try:
            await عضو.edit(nick=الاسم)
            await ctx.send(f"✅ تم تغيير اسم {عضو.mention} إلى **{الاسم}**!")
        except discord.Forbidden:
            await ctx.send("❌ ما أقدر أغير اسم هذا العضو!")


async def setup(bot):
    await bot.add_cog(تغيير_اسم(bot))
