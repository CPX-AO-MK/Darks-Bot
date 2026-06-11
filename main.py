import discord
from discord.ext import commands
import os
import json
from flask import Flask
from threading import Thread

# --- ESTRUTURA DO SERVIDOR (NÃO REMOVER) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Darks está online!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

t = Thread(target=run_flask)
t.start()
# -------------------------------------------

# Configurações do Bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- AQUI VÃO OS TEUS COMANDOS ---
@bot.command()
async def config_server(ctx):
    # Insere aqui a lógica que tinhas antes para o comando !config_server
    await ctx.send("Configurando o servidor...")

@bot.event
async def on_ready():
    print(f"{bot.user.name} está online!")

# --- INICIALIZAÇÃO ---
if __name__ == "__main__":
    token = os.environ.get('DISCORD_TOKEN')
    if token:
        bot.run(token)