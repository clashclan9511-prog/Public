import discord
from discord.ext import commands
import random
import asyncio


EIGHT_BALL_ANSWERS = [
    ("✅ نعم بالتأكيد!", 0x2ecc71),
    ("✅ من وجهة نظري، نعم.", 0x2ecc71),
    ("✅ الإشارات تقول نعم.", 0x2ecc71),
    ("✅ بكل تأكيد!", 0x2ecc71),
    ("✅ توقعاتي إيجابية.", 0x2ecc71),
    ("🤔 الأمور ضبابية، حاول مرة أخرى.", 0xf39c12),
    ("🤔 لا يمكنني التنبؤ الآن.", 0xf39c12),
    ("🤔 ركز وحاول مجدداً.", 0xf39c12),
    ("❌ لا تعتمد عليه.", 0xe74c3c),
    ("❌ إجابتي لا.", 0xe74c3c),
    ("❌ التوقعات لا.", 0xe74c3c),
    ("❌ بالتأكيد لا!", 0xe74c3c),
]

COMPLIMENTS = [
    "أنت شخص رائع جداً! 🌟",
    "ابتسامتك تضيء المكان! 😊",
    "العالم أفضل بوجودك! 💫",
    "أنت مصدر إلهام للجميع! 🎯",
    "إبداعك لا حدود له! 🚀",
    "أنت من أذكى الناس! 🧠",
    "قلبك طيب وكبير! ❤️",
    "موهبتك استثنائية! 🏆",
]

INSULTS_FUNNY = [
    "أنت تأخذ السيلفي مع نفسك وتحذفه لأنه ما صار! 😂",
    "حتى الواي فاي يقطع لما تقترب منه! 📶",
    "أخبارك أقل إثارة من المطر! ☔",
    "لو كنت سلاحاً ما كنت حتى مقلمة! ✏️",
    "حتى السبام أقل إزعاجاً منك! 📧",
]

WOULD_YOU_RATHER = [
    ("تطير بدون أجنحة ⬆️", "تغوص بدون أوكسجين 🌊"),
    ("تأكل شيء كريه المذاق يومياً 🤢", "تسمع موسيقى مزعجة 24/7 🎵"),
    ("تكون ثري بلا أصدقاء 💰", "تكون فقير مع أصدقاء أوفياء ❤️"),
    ("تعرف تاريخ وفاتك 💀", "تعرف طريقة وفاتك ⚰️"),
    ("تعيش بدون إنترنت 🚫", "تعيش بدون هاتف 📵"),
    ("تكون مشهور ولا أحد يحبك 📸", "تكون غير معروف وكل من يعرفك يحبك ❤️"),
]

TRUTH_QUESTIONS = [
    "ما أكثر شيء تشعر بالخجل منه؟",
    "ما أكذوبة قلتها وما زلت تتذكرها؟",
    "ما أغرب شيء فعلته وحيداً؟",
    "من آخر شخص بحثت عن بروفايله؟",
    "ما الشيء الذي لو علمه أهلك لعاقبوك؟",
    "ما أكثر رسالة تندم على إرسالها؟",
    "هل سبق أن حذفت تعليقاً بعد كتابته؟",
    "ما أكثر شيء تكذب فيه على نفسك؟",
]

DARE_CHALLENGES = [
    "اكتب جملة بالكلام المقلوب!",
    "اكتب رسالة حب لأحد في الشات!",
    "غير اسمك في الديسكورد لـ 10 دقائق!",
    "أرسل أول صورة في معرضك!",
    "اكتب أغرب شيء يخطر ببالك الآن!",
    "اكتب كلاماً وكأنك روبوت!",
    "اكتب قصيدة بسيطة في 3 أسطر!",
    "قلد أحد الأشخاص في الشات بالكتابة!",
]


