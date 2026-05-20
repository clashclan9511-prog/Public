import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime

CONFIG_FILE = "data/tickets_config.json"
STATS_FILE  = "data/tickets_stats.json"

PARTNER_ROLE_ID    = 1505174149625151529
DEFAULT_CATEGORY   = 1505141688912314510
DEFAULT_LOG_CH     = 1505529075635065014


# ── helpers ──────────────────────────────────────────────────────────────────

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(data):
    os.makedirs("data", exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_stats():
    if not os.path.exists(STATS_FILE):
        return {}
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_stats(data):
    os.makedirs("data", exist_ok=True)
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_admin_stats(admin_id: int):
    stats = load_stats()
    uid = str(admin_id)
    if uid not in stats:
        stats[uid] = {"claimed": 0, "closed": 0}
    return stats, uid

def get_cfg_value(guild_id: str, key: str, default):
    config = load_config()
    return config.get(guild_id, {}).get(key, default)


# ── Modal إغلاق بسبب ─────────────────────────────────────────────────────────

class CloseReasonModal(discord.ui.Modal, title="إغلاق التذكرة"):
    السبب = discord.ui.TextInput(
        label="سبب الإغلاق",
        placeholder="مثال: تم حل المشكلة",
        min_length=2,
        max_length=200,
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        config    = load_config()
        guild_id  = str(interaction.guild.id)
        channel_id= str(interaction.channel.id)
        ticket_info     = config.get(guild_id, {}).get("open_tickets", {}).get(channel_id, {})
        member_id        = ticket_info.get("member_id")
        claimed_by_name  = ticket_info.get("claimed_by_name", "لم يُستلم")

        stats, uid = get_admin_stats(interaction.user.id)
        stats[uid]["closed"] += 1
        save_stats(stats)

        await interaction.response.defer()

        # رسالة الإغلاق في القناة
        embed = discord.Embed(
            title="🔒 تم إغلاق التذكرة",
            description=(
                f"📝 **السبب:** {self.السبب.value}\n"
                f"👮 **أُغلقت بواسطة:** {interaction.user.mention}\n"
                f"🧑‍💼 **استلمها:** {claimed_by_name}\n\n"
                "ستُحذف هذه القناة خلال **5 ثواني**..."
            ),
            color=0xe74c3c
        )
        await interaction.channel.send(embed=embed)

        # DM للعضو
        if member_id:
            member = interaction.guild.get_member(member_id)
            if member:
                try:
                    dm_embed = discord.Embed(
                        title="🔒 تم إغلاق تذكرتك",
                        description=(
                            f"تم إغلاق تذكرتك في **{interaction.guild.name}**\n\n"
                            f"📝 **السبب:** {self.السبب.value}\n"
                            f"🧑‍💼 **استلمها:** {claimed_by_name}\n"
                            f"👮 **أغلقها:** {interaction.user.display_name}\n"
                            f"📅 {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC"
                        ),
                        color=0xe74c3c
                    )
                    await member.send(embed=dm_embed)
                except Exception:
                    pass

        # سجل الإغلاق
        log_ch_id = get_cfg_value(guild_id, "log_channel", DEFAULT_LOG_CH)
        log_ch    = interaction.guild.get_channel(log_ch_id)
        if log_ch:
            log_embed = discord.Embed(title="📋 سجل التذاكر — إغلاق", color=0xe74c3c)
            log_embed.add_field(name="📌 القناة",  value=interaction.channel.name,       inline=True)
            log_embed.add_field(name="🧑‍💼 استلمها", value=claimed_by_name,               inline=True)
            log_embed.add_field(name="👮 أغلقها",  value=interaction.user.display_name,  inline=True)
            log_embed.add_field(name="📝 السبب",   value=self.السبب.value,               inline=False)
            log_embed.set_footer(text=datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'))
            await log_ch.send(embed=log_embed)

        # حذف من config ثم حذف القناة
        if guild_id in config and "open_tickets" in config[guild_id]:
            config[guild_id]["open_tickets"].pop(channel_id, None)
            save_config(config)

        await asyncio.sleep(5)
        await interaction.channel.delete()


# ── View: زر إغلاق فقط (يظهر بعد الاستلام) ──────────────────────────────────

class CloseOnlyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="إغلاق بسبب ❌",
        style=discord.ButtonStyle.danger,
        custom_id="close_only_btn"
    )
    async def close_only(self, interaction: discord.Interaction, button: discord.ui.Button):
        partner_role = interaction.guild.get_role(PARTNER_ROLE_ID)
        if partner_role and partner_role not in interaction.user.roles:
            await interaction.response.send_message("❌ ليس لديك صلاحية!", ephemeral=True)
            return
        await interaction.response.send_modal(CloseReasonModal())


# ── View: أزرار الاداري (استلام + إغلاق) ─────────────────────────────────────

class AdminTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="استلام التذكرة ✅",
        style=discord.ButtonStyle.success,
        custom_id="claim_ticket_btn"
    )
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        partner_role = interaction.guild.get_role(PARTNER_ROLE_ID)
        if partner_role and partner_role not in interaction.user.roles:
            await interaction.response.send_message("❌ ليس لديك صلاحية لاستلام التذاكر!", ephemeral=True)
            return

        config     = load_config()
        guild_id   = str(interaction.guild.id)
        channel_id = str(interaction.channel.id)
        ticket_info = config.get(guild_id, {}).get("open_tickets", {}).get(channel_id, {})
        member_id   = ticket_info.get("member_id")

        stats, uid = get_admin_stats(interaction.user.id)
        stats[uid]["claimed"] += 1
        save_stats(stats)
        total_claimed = stats[uid]["claimed"]

        await interaction.response.defer()

        # ① استبدل أزرار الاداري بزر الإغلاق فقط (لا يختفي!)
        await interaction.message.edit(view=CloseOnlyView())

        # ② رسالة الاستلام مع زر استدعاء الاداري للعضو
        embed = discord.Embed(
            title="👋 أهلاً بك عزيزي العضو",
            description=(
                f"🧑‍💼 معك الإداري: {interaction.user.mention}\n\n"
                "📨 نحن هنا لمساعدتك، تفضل بطرح مشكلتك أو استفسارك\n"
                "وسيتم خدمتك بأفضل شكل ممكن 💎\n\n"
                f"🙏 شكراً لاختيارك **Respect Life**"
            ),
            color=0x2ecc71
        )
        embed.set_footer(
            text=f"استلم التذكرة: {interaction.user.display_name} | إجمالي تذاكره: {total_claimed}"
        )
        await interaction.channel.send(embed=embed, view=MemberTicketView())

        # ③ حفظ بيانات الاستلام
        if guild_id in config and "open_tickets" in config[guild_id] and channel_id in config[guild_id]["open_tickets"]:
            config[guild_id]["open_tickets"][channel_id]["claimed_by"]      = interaction.user.id
            config[guild_id]["open_tickets"][channel_id]["claimed_by_name"] = interaction.user.display_name
            save_config(config)

        # ④ DM للعضو
        if member_id:
            member = interaction.guild.get_member(member_id)
            if member:
                try:
                    dm_embed = discord.Embed(
                        title="✅ تم استلام تذكرتك",
                        description=(
                            f"تم استلام تذكرتك في **{interaction.guild.name}**\n\n"
                            f"🧑‍💼 الإداري المستلم: **{interaction.user.display_name}**\n"
                            f"📅 {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC"
                        ),
                        color=0x2ecc71
                    )
                    await member.send(embed=dm_embed)
                except Exception:
                    pass

    @discord.ui.button(
        label="إغلاق بسبب ❌",
        style=discord.ButtonStyle.danger,
        custom_id="close_ticket_reason_btn"
    )
    async def close_with_reason(self, interaction: discord.Interaction, button: discord.ui.Button):
        partner_role = interaction.guild.get_role(PARTNER_ROLE_ID)
        if partner_role and partner_role not in interaction.user.roles:
            await interaction.response.send_message("❌ ليس لديك صلاحية!", ephemeral=True)
            return
        await interaction.response.send_modal(CloseReasonModal())


# ── View: زر استدعاء الاداري (للعضو) ─────────────────────────────────────────

class MemberTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="استدعاء الاداري 🔔",
        style=discord.ButtonStyle.secondary,
        custom_id="call_admin_btn"
    )
    async def call_admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🔔 تم استدعاء الاداري! سيصلك رد في أقرب وقت.",
            ephemeral=True
        )
        partner_role = interaction.guild.get_role(PARTNER_ROLE_ID)
        mention = partner_role.mention if partner_role else "@الاداري"
        await interaction.channel.send(
            f"{mention} تم استدعاؤك من قِبل {interaction.user.mention} في هذه التذكرة!"
        )


