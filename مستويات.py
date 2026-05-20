import discord
from discord.ext import commands
import json
import os
import random
import asyncio
from datetime import datetime, date, timezone

XP_FILE      = "data/xp.json"
LEVELUP_CH   = 1505022803701665863   # قناة إشعارات الترقي فقط

# voice join tracking: f"{guild_id}_{user_id}" -> datetime
_voice_start: dict[str, datetime] = {}


# ─── Persistence ─────────────────────────────────────────────────────────────

def load_xp() -> dict:
    if not os.path.exists(XP_FILE):
        return {}
    with open(XP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_xp(data: dict):
    os.makedirs("data", exist_ok=True)
    with open(XP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def today_key() -> str:
    return str(date.today())


def week_key() -> str:
    iso = date.today().isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def get_user(data: dict, gid: str, uid: str) -> dict:
    data.setdefault(gid, {})
    if uid not in data[gid]:
        data[gid][uid] = {
            "xp": 0, "level": 0,
            "messages": 0, "voice_minutes": 0,
            "daily":  {"date": "",  "messages": 0, "voice_minutes": 0},
            "weekly": {"week": "",  "messages": 0, "voice_minutes": 0},
        }
    u = data[gid][uid]
    # Reset daily if new day
    if u.get("daily", {}).get("date") != today_key():
        u["daily"] = {"date": today_key(), "messages": 0, "voice_minutes": 0}
    # Reset weekly if new week
    if u.get("weekly", {}).get("week") != week_key():
        u["weekly"] = {"week": week_key(), "messages": 0, "voice_minutes": 0}
    return u


# ─── XP helpers ──────────────────────────────────────────────────────────────

def xp_needed(level: int) -> int:
    return 100 * level


def get_level(xp: int) -> int:
    level = 0
    while xp >= xp_needed(level + 1):
        xp -= xp_needed(level + 1)
        level += 1
    return level


def xp_bar(current: int, total: int, length: int = 10) -> str:
    filled = int((current / total) * length) if total > 0 else 0
    return f"{'█' * filled}{'░' * (length - filled)}  {current}/{total} XP"


def fmt_voice(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes} دقيقة"
    h, m = divmod(minutes, 60)
    return f"{h} ساعة {m} دقيقة" if m else f"{h} ساعة"


# ─── Cog ─────────────────────────────────────────────────────────────────────

class مستويات(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot       = bot
        self.cooldowns: dict[str, bool] = {}

    # ── Message XP + stats ───────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        uid = str(message.author.id)
        gid = str(message.guild.id)
        key = f"{gid}_{uid}"

        # XP cooldown (1 per minute)
        xp_gain = 0
        if key not in self.cooldowns:
            self.cooldowns[key] = True
            xp_gain = random.randint(15, 30)
            async def _remove():
                await asyncio.sleep(60)
                self.cooldowns.pop(key, None)
            self.bot.loop.create_task(_remove())

        data = load_xp()
        u    = get_user(data, gid, uid)

        # always count messages + XP if gained
        u["messages"]              = u.get("messages", 0) + 1
        u["daily"]["messages"]    += 1
        u["weekly"]["messages"]   += 1
        if xp_gain:
            u["xp"] += xp_gain

        old_level = u["level"]
        u["level"] = get_level(u["xp"])
        save_xp(data)

        # Level-up → post ONLY in LEVELUP_CH
        if u["level"] > old_level:
            ch = message.guild.get_channel(LEVELUP_CH)
            if ch:
                embed = discord.Embed(
                    title="🎉 ترقية مستوى!",
                    description=(
                        f"مبروك {message.author.mention}!\n"
                        f"وصلت إلى المستوى **{u['level']}** 🚀"
                    ),
                    color=0xf1c40f
                )
                embed.set_thumbnail(url=message.author.display_avatar.url)
                embed.set_footer(text=f"{message.guild.name} • نظام المستويات")
                await ch.send(embed=embed)

    # ── Voice tracking ───────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        if member.bot:
            return
        key = f"{member.guild.id}_{member.id}"

        # Joined a voice channel
        if after.channel and not before.channel:
            _voice_start[key] = datetime.now(timezone.utc)

        # Left a voice channel
        elif before.channel and not after.channel:
            start = _voice_start.pop(key, None)
            if start:
                minutes = int((datetime.now(timezone.utc) - start).total_seconds() // 60)
                if minutes > 0:
                    data = load_xp()
                    u    = get_user(data, str(member.guild.id), str(member.id))
                    u["voice_minutes"]           = u.get("voice_minutes", 0) + minutes
                    u["daily"]["voice_minutes"]  += minutes
                    u["weekly"]["voice_minutes"] += minutes
                    # bonus XP for voice (1 XP per minute, max 60/session)
                    u["xp"]   += min(minutes, 60)
                    u["level"] = get_level(u["xp"])
                    save_xp(data)

    # ── !t  / !t day / !t week ───────────────────────────────────────────────

    @commands.command(name="t")
    async def stats(self, ctx, period: str = ""):
        """إحصائيات جميع الأعضاء. !t = الكلي | !t day = اليوم | !t week = الأسبوع"""
        if ctx.channel.id != LEVELUP_CH:
            try:
                await ctx.message.delete()
            except Exception:
                pass
            ch = ctx.guild.get_channel(LEVELUP_CH)
            await ctx.send(
                f"❌ هذا الأمر متاح فقط في {ch.mention if ch else f'<#{LEVELUP_CH}>'}!",
                delete_after=5
            )
            return

        period = period.strip().lower()
        data   = load_xp()
        gid    = str(ctx.guild.id)

        rows = []
        for uid, u in data.get(gid, {}).items():
            member = ctx.guild.get_member(int(uid))
            if not member or member.bot:
                continue

            if period == "day":
                daily_info = u.get("daily", {})
                if daily_info.get("date") == today_key():
                    msgs  = daily_info.get("messages", 0)
                    voice = daily_info.get("voice_minutes", 0)
                else:
                    msgs = voice = 0
            elif period == "week":
                weekly_info = u.get("weekly", {})
                if weekly_info.get("week") == week_key():
                    msgs  = weekly_info.get("messages", 0)
                    voice = weekly_info.get("voice_minutes", 0)
                else:
                    msgs = voice = 0
            else:
                msgs  = u.get("messages", 0)
                voice = u.get("voice_minutes", 0)

            if msgs > 0 or voice > 0:
                rows.append((member.display_name, msgs, voice, u.get("level", 0)))

        if period == "day":
            title  = f"📅 إحصائيات اليوم — {today_key()}"
            footer = "تُصفَّر يومياً عند منتصف الليل"
            color  = 0x3498db
        elif period == "week":
            title  = f"📆 إحصائيات الأسبوع — {week_key()}"
            footer = "تُصفَّر أسبوعياً"
            color  = 0x9b59b6
        else:
            title  = "📊 الإحصائيات الكاملة للسيرفر"
            footer = "إجمالي منذ بداية التسجيل"
            color  = 0xf1c40f

        if not rows:
            await ctx.send("❌ لا توجد إحصائيات بعد!")
            return

        # Sort by messages desc then voice desc
        rows.sort(key=lambda x: (x[1], x[2]), reverse=True)

        medals  = ["🥇","🥈","🥉"] + [f"{i}️⃣" for i in range(4, 11)]
        lines   = []
        for i, (name, msgs, voice, level) in enumerate(rows[:15]):
            medal = medals[i] if i < len(medals) else f"`{i+1}.`"
            voice_str = f" | 🎙️ {fmt_voice(voice)}" if voice > 0 else ""
            lvl_str   = f" | 🏆 {level}" if period == "" else ""
            lines.append(f"{medal} **{name}** — ✍️ {msgs:,}{voice_str}{lvl_str}")

        embed = discord.Embed(
            title=title,
            description="\n".join(lines),
            color=color
        )
        embed.set_footer(text=footer)
        embed.set_author(
            name=ctx.guild.name,
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        await ctx.send(embed=embed)

    # ── !مستوى ───────────────────────────────────────────────────────────────

    @commands.command(name="مستوى")
    async def level_cmd(self, ctx, عضو: discord.Member = None):
        """عرض مستواك. مثال: !مستوى @شخص"""
        target = عضو or ctx.author
        data   = load_xp()
        gid    = str(ctx.guild.id)
        uid    = str(target.id)
        u      = get_user(data, gid, uid)

        level    = u["level"]
        total_xp = u["xp"]
        cur_xp   = total_xp
        for i in range(1, level + 1):
            cur_xp -= xp_needed(i)
        needed = xp_needed(level + 1)
        bar    = xp_bar(max(0, cur_xp), needed)

        embed = discord.Embed(
            title=f"📊 مستوى {target.display_name}",
            color=target.color if target.color.value != 0 else 0x9b59b6
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="🏆 المستوى",   value=f"**{level}**",                        inline=True)
        embed.add_field(name="✨ إجمالي XP", value=f"**{total_xp:,}**",                   inline=True)
        embed.add_field(name="💬 الرسائل",   value=f"**{u.get('messages',0):,}**",         inline=True)
        embed.add_field(name="🎙️ وقت الصوت",value=f"**{fmt_voice(u.get('voice_minutes',0))}**", inline=True)
        embed.add_field(name="📈 للمستوى التالي", value=f"`{bar}`",                        inline=False)
        await ctx.send(embed=embed)

    # ── !ترتيب ────────────────────────────────────────────────────────────────

    @commands.command(name="ترتيب")
    async def leaderboard(self, ctx):
        """قائمة أعلى المستويات في السيرفر"""
        data       = load_xp()
        gid        = str(ctx.guild.id)
        guild_data = data.get(gid, {})

        rows = []
        for uid, info in guild_data.items():
            m = ctx.guild.get_member(int(uid))
            if m:
                rows.append((m.display_name, info.get("level", 0), info.get("xp", 0)))
        rows.sort(key=lambda x: (x[1], x[2]), reverse=True)
        top = rows[:10]

        if not top:
            await ctx.send("❌ لا توجد بيانات بعد! ابدأ بالمحادثة.")
            return

        medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        desc   = "\n".join(
            f"{medals[i]} **{name}** — المستوى {lvl} ({xp:,} XP)"
            for i, (name, lvl, xp) in enumerate(top)
        )
        embed = discord.Embed(title="🏆 قائمة المستويات", description=desc, color=0xf1c40f)
        embed.set_footer(text="اكتب أكثر وكن في الصوت لترفع مستواك!")
        await ctx.send(embed=embed)

    # ── Admin ─────────────────────────────────────────────────────────────────

    @commands.command(name="اعطِ-xp")
    @commands.has_permissions(administrator=True)
    async def give_xp(self, ctx, عضو: discord.Member, الكمية: int):
        data = load_xp()
        gid  = str(ctx.guild.id)
        uid  = str(عضو.id)
        u    = get_user(data, gid, uid)
        u["xp"]   += الكمية
        u["level"] = get_level(u["xp"])
        save_xp(data)
        await ctx.send(f"✅ تم إعطاء **{الكمية:,} XP** لـ {عضو.mention}!")

    @commands.command(name="إعادة-xp")
    @commands.has_permissions(administrator=True)
    async def reset_xp(self, ctx, عضو: discord.Member):
        data = load_xp()
        gid  = str(ctx.guild.id)
        uid  = str(عضو.id)
        if gid in data and uid in data[gid]:
            data[gid][uid] = {
                "xp": 0, "level": 0,
                "messages": 0, "voice_minutes": 0,
                "daily":  {"date": "", "messages": 0, "voice_minutes": 0},
                "weekly": {"week": "", "messages": 0, "voice_minutes": 0},
            }
            save_xp(data)
        await ctx.send(f"✅ تم إعادة تعيين XP لـ {عضو.mention}!")


async def setup(bot: commands.Bot):
    await bot.add_cog(مستويات(bot))
