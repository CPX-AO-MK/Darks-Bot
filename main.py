import discord
from discord.ext import commands
import os
import json
from flask import Flask
from threading import Thread

# --- ESTRUTURA PARA O RENDER (MANTÉM O BOT ONLINE) ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot Darks está online!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

t = Thread(target=run_flask)
t.start()

import discord
from discord.ext import commands
import os

# CONFIGURAÇÕES (SUBSTITUI PELOS TEUS IDs)
CAT_RECRUTAMENTO_ID = 1514628973743702126
CANAL_LOGS_PONTO_ID = 1514613721610321972

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 1. SISTEMA DE PONTO (BOTÕES INTERATIVOS) ---
class PontoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="ABRIR", style=discord.ButtonStyle.green, custom_id="abrir_ponto")
    async def abrir(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ponto iniciado!", ephemeral=True)
        # Lógica para guardar o início (ex: num dicionário ou BD)

    @discord.ui.button(label="FECHAR", style=discord.ButtonStyle.red, custom_id="fechar_ponto")
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ponto fechado! Total: 2 horas.", ephemeral=True)

# --- 2. FORMULÁRIO INTERATIVO (PERGUNTA A PERGUNTA) ---
class FormularioModal(discord.ui.Modal, title="Recrutamento RP"):
    pergunta = discord.ui.TextInput(label="Pergunta 1: Como defines o teu RP?")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Resposta enviada!", ephemeral=True)
        # Aqui o bot enviaria a pergunta 2, 3... e no final criaria o canal de log p/ ADM

# --- COMANDOS PARA INICIAR OS PAINÉIS ---
@bot.command()
async def setup_ponto(ctx):
    embed = discord.Embed(title="⏰ Bate-Ponto", description="Usa os botões abaixo:")
    await ctx.send(embed=embed, view=PontoView())

@bot.command()
async def aplicar(ctx):
    await ctx.send("Clica para iniciar o formulário:", view=FormularioStartView())

class FormularioStartView(discord.ui.View):
    @discord.ui.button(label="Iniciar Formulário", style=discord.ButtonStyle.blurple)
    async def iniciar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FormularioModal())

@bot.event
async def on_ready():
    bot.add_view(PontoView())
    print("Sistema interativo pronto!")

bot.run(os.environ.get('DISCORD_TOKEN'))