import discord
from discord.ext import commands
import json
import os
from datetime import datetime

BACKUP_DIR = "data/backups"


def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)


def role_to_dict(role: discord.Role) -> dict:
    return {
        "name":        role.name,
        "color":       role.color.value,
        "hoist":       role.hoist,
        "mentionable": role.mentionable,
        "permissions": role.permissions.value,
        "position":    role.position,
    }


def channel_to_dict(ch) -> dict:
    base = {
        "name":     ch.name,
        "type":     str(ch.type),
        "position": ch.position,
        "overwrites": {},
    }
    for target, overwrite in ch.overwrites.items():
        ow_allow, ow_deny = overwrite.pair()
        key = f"role:{target.name}" if isinstance(target, discord.Role) else f"member:{target.id}"
        base["overwrites"][key] = {"allow": ow_allow.value, "deny": ow_deny.value}

    if isinstance(ch, discord.TextChannel):
        base["topic"]      = ch.topic or ""
        base["slowmode"]   = ch.slowmode_delay
        base["nsfw"]       = ch.is_nsfw()
    elif isinstance(ch, discord.VoiceChannel):
        base["bitrate"]    = ch.bitrate
        base["user_limit"] = ch.user_limit
    return base


class نسخ(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        os.makedirs(BACKUP_DIR, exist_ok=True)

    # ── نسخ كامل ─────────────────────────────────────────────────────────────

    @commands.command(name="نسخ-سيرفر")
    @is_admin()
    async def backup_server(self, ctx):
        """نسخ احتياطي كامل للسيرفر"""
        msg = await ctx.send("⏳ جاري إنشاء النسخة الاحتياطية...")
        g = ctx.guild

        backup = {
            "meta": {
                "guild_id":   g.id,
                "guild_name": g.name,
                "created_at": datetime.utcnow().isoformat(),
                "created_by": str(ctx.author),
            },
            "server": {
                "name":               g.name,
                "description":        g.description or "",
                "afk_timeout":        g.afk_timeout,
                "verification_level": str(g.verification_level),
                "default_notifications": str(g.default_notifications),
            },
            "roles":      [],
            "categories": [],
            "channels":   [],
            "emojis":     [],
        }

        # Roles (skip @everyone)
        for role in sorted(g.roles, key=lambda r: r.position):
            if role.is_default():
                continue
            backup["roles"].append(role_to_dict(role))

        # Categories + their channels
        for cat in sorted(g.categories, key=lambda c: c.position):
            cat_data = {
                "name":     cat.name,
                "position": cat.position,
                "channels": [],
                "overwrites": {},
            }
            for target, overwrite in cat.overwrites.items():
                ow_allow, ow_deny = overwrite.pair()
                key = f"role:{target.name}" if isinstance(target, discord.Role) else f"member:{target.id}"
                cat_data["overwrites"][key] = {"allow": ow_allow.value, "deny": ow_deny.value}
            for ch in sorted(cat.channels, key=lambda c: c.position):
                cat_data["channels"].append(channel_to_dict(ch))
            backup["categories"].append(cat_data)

        # Channels without category
        for ch in sorted(g.channels, key=lambda c: c.position):
            if ch.category is None and not isinstance(ch, discord.CategoryChannel):
                backup["channels"].append(channel_to_dict(ch))

        # Emojis
        for emoji in g.emojis:
            backup["emojis"].append({"name": emoji.name, "animated": emoji.animated})

        # Save to file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename  = f"{BACKUP_DIR}/{g.id}_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(backup, f, ensure_ascii=False, indent=2)

        role_count = len(backup["roles"])
        cat_count  = len(backup["categories"])
        ch_count   = sum(len(c["channels"]) for c in backup["categories"]) + len(backup["channels"])

        embed = discord.Embed(
            title="✅ تم إنشاء النسخة الاحتياطية",
            description=f"**{g.name}** — {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC",
            color=0x2ecc71
        )
        embed.add_field(name="🎭 الرتب",    value=f"{role_count} رتبة",   inline=True)
        embed.add_field(name="📁 الفئات",   value=f"{cat_count} فئة",     inline=True)
        embed.add_field(name="💬 القنوات",  value=f"{ch_count} قناة",     inline=True)
        embed.add_field(name="😀 الإيموجي", value=f"{len(backup['emojis'])} إيموجي", inline=True)
        embed.add_field(name="📄 اسم الملف", value=f"`{os.path.basename(filename)}`", inline=False)
        embed.set_footer(text=f"بواسطة {ctx.author.display_name}")
        await msg.edit(content=None, embed=embed)

    # ── عرض النسخ ────────────────────────────────────────────────────────────

    @commands.command(name="قائمة-النسخ")
    @is_admin()
    async def list_backups(self, ctx):
        """عرض قائمة النسخ الاحتياطية المحفوظة"""
        files = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".json")]
        if not files:
            await ctx.send("❌ لا توجد نسخ احتياطية محفوظة!")
            return

        files.sort(reverse=True)
        lines = []
        for i, fname in enumerate(files[:15], 1):
            path = f"{BACKUP_DIR}/{fname}"
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                meta = data.get("meta", {})
                lines.append(
                    f"`{i}.` **{meta.get('guild_name','؟')}** — "
                    f"`{meta.get('created_at','')[:16].replace('T',' ')}` UTC\n"
                    f"    📄 `{fname}`"
                )
            except Exception:
                lines.append(f"`{i}.` `{fname}`")

        embed = discord.Embed(
            title="📋 قائمة النسخ الاحتياطية",
            description="\n".join(lines),
            color=0x3498db
        )
        embed.set_footer(text=f"إجمالي: {len(files)} نسخة")
        await ctx.send(embed=embed)

    # ── عرض تفاصيل نسخة ──────────────────────────────────────────────────────

    @commands.command(name="تفاصيل-نسخة")
    @is_admin()
    async def backup_details(self, ctx, *, اسم_الملف: str):
        """عرض تفاصيل نسخة معينة. مثال: !تفاصيل-نسخة اسم_الملف.json"""
        path = f"{BACKUP_DIR}/{اسم_الملف}"
        if not os.path.exists(path):
            await ctx.send(f"❌ الملف `{اسم_الملف}` غير موجود! استخدم `!قائمة-النسخ` لرؤية الأسماء.")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            await ctx.send("❌ فشل قراءة الملف!")
            return

        meta = data.get("meta", {})
        roles = data.get("roles", [])
        cats  = data.get("categories", [])
        chs   = data.get("channels", [])
        total_ch = sum(len(c["channels"]) for c in cats) + len(chs)

        role_names = ", ".join(r["name"] for r in roles[:20])
        if len(roles) > 20:
            role_names += f" ... وأكثر ({len(roles) - 20})"

        embed = discord.Embed(
            title=f"📄 تفاصيل النسخة — {meta.get('guild_name','؟')}",
            color=0x9b59b6
        )
        embed.add_field(name="📅 التاريخ",   value=meta.get("created_at","")[:16].replace("T"," ") + " UTC", inline=True)
        embed.add_field(name="👤 بواسطة",    value=meta.get("created_by","؟"), inline=True)
        embed.add_field(name="🆔 Guild ID",  value=meta.get("guild_id","؟"),   inline=True)
        embed.add_field(name="🎭 الرتب",     value=f"{len(roles)} رتبة", inline=True)
        embed.add_field(name="📁 الفئات",    value=f"{len(cats)} فئة",   inline=True)
        embed.add_field(name="💬 القنوات",   value=f"{total_ch} قناة",   inline=True)
        embed.add_field(name="🎭 أسماء الرتب", value=role_names or "لا توجد", inline=False)
        cat_names = " | ".join(c["name"] for c in cats)
        embed.add_field(name="📁 الفئات",    value=cat_names or "لا توجد", inline=False)
        await ctx.send(embed=embed)

    # ── استعادة الرتب ─────────────────────────────────────────────────────────

    @commands.command(name="استعادة-رتب")
    @is_admin()
    async def restore_roles(self, ctx, *, اسم_الملف: str):
        """استعادة الرتب من نسخة احتياطية. مثال: !استعادة-رتب اسم_الملف.json"""
        path = f"{BACKUP_DIR}/{اسم_الملف}"
        if not os.path.exists(path):
            await ctx.send(f"❌ الملف `{اسم_الملف}` غير موجود!")
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        roles = data.get("roles", [])
        if not roles:
            await ctx.send("❌ لا توجد رتب في هذه النسخة!")
            return

        msg = await ctx.send(f"⏳ جاري استعادة **{len(roles)}** رتبة...")
        created = 0
        skipped = 0
        for role_data in roles:
            existing = discord.utils.get(ctx.guild.roles, name=role_data["name"])
            if existing:
                skipped += 1
                continue
            try:
                await ctx.guild.create_role(
                    name=role_data["name"],
                    color=discord.Color(role_data["color"]),
                    hoist=role_data["hoist"],
                    mentionable=role_data["mentionable"],
                    permissions=discord.Permissions(role_data["permissions"]),
                )
                created += 1
            except Exception:
                skipped += 1

        embed = discord.Embed(
            title="✅ تمت استعادة الرتب",
            description=f"✅ أُنشئت: **{created}** رتبة\n⏭️ تجاوزت (موجودة): **{skipped}** رتبة",
            color=0x2ecc71
        )
        await msg.edit(content=None, embed=embed)

    # ── استعادة القنوات ───────────────────────────────────────────────────────

    @commands.command(name="استعادة-قنوات")
    @is_admin()
    async def restore_channels(self, ctx, *, اسم_الملف: str):
        """استعادة الفئات والقنوات من نسخة. مثال: !استعادة-قنوات اسم_الملف.json"""
        path = f"{BACKUP_DIR}/{اسم_الملف}"
        if not os.path.exists(path):
            await ctx.send(f"❌ الملف `{اسم_الملف}` غير موجود!")
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        categories = data.get("categories", [])
        if not categories:
            await ctx.send("❌ لا توجد فئات/قنوات في هذه النسخة!")
            return

        msg = await ctx.send(f"⏳ جاري استعادة **{len(categories)}** فئة...")
        created_cats = 0
        created_chs  = 0

        for cat_data in categories:
            existing_cat = discord.utils.get(ctx.guild.categories, name=cat_data["name"])
            if not existing_cat:
                try:
                    existing_cat = await ctx.guild.create_category(name=cat_data["name"])
                    created_cats += 1
                except Exception:
                    continue

            for ch_data in cat_data.get("channels", []):
                existing_ch = discord.utils.get(ctx.guild.channels, name=ch_data["name"])
                if existing_ch:
                    continue
                try:
                    ch_type = ch_data.get("type", "text")
                    if "voice" in ch_type:
                        await ctx.guild.create_voice_channel(
                            name=ch_data["name"], category=existing_cat)
                    else:
                        await ctx.guild.create_text_channel(
                            name=ch_data["name"], category=existing_cat,
                            topic=ch_data.get("topic") or None)
                    created_chs += 1
                except Exception:
                    pass

        embed = discord.Embed(
            title="✅ تمت استعادة القنوات",
            description=f"📁 فئات أُنشئت: **{created_cats}**\n💬 قنوات أُنشئت: **{created_chs}**",
            color=0x2ecc71
        )
        await msg.edit(content=None, embed=embed)

    # ── حذف نسخة ─────────────────────────────────────────────────────────────

    @commands.command(name="حذف-نسخة")
    @is_admin()
    async def delete_backup(self, ctx, *, اسم_الملف: str):
        """حذف نسخة احتياطية. مثال: !حذف-نسخة اسم_الملف.json"""
        path = f"{BACKUP_DIR}/{اسم_الملف}"
        if not os.path.exists(path):
            await ctx.send(f"❌ الملف `{اسم_الملف}` غير موجود!")
            return
        os.remove(path)
        await ctx.send(f"🗑️ تم حذف النسخة `{اسم_الملف}` بنجاح!")

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ هذا الأمر للأدمن فقط!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ ناقص اسم الملف! استخدم `!قائمة-النسخ` لرؤية الأسماء.")


async def setup(bot):
    await bot.add_cog(نسخ(bot))
