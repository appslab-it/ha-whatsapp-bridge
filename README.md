# WhatsApp Bridge — Home Assistant Integration

Invia messaggi, immagini, video e file WhatsApp direttamente dalle automazioni di Home Assistant, senza toccare `configuration.yaml`.

Basato su [WAHA](https://waha.devlike.pro/) (WhatsApp HTTP API).

---

## Architettura

```
[Home Assistant]                    [WAHA — Docker]
  Automation
    └─► whatsapp_bridge.send_message  ──HTTP──►  API :3000  ──► WhatsApp ──► 📱
  sensor.whatsapp_bridge_default_session_status ◄──poll──┘
```

- **WAHA** gira come container Docker (sul tuo NAS, VM o stesso host di HA)
- **L'integration HACS** si connette all'API WAHA e registra i servizi nativi in HA

---

## Installazione

### 1. Avvia WAHA con Docker Compose

Clona il repo e avvia WAHA:

```bash
git clone https://github.com/appslab-it/ha-whatsapp-bridge.git
cd ha-whatsapp-bridge
# Modifica WHATSAPP_API_KEY in docker-compose.yml
mkdir -p data/sessions data/files
docker compose up -d
```

I dati di sessione (QR code pairing) vengono salvati in `./data/sessions/` nella stessa cartella.

### 2. Associa il tuo account WhatsApp

1. Apri il dashboard WAHA: `http://<ip-host>:3000`
2. Vai in **Sessions** → clicca sulla sessione → **QR Code**
3. Scansiona il QR code con WhatsApp sul tuo telefono (**Dispositivi collegati → Collega un dispositivo**)
4. Lo stato diventa `WORKING` — pronto

Devi farlo una volta sola. La sessione persiste tra i riavvii.

### 3. Installa l'integration via HACS

1. In HACS → **Repository personalizzati** → aggiungi `https://github.com/appslab-it/ha-whatsapp-bridge` come tipo **Integration**
2. Cerca **WhatsApp Bridge** → **Scarica**
3. Riavvia Home Assistant

### 4. Configura l'integration

1. Vai in **Impostazioni → Dispositivi & Servizi → Aggiungi integrazione**
2. Cerca **WhatsApp Bridge**
3. Compila il form:
   - **Host**: IP o hostname del server WAHA (es. `192.168.1.100`)
   - **Porta**: `3000`
   - **API Key**: quella impostata in `docker-compose.yml`
   - **Session Name**: `default`
4. Salva — HA verifica la connessione in tempo reale

---

## Migrazione da Addon HA (utenti esistenti)

Se stavi usando il vecchio addon, ecco come preservare il QR code pairing.

### Step 1 — Backup della sessione dall'addon

Dall'addon SSH di HA (o dal terminale di HA OS):

```bash
# Trova la cartella dati dell'addon
ls /mnt/data/supervisor/addons/data/waha_whatsapp/sessions/

# Copia in una posizione temporanea
cp -r /mnt/data/supervisor/addons/data/waha_whatsapp/sessions/ /tmp/waha-sessions-backup/
```

> In alternativa usa il File Editor di HA per navigare in `/addon_configs/waha_whatsapp/`.

### Step 2 — Prepara la cartella dati per Docker Compose

Sul server dove girerai WAHA con Docker Compose:

```bash
mkdir -p /percorso/waha-addon/data/sessions
cp -r /tmp/waha-sessions-backup/* /percorso/waha-addon/data/sessions/
```

### Step 3 — Avvia WAHA con Docker Compose

```bash
cd /percorso/waha-addon
docker compose up -d
```

WAHA troverà la sessione esistente e si connetterà senza richiedere un nuovo QR code.

### Step 4 — Rimuovi il vecchio addon

In HA → **Impostazioni → Add-on** → **WAHA WhatsApp** → **Disinstalla**.

### Step 5 — Installa l'integration HACS

Segui i punti 3 e 4 della sezione Installazione sopra.

### Step 6 — Aggiorna le automazioni

Sostituisci nelle automazioni esistenti:

```yaml
# Prima (rest_command)
service: rest_command.whatsapp_send_message

# Dopo (integration nativa)
service: whatsapp_bridge.send_message
```

---

## Servizi disponibili

| Servizio | Parametri |
|---|---|
| `whatsapp_bridge.send_message` | `phone`, `message` |
| `whatsapp_bridge.send_image` | `phone`, `url`, `caption` (opz.) |
| `whatsapp_bridge.send_video` | `phone`, `url`, `caption` (opz.) |
| `whatsapp_bridge.send_file` | `phone`, `url`, `filename` (opz.) |
| `whatsapp_bridge.send_voice` | `phone`, `url` |

Tutti i servizi accettano anche `session_name` (opzionale, per multi-sessione).

**Formato numero di telefono:** internazionale senza `+` — es. `393331234567` (Italia), `12125551234` (USA).

---

## Sensore

L'integration crea automaticamente `sensor.whatsapp_bridge_default_session_status` con i valori:
- `WORKING` — sessione attiva, pronto all'invio
- `STOPPED` — sessione ferma
- `FAILED` — errore di connessione WhatsApp

---

## Engines

| Engine | RAM | ARM | Note |
|---|---|---|---|
| **NOWEB** ✅ | ~100 MB | Sì | Consigliato — protocollo nativo |
| **WEBJS** | ~500 MB | Limitato | Headless Chromium |

---

## Esempi automazioni

Vedi [ha-examples/automations.yaml](ha-examples/automations.yaml).

```yaml
- alias: "Notifica porta aperta"
  trigger:
    platform: state
    entity_id: binary_sensor.porta_ingresso
    to: "on"
  action:
    service: whatsapp_bridge.send_message
    data:
      phone: "393331234567"
      message: "La porta è stata aperta alle {{ now().strftime('%H:%M') }}"
```

---

## Troubleshooting

| Problema | Soluzione |
|---|---|
| HACS non trova l'integration | Riavvia HA dopo il download HACS |
| "Cannot connect" al setup | Verifica che WAHA sia avviato e raggiungibile sulla porta 3000 |
| QR code non appare | Apri `http://<ip>:3000`, vai in Sessions e avvia la sessione manualmente |
| Sessione si disconnette | Rescansiona il QR code; usa il motore NOWEB |
| Messaggi non arrivano | Verifica che `sensor.waha_session_status` sia `WORKING` |

---

## License

MIT
