import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Синхронизировано {len(synced)} slash команд")
    except Exception as e:
        print(e)

@bot.tree.command(name="join", description="Подключить бота к голосовому каналу по ID")
async def join(interaction: discord.Interaction, channel_id: str):

    channel = interaction.guild.get_channel(int(channel_id))

    if channel is None:
        await interaction.response.send_message("Канал не найден", ephemeral=True)
        return

    if not isinstance(channel, discord.VoiceChannel):
        await interaction.response.send_message("Это не голосовой канал", ephemeral=True)
        return

    try:
        await channel.connect(reconnect=True)
        await interaction.response.send_message(f"Подключился к {channel.name}")
    except Exception as e:
        await interaction.response.send_message(f"Ошибка: {e}")

bot.run(TOKEN)
