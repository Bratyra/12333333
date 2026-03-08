import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# чтобы помнить канал
voice_channel_id = None


@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Синхронизировано {len(synced)} команд")
    except Exception as e:
        print(e)


@bot.tree.command(name="join", description="Бот заходит в голосовой канал по ID")
async def join(interaction: discord.Interaction, channel_id: str):
    global voice_channel_id

    await interaction.response.defer()

    channel = interaction.guild.get_channel(int(channel_id))

    if channel is None:
        await interaction.followup.send("Канал не найден")
        return

    if not isinstance(channel, discord.VoiceChannel):
        await interaction.followup.send("Это не голосовой канал")
        return

    vc = interaction.guild.voice_client

    if vc is not None:
        await interaction.followup.send("Бот уже подключен к голосовому каналу")
        return

    try:
        await channel.connect(reconnect=True)
        voice_channel_id = channel.id
        await interaction.followup.send(f"Подключился к {channel.name}")
    except Exception as e:
        await interaction.followup.send(f"Ошибка подключения: {e}")


# если бота кикнули — он возвращается
@bot.event
async def on_voice_state_update(member, before, after):
    global voice_channel_id

    if member.id != bot.user.id:
        return

    if after.channel is None and voice_channel_id is not None:
        guild = before.channel.guild
        channel = guild.get_channel(voice_channel_id)

        if channel:
            try:
                await channel.connect(reconnect=True)
                print("Переподключился к голосовому каналу")
            except:
                pass


bot.run(TOKEN)
