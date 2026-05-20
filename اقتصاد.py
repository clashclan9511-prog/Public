import discord
from discord.ext import commands
import random
import json
import os
import asyncio
from datetime import datetime, date

DATA_FILE        = "data/economy.json"
ECONOMY_CHANNEL  = 1506453303569944786

# active fruit games: channel_id -> True
active_games: dict[int, bool] = {}

FRUITS = [
    ("🍎", "تفاحة",   ["تفاحه", "تفاح"]),
    ("🍊", "برتقالة", ["برتقاله", "برتقال"]),
    ("🍋", "ليمونة",  ["ليمونه", "ليمون"]),
    ("🍇", "عنب",     []),
    ("🍓", "فراولة",  ["فراوله", "فراولا", "فراولة"]),
    ("🍑", "خوخة",    ["خوخه", "خوخ"]),
    ("🍒", "كرز",     []),
    ("🍍", "أناناس",  ["اناناس", "اناناسة"]),
    ("🥭", "مانجو",   ["منجو"]),
    ("🍉", "بطيخة",   ["بطيخه", "بطيخ"]),
    ("🍌", "موزة",    ["موزه", "موز"]),
    ("🍐", "كمثرى",   ["كمثري"]),
    ("🥝", "كيوي",    []),
    ("🫐", "توت",     []),
    ("🍈", "شمام",    ["شمامة"]),
    ("🍑", "مشمش",   ["مشمشة"]),
    ("🌴", "تمر",     ["تمرة"]),
    ("🍏", "تفاحة خضراء", ["تفاحه خضرا", "تفاح اخضر"]),
]


# ─── Helpers ─────────────────────────────────────────────────────────────────

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(data, user_id):
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"coins": 100, "last_daily": None, "last_work": None, "bank": 0}
    return data[uid]


def fmt_remaining(seconds: float) -> str:
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    parts = []
    if h:
        parts.append(f"{h} ساعة")
    if m:
        parts.append(f"{m} دقيقة")
    if sec and not h:
        parts.append(f"{sec} ثانية")
    return " و ".join(parts) if parts else "أقل من ثانية"


# ─── Cog ─────────────────────────────────────────────────────────────────────

