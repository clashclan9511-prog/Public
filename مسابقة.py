import discord
from discord.ext import commands
import random
import asyncio

QUESTIONS = [
    {"سؤال": "ما عاصمة المملكة العربية السعودية؟", "إجابة": "الرياض", "خيارات": ["الرياض","جدة","مكة","الدمام"]},
    {"سؤال": "كم عدد أيام السنة؟", "إجابة": "365", "خيارات": ["360","365","366","364"]},
    {"سؤال": "ما أكبر كوكب في المجموعة الشمسية؟", "إجابة": "المشتري", "خيارات": ["زحل","المشتري","أورانوس","نبتون"]},
    {"سؤال": "ما عاصمة مصر؟", "إجابة": "القاهرة", "خيارات": ["القاهرة","الإسكندرية","أسوان","الجيزة"]},
    {"سؤال": "كم عدد ساعات اليوم؟", "إجابة": "24", "خيارات": ["12","24","48","36"]},
    {"سؤال": "ما أطول نهر في العالم؟", "إجابة": "النيل", "خيارات": ["الأمازون","النيل","المسيسيبي","اليانغتسي"]},
    {"سؤال": "كم كيلومتراً في الميل الواحد؟", "إجابة": "1.6", "خيارات": ["1.2","1.6","2.0","0.8"]},
    {"سؤال": "ما لون السماء الصافية؟", "إجابة": "الأزرق", "خيارات": ["الأحمر","الأخضر","الأزرق","الأصفر"]},
    {"سؤال": "كم عدد أشهر السنة؟", "إجابة": "12", "خيارات": ["10","11","12","13"]},
    {"سؤال": "ما عاصمة الإمارات؟", "إجابة": "أبوظبي", "خيارات": ["دبي","أبوظبي","الشارقة","عجمان"]},
    {"سؤال": "ما أصغر قارة في العالم؟", "إجابة": "أستراليا", "خيارات": ["أوروبا","أستراليا","أنتاركتيكا","أمريكا الجنوبية"]},
    {"سؤال": "كم عدد أضلاع المثلث؟", "إجابة": "3", "خيارات": ["2","3","4","5"]},
    {"سؤال": "ما أكبر دولة في العالم مساحةً؟", "إجابة": "روسيا", "خيارات": ["الصين","كندا","روسيا","أمريكا"]},
    {"سؤال": "ما عاصمة فرنسا؟", "إجابة": "باريس", "خيارات": ["لندن","برلين","باريس","روما"]},
    {"سؤال": "كم لون في قوس قزح؟", "إجابة": "7", "خيارات": ["5","6","7","8"]},
    {"سؤال": "ما أسرع حيوان بري؟", "إجابة": "الفهد", "خيارات": ["الأسد","الفهد","الحصان","الغزال"]},
    {"سؤال": "كم عدد أصابع اليد؟", "إجابة": "5", "خيارات": ["4","5","6","7"]},
    {"سؤال": "ما عاصمة اليابان؟", "إجابة": "طوكيو", "خيارات": ["أوساكا","طوكيو","كيوتو","هيروشيما"]},
    {"سؤال": "ما أعلى جبل في العالم؟", "إجابة": "إيفرست", "خيارات": ["كيليمنجارو","إيفرست","ديناللي","مونت بلانك"]},
    {"سؤال": "كم حرفاً في الأبجدية العربية؟", "إجابة": "28", "خيارات": ["26","28","29","30"]},
]

EMOJIS = ["🇦","🇧","🇨","🇩"]
LETTERS = ["أ", "ب", "ج", "د"]

