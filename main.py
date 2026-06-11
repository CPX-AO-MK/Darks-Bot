import discord
from discord.ext import commands
from discord.ui import Button, View
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
    # Usa a porta fornecida pelo Render ou a 10000 por padrão
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

# Ficheiro para salvar dados
DATA_FILE = "dados.json"

def carregar_dados():
    if not os.path.exists(DATA_FILE):
        return {"metas": {}, "tickets_ativos": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# Classe do Painel de Recrutamento
class PainelRecrutamentoView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fazer Recrutamento 🛡️", style=discord.ButtonStyle.danger, custom_id="btn_ticket")
    async def criar_ticket(self, interaction: discord.Interaction, button: discord.Button):
        dados = carregar_dados()
        user_id = str(interaction.user.id)

        if user_id in dados["tickets_ativos"]:
            await interaction.response.send_message("Tu já tens um canal de recrutamento aberto!", ephemeral=True)
            return
        
        # Aqui podes continuar a tua lógica de criação de canal...
        await interaction.response.send_message("A criar o teu canal de recrutamento...", ephemeral=True)

@bot.event
async def on_ready():
    print(f"{bot.user.name} está online e pronto para o MTA Angola!")
    bot.add_view(PainelRecrutamentoView())

# Iniciar o Bot
# Certifica-te de que a variável DISCORD_TOKEN está definida no Render
if __name__ == "__main__":
    token = os.environ.get('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("Erro: A variável DISCORD_TOKEN não está definida!")