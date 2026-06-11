import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os

# --- CÓDIGO DO SERVIDOR PARA O RENDER ---
from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot Darks está online!"

def run():
    app.run(host='0.0.0.0', port=10000)

t = Thread(target=run)
t.start()
# ----------------------------------------

# Configurações Iniciais
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Ficheiro para salvar os dados das metas e tickets
DATA_FILE = "dados.json"

def carregar_dados():
    if not os.path.exists(DATA_FILE):
        return {"metas": {}, "tickets_ativos": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

@bot.event
async def on_ready():
    print(f"🦅 {bot.user.name} está online e pronto para o MTA Angola!")
    bot.add_view(PainelRecrutamentoView()) # Mantém o botão ativo após reiniciar

# --- FASE DE RECRUTAMENTO (TICKETS) ---
class PainelRecrutamentoView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fazer Recrutamento 🤝", style=discord.ButtonStyle.danger, custom_id="btn_ticket")
    async def criar_ticket(self, interaction: discord.Interaction, button: discord.Button):
        dados = carregar_dados()
        user_id = str(interaction.user.id)

        # Evita que o mesmo jogador abra vários canais
        if user_id in dados["tickets_ativos"]:
            await interaction.response.send_message("Tu já tens um canal de recrutamento aberto!", ephemeral=True)
            return

        guild = interaction.guild
        # Cria o canal de texto privado para a entrevista
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        canal_ticket = await guild.create_text_channel(
            name=f"recruta-{interaction.user.name}",
            overwrites=overwrites,
            topic=f"Entrevista de {interaction.user.mention}"
        )

        dados["tickets_ativos"][user_id] = canal_ticket.id
        salvar_dados(dados)

        # Mensagem inicial dentro do ticket
        embed = discord.Embed(
            title="Formulário de Entrada",
            description=f"Olá {interaction.user.mention}, bem-vindo ao recrutamento!\n\n"
                        "**Responde às seguintes perguntas enquanto aguardas um Líder:**\n"
                        "1. Qual é o teu nome e idade no ID do MTA?\n"
                        "2. Há quanto tempo jogas Roleplay?\n"
                        "3. Já estiveste noutra fação neste ou noutro server?",
            color=discord.Color.dark_red()
        )
        await canal_ticket.send(embed=embed, view=FecharTicketView(user_id))
        await interaction.response.send_message(f"Canal de recrutamento criado: {canal_ticket.mention}", ephemeral=True)

class FecharTicketView(View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="Fechar Canal 🔒", style=discord.ButtonStyle.secondary, custom_id="btn_fechar_ticket")
    async def fechar_ticket(self, interaction: discord.Interaction, button: discord.Button):
        dados = carregar_dados()
        if self.user_id in dados["tickets_ativos"]:
            del dados["tickets_ativos"][self.user_id]
            salvar_dados(dados)
        
        await interaction.response.send_message("A fechar o canal em 3 segundos...")
        await interaction.channel.delete()

# --- FASE DE COMANDOS (PAINEL E METAS) ---

@bot.command()
@commands.has_permissions(administrator=True)
async def criar_cargos(ctx):
    guild = ctx.guild
    await ctx.send("⏳ *A gerar a hierarquia e a configurar as permissões avançadas de cada cargo...*")
    
    try:
        # 1. Definição de pacotes de permissões nativas
        perms_lider = discord.Permissions(administrator=True)
        
        perms_gerencia = discord.Permissions(
            manage_messages=True, kick_members=True, mute_members=True,
            deafen_members=True, move_members=True, view_channel=True,
            send_messages=True, connect=True, speak=True
        )
        
        perms_membros = discord.Permissions(
            view_channel=True, send_messages=True, embed_links=True,
            attach_files=True, read_message_history=True, connect=True,
            speak=True, use_voice_activation=True
        )
        
        perms_castigado = discord.Permissions(
            view_channel=True, read_message_history=True,
            send_messages=False, connect=False
        )

        # 2. Lista estruturada com a nova nomenclatura da org
        hierarquia_cargos = [
            ("👑 ┃ Líder", 0x990000, perms_lider),
            ("🥈 ┃ Sub-Líder", 0xcc0000, perms_lider),
            ("📊 ┃ Gerente", 0xe67e22, perms_gerencia),
            ("🛡️ ┃ Corregedor / RH", 0x2ecc71, perms_gerencia),
            ("⭐ ┃ Membro Elite", 0x9b59b6, perms_membros),
            ("⚔️ ┃ Cota ⭐⭐⭐⭐⭐", 0x3498db, perms_membros),
            ("⚔️ ┃ Cota ⭐⭐⭐⭐", 0x2980b9, perms_membros),
            ("⚔️ ┃ Cota ⭐⭐⭐", 0x41729f, perms_membros),
            ("⚔️ ┃ Cota ⭐⭐", 0x5c8ebb, perms_membros),
            ("⚔️ ┃ Cota ⭐", 0x75aadb, perms_membros),
            ("🔫 ┃ Cassule", 0xf1c40f, perms_membros),
            ("🐌 ┃ Novato", 0x95a5a6, perms_membros),
            ("🤝 ┃ Parceiros", 0x1abc9c, perms_membros),
            ("🚫 ┃ Castigado", 0x34495e, perms_castigado)
        ]
        
        cargos_criados = 0
        for nome, cor_hex, permissoes in hierarquia_cargos:
            cargo_existente = discord.utils.get(guild.roles, name=nome)
            if not cargo_existente:
                await guild.create_role(
                    name=nome,
                    color=discord.Color(cor_hex),
                    permissions=permissoes,
                    hoist=True,
                    mentionable=True
                )
                cargos_criados += 1
                
        await ctx.send(f"✅ **Hierarquia Concluída!** {cargos_criados} cargos criados e blindados com as permissões corretas.")
    except Exception as e:
        await ctx.send(f"❌ Erro ao configurar permissões: {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def trancar_servidor(ctx):
    guild = ctx.guild
    await ctx.send("⏳ *A organizar as permissões e a blindar o servidor...*")
    
    # 1. Obter os cargos
    role_everyone = guild.default_role
    role_novato = discord.utils.get(guild.roles, name="🐌 ┃ Novato")
    
    # Lista de cargos que têm acesso total
    cargos_staff = [
        discord.utils.get(guild.roles, name="👑 ┃ Líder"),
        discord.utils.get(guild.roles, name="🥈 ┃ Sub-Líder"),
        discord.utils.get(guild.roles, name="📊 ┃ Gerente"),
        discord.utils.get(guild.roles, name="🛡️ ┃ Corregedor / RH")
    ]
    
    count_categorias = 0
    
    # 2. Percorrer categorias
    for category in guild.categories:
        nome_cat = category.name.upper()
        
        # Categorias que queremos blindar
        if any(x in nome_cat for x in ["GERÊNCIA", "RH", "COMANDOS", "CHAT ORG", "BATE PONTO", "CALLS", "ATENDIMENTO"]):
            
            # Definir permissões de visualização
            # Ninguém vê, exceto a staff
            overwrites = {
                role_everyone: discord.PermissionOverwrite(view_channel=False),
            }
            if role_novato:
                overwrites[role_novato] = discord.PermissionOverwrite(view_channel=False)
            
            # Adicionar Staff com acesso
            for cargo in cargos_staff:
                if cargo:
                    overwrites[cargo] = discord.PermissionOverwrite(view_channel=True)
            
            # 3. Aplicar na Categoria
            await category.edit(overwrites=overwrites)
            
            # 4. FORÇAR ORGANIZAÇÃO NOS CANAIS
            # Isto faz com que todos os canais dentro da categoria sigam a regra acima
            for channel in category.channels:
                await channel.edit(sync_permissions=True)
                
            count_categorias += 1
            
    await ctx.send(f"✅ **Servidor Organizado!** {count_categorias} categorias foram blindadas e todos os canais foram sincronizados.")
import os
bot.run(os.environ['DISCORD_TOKEN'])