class مرح(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="8بول")
    async def eight_ball(self, ctx, *, السؤال: str):
        """اسأل الكرة السحرية. مثال: !8بول هل سأنجح؟"""
        answer, color = random.choice(EIGHT_BALL_ANSWERS)
        embed = discord.Embed(
            title="🎱 الكرة السحرية",
            color=color
        )
        embed.add_field(name="❓ سؤالك", value=السؤال, inline=False)
        embed.add_field(name="🔮 الإجابة", value=answer, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="مدح")
    async def compliment(self, ctx, عضو: discord.Member = None):
        """امدح نفسك أو شخص آخر. مثال: !مدح @شخص"""
        target = عضو or ctx.author
        embed = discord.Embed(
            title="💐 مدح",
            description=f"{target.mention} — {random.choice(COMPLIMENTS)}",
            color=0xf1c40f
        )
        await ctx.send(embed=embed)

    @commands.command(name="شتيمة")
    async def roast(self, ctx, عضو: discord.Member = None):
        """شتيمة مضحكة لطيفة. مثال: !شتيمة @شخص"""
        target = عضو or ctx.author
        embed = discord.Embed(
            title="🔥 شتيمة مضحكة",
            description=f"{target.mention} — {random.choice(INSULTS_FUNNY)}",
            color=0xe74c3c
        )
        embed.set_footer(text="هذا مجرد مزاح 😄")
        await ctx.send(embed=embed)

    @commands.command(name="أو")
    async def would_you_rather(self, ctx):
        """لعبة أيهما تفضل؟"""
        a, b = random.choice(WOULD_YOU_RATHER)
        embed = discord.Embed(
            title="🤔 أيهما تفضل؟",
            description=f"**الخيار الأول:** {a}\n\n**أم الخيار الثاني:** {b}",
            color=0x9b59b6
        )
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")

    @commands.command(name="صح-أو-جرأة")
    async def truth_or_dare(self, ctx):
        """لعبة صح أو جرأة"""
        embed = discord.Embed(
            title="🎭 صح أو جرأة؟",
            description="اختر: **صح** أم **جرأة**؟",
            color=0xe67e22
        )
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("🔥")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅","🔥"] and reaction.message.id == msg.id

        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=20.0)
        except asyncio.TimeoutError:
            await ctx.send("⏰ انتهى الوقت!")
            return

        if str(reaction.emoji) == "✅":
            result = random.choice(TRUTH_QUESTIONS)
            title = "✅ صح — أجب بصدق!"
            color = 0x3498db
        else:
            result = random.choice(DARE_CHALLENGES)
            title = "🔥 جرأة — نفذ!"
            color = 0xe74c3c

        embed2 = discord.Embed(title=title, description=result, color=color)
        await ctx.send(embed=embed2)

    @commands.command(name="عمر")
    async def age_game(self, ctx, عضو: discord.Member = None):
        """تخمين عشوائي لعمرك 😄"""
        target = عضو or ctx.author
        age = random.randint(12, 65)
        embed = discord.Embed(
            title="🎂 تخمين العمر",
            description=f"{target.mention} يبدو وكأن عمره **{age} سنة**! 😄",
            color=0xf39c12
        )
        embed.set_footer(text="هذا مجرد تخمين عشوائي للمتعة!")
        await ctx.send(embed=embed)

    @commands.command(name="ذكاء")
    async def iq_game(self, ctx, عضو: discord.Member = None):
        """تخمين عشوائي لنسبة الذكاء 😄"""
        target = عضو or ctx.author
        iq = random.randint(60, 180)
        if iq >= 140:
            msg = "عبقري فوق المستوى! 🧠✨"
        elif iq >= 110:
            msg = "ذكاء فوق المتوسط. 👍"
        elif iq >= 90:
            msg = "ذكاء عادي، لا بأس. 😊"
        else:
            msg = "...لا تقلق، لكل واحد موهبته! 😅"
        embed = discord.Embed(
            title="🧠 مقياس الذكاء",
            description=f"{target.mention}: نسبة ذكاء **{iq}** — {msg}",
            color=0x9b59b6
        )
        embed.set_footer(text="هذا مجرد مزاح!")
        await ctx.send(embed=embed)

    @commands.command(name="عشق")
    async def love_calc(self, ctx, شخص1: discord.Member, شخص2: discord.Member = None):
        """احسب نسبة العشق بين شخصين 💕"""
        partner = شخص2 or ctx.author
        percent = random.randint(0, 100)
        if percent >= 80:
            hearts = "❤️❤️❤️❤️❤️"
            msg = "قصة حب من الزمن الجميل!"
        elif percent >= 60:
            hearts = "❤️❤️❤️💔💔"
            msg = "في أمل كبير!"
        elif percent >= 40:
            hearts = "❤️❤️💔💔💔"
            msg = "يحتاج شوي جهد."
        else:
            hearts = "💔💔💔💔💔"
            msg = "الأمور صعبة شوي..."
        embed = discord.Embed(
            title="💕 حاسبة العشق",
            description=f"{شخص1.mention} ❤️ {partner.mention}\n\n**{percent}%** {hearts}\n{msg}",
            color=0xe91e8c
        )
        await ctx.send(embed=embed)

    @commands.command(name="هروب")
    async def escape_rate(self, ctx):
        """ما نسبة نجاحك في الهروب من موقف محرج؟"""
        rate = random.randint(0, 100)
        embed = discord.Embed(
            title="🏃 نسبة الهروب الناجح",
            description=f"لو حاولت الهروب من موقف محرج، نسبة نجاحك **{rate}%**!",
            color=0x1abc9c
        )
        await ctx.send(embed=embed)

    @commands.command(name="اقتباس")
    async def quote(self, ctx):
        """اقتباس عربي ملهم"""
        quotes = [
            ("الحياة قصيرة، فلا تضيع وقتك في الكراهية.", "مجهول"),
            ("النجاح ليس نهاية المطاف، والفشل ليس قاتلاً.", "ونستون تشرشل"),
            ("كن التغيير الذي تريد أن تراه في العالم.", "غاندي"),
            ("العقل السليم في الجسم السليم.", "مثل عربي"),
            ("من جد وجد، ومن زرع حصد.", "مثل عربي"),
            ("الصبر مفتاح الفرج.", "مثل عربي"),
            ("لا تؤجل عمل اليوم إلى الغد.", "مثل عربي"),
            ("العلم نور والجهل ظلام.", "مثل عربي"),
            ("القراءة خير جليس.", "مثل عربي"),
            ("اللي ما يعرف الصقر يشويه.", "مثل خليجي"),
        ]
        text, author = random.choice(quotes)
        embed = discord.Embed(
            title="💬 اقتباس",
            description=f"*\"{text}\"*\n\n— **{author}**",
            color=0x2c3e50
        )
        await ctx.send(embed=embed)

    @commands.command(name="طالعلك")
    async def fortune(self, ctx):
        """ما الذي طالع لك اليوم؟"""
        fortunes = [
            "🍕 طالعلك أكل لذيذ اليوم!",
            "💰 طالعلك فلوس من مكان غير متوقع!",
            "😴 طالعلك نوم طويل وعميق!",
            "📱 طالعلك رسالة من شخص غريب!",
            "🎮 طالعلك يوم ألعاب بلا نهاية!",
            "☕ طالعلك قهوة تعدل مزاجك!",
            "🌧️ طالعلك موقف محرج اليوم... احذر!",
            "🏆 طالعلك نجاح في شيء صعب!",
            "🤝 طالعلك صداقة جديدة!",
            "📚 طالعلك معلومة جديدة تستفيد منها!",
        ]
        embed = discord.Embed(
            title=f"🔮 طالع {ctx.author.display_name}",
            description=random.choice(fortunes),
            color=0x8e44ad
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(مرح(bot))
