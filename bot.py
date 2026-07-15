import discord
from discord.ext import commands
import requests
import asyncio

TOKEN = "9b5f896e199287ac7d2e9e33508204d73e16667a76dd269cf607fbf87e02996e"

API_URL = "https://lostfront.ru/api/confirm.php"

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

# ИСПРАВЛЕНИЕ: добавлен command_prefix="!"
bot = commands.Bot(command_prefix="!", intents=intents)

class VerifyModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Привязка аккаунта")
        # ИСПРАВЛЕНИЕ: TextInput вместо InputText
        self.code = discord.ui.TextInput(
            label="Введите код с сайта",
            placeholder="LF-XXXX-XXXX",
            required=True,
            max_length=30
        )
        self.add_item(self.code)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            r = requests.post(API_URL, json={
                "code": self.code.value,
                "discord_id": str(interaction.user.id),
                "discord_name": interaction.user.name
            }, timeout=10)
            data = r.json()
        except Exception:
            await interaction.followup.send("❌ Не удалось связаться с сайтом.", ephemeral=True)
            return

        if data.get("success"):
            await interaction.followup.send("✅ Аккаунт успешно привязан!", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {data.get('message','Ошибка')}", ephemeral=True)

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔗 Привязать аккаунт",
        style=discord.ButtonStyle.green,
        custom_id="lostfront_verify"
    )
    async def verify_button(self, button, interaction):
        await interaction.response.send_modal(VerifyModal())

@bot.event
async def on_ready():
    print("=" * 40)
    print(f"Бот: {bot.user}")
    print("Статус: ONLINE")
    bot.add_view(VerifyView())
    await bot.change_presence(activity=discord.Game(name="LostFront"))
    print("=" * 40)

# Примечание: slash_command работает в discord.py через app_commands, 
# если не установлена библиотека py-cord.
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(
        title="🪖 Регистрация LostFront",
        description="Для привязки аккаунта нажмите кнопку ниже.",
        color=0xc62828
    )
    await ctx.send(embed=embed, view=VerifyView())

bot.run(TOKEN)
