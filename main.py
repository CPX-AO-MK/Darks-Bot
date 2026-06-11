import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
from flask import Flask
from threading import Thread

# --- ESTRUTURA PARA O RENDER (MANTÉM O BOT ONLINE) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Darks está online!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

t = Thread(target=run_flask)
t.start()

# --- CONFIGURAÇÕES DO BOT ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "dados.json"

def carregar_dados():
    if not os.path.exists(DATA_FILE):
        return {"metas": {}, "tickets_ativos": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# --- CLASSE DO PAINEL DE RECRUTAMENTO ---
class PainelRecrutamentoView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fazer Recrutamento 🛡️", style=discord.ButtonStyle.danger, custom_id="btn_ticket")
    async def criar_ticket(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.send_message("A criar o teu canal de recrutamento...", ephemeral=True)

# --- COMANDOS ---
@bot.command()
@commands.has_permissions(administrator=True)
async def config_server(ctx):
    await ctx.send("⚙️ A moldar a estrutura do servidor: Categorias e canais criados com sucesso!")
    # Aqui podes colocar o código que clona os canais/categorias que usavas antes

@bot.command()
async def enviar_painel(ctx):
    view = PainelRecrutamentoView()
    embed = discord.Embed(title="INGRESSAR NA ORGANIZAÇÃO 🛡️", description="Clica no botão abaixo para abrir o teu processo seletivo privado.", color=discord.Color.red())
    await ctx.send(embed=embed, view=view)

# --- EVENTOS ---
@bot.event
async def on_ready():
    bot.add_view(PainelRecrutamentoView())
    print(f"{bot.user.name} está online!")

# --- ARRANQUE ---
if __name__ == "__main__":
    token = os.environ.get('DISCORD_TOKEN')
    bot.run(token)