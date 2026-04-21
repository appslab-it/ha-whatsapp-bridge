# WAHA WhatsApp Addon

Send WhatsApp messages, photos, and videos from Home Assistant using [WAHA](https://waha.devlike.pro/).

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_key` | string | `changeme` | Secret key to protect the WAHA API |
| `session_name` | string | `default` | WhatsApp session identifier |
| `engine` | enum | `NOWEB` | WhatsApp engine: `NOWEB` (recommended) or `WEBJS` |
| `webhook_url` | string | _(empty)_ | URL to receive incoming WhatsApp events |
| `webhook_events` | string | `message,session.status` | Comma-separated list of events to forward |
| `log_level` | enum | `INFO` | Log verbosity: `INFO`, `DEBUG`, `WARN`, `ERROR` |

## Initial Setup

1. Start the addon
2. Open the WAHA dashboard: **http://\<home-assistant-ip\>:3000**
3. Go to **Sessions → Start** and click **QR Code**
4. Scan the QR code with your WhatsApp mobile app
5. The session status will change to `WORKING`

## Engine Choice

- **NOWEB** (recommended): Uses the WhatsApp multi-device protocol directly. No browser required, low resource usage. Best for Synology NAS and ARM devices.
- **WEBJS**: Uses WhatsApp Web inside a headless Chromium browser. Higher resource usage.

## Home Assistant Integration

Add to `configuration.yaml`:

```yaml
rest_command:
  whatsapp_send_message:
    url: "http://localhost:3000/api/default/sendText"
    method: POST
    headers:
      X-Api-Key: "your_api_key"
      Content-Type: "application/json"
    payload: '{"chatId": "{{ phone }}@c.us", "text": "{{ message }}"}'

  whatsapp_send_image:
    url: "http://localhost:3000/api/default/sendImage"
    method: POST
    headers:
      X-Api-Key: "your_api_key"
      Content-Type: "application/json"
    payload: '{"chatId": "{{ phone }}@c.us", "caption": "{{ caption }}", "file": {"url": "{{ url }}"}}'

  whatsapp_send_video:
    url: "http://localhost:3000/api/default/sendVideo"
    method: POST
    headers:
      X-Api-Key: "your_api_key"
      Content-Type: "application/json"
    payload: '{"chatId": "{{ phone }}@c.us", "caption": "{{ caption }}", "file": {"url": "{{ url }}"}}'

  whatsapp_send_file:
    url: "http://localhost:3000/api/default/sendFile"
    method: POST
    headers:
      X-Api-Key: "your_api_key"
      Content-Type: "application/json"
    payload: '{"chatId": "{{ phone }}@c.us", "caption": "{{ caption }}", "file": {"url": "{{ url }}"}}'
```

Replace `default` in the URL with your `session_name` if you changed it.

### Sending Messages from Automations

```yaml
service: rest_command.whatsapp_send_message
data:
  phone: "393331234567"
  message: "Allarme attivato alle {{ now().strftime('%H:%M') }}"
```

### Phone Number Format

Use the international format **without** the `+` sign and **without** spaces:
- Italy: `393331234567` (39 = country code, then number without leading 0)
- USA: `12125551234`

## API Documentation

Full WAHA API docs are available at `http://<ha-ip>:3000/api` (Swagger UI).

## Synology DS218+ Notes

The DS218+ (Intel Celeron J3355, x86_64) is fully supported. The NOWEB engine is recommended as it uses minimal resources (~100MB RAM).

## Support

- [WAHA Documentation](https://waha.devlike.pro/)
- [Addon Issues](https://github.com/appslab-it/waha-addon/issues)