class مسابقة(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}

    @commands.command(name="مسابقة")
    async def quiz(self, ctx):
        """ابدأ مسابقة معلومات عامة"""
        if ctx.channel.id in self.active:
            await ctx.send("❌ يوجد مسابقة نشطة في هذه القناة!")
            return

        self.active[ctx.channel.id] = True
        q = random.choice(QUESTIONS)
        choices = q["خيارات"][:]
        random.shuffle(choices)
        correct_idx = choices.index(q["إجابة"])

        desc = f"**{q['سؤال']}**\n\n"
        for i, choice in enumerate(choices):
            desc += f"{EMOJIS[i]} {LETTERS[i]}) {choice}\n"

        embed = discord.Embed(
            title="🧠 مسابقة معلومات عامة",
            description=desc,
            color=0x3498db
        )
        embed.set_footer(text="⏰ عندك 20 ثانية للإجابة! اكتب أ، ب، ج، أو د")
        await ctx.send(embed=embed)

        def check(m):
            return m.channel == ctx.channel and not m.author.bot and m.content.strip() in ["أ","ب","ج","د","a","b","c","d","A","B","C","D","1","2","3","4"]

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=20.0)
        except asyncio.TimeoutError:
            del self.active[ctx.channel.id]
            embed = discord.Embed(
                title="⏰ انتهى الوقت!",
                description=f"الإجابة الصحيحة كانت: **{q['إجابة']}**",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        answer_map = {"أ":0,"ب":1,"ج":2,"د":3,"a":0,"b":1,"c":2,"d":3,"A":0,"B":1,"C":2,"D":3,"1":0,"2":1,"3":2,"4":3}
        chosen = answer_map.get(msg.content.strip(), -1)

        del self.active[ctx.channel.id]

        if chosen == correct_idx:
            embed = discord.Embed(
                title="✅ إجابة صحيحة!",
                description=f"مبروك {msg.author.mention}! الإجابة هي **{q['إجابة']}** 🎉",
                color=0x2ecc71
            )
        else:
            embed = discord.Embed(
                title="❌ إجابة خاطئة!",
                description=f"{msg.author.mention} الإجابة الصحيحة هي **{q['إجابة']}**",
                color=0xe74c3c
            )
        await ctx.send(embed=embed)

    @commands.command(name="مسابقة-سريعة")
    async def fast_quiz(self, ctx, العدد: int = 5):
        """مسابقة سريعة متعددة الأسئلة. مثال: !مسابقة-سريعة 5"""
        if العدد < 1 or العدد > 10:
            await ctx.send("❌ اختر عدداً بين 1 و 10!")
            return
        if ctx.channel.id in self.active:
            await ctx.send("❌ يوجد مسابقة نشطة!")
            return

        self.active[ctx.channel.id] = True
        questions = random.sample(QUESTIONS, min(العدد, len(QUESTIONS)))
        scores = {}

        embed = discord.Embed(
            title="🚀 مسابقة سريعة!",
            description=f"ستبدأ مسابقة من **{len(questions)}** أسئلة!\nاكتب الإجابة مباشرة (أ، ب، ج، د)",
            color=0xf39c12
        )
        await ctx.send(embed=embed)
        await asyncio.sleep(2)

        for i, q in enumerate(questions):
            choices = q["خيارات"][:]
            random.shuffle(choices)
            correct_idx = choices.index(q["إجابة"])

            desc = f"**{q['سؤال']}**\n\n"
            for j, choice in enumerate(choices):
                desc += f"{EMOJIS[j]} {LETTERS[j]}) {choice}\n"

            embed = discord.Embed(
                title=f"❓ سؤال {i+1}/{len(questions)}",
                description=desc,
                color=0x9b59b6
            )
            embed.set_footer(text="⏰ 15 ثانية!")
            await ctx.send(embed=embed)

            def check(m):
                return m.channel == ctx.channel and not m.author.bot and m.content.strip() in ["أ","ب","ج","د","a","b","c","d","A","B","C","D"]

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=15.0)
                answer_map = {"أ":0,"ب":1,"ج":2,"د":3,"a":0,"b":1,"c":2,"d":3,"A":0,"B":1,"C":2,"D":3}
                chosen = answer_map.get(msg.content.strip(), -1)
                if chosen == correct_idx:
                    scores[msg.author.display_name] = scores.get(msg.author.display_name, 0) + 1
                    await ctx.send(f"✅ {msg.author.mention} صح! +1 نقطة")
                else:
                    await ctx.send(f"❌ {msg.author.mention} غلط! الإجابة: **{q['إجابة']}**")
            except asyncio.TimeoutError:
                await ctx.send(f"⏰ انتهى الوقت! الإجابة: **{q['إجابة']}**")
            await asyncio.sleep(1)

        del self.active[ctx.channel.id]

        if not scores:
            await ctx.send("📊 لا أحد أجاب صح!")
            return

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        result = "\n".join([f"{'🥇' if i==0 else '🥈' if i==1 else '🥉'} **{name}**: {pts} نقطة" for i, (name, pts) in enumerate(sorted_scores[:3])])
        winner = sorted_scores[0][0]
        embed = discord.Embed(
            title="🏆 نتائج المسابقة",
            description=f"🎉 الفائز: **{winner}**!\n\n{result}",
            color=0xf1c40f
        )
        await ctx.send(embed=embed)

    @commands.command(name="صح-خطأ")
    async def true_false(self, ctx):
        """سؤال صح أو خطأ"""
        statements = [
            ("الأرض هي أقرب كوكب للشمس", False, "عطارد هو الأقرب"),
            ("الحوت الأزرق هو أضخم حيوان على الإطلاق", True, "نعم، هو الأضخم"),
            ("باريس عاصمة إيطاليا", False, "روما هي عاصمة إيطاليا"),
            ("القرآن الكريم 114 سورة", True, "نعم، 114 سورة"),
            ("الذهب عنصر كيميائي رمزه Ag", False, "رمز الذهب Au، وAg هو الفضة"),
            ("عدد لاعبي كرة القدم في الملعب 11 لكل فريق", True, "نعم، 11 لاعب"),
            ("الجمل يخزن الماء في سنامه", False, "يخزن دهوناً وليس ماء"),
            ("اللغة العربية تُكتب من اليمين لليسار", True, "صحيح"),
        ]
        stmt, answer, explanation = random.choice(statements)
        embed = discord.Embed(
            title="✅❌ صح أو خطأ؟",
            description=f"**{stmt}**",
            color=0x3498db
        )
        embed.set_footer(text="⏰ 15 ثانية — اكتب صح أو خطأ")
        await ctx.send(embed=embed)

        def check(m):
            return m.channel == ctx.channel and not m.author.bot and m.content.strip() in ["صح","خطأ","خطا","صحيح","true","false"]

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=15.0)
            user_answer = msg.content.strip() in ["صح","صحيح","true"]
            if user_answer == answer:
                embed = discord.Embed(title="✅ صح!", description=f"{msg.author.mention} أجاب صح! {explanation}", color=0x2ecc71)
            else:
                correct_text = "صح ✅" if answer else "خطأ ❌"
                embed = discord.Embed(title="❌ غلط!", description=f"{msg.author.mention} الإجابة الصحيحة: **{correct_text}**\n{explanation}", color=0xe74c3c)
            await ctx.send(embed=embed)
        except asyncio.TimeoutError:
            correct_text = "صح ✅" if answer else "خطأ ❌"
            await ctx.send(f"⏰ انتهى الوقت! الإجابة: **{correct_text}** — {explanation}")


async def setup(bot):
    await bot.add_cog(مسابقة(bot))