# ── View: زر فتح التذكرة (البانل الخارجي) ────────────────────────────────────

class TicketOpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="الـشـراكـة 🤝",
        style=discord.ButtonStyle.primary,
        custom_id="open_ticket_btn"
    )
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild    = interaction.guild
        member   = interaction.user
        config   = load_config()
        guild_id = str(guild.id)

        if guild_id not in config:
            config[guild_id] = {}
        if "open_tickets" not in config[guild_id]:
            config[guild_id]["open_tickets"] = {}

        # منع فتح أكثر من تذكرة
        for ch_id, info in config[guild_id]["open_tickets"].items():
            if info.get("member_id") == member.id:
                ch = guild.get_channel(int(ch_id))
                if ch:
                    await interaction.response.send_message(
                        f"❌ عندك تذكرة مفتوحة بالفعل! {ch.mention}", ephemeral=True
                    )
                    return

        partner_role = guild.get_role(PARTNER_ROLE_ID)
        cat_id       = get_cfg_value(guild_id, "ticket_category", DEFAULT_CATEGORY)
        category     = guild.get_channel(cat_id)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member:             discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
        }
        if partner_role:
            overwrites[partner_role] = discord.PermissionOverwrite(
                read_messages=True, send_messages=True, manage_channels=True
            )

        channel = await guild.create_text_channel(
            name=f"شراكة-{member.display_name[:15]}",
            overwrites=overwrites,
            category=category,
            topic=f"تذكرة شراكة | {member.display_name}"
        )

        config[guild_id]["open_tickets"][str(channel.id)] = {
            "member_id":       member.id,
            "member_name":     member.display_name,
            "opened_at":       datetime.utcnow().isoformat(),
            "claimed_by":      None,
            "claimed_by_name": "لم يُستلم"
        }
        save_config(config)

        await interaction.response.send_message(
            f"✅ تم فتح تذكرتك: {channel.mention}", ephemeral=True
        )

        partner_mention = partner_role.mention if partner_role else ""
        embed = discord.Embed(
            title="🎫 Respect Life — تذكرة شراكة",
            description=(
                f"مرحباً {member.mention} 👋\n\n"
                "تم استلام طلبك، يرجى الانتظار حتى يستلم أحد الإداريين تذكرتك.\n\n"
                "📌 **يرجى تقديم طلب الشراكة أو استفسارك فوراً.**"
            ),
            color=0x3498db
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text="Respect Life | رويال شوب 💎")

        await channel.send(
            content=f"{member.mention} {partner_mention}",
            embed=embed,
            view=AdminTicketView()
        )

        # سجل الفتح
        log_ch_id = get_cfg_value(guild_id, "log_channel", DEFAULT_LOG_CH)
        log_ch    = guild.get_channel(log_ch_id)
        if log_ch:
            log_embed = discord.Embed(title="📋 سجل التذاكر — فتح", color=0x3498db)
            log_embed.add_field(name="👤 العضو",  value=str(member),      inline=True)
            log_embed.add_field(name="📌 القناة", value=channel.mention,  inline=True)
            log_embed.set_footer(text=datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'))
            await log_ch.send(embed=log_embed)


# ── Cog الرئيسي ───────────────────────────────────────────────────────────────

class تذاكر(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(TicketOpenView())
        bot.add_view(AdminTicketView())
        bot.add_view(MemberTicketView())
        bot.add_view(CloseOnlyView())

    @commands.command(name="تذاكر")
    @commands.has_permissions(administrator=True)
    async def send_ticket_panel(self, ctx):
        """إرسال بانل التذاكر"""
        await ctx.message.delete()
        embed = discord.Embed(
            title="Respect Life",
            description=(
                "تذكرة رويال شوب لـ خدمتكم 24 ساعة متواصلة\n"
                "واتمنى منكم الالتزام بالقوانين :\n\n"
                "**1 -** عدم فتح أكثر من تذكرة واحدة\n"
                "**2 -** عدم إزعاج المسؤولين في التذكرة\n"
                "**3 -** اتمنى منك تقديم شراكة حقك أو طلبك فوراً"
            ),
            color=0x2c3e50
        )
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
            embed.set_image(url=ctx.guild.icon.url)
        embed.set_footer(text="Respect Life 💎 | رويال شوب")
        await ctx.send(embed=embed, view=TicketOpenView())

    @commands.command(name="قناة-سجل-تذاكر")
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx, قناة: discord.TextChannel):
        """تعيين قناة سجل التذاكر (اختياري - يوجد افتراضي)"""
        config = load_config()
        guild_id = str(ctx.guild.id)
        if guild_id not in config:
            config[guild_id] = {}
        config[guild_id]["log_channel"] = قناة.id
        save_config(config)
        await ctx.send(f"✅ تم تعيين {قناة.mention} كقناة سجل التذاكر!")

    @commands.command(name="فئة-تذاكر")
    @commands.has_permissions(administrator=True)
    async def set_ticket_category(self, ctx, فئة: discord.CategoryChannel):
        """تعيين فئة التذاكر (اختياري - يوجد افتراضي)"""
        config = load_config()
        guild_id = str(ctx.guild.id)
        if guild_id not in config:
            config[guild_id] = {}
        config[guild_id]["ticket_category"] = فئة.id
        save_config(config)
        await ctx.send(f"✅ ستفتح التذاكر في فئة **{فئة.name}**!")

    @commands.command(name="إحصاء-اداري")
    async def admin_stats(self, ctx, عضو: discord.Member = None):
        """إحصاءات تذاكر الاداري"""
        target = عضو or ctx.author
        stats, uid = get_admin_stats(target.id)
        s = stats[uid]
        embed = discord.Embed(title=f"📊 إحصاءات {target.display_name}", color=0x9b59b6)
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="✅ تذاكر مستلمة", value=f"**{s['claimed']}**", inline=True)
        embed.add_field(name="🔒 تذاكر مغلقة",  value=f"**{s['closed']}**",  inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="إحصاء-كل-الاداريين")
    @commands.has_permissions(administrator=True)
    async def all_admin_stats(self, ctx):
        """إحصاءات جميع الإداريين"""
        stats = load_stats()
        if not stats:
            await ctx.send("❌ لا توجد إحصاءات بعد!")
            return
        entries = []
        for uid, s in stats.items():
            m = ctx.guild.get_member(int(uid))
            entries.append((m.display_name if m else f"({uid})", s["claimed"], s["closed"]))
        entries.sort(key=lambda x: x[1], reverse=True)
        medals = ["🥇","🥈","🥉"]
        desc = "\n".join([
            f"{medals[i] if i < 3 else '▫️'} **{n}** — استلم: {c} | أغلق: {cl}"
            for i, (n, c, cl) in enumerate(entries)
        ])
        embed = discord.Embed(title="📊 إحصاءات الإداريين", description=desc, color=0xf1c40f)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(تذاكر(bot))
