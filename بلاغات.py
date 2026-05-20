import discord
from discord.ext import commands
import datetime

REPORT_CHANNEL_ID = 1505316741348331602   # قناة البلاغات
NOTIFY_ROLE_ID    = 1506457090191921282   # رتبة تُنبَّه عند ورود بلاغ
MOD_ROLE_ID       = 1505181303971250256   # رتبة الإشراف (تقدر ترفع بلاغ)


def is_mod():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        return any(r.id == MOD_ROLE_ID for r in ctx.author.roles)
    return commands.check(predicate)


async def send_dm(member: discord.Member, embed: discord.Embed):
    try:
        await member.send(embed=embed)
    except Exception:
        pass


# ─── Modals ───────────────────────────────────────────────────────────────────

class MuteDurationModal(discord.ui.Modal, title="⏱️ مدة الكتم"):
    duration = discord.ui.TextInput(
        label="المدة (بالدقائق)",
        placeholder="مثال: 10",
        min_length=1,
        max_length=5
    )

    def __init__(self, target: discord.Member, reporter: discord.Member,
                 reason: str, report_msg: discord.Message):
        super().__init__()
        self.target     = target
        self.reporter   = reporter
        self.reason     = reason
        self.report_msg = report_msg

    async def on_submit(self, interaction: discord.Interaction):
        try:
            mins = int(self.duration.value)
            if mins < 1 or mins > 40320:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                "❌ أدخل رقماً صحيحاً بين 1 و 40320 دقيقة!", ephemeral=True)
            return

        until = discord.utils.utcnow() + datetime.timedelta(minutes=mins)
        try:
            await self.target.timeout(until, reason=self.reason)
        except Exception as e:
            await interaction.response.send_message(f"❌ فشل الكتم: {e}", ephemeral=True)
            return

        # DM to violator
        dm = discord.Embed(
            title=f"🔇 تم كتمك في {interaction.guild.name}",
            description=f"📝 **السبب:** {self.reason}\n⏱️ **المدة:** {mins} دقيقة\n👮 **بواسطة:** {interaction.user.display_name}",
            color=0xe74c3c
        )
        await send_dm(self.target, dm)

        # Update report embed
        await _update_report(
            self.report_msg, interaction,
            f"🔇 تم الكتم لمدة {mins} دقيقة",
            0xe74c3c, self.reason
        )
        await interaction.response.send_message(
            f"✅ تم كتم {self.target.mention} لمدة **{mins} دقيقة**!", ephemeral=True)


# ─── Helper to update the report embed after action ──────────────────────────

async def _update_report(report_msg: discord.Message, interaction: discord.Interaction,
                          action: str, color: int, reason: str):
    try:
        old_embed = report_msg.embeds[0]
        new_embed = old_embed.copy()
        new_embed.color = discord.Color(color)
        new_embed.add_field(
            name="⚖️ الإجراء المتخذ",
            value=f"{action}\n👮 **بواسطة:** {interaction.user.mention}\n📝 **السبب:** {reason}",
            inline=False
        )
        new_embed.set_footer(text=f"✅ تمت المعالجة بواسطة {interaction.user.display_name}")
        await report_msg.edit(embed=new_embed, view=None)
    except Exception:
        pass


# ─── Action Buttons View ──────────────────────────────────────────────────────

