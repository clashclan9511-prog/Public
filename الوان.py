import discord
from discord.ext import commands

# Define colors: (label, emoji, role_name, button_style, hex_color)
COLORS = [
    ("أزرق",    "🔵", "أزرق",    discord.ButtonStyle.primary,   0x3498db),
    ("أحمر",    "🔴", "أحمر",    discord.ButtonStyle.danger,    0xe74c3c),
    ("بنفسجي",  "🟣", "بنفسجي",  discord.ButtonStyle.secondary, 0x9b59b6),
    ("أخضر",    "🟢", "أخضر",    discord.ButtonStyle.success,   0x2ecc71),
    ("أصفر",    "🟡", "أصفر",    discord.ButtonStyle.secondary, 0xf1c40f),
    ("وردي",    "🌸", "وردي",    discord.ButtonStyle.secondary, 0xff69b4),
]

MOD_ROLE_ID  = 1505181303971250256
HELP_ROLE_ID = 1505174149625151529


def is_staff():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        return any(r.id in (MOD_ROLE_ID, HELP_ROLE_ID) for r in ctx.author.roles)
    return commands.check(predicate)


def find_role(guild: discord.Guild, name: str) -> discord.Role | None:
    name_l = name.lower().strip()
    for role in guild.roles:
        if role.name.lower().strip() == name_l:
            return role
    return None


class ColorButton(discord.ui.Button):
    def __init__(self, label: str, emoji: str, role_name: str,
                 style: discord.ButtonStyle, color: int):
        super().__init__(label=f"{emoji} {label}", style=style,
                         custom_id=f"color_role_{role_name}")
        self.role_name  = role_name
        self.hex_color  = color

    async def callback(self, interaction: discord.Interaction):
        role = find_role(interaction.guild, self.role_name)
        if not role:
            await interaction.response.send_message(
                f"❌ الرتبة **{self.role_name}** غير موجودة في السيرفر!\n"
                f"اطلب من الإدارة إنشاء رتبة باسم `{self.role_name}`.",
                ephemeral=True
            )
            return

        member = interaction.user
        if role in member.roles:
            await member.remove_roles(role)
            embed = discord.Embed(
                description=f"تم إزالة لون **{role.name}** منك.",
                color=self.hex_color
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            # Remove all other color roles first
            color_roles = [find_role(interaction.guild, c[2]) for c in COLORS]
            color_roles = [r for r in color_roles if r and r in member.roles]
            if color_roles:
                await member.remove_roles(*color_roles)
            await member.add_roles(role)
            embed = discord.Embed(
                description=f"✅ حصلت على لون **{role.name}**!",
                color=self.hex_color
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


class ColorView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for label, emoji, role_name, style, color in COLORS:
            self.add_item(ColorButton(label, emoji, role_name, style, color))


class الوان(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.add_view(ColorView())

    @commands.command(name="زر-الوان")
    @is_staff()
    async def send_color_panel(self, ctx):
        """إرسال بانل اختيار الألوان"""
        embed = discord.Embed(
            title="🎨 اختر لون رتبتك",
            description=(
                "اضغط على الزر الذي يعجبك لتحصل على لون مميز!\n\n"
                "🔵 **أزرق** — هادئ وأنيق\n"
                "🔴 **أحمر** — قوي وجريء\n"
                "🟣 **بنفسجي** — فاخر وملكي\n"
                "🟢 **أخضر** — طبيعي ومنعش\n"
                "🟡 **أصفر** — مشرق ومبهج\n"
                "🌸 **وردي** — رقيق وجميل\n\n"
                "💡 الضغط مرة ثانية على نفس اللون يزيله!"
            ),
            color=0x5865f2
        )
        embed.set_footer(text="Respect Life RP 🎮 | اختر لونك المفضل")
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.message.delete()
        await ctx.send(embed=embed, view=ColorView())


async def setup(bot: commands.Bot):
    await bot.add_cog(الوان(bot))
