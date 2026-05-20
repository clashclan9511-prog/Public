import discord
from discord.ext import commands

JOIN_TO_CREATE_ID = 1505135835974991964
CATEGORY_ID       = 1505135792572596224
PANEL_CHANNEL_ID  = 1505135835974991964

# owner_id -> channel_id
voice_channels: dict[int, int] = {}


# ─── Modals ──────────────────────────────────────────────────────────────────

class RenameModal(discord.ui.Modal, title="✏️ تغيير اسم الروم"):
    new_name = discord.ui.TextInput(
        label="الاسم الجديد",
        placeholder="مثال: روم الأصدقاء",
        min_length=1,
        max_length=50
    )

    def __init__(self, channel: discord.VoiceChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await self.channel.edit(name=self.new_name.value)
            await interaction.response.send_message(
                f"✅ تم تغيير الاسم إلى **{self.new_name.value}**", ephemeral=True)
        except Exception:
            await interaction.response.send_message("❌ فشل تغيير الاسم!", ephemeral=True)


class LimitModal(discord.ui.Modal, title="👥 تحديد عدد الأعضاء"):
    limit = discord.ui.TextInput(
        label="العدد الأقصى (0 = بدون حد)",
        placeholder="مثال: 5",
        min_length=1,
        max_length=2
    )

    def __init__(self, channel: discord.VoiceChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        try:
            val = int(self.limit.value)
            if val < 0 or val > 99:
                raise ValueError
            await self.channel.edit(user_limit=val)
            msg = f"✅ تم تحديد الحد بـ **{val}** عضو" if val > 0 else "✅ تم إزالة حد الأعضاء"
            await interaction.response.send_message(msg, ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ أدخل رقماً بين 0 و 99!", ephemeral=True)


# ─── Kick select ─────────────────────────────────────────────────────────────

class KickSelect(discord.ui.Select):
    def __init__(self, channel: discord.VoiceChannel, members: list[discord.Member]):
        self.vc = channel
        options = [
            discord.SelectOption(label=m.display_name, value=str(m.id))
            for m in members
        ]
        super().__init__(placeholder="اختر من تريد طرده...", options=options)

    async def callback(self, interaction: discord.Interaction):
        member = interaction.guild.get_member(int(self.values[0]))
        if member and member.voice and member.voice.channel == self.vc:
            await member.move_to(None)
            await interaction.response.send_message(
                f"👢 تم طرد **{member.display_name}** من الروم!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ هذا الشخص غادر الروم مسبقاً!", ephemeral=True)


class KickView(discord.ui.View):
    def __init__(self, channel, members):
        super().__init__(timeout=30)
        self.add_item(KickSelect(channel, members))


# ─── Control Panel ───────────────────────────────────────────────────────────

class ControlPanel(discord.ui.View):
    def __init__(self, channel: discord.VoiceChannel, owner_id: int):
        super().__init__(timeout=None)
        self.channel   = channel
        self.owner_id  = owner_id

    async def _check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "❌ فقط صاحب الروم يستطيع التحكم!", ephemeral=True)
            return False
        vc = interaction.user.voice
        if not vc or vc.channel != self.channel:
            await interaction.response.send_message(
                "❌ يجب أن تكون داخل الروم لاستخدام اللوحة!", ephemeral=True)
            return False
        return True

    # ── Row 0 ────────────────────────────────────────────────────────────────

    @discord.ui.button(label="✏️ تغيير الاسم",
                       style=discord.ButtonStyle.primary, row=0)
    async def rename(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if not await self._check(interaction):
            return
        await interaction.response.send_modal(RenameModal(self.channel))

    @discord.ui.button(label="🔒 إغلاق الروم",
                       style=discord.ButtonStyle.danger, row=0)
    async def lock(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if not await self._check(interaction):
            return
        ow = self.channel.overwrites_for(interaction.guild.default_role)
        ow.connect = False
        await self.channel.set_permissions(interaction.guild.default_role, overwrite=ow)
        await interaction.response.send_message("🔒 تم إغلاق الروم! لا أحد يستطيع الدخول الآن.", ephemeral=True)

    @discord.ui.button(label="🔓 فتح الروم",
                       style=discord.ButtonStyle.success, row=0)
    async def unlock(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if not await self._check(interaction):
            return
        ow = self.channel.overwrites_for(interaction.guild.default_role)
        ow.connect = None
        await self.channel.set_permissions(interaction.guild.default_role, overwrite=ow)
        await interaction.response.send_message("🔓 تم فتح الروم! يمكن للجميع الدخول.", ephemeral=True)

    # ── Row 1 ────────────────────────────────────────────────────────────────

    @discord.ui.button(label="👥 تحديد الأعضاء",
                       style=discord.ButtonStyle.secondary, row=1)
    async def set_limit(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if not await self._check(interaction):
            return
        await interaction.response.send_modal(LimitModal(self.channel))

    @discord.ui.button(label="👢 طرد شخص",
                       style=discord.ButtonStyle.danger, row=1)
    async def kick_member(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if not await self._check(interaction):
            return
        members = [m for m in self.channel.members if m.id != self.owner_id]
        if not members:
            await interaction.response.send_message("❌ لا يوجد أحد آخر في الروم!", ephemeral=True)
            return
        await interaction.response.send_message(
            "اختر من تريد طرده:", view=KickView(self.channel, members), ephemeral=True)

    @discord.ui.button(label="🗑️ حذف الروم",
                       style=discord.ButtonStyle.danger, row=1)
    async def delete_room(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if not await self._check(interaction):
            return
        await interaction.response.send_message("✅ تم حذف رومك!", ephemeral=True)
        try:
            await self.channel.delete()
        except Exception:
            pass
        voice_channels.pop(self.owner_id, None)
        self.stop()


# ─── Cog ─────────────────────────────────────────────────────────────────────

class صوت(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        guild = member.guild

        # ── User joins the "join to create" channel ──────────────────────────
        if after.channel and after.channel.id == JOIN_TO_CREATE_ID:
            category = guild.get_channel(CATEGORY_ID)
            if not isinstance(category, discord.CategoryChannel):
                category = after.channel.category

            new_vc = await guild.create_voice_channel(
                name=f"🎮 روم {member.display_name}",
                category=category
            )
            await member.move_to(new_vc)

            embed = discord.Embed(
                title="🎮 لوحة التحكم في الروم",
                description=(
                    f"👤 **صاحب الروم:** {member.mention}\n"
                    f"🔊 **الروم:** {new_vc.mention}\n\n"
                    "استخدم الأزرار أدناه للتحكم الكامل في رومك الصوتي:"
                ),
                color=0x5865f2
            )
            embed.add_field(name="✏️ تغيير الاسم",  value="غيّر اسم الروم",          inline=True)
            embed.add_field(name="🔒 إغلاق",         value="امنع الدخول",             inline=True)
            embed.add_field(name="🔓 فتح",            value="السماح بالدخول",          inline=True)
            embed.add_field(name="👥 حد الأعضاء",    value="حدد أقصى عدد",            inline=True)
            embed.add_field(name="👢 طرد",            value="أطرد شخصاً من الروم",     inline=True)
            embed.add_field(name="🗑️ حذف",           value="احذف الروم نهائياً",      inline=True)
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
                embed.set_image(url=guild.icon.url)
            embed.set_footer(
                text=f"{guild.name} • الأزرار تعمل فقط لصاحب الروم",
                icon_url=guild.icon.url if guild.icon else None
            )

            panel_ch = guild.get_channel(PANEL_CHANNEL_ID)
            if panel_ch:
                panel_msg = await panel_ch.send(embed=embed, view=ControlPanel(new_vc, member.id))
                # store msg id so we can delete it when the room is gone
                voice_channels[member.id] = {"vc": new_vc.id, "msg": panel_msg.id}
            else:
                voice_channels[member.id] = {"vc": new_vc.id, "msg": None}

        # ── Auto-delete empty owned channels ─────────────────────────────────
        if before.channel and before.channel.id != JOIN_TO_CREATE_ID:
            for uid, data in list(voice_channels.items()):
                vc_id  = data["vc"]  if isinstance(data, dict) else data
                msg_id = data["msg"] if isinstance(data, dict) else None
                if vc_id == before.channel.id and len(before.channel.members) == 0:
                    try:
                        await before.channel.delete()
                    except Exception:
                        pass
                    # delete the control panel message too
                    if msg_id:
                        panel_ch = before.channel.guild.get_channel(PANEL_CHANNEL_ID)
                        if panel_ch:
                            try:
                                msg = await panel_ch.fetch_message(msg_id)
                                await msg.delete()
                            except Exception:
                                pass
                    voice_channels.pop(uid, None)
                    break


async def setup(bot: commands.Bot):
    await bot.add_cog(صوت(bot))