class PunishView(discord.ui.View):
    def __init__(self, target: discord.Member, reporter: discord.Member, reason: str):
        super().__init__(timeout=None)
        self.target   = target
        self.reporter = reporter
        self.reason   = reason

    async def _check_permission(self, interaction: discord.Interaction) -> bool:
        has_role = any(r.id == NOTIFY_ROLE_ID for r in interaction.user.roles)
        is_admin = interaction.user.guild_permissions.administrator
        if not (has_role or is_admin):
            await interaction.response.send_message(
                "❌ فقط الإدارة العليا يمكنها تنفيذ الإجراءات!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="⏱️ كتم", style=discord.ButtonStyle.danger,
                        custom_id="punish_mute", row=0)
    async def mute_btn(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if not await self._check_permission(interaction):
            return
        await interaction.response.send_modal(
            MuteDurationModal(self.target, self.reporter, self.reason, interaction.message)
        )

    @discord.ui.button(label="🔨 حظر", style=discord.ButtonStyle.danger,
                        custom_id="punish_ban", row=0)
    async def ban_btn(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if not await self._check_permission(interaction):
            return
        try:
            dm = discord.Embed(
                title=f"🔨 تم حظرك من {interaction.guild.name}",
                description=f"📝 **السبب:** {self.reason}\n👮 **بواسطة:** {interaction.user.display_name}",
                color=0xe74c3c
            )
            await send_dm(self.target, dm)
            await self.target.ban(reason=self.reason)
        except Exception as e:
            await interaction.response.send_message(f"❌ فشل الحظر: {e}", ephemeral=True)
            return
        await _update_report(interaction.message, interaction, "🔨 تم الحظر", 0xe74c3c, self.reason)
        await interaction.response.send_message(
            f"✅ تم حظر **{self.target}**!", ephemeral=True)

    @discord.ui.button(label="👢 طرد", style=discord.ButtonStyle.secondary,
                        custom_id="punish_kick", row=0)
    async def kick_btn(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if not await self._check_permission(interaction):
            return
        try:
            dm = discord.Embed(
                title=f"👢 تم طردك من {interaction.guild.name}",
                description=f"📝 **السبب:** {self.reason}\n👮 **بواسطة:** {interaction.user.display_name}",
                color=0xe67e22
            )
            await send_dm(self.target, dm)
            await self.target.kick(reason=self.reason)
        except Exception as e:
            await interaction.response.send_message(f"❌ فشل الطرد: {e}", ephemeral=True)
            return
        await _update_report(interaction.message, interaction, "👢 تم الطرد", 0xe67e22, self.reason)
        await interaction.response.send_message(
            f"✅ تم طرد **{self.target}**!", ephemeral=True)

    @discord.ui.button(label="⚠️ تحذير", style=discord.ButtonStyle.primary,
                        custom_id="punish_warn", row=0)
    async def warn_btn(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if not await self._check_permission(interaction):
            return
        dm = discord.Embed(
            title=f"⚠️ تلقيت تحذيراً في {interaction.guild.name}",
            description=f"📝 **السبب:** {self.reason}\n👮 **بواسطة:** {interaction.user.display_name}",
            color=0xf39c12
        )
        await send_dm(self.target, dm)
        await _update_report(interaction.message, interaction, "⚠️ تم التحذير", 0xf39c12, self.reason)
        await interaction.response.send_message(
            f"✅ تم تحذير {self.target.mention}!", ephemeral=True)

    @discord.ui.button(label="✅ إغلاق البلاغ", style=discord.ButtonStyle.success,
                        custom_id="punish_close", row=1)
    async def close_btn(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if not await self._check_permission(interaction):
            return
        await _update_report(
            interaction.message, interaction,
            "✅ تم إغلاق البلاغ بدون إجراء", 0x95a5a6, self.reason
        )
        await interaction.response.send_message("✅ تم إغلاق البلاغ!", ephemeral=True)


# ─── Cog ─────────────────────────────────────────────────────────────────────

class بلاغات(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="بلاغ")
    @is_mod()
    async def report(self, ctx, مخالف: discord.Member, *, السبب: str):
        """رفع بلاغ على عضو مع دليل. مثال: !بلاغ @شخص يشتم في الشات"""
        if مخالف.bot:
            await ctx.send("❌ لا يمكنك رفع بلاغ على بوت!", delete_after=5)
            return
        if مخالف.id == ctx.author.id:
            await ctx.send("❌ لا تقدر ترفع بلاغ على نفسك!", delete_after=5)
            return

        # Check for image evidence
        image_url = None
        if ctx.message.attachments:
            att = ctx.message.attachments[0]
            if any(att.filename.lower().endswith(ext)
                   for ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".mov")):
                image_url = att.url

        report_ch = ctx.guild.get_channel(REPORT_CHANNEL_ID)
        if not report_ch:
            await ctx.send("❌ قناة البلاغات غير موجودة!", delete_after=5)
            return

        notify_role = ctx.guild.get_role(NOTIFY_ROLE_ID)

        # Build the report embed
        embed = discord.Embed(
            title="🚨 بلاغ جديد",
            description=(
                f"📌 **المخالف:** {مخالف.mention} (`{مخالف}` — `{مخالف.id}`)\n"
                f"📝 **سبب البلاغ:** {السبب}\n"
                f"👮 **رُفع بواسطة:** {ctx.author.mention}\n"
                f"📍 **القناة:** {ctx.channel.mention}\n"
                f"🕐 **الوقت:** <t:{int(ctx.message.created_at.timestamp())}:F>"
            ),
            color=0xe74c3c
        )
        embed.set_thumbnail(url=مخالف.display_avatar.url)

        if image_url:
            if image_url.endswith((".mp4", ".mov")):
                embed.add_field(name="🎥 الدليل (فيديو)", value=f"[اضغط لعرض الدليل]({image_url})", inline=False)
            else:
                embed.set_image(url=image_url)
                embed.add_field(name="📸 الدليل", value="موجود ⬆️", inline=False)
        else:
            embed.add_field(name="📸 الدليل", value="❌ لا يوجد دليل مرفق", inline=False)

        embed.set_footer(
            text=f"الإدارة: استخدم الأزرار لاتخاذ الإجراء",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )

        notify_mention = notify_role.mention if notify_role else ""
        view = PunishView(مخالف, ctx.author, السبب)

        await ctx.message.delete()
        report_msg = await report_ch.send(
            content=f"🚨 {notify_mention} — بلاغ جديد يحتاج مراجعة!",
            embed=embed,
            view=view
        )

        # Confirm to the mod
        confirm = discord.Embed(
            title="✅ تم رفع البلاغ",
            description=f"تم إرسال بلاغك إلى {report_ch.mention}",
            color=0x2ecc71
        )
        try:
            await ctx.author.send(embed=confirm)
        except Exception:
            pass

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ فقط المشرفين يمكنهم رفع البلاغات!", delete_after=5)
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ ما وجدت هذا العضو!", delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "❌ ناقص معلومات!\n**الاستخدام:** `!بلاغ @شخص سبب المخالفة`\n"
                "يمكنك إرفاق صورة دليل مع الأمر.", delete_after=8
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(بلاغات(bot))
