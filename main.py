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

# --- CONFIGURAÇÃO BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- COMANDOS v1.4.1 ---
@bot.command()
async def meta(ctx, valor: str): await ctx.send(f"📊 Meta definida: {valor}")

@bot.command()
async def bateponto(ctx): await ctx.send(f"✅ {ctx.author.mention}, ponto batido!")

@bot.command()
async def registro(ctx, *, info: str): await ctx.send(f"📝 Registro salvo: {info}")

@bot.command()
@commands.has_permissions(administrator=True)
async def advertencia(ctx, membro: discord.Member, *, motivo: str):
    await ctx.send(f"⚠️ {membro.mention} advertido: {motivo}")

@bot.command()
async def ausencia(ctx, *, motivo: str): await ctx.send(f"🗓️ Ausência de {ctx.author.name}: {motivo}")

@bot.command()
async def ticket(ctx): await ctx.send("📩 Ticket criado! Aguarde.")

@bot.command()
async def formulario(ctx): await ctx.send("📋 Preencha: [LINK]")

# --- INICIALIZAÇÃO ---
@bot.event
async def on_ready(): print(f"{bot.user.name} online!")

if __name__ == "__main__":
    bot.run(os.environ.get('DISCORD_TOKEN'))