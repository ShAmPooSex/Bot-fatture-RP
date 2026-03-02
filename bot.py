import discord
from discord.ext import commands
from discord import ui
import json
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env (se esiste)
load_dotenv()

# Configurazione del bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

DATA_FILE = 'users_data.json'
ALLOWED_CHANNEL_ID = int(os.getenv('ALLOWED_CHANNEL_ID', 1476211759546237082))

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- CHECK PER IL CANALE ---
def is_allowed_channel():
    async def predicate(ctx):
        if ctx.channel.id != ALLOWED_CHANNEL_ID:
            await ctx.send(f"❌ Questo comando può essere usato solo nel canale <#{ALLOWED_CHANNEL_ID}>.", delete_after=10)
            return False
        return True
    return commands.check(predicate)

# --- MODAL PER L'INSERIMENTO DATI ---
class FatturaModal(ui.Modal, title='Inserimento Fattura'):
    # Prima scelta: Cosa hai venduto?
    motivazione = ui.TextInput(
        label='Che cosa hai venduto?',
        placeholder='Es: Consulenza, Prodotto X...',
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )
    
    # Seconda scelta: L'importo
    importo = ui.TextInput(
        label='Importo (€)',
        placeholder='Es: 100 o 100,50',
        style=discord.TextStyle.short,
        required=True,
        max_length=20
    )

    # Terza scelta: Open Bar?
    open_bar = ui.TextInput(
        label='È un Open Bar? (Sì/No)',
        placeholder='Scrivi "Sì" se è un open bar, altrimenti lascia vuoto o scrivi "No"',
        style=discord.TextStyle.short,
        required=False,
        max_length=5
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Gestione dell'importo
        try:
            importo_valore = float(self.importo.value.replace(',', '.'))
        except ValueError:
            await interaction.response.send_message("❌ Errore: L'importo deve essere un numero valido.", ephemeral=True)
            return

        if importo_valore < 0:
            await interaction.response.send_message("❌ Errore: L'importo non può essere negativo.", ephemeral=True)
            return

        # Controllo Open Bar
        is_open_bar = self.open_bar.value.strip().lower() in ['si', 'sì', 'yes', 'y']
        
        # Calcolo del guadagno (35% o 0% se open bar)
        percentuale = 0.35 if not is_open_bar else 0.0
        guadagno_dipendente = importo_valore * percentuale

        # Gestione dati utente
        user_id = str(interaction.user.id)
        data = load_data()

        if user_id not in data:
            data[user_id] = {'total': 0.0, 'history': []}

        # Aggiorna il totale
        data[user_id]['total'] += guadagno_dipendente
        
        # Aggiungi alla cronologia
        data[user_id]['history'].append({
            'importo_totale': importo_valore,
            'guadagno': guadagno_dipendente,
            'motivazione': self.motivazione.value,
            'open_bar': is_open_bar
        })

        save_data(data)

        # Risposta finale con Embed
        totale_spettante = data[user_id]['total']
        
        embed = discord.Embed(
            title="✅ Fattura Registrata con Successo",
            color=discord.Color.green() if not is_open_bar else discord.Color.blue(),
            description=f"Dati salvati per {interaction.user.mention}"
        )
        embed.add_field(name="📦 Oggetto Vendita", value=self.motivazione.value, inline=False)
        embed.add_field(name="🍹 Open Bar", value="SÌ" if is_open_bar else "NO", inline=True)
        embed.add_field(name="💰 Importo Totale", value=f"€{importo_valore:.2f}", inline=True)
        
        if is_open_bar:
            embed.add_field(name="📉 Guadagno (0%)", value="**€0.00** (Open Bar)", inline=False)
        else:
            embed.add_field(name="📉 Guadagno (35%)", value=f"€{guadagno_dipendente:.2f}", inline=True)
            
        embed.add_field(name="🏆 Saldo Totale Spettante", value=f"**€{totale_spettante:.2f}**", inline=False)
        embed.set_footer(text="Bot Gestione Fatture")

        await interaction.response.send_message(embed=embed)

# --- VIEW CON IL BOTTONE PER APRIRE IL MODAL ---
class FatturaView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label='Inserisci Dati Fattura', style=discord.ButtonStyle.primary, emoji='📝', custom_id='persistent_fattura_button')
    async def open_modal(self, interaction: discord.Interaction, button: ui.Button):
        # Ulteriore controllo anche sul click del bottone per sicurezza
        if interaction.channel_id != ALLOWED_CHANNEL_ID:
            await interaction.response.send_message(f"❌ Questo pulsante funziona solo nel canale <#{ALLOWED_CHANNEL_ID}>.", ephemeral=True)
            return
        await interaction.response.send_modal(FatturaModal())

@bot.event
async def on_ready():
    # Registriamo la View per renderla persistente tra i riavvii
    bot.add_view(FatturaView())
    print(f'✅ Bot connesso come {bot.user}')
    print(f'📢 Canale autorizzato ID: {ALLOWED_CHANNEL_ID}')
    print('-----------------------------------------')

@bot.event
async def on_message(message):
    # Ignora i messaggi del bot stesso
    if message.author == bot.user:
        return

    # Debug in console per aiutarti a capire se il bot vede i messaggi
    if message.content.startswith('!'):
        print(f'📩 Comando ricevuto: "{message.content}"')
        print(f'📍 ID Canale: {message.channel.id}')
        print(f'🔐 Autorizzato: {"SÌ" if message.channel.id == ALLOWED_CHANNEL_ID else "NO"}')
        print('-----------------------------------------')

    # IMPORTANTE: permette al bot di processare i comandi
    await bot.process_commands(message)

