import discord
from discord.ext import commands

HELP_ROLE_ID = 1505174149625151529


def has_help_role():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        return any(r.id == HELP_ROLE_ID for r in ctx.author.roles)
    return commands.check(predicate)


class العاب(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="مساعدة")
    @has_help_role()
    async def help_command(self, ctx):
        """عرض قائمة الأوامر (للمشرفين فقط)"""
        embed = discord.Embed(
            title="📋 قائمة الأوامر الكاملة",
            description="مرحباً! هذه جميع الأوامر المتاحة:",
            color=0x3498db
        )
        embed.add_field(name="😂 مرح", value=(
            "`!8بول [سؤال]` — الكرة السحرية\n"
            "`!مدح [@شخص]` — مدح\n"
            "`!شتيمة [@شخص]` — شتيمة مضحكة\n"
            "`!أو` — أيهما تفضل؟\n"
            "`!صح-أو-جرأة` — صح أو جرأة\n"
            "`!عمر [@شخص]` — تخمين العمر\n"
            "`!ذكاء [@شخص]` — نسبة الذكاء\n"
            "`!عشق @ش1 @ش2` — حاسبة العشق\n"
            "`!هروب` — نسبة الهروب\n"
            "`!اقتباس` — اقتباس ملهم\n"
            "`!طالعلك` — طالعك اليوم\n"
            "`!نكتة` — نكتة عربية"
        ), inline=True)
        embed.add_field(name="💰 الاقتصاد", value=(
            "`!رصيد [@شخص]` — رصيدك\n"
            "`!يومي` — مكافأة يومية\n"
            "`!شغل` — اكسب عملات\n"
            "`!قمار [مبلغ/كل]` — القمار\n"
            "`!إيداع [مبلغ]` — أودع في البنك\n"
            "`!سحب [مبلغ]` — اسحب من البنك\n"
            "`!تحويل @شخص [مبلغ]` — تحويل\n"
            "`!أثرياء` — قائمة الأثرياء"
        ), inline=True)
        embed.add_field(name="📊 معلومات (للجميع)", value=(
            "`!سيرفر` — معلومات السيرفر\n"
            "`!وقت` — الوقت الحالي"
        ), inline=True)
        embed.add_field(name="📊 معلومات (مشرفين)", value=(
            "`!بروفايل [@شخص]` — بروفايل عضو\n"
            "`!بينق` — سرعة البوت\n"
            "`!عد` — عدد الأعضاء\n"
            "`!رتبة [اسم]` — معلومات رتبة"
        ), inline=True)
        embed.add_field(name="🛡️ الإدارة (رتبة الإشراف)", value=(
            "`!مسح [عدد]` — مسح رسائل\n"
            "`!كتم @شخص [دق] [سبب]` — كتم\n"
            "`!فك-كتم @شخص` — فك كتم\n"
            "`!طرد @شخص [سبب]` — طرد\n"
            "`!فك-حظر [اسم]` — فك حظر\n"
            "`!تحذير @شخص [سبب]` — تحذير\n"
            "`!قفل / !فتح` — قفل/فتح القناة\n"
            "`!إعلان [نص]` — إعلان\n"
            "`!تصويت [سؤال]` — تصويت"
        ), inline=True)
        embed.add_field(name="🔨 الحظر (أدمن فقط)", value=(
            "`!حظر @شخص [سبب]` — حظر عضو\n"
        ), inline=True)
        embed.add_field(name="🧠 مسابقات", value=(
            "`!مسابقة` — سؤال معلومات\n"
            "`!مسابقة-سريعة [عدد]` — أسئلة متعددة\n"
            "`!صح-خطأ` — سؤال صح أو خطأ"
        ), inline=True)
        embed.add_field(name="🎁 هدايا (مشرفين)", value=(
            "`!هدية [ثواني] [فائزون] [جائزة]`\n"
            "`!هدية-سريعة [جائزة]` — 30 ثانية"
        ), inline=True)
        embed.add_field(name="🔧 أدوات", value=(
            "`!شنقة` — لعبة شنقة الكلمة\n"
            "`!عد-تنازلي [ثواني]`\n"
            "`!تذكير [ثواني] [رسالة]`\n"
            "`!عمليات [رقم] [عملية] [رقم]`\n"
            "`!توليد-رقم [أدنى] [أعلى]`\n"
            "`!تشفير [نص]` — عكس النص\n"
            "`!رسالة-سرية @شخص [رسالة]`"
        ), inline=True)
        embed.add_field(name="📈 المستويات", value=(
            "`!مستوى [@شخص]` — مستواك\n"
            "`!ترتيب` — قائمة المستويات"
        ), inline=True)
        embed.add_field(name="👋 الترحيب (أدمن)", value=(
            "`!قناة-ترحيب #قناة`\n"
            "`!قناة-وداع #قناة`\n"
            "`!رسالة-ترحيب [نص]`\n"
            "`!رتبة-تلقائية @رتبة`"
        ), inline=True)
        embed.add_field(name="🎫 التذاكر (أدمن)", value=(
            "`!تذاكر` — إرسال بانل التذاكر\n"
            "`!إحصاء-اداري [@شخص]`\n"
            "`!إحصاء-كل-الاداريين`"
        ), inline=True)
        embed.add_field(name="💡 الاقتراحات (أدمن)", value=(
            "`!روم-اقتراحات #قناة`\n"
            "`!قبول-اقتراح [ID] [سبب]`\n"
            "`!رفض-اقتراح [ID] [سبب]`\n"
            "`!اقتراح-يدوي [نص]`"
        ), inline=True)
        embed.add_field(name="✏️ تغيير الاسم (أدمن)", value=(
            "`!زر-اسم` — بانل تغيير الاسم\n"
            "`!غير-اسم @شخص [اسم]`\n"
            "`!اعادة-اسم @شخص`"
        ), inline=True)
        embed.set_footer(text="Respect Life 🎮 | البريفيكس: !")
        await ctx.send(embed=embed)

    @help_command.error
    async def help_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(العاب(bot))