class اقتصاد(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        if ctx.channel.id != ECONOMY_CHANNEL:
            try:
                await ctx.message.delete()
            except Exception:
                pass
            ch = ctx.guild.get_channel(ECONOMY_CHANNEL)
            hint = ch.mention if ch else f"<#{ECONOMY_CHANNEL}>"
            msg = await ctx.send(
                f"❌ أوامر الاقتصاد تعمل فقط في {hint}!", delete_after=5
            )
            return False
        return True

    # ── رصيد ──────────────────────────────────────────────────────────────────

    @commands.command(name="رصيد")
    async def balance(self, ctx, عضو: discord.Member = None):
        target = عضو or ctx.author
        data = load_data()
        user = get_user(data, target.id)
        embed = discord.Embed(title=f"💰 رصيد {target.display_name}", color=0xf1c40f)
        embed.add_field(name="👛 المحفظة", value=f"{user['coins']:,} 🪙", inline=True)
        embed.add_field(name="🏦 البنك",   value=f"{user['bank']:,} 🪙",  inline=True)
        embed.add_field(name="💎 الإجمالي",value=f"{user['coins']+user['bank']:,} 🪙", inline=True)
        embed.set_thumbnail(url=target.display_avatar.url)
        await ctx.send(embed=embed)

    # ── الوقت ─────────────────────────────────────────────────────────────────

    @commands.command(name="الوقت")
    async def cooldowns(self, ctx):
        """اعرف متى تقدر تستخدم أوامر الاقتصاد"""
        data = load_data()
        user = get_user(data, ctx.author.id)
        now  = datetime.now()
        today = str(date.today())

        # يومي
        if user["last_daily"] == today:
            from datetime import timedelta
            tomorrow = datetime.combine(date.today(), datetime.min.time()) + timedelta(days=1)
            daily_left = (tomorrow - now).total_seconds()
            daily_txt = f"⏳ بعد **{fmt_remaining(daily_left)}**"
        else:
            daily_txt = "✅ **جاهز الآن!**"

        # شغل
        last_work = user.get("last_work")
        if last_work:
            last_time = datetime.fromisoformat(last_work)
            diff = (now - last_time).total_seconds()
            if diff < 3600:
                work_left = 3600 - diff
                work_txt = f"⏳ بعد **{fmt_remaining(work_left)}**"
            else:
                work_txt = "✅ **جاهز الآن!**"
        else:
            work_txt = "✅ **جاهز الآن!**"

        embed = discord.Embed(
            title=f"⏰ مواعيد أوامر الاقتصاد — {ctx.author.display_name}",
            color=0x3498db
        )
        embed.add_field(name="🎁 !يومي",  value=daily_txt, inline=False)
        embed.add_field(name="💼 !شغل",   value=work_txt,  inline=False)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(text="استخدم الأوامر لما تكون جاهزة!")
        await ctx.send(embed=embed)

    # ── يومي ──────────────────────────────────────────────────────────────────

    @commands.command(name="يومي")
    async def daily(self, ctx):
        data = load_data()
        user = get_user(data, ctx.author.id)
        today = str(date.today())
        if user["last_daily"] == today:
            await ctx.send("❌ استلمت مكافأتك اليومية! استخدم `!الوقت` لمعرفة متى تقدر تأخذها.")
            return
        amount = random.randint(100, 300)
        user["coins"] += amount
        user["last_daily"] = today
        save_data(data)
        embed = discord.Embed(
            title="🎁 المكافأة اليومية",
            description=f"{ctx.author.mention} حصل على **{amount:,} 🪙**!\nرصيدك الآن: **{user['coins']:,} 🪙**",
            color=0x2ecc71
        )
        await ctx.send(embed=embed)

    # ── شغل ───────────────────────────────────────────────────────────────────

    @commands.command(name="شغل")
    async def work(self, ctx):
        data = load_data()
        user = get_user(data, ctx.author.id)
        now  = datetime.now()
        last = user.get("last_work")
        if last:
            diff = (now - datetime.fromisoformat(last)).total_seconds()
            if diff < 3600:
                await ctx.send(f"⏰ تعبت! استخدم `!الوقت` لمعرفة متى تقدر تشتغل.")
                return
        jobs = [
            ("👨‍💻 برمجت تطبيقاً", 80, 200),
            ("🚗 وصّلت ناس",       50, 120),
            ("🍕 وزّعت بيتزا",      40, 100),
            ("🧹 نظّفت مكتباً",     30,  80),
            ("📦 رتّبت مستودعاً",   60, 150),
            ("🎨 رسمت لوحة",       70, 180),
            ("📱 رددت على ايميلات", 45, 110),
            ("🔧 صلّحت جهازاً",    90, 220),
        ]
        job, lo, hi = random.choice(jobs)
        amount = random.randint(lo, hi)
        user["coins"] += amount
        user["last_work"] = now.isoformat()
        save_data(data)
        embed = discord.Embed(
            title="💼 عملت!",
            description=f"{job} وكسبت **{amount:,} 🪙**!\nرصيدك الآن: **{user['coins']:,} 🪙**",
            color=0x3498db
        )
        await ctx.send(embed=embed)

    # ── تخمين فواكة ───────────────────────────────────────────────────────────

    @commands.command(name="تخمين-فواكة")
    async def fruit_guess(self, ctx):
        """خمّن اسم الفاكهة واربح عملات!"""
        if active_games.get(ctx.channel.id):
            await ctx.send("❌ يوجد لعبة تخمين جارية في هذه القناة! انتظر انتهاءها.")
            return

        emoji, name, aliases = random.choice(FRUITS)
        prize = random.randint(50, 200)
        active_games[ctx.channel.id] = True

        # Reveal emoji + partial hint (show first letter, hide rest)
        hint = name[0] + " _ " * (len(name) - 1)
        embed = discord.Embed(
            title="🍉 تخمين الفاكهة!",
            description=(
                f"ما هذه الفاكهة؟\n\n"
                f"# {emoji}\n\n"
                f"🔤 **تلميح:** `{hint}`\n"
                f"💰 **الجائزة:** {prize} 🪙\n"
                f"⏱️ **الوقت:** 30 ثانية"
            ),
            color=0xf39c12
        )
        embed.set_footer(text="اكتب اسم الفاكهة في الدردشة!")
        question_msg = await ctx.send(embed=embed)

        correct = {name.lower()} | {a.lower() for a in aliases}

        def check(m: discord.Message):
            return (
                m.channel.id == ctx.channel.id
                and not m.author.bot
                and m.content.strip().lower() in correct
            )

        try:
            winner_msg = await self.bot.wait_for("message", check=check, timeout=30)
            winner = winner_msg.author
            data = load_data()
            user = get_user(data, winner.id)
            user["coins"] += prize
            save_data(data)
            result = discord.Embed(
                title="🎉 صح!",
                description=(
                    f"{winner.mention} خمّن الفاكهة الصحيحة!\n"
                    f"الجواب: **{name}** {emoji}\n"
                    f"ربح **{prize:,} 🪙** | رصيده الآن: **{user['coins']:,} 🪙**"
                ),
                color=0x2ecc71
            )
        except asyncio.TimeoutError:
            result = discord.Embed(
                title="⏰ انتهى الوقت!",
                description=f"الجواب الصحيح كان: **{name}** {emoji}\nما فاز أحد هذه المرة!",
                color=0xe74c3c
            )
        finally:
            active_games.pop(ctx.channel.id, None)

        await question_msg.edit(embed=result)

    # ── قمار ──────────────────────────────────────────────────────────────────

    @commands.command(name="قمار")
    async def gamble(self, ctx, المبلغ: str):
        data = load_data()
        user = get_user(data, ctx.author.id)
        if المبلغ.lower() in ["كل", "all"]:
            amount = user["coins"]
        else:
            if not المبلغ.isdigit():
                await ctx.send("❌ أدخل رقماً أو كلمة 'كل'")
                return
            amount = int(المبلغ)
        if amount <= 0:
            await ctx.send("❌ ما عندك عملات!")
            return
        if amount > user["coins"]:
            await ctx.send(f"❌ ما عندك كافي! رصيدك: **{user['coins']:,} 🪙**")
            return
        win = random.random() < 0.45
        if win:
            user["coins"] += amount
            embed = discord.Embed(title="🎰 فزت!", description=f"ربحت **{amount:,} 🪙**! 🎉\nرصيدك: **{user['coins']:,} 🪙**", color=0x2ecc71)
        else:
            user["coins"] -= amount
            embed = discord.Embed(title="🎰 خسرت!", description=f"خسرت **{amount:,} 🪙**! 😢\nرصيدك: **{user['coins']:,} 🪙**", color=0xe74c3c)
        save_data(data)
        await ctx.send(embed=embed)

    # ── إيداع ─────────────────────────────────────────────────────────────────

    @commands.command(name="إيداع")
    async def deposit(self, ctx, المبلغ: str):
        data = load_data()
        user = get_user(data, ctx.author.id)
        if المبلغ.lower() in ["كل", "all"]:
            amount = user["coins"]
        else:
            if not المبلغ.isdigit():
                await ctx.send("❌ أدخل رقماً!")
                return
            amount = int(المبلغ)
        if amount <= 0 or amount > user["coins"]:
            await ctx.send(f"❌ رصيدك: **{user['coins']:,} 🪙**")
            return
        user["coins"] -= amount
        user["bank"]  += amount
        save_data(data)
        embed = discord.Embed(title="🏦 إيداع ناجح", description=f"أودعت **{amount:,} 🪙**\nالمحفظة: **{user['coins']:,}** | البنك: **{user['bank']:,} 🪙**", color=0x2ecc71)
        await ctx.send(embed=embed)

    # ── سحب ───────────────────────────────────────────────────────────────────

    @commands.command(name="سحب")
    async def withdraw(self, ctx, المبلغ: str):
        data = load_data()
        user = get_user(data, ctx.author.id)
        if المبلغ.lower() in ["كل", "all"]:
            amount = user["bank"]
        else:
            if not المبلغ.isdigit():
                await ctx.send("❌ أدخل رقماً!")
                return
            amount = int(المبلغ)
        if amount <= 0 or amount > user["bank"]:
            await ctx.send(f"❌ رصيد البنك: **{user['bank']:,} 🪙**")
            return
        user["bank"]  -= amount
        user["coins"] += amount
        save_data(data)
        embed = discord.Embed(title="🏦 سحب ناجح", description=f"سحبت **{amount:,} 🪙**\nالمحفظة: **{user['coins']:,}** | البنك: **{user['bank']:,} 🪙**", color=0x3498db)
        await ctx.send(embed=embed)

    # ── تحويل ─────────────────────────────────────────────────────────────────

    @commands.command(name="تحويل")
    async def transfer(self, ctx, عضو: discord.Member, المبلغ: int):
        if عضو.bot or عضو.id == ctx.author.id:
            await ctx.send("❌ لا يمكن التحويل!")
            return
        data = load_data()
        sender   = get_user(data, ctx.author.id)
        receiver = get_user(data, عضو.id)
        if المبلغ <= 0 or المبلغ > sender["coins"]:
            await ctx.send(f"❌ رصيدك: **{sender['coins']:,} 🪙**")
            return
        sender["coins"]   -= المبلغ
        receiver["coins"] += المبلغ
        save_data(data)
        embed = discord.Embed(title="💸 تحويل ناجح", description=f"{ctx.author.mention} حوّل **{المبلغ:,} 🪙** لـ {عضو.mention}!", color=0x9b59b6)
        await ctx.send(embed=embed)

    # ── أثرياء ────────────────────────────────────────────────────────────────

    @commands.command(name="أثرياء")
    async def leaderboard(self, ctx):
        data = load_data()
        members_data = []
        for uid, info in data.items():
            m = ctx.guild.get_member(int(uid))
            if m:
                members_data.append((m.display_name, info["coins"] + info["bank"]))
        members_data.sort(key=lambda x: x[1], reverse=True)
        top = members_data[:10]
        if not top:
            await ctx.send("❌ لا توجد بيانات!")
            return
        medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        desc = "\n".join([f"{medals[i]} **{n}** — {t:,} 🪙" for i,(n,t) in enumerate(top)])
        embed = discord.Embed(title="💎 قائمة الأثرياء", description=desc, color=0xf1c40f)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(اقتصاد(bot))