@bot.command(name='fattura', help='Avvia la procedura interattiva per inserire una fattura.')
@is_allowed_channel()
async def fattura(ctx):
    embed = discord.Embed(
        title="Gestione Fattura",
        description="Clicca il pulsante qui sotto per inserire i dati della tua vendita (Cosa hai venduto e l'importo).",
        color=discord.Color.blue()
    )
    view = FatturaView()
    await ctx.send(embed=embed, view=view)

@bot.command(name='saldo', help='Mostra il totale accumulato spettante.')
@is_allowed_channel()
async def saldo(ctx):
    user_id = str(ctx.author.id)
    data = load_data()

    totale = data.get(user_id, {}).get('total', 0.0)
    
    embed = discord.Embed(
        title="💰 Saldo Attuale",
        description=f"Il totale spettante per {ctx.author.mention} è:",
        color=discord.Color.gold()
    )
    embed.add_field(name="Saldo Totale", value=f"**€{totale:.2f}**", inline=True)
    await ctx.send(embed=embed)

@bot.command(name='reset', help='Resetta il saldo accumulato (Solo amministratore).')
@commands.has_permissions(administrator=True)
@is_allowed_channel()
async def reset(ctx, member: discord.Member):
    user_id = str(member.id)
    data = load_data()

    if user_id in data:
        data[user_id]['total'] = 0.0
        save_data(data)
        await ctx.send(f"✅ Saldo resettato correttamente per {member.mention}.")
    else:
        await ctx.send(f"❌ Nessun dato trovato per {member.mention}.")

@bot.command(name='modifica_saldo', help='Imposta un nuovo saldo per un utente (Solo amministratore). Uso: !modifica_saldo @utente <nuovo_importo>')
@commands.has_permissions(administrator=True)
@is_allowed_channel()
async def modifica_saldo(ctx, member: discord.Member, nuovo_importo: str):
    try:
        nuovo_importo_float = float(nuovo_importo.replace(',', '.'))
    except ValueError:
        await ctx.send("❌ Errore: L'importo deve essere un numero valido.")
        return

    user_id = str(member.id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {'total': 0.0, 'history': []}

    vecchio_saldo = data[user_id]['total']
    data[user_id]['total'] = nuovo_importo_float
    save_data(data)

    embed = discord.Embed(
        title="🔧 Saldo Modificato dall'Amministratore",
        color=discord.Color.orange(),
        description=f"Il saldo di {member.mention} è stato aggiornato."
    )
    embed.add_field(name="Vecchio Saldo", value=f"€{vecchio_saldo:.2f}", inline=True)
    embed.add_field(name="Nuovo Saldo", value=f"**€{nuovo_importo_float:.2f}**", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='check_saldo', help='Controlla il saldo di un utente specifico (Solo amministratore). Uso: !check_saldo @utente')
@commands.has_permissions(administrator=True)
@is_allowed_channel()
async def check_saldo(ctx, member: discord.Member):
    user_id = str(member.id)
    data = load_data()

    totale = data.get(user_id, {}).get('total', 0.0)
    
    embed = discord.Embed(
        title="🔍 Controllo Saldo Utente",
        description=f"Visualizzazione saldo per {member.mention}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Saldo Totale Spettante", value=f"**€{totale:.2f}**", inline=True)
    embed.set_footer(text=f"Richiesto da {ctx.author.name}")
    
    await ctx.send(embed=embed)

@bot.command(name='comandi', help='Mostra la lista di tutti i comandi disponibili.')
@is_allowed_channel()
async def comandi(ctx):
    embed = discord.Embed(
        title="📜 Lista Comandi del Bot",
        description="Ecco tutti i comandi che puoi utilizzare nel canale autorizzato:",
        color=discord.Color.purple()
    )
    
    # Comandi Utente
    embed.add_field(
        name="👤 Comandi Utente",
        value=(
            "`!fattura` - Invia il messaggio permanente con il pulsante per inserire le fatture.\n"
            "`!saldo` - Visualizza il tuo saldo attuale spettante.\n"
            "`!comandi` - Mostra questo messaggio di aiuto."
        ),
        inline=False
    )
    
    # Comandi Amministratore
    embed.add_field(
        name="🛠️ Comandi Amministratore",
        value=(
            "`!check_saldo @utente` - Visualizza il saldo di un utente specifico.\n"
            "`!reset @utente` - Azzera completamente il saldo di un utente.\n"
            "`!modifica_saldo @utente <importo>` - Imposta manualmente il saldo di un utente."
        ),
        inline=False
    )
    
    embed.set_footer(text="Bot Gestione Fatture | Solo canali autorizzati")
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    # Gestisce l'errore di canale sbagliato (CheckFailure)
    if isinstance(error, commands.CheckFailure):
        # Non scriviamo nulla nella console, l'errore è già gestito nel check is_allowed_channel
        return
    
    # Gestisce errori di permessi mancanti (Solo Admin)
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Non hai i permessi per usare questo comando.", delete_after=5)
        return

    # Gestisce il comando non trovato
    if isinstance(error, commands.CommandNotFound):
        return

    # Altri errori vengono stampati solo se necessario
    print(f'Errore: {error}')

# Esegui il bot
TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("Errore: Token del bot non trovato.")
