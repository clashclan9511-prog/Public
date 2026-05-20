import discord
from discord.ext import commands
import random
import asyncio


HANGMAN_WORDS = [
    "ديسكورد", "برمجة", "حاسوب", "إنترنت", "هاتف",
    "سيارة", "طائرة", "مدرسة", "جامعة", "مستشفى",
    "مطعم", "شاطئ", "جبال", "صحراء", "مدينة",
    "كتاب", "قلم", "ورقة", "مفتاح", "نافذة",
]

WORD_CHAIN_USED = {}


class أوامر_متفرقة(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hangman_games = {}

    @commands.command(name="شنقة")
    async def hangman(self, ctx):
        """لعبة شنقة الكلمة"""
        if ctx.channel.id in self.hangman_games:
            await ctx.send("❌ يوجد لعبة نشطة! اكتب `!تخمين-حرف [حرف]`")
            return

        word = random.choice(HANGMAN_WORDS)
        guessed = set()
        attempts = 6

        self.hangman_games[ctx.channel.id] = {
            "word": word,
            "guessed": guessed,
            "attempts": attempts,
        }

        display = " ".join(["_" if c not in guessed else c for c in word])
        embed = discord.Embed(
            title="🎯 لعبة الشنقة",
            description=f"**الكلمة:** `{display}`\n\n💔 المحاولات المتبقية: **{attempts}**\n\nاكتب `!تخمين-حرف [حرف]` لتخمين حرف",
            color=0x3498db
        )
        await ctx.send(embed=embed)

    @commands.command(name="تخمين-حرف")
    async def guess_letter(self, ctx, حرف: str):
        """تخمين حرف في لعبة الشنقة. مثال: !تخمين-حرف م"""
        if ctx.channel.id not in self.hangman_games:
            await ctx.send("❌ لا توجد لعبة! ابدأ بـ `!شنقة`")
            return

        game = self.hangman_games[ctx.channel.id]
        word = game["word"]
        guessed = game["guessed"]
        letter = حرف.strip()[0]

        if letter in guessed:
            await ctx.send(f"❌ خمّنت **{letter}** من قبل!")
            return

        guessed.add(letter)
        display = " ".join([c if c in guessed else "_" for c in word])

        if letter not in word:
            game["attempts"] -= 1
            attempts = game["attempts"]
            hangman_stages = ["😵","😨","😰","😟","😕","🙁","😐"]
            stage = hangman_stages[max(0, 6 - attempts)]

            if attempts <= 0:
                del self.hangman_games[ctx.channel.id]
                embed = discord.Embed(
                    title=f"💀 انتهت اللعبة! {stage}",
                    description=f"الكلمة كانت: **{word}**",
                    color=0xe74c3c
                )
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title=f"❌ خطأ! {stage}",
                description=f"**الكلمة:** `{display}`\n\n💔 محاولات متبقية: **{attempts}**\n🔤 حروف مخمّنة: {' '.join(guessed)}",
                color=0xe67e22
            )
        else:
            if all(c in guessed for c in word):
                del self.hangman_games[ctx.channel.id]
                embed = discord.Embed(
                    title="🎉 فزت!",
                    description=f"الكلمة هي: **{word}** 🏆",
                    color=0x2ecc71
                )
                await ctx.send(embed=embed)
                return
            embed = discord.Embed(
                title="✅ صح!",
                description=f"**الكلمة:** `{display}`\n\n💔 محاولات متبقية: **{game['attempts']}**\n🔤 حروف مخمّنة: {' '.join(guessed)}",
                color=0x2ecc71
            )
        await ctx.send(embed=embed)

    @commands.command(name="عد-تنازلي")
    async def countdown(self, ctx, الثواني: int = 10):
        """عد تنازلي. مثال: !عد-تنازلي 10"""
        if الثواني < 1 or الثواني > 60:
            await ctx.send("❌ اختر رقماً بين 1 و 60!")
            return
        embed = discord.Embed(title=f"⏳ عد تنازلي: {الثواني}", color=0xf39c12)
        msg = await ctx.send(embed=embed)
        for i in range(الثواني - 1, 0, -1):
            await asyncio.sleep(1)
            embed = discord.Embed(title=f"⏳ عد تنازلي: {i}", color=0xf39c12 if i > 3 else 0xe74c3c)
            await msg.edit(embed=embed)
        await asyncio.sleep(1)
        embed = discord.Embed(title="💥 انتهى الوقت!", color=0xe74c3c)
        await msg.edit(embed=embed)

    @commands.command(name="قرار")
    async def decision(self, ctx, *, الموقف: str):
        """احصل على قرار لموقف. مثال: !قرار هل أنام مبكراً؟"""
        decisions = ["✅ نعم، افعلها!", "❌ لا، تجنب ذلك.", "🤔 فكّر مرة أخرى.", "😂 بالتأكيد لا!", "🎯 الوقت مناسب!", "⏰ انتظر قليلاً."]
        embed = discord.Embed(
            title="🎱 القرار",
            description=f"**الموقف:** {الموقف}\n\n**القرار:** {random.choice(decisions)}",
            color=0x9b59b6
        )
        await ctx.send(embed=embed)

    @commands.command(name="تذكير")
    async def reminder(self, ctx, الثواني: int, *, الرسالة: str):
        """ذكّرني بشيء. مثال: !تذكير 60 اشرب ماء"""
        if الثواني < 5 or الثواني > 3600:
            await ctx.send("❌ اختر وقتاً بين 5 ثواني و3600 ثانية (ساعة)!")
            return
        await ctx.send(f"✅ سأذكّرك بـ **{الرسالة}** خلال **{الثواني}** ثانية!")
        await asyncio.sleep(الثواني)
        embed = discord.Embed(
            title="⏰ تذكير!",
            description=f"{ctx.author.mention} — **{الرسالة}**",
            color=0x3498db
        )
        await ctx.send(embed=embed)

    @commands.command(name="رسالة-سرية")
    async def secret_message(self, ctx, عضو: discord.Member, *, الرسالة: str):
        """أرسل رسالة سرية لعضو عبر DM. مثال: !رسالة-سرية @شخص مرحباً!"""
        try:
            embed = discord.Embed(
                title=f"📩 رسالة سرية من {ctx.author.display_name}",
                description=الرسالة,
                color=0x2c3e50
            )
            embed.set_footer(text=f"من: {ctx.guild.name}")
            await عضو.send(embed=embed)
            await ctx.message.delete()
            confirm = await ctx.send(f"✅ تم إرسال الرسالة السرية لـ {عضو.mention}!")
            await asyncio.sleep(3)
            await confirm.delete()
        except discord.Forbidden:
            await ctx.send("❌ لا يمكن إرسال رسالة لهذا العضو (DM مغلق).")

    @commands.command(name="توليد-رقم")
    async def random_number(self, ctx, الأدنى: int = 1, الأعلى: int = 100):
        """توليد رقم عشوائي. مثال: !توليد-رقم 1 1000"""
        if الأدنى >= الأعلى:
            await ctx.send("❌ الرقم الأدنى يجب أن يكون أصغر من الأعلى!")
            return
        result = random.randint(الأدنى, الأعلى)
        embed = discord.Embed(
            title="🎲 رقم عشوائي",
            description=f"بين **{الأدنى}** و **{الأعلى}**:\n\n# **{result}**",
            color=0x1abc9c
        )
        await ctx.send(embed=embed)

    @commands.command(name="عمليات")
    async def math(self, ctx, الرقم_الأول: float, العملية: str, الرقم_الثاني: float):
        """حاسبة. مثال: !عمليات 10 + 5"""
        ops = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "x": lambda a, b: a * b, "×": lambda a, b: a * b}
        if العملية == "/" or العملية == "÷":
            if الرقم_الثاني == 0:
                await ctx.send("❌ لا يمكن القسمة على صفر!")
                return
            result = الرقم_الأول / الرقم_الثاني
        elif العملية in ops:
            result = ops[العملية](الرقم_الأول, الرقم_الثاني)
        else:
            await ctx.send("❌ العملية غير صحيحة! استخدم: + - * /")
            return

        embed = discord.Embed(
            title="🔢 الحاسبة",
            description=f"`{الرقم_الأول} {العملية} {الرقم_الثاني} = **{result:g}**`",
            color=0x3498db
        )
        await ctx.send(embed=embed)

    @commands.command(name="اختصار")
    async def mock_shorten(self, ctx, *, النص: str):
        """اقلب النص بين كبير وصغير 🤪"""
        result = "".join([c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(النص)])
        await ctx.send(f"```{result}```")

    @commands.command(name="تشفير")
    async def reverse_text(self, ctx, *, النص: str):
        """اعكس النص. مثال: !تشفير مرحبا"""
        embed = discord.Embed(
            title="🔄 النص المعكوس",
            description=f"`{النص[::-1]}`",
            color=0x8e44ad
        )
        await ctx.send(embed=embed)

    @commands.command(name="تكرار")
    @commands.has_permissions(manage_messages=True)
    async def repeat(self, ctx, العدد: int, *, الرسالة: str):
        """كرر رسالة. مثال: !تكرار 3 مرحبا"""
        if العدد < 1 or العدد > 5:
            await ctx.send("❌ اختر عدداً بين 1 و 5!")
            return
        await ctx.message.delete()
        for _ in range(العدد):
            await ctx.send(الرسالة)

    @commands.command(name="أفضل")
    async def best_of(self, ctx, *الأشخاص: discord.Member):
        """من هو الأفضل؟ مثال: !أفضل @شخص1 @شخص2 @شخص3"""
        if len(الأشخاص) < 2:
            await ctx.send("❌ أضف شخصين على الأقل!")
            return
        winner = random.choice(الأشخاص)
        embed = discord.Embed(
            title="🏆 الأفضل هو...",
            description=f"من بين {len(الأشخاص)} أشخاص...\n\n🌟 **{winner.display_name}** هو الأفضل! 🌟",
            color=0xf1c40f
        )
        embed.set_thumbnail(url=winner.display_avatar.url)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(أوامر_متفرقة(bot))
