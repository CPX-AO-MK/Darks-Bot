import discord
from discord.ext import commands
from discord.ui import View
import json
import os
from flask import Flask
from threading import Thread

# --- CÓDIGO DO SERVIDOR PARA O RENDER (MANTÉM O BOT ACORDADO) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Darks está online!"

def run():
    # O Render atribui uma porta dinâmica, vamos usá-la
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

t = Thread(target=run)
t.start()
# -------------------------------------------------------------

# Configurações Iniciais
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

@bot.event
async def on_ready():
    print(f"{bot.user.name} está online!")

# Iniciar o Bot
if __name__ == "__main__":
    token = os.environ.get('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("Erro: A variável DISCORD_TOKEN não está definida!")