import discord
from discord.ext import commands
import os
import json
from flask import Flask
from threading import Thread

# 1. Configuração do Flask (o "servidor" que mantém o bot acordado)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Darks está online!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. Iniciar o servidor Flask numa Thread separada
t = Thread(target=run_flask)
t.start()

# 3. Configuração do Bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} está online!")

# 4. Iniciar o Bot
if __name__ == "__main__":
    token = os.environ.get('DISCORD_TOKEN')
    bot.run(token)