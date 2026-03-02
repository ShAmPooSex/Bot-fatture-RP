# Bot-fatture-RP
Questo bot permette ai dipendenti di inserire fatture e calcola automaticamente il 35% dell'importo come compenso, tenendo traccia del totale accumulato per ogni utente.

## Installazione

1.  Assicurati di avere Python 3.11 installato.
2.  Installa le dipendenze globalmente:
    ```powershell
    & C:/Users/angio/AppData/Local/Microsoft/WindowsApps/python3.11.exe -m pip install -r requirements.txt
    ```

## Configurazione

1.  Crea un file `.env` nella stessa cartella del bot.
2.  Inserisci il tuo Token Discord e l'ID del canale nel file `.env`:
    ```
    DISCORD_TOKEN=il_tuo_token_qui
    ```
3.  **IMPORTANTE**: Abilita il "Message Content Intent" nel [Discord Developer Portal](https://discord.com/developers/applications) sotto la sezione "Bot".
4.  **RESTRICAZIONE CANALE**: I comandi del bot funzioneranno solo nel canale specificato dall'ID sopra.

## Avvio Rapido e Automatico

Ho creato degli strumenti per rendere l'uso del bot semplicissimo:

1.  **Avvio Rapido (Desktop)**:
    - Trascina il file `AvviaBot.bat` sul tuo Desktop (tasto destro -> Invia a -> Desktop).
    - Basta un doppio clic su questo file per far partire il bot senza aprire Trae o terminali.

2.  **Avvio Automatico (Windows)**:
    - Se vuoi che il bot si accenda da solo ogni volta che accendi il PC:
    - Fai tasto destro sul file `ImpostaAvvioAutomatico.ps1` e seleziona **"Esegui con PowerShell"**.
    - Il bot verrà aggiunto alla cartella di Esecuzione Automatica di Windows.

## Avvio Manuale (Terminal)
Esegui il bot in locale con il comando:
```powershell
& C:/Users/angio/AppData/Local/Microsoft/WindowsApps/python3.11.exe bot.py
```

## Comandi

-   `!fattura`: Invia il messaggio permanente per l'inserimento fatture. 
    **Nota**: Questo messaggio rimarrà attivo per sempre. Clicca sul pulsante "Inserisci Dati Fattura" per aprire il Modal.
-   `!comandi`: Mostra la lista completa dei comandi disponibili.
-   `!saldo`: Mostra il totale accumulato spettante in un Embed elegante.
-   `!check_saldo @utente`: (Solo Admin) Visualizza il saldo attuale di un utente specifico.
-   `!reset @utente`: (Solo Admin) Resetta il saldo di un utente a 0.
-   `!modifica_saldo @utente <importo>`: (Solo Admin) Imposta manualmente il saldo di un utente a una cifra specifica.
   

## Note

-   I dati vengono salvati automaticamente nel file `users_data.json`.
-   L'importo può essere inserito con la virgola o il punto (es. `10,50` o `10.50`).
