import discord
from discord.ext import commands
import os
from openai import AsyncOpenAI

AI_CHANNEL_ID = 1506464861801152562

# conversation history per user: user_id -> list of messages
histories: dict[int, list[dict]] = {}
MAX_HISTORY = 10  # last N exchanges to keep context

client = AsyncOpenAI(
    base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL"),
    api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY"),
)

SYSTEM_PROMPT = (
    "أنت مساعد ذكي اسمك 'Respect AI'، تابع لسيرفر Respect Life RP. "
    "تتحدث باللغة العربية فقط. ردودك قصيرة ومفيدة ومحترمة. "
    "لا تتحدث عن مواضيع غير لائقة أو مسيئة. "
    "إذا سألك أحد عن هويتك، قل أنك بوت ذكاء اصطناعي للسيرفر."
)


class ذكاء(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.guild:
            return
        if message.channel.id != AI_CHANNEL_ID:
            return
        if message.content.startswith("!"):
            return

        uid = message.author.id

        # Build history
        if uid not in histories:
            histories[uid] = []

        histories[uid].append({"role": "user", "content": message.content})

        # Keep only last MAX_HISTORY exchanges
        if len(histories[uid]) > MAX_HISTORY * 2:
            histories[uid] = histories[uid][-(MAX_HISTORY * 2):]

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + histories[uid]

        async with message.channel.typing():
            try:
                response = await client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=messages,
                    max_completion_tokens=1024,
                )
                reply = response.choices[0].message.content.strip()
            except Exception as e:
                reply = f"❌ حدث خطأ أثناء الاتصال بالذكاء الاصطناعي. حاول مرة ثانية."
                histories[uid].pop()  # remove failed message
                await message.channel.send(reply)
                return

        histories[uid].append({"role": "assistant", "content": reply})

        embed = discord.Embed(description=reply, color=0x5865f2)
        embed.set_author(
            name="Respect AI 🤖",
            icon_url=self.bot.user.display_avatar.url if self.bot.user else None
        )
        embed.set_footer(
            text=f"رد على {message.author.display_name}",
            icon_url=message.author.display_avatar.url
        )
        await message.channel.send(embed=embed)

    @commands.command(name="مسح-محادثة")
    async def clear_history(self, ctx):
        """مسح سجل محادثتك مع الذكاء الاصطناعي"""
        if ctx.channel.id != AI_CHANNEL_ID:
            return
        histories.pop(ctx.author.id, None)
        await ctx.send(f"✅ {ctx.author.mention} تم مسح سجل محادثتك!", delete_after=5)
        await ctx.message.delete()


async def setup(bot: commands.Bot):
    await bot.add_cog(ذكاء(bot))
