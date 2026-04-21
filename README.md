# WAHA WhatsApp - Home Assistant Addon Repository

Send WhatsApp messages, photos, and videos directly from Home Assistant using [WAHA](https://waha.devlike.pro/) (WhatsApp HTTP API).

## Installation

1. In Home Assistant, navigate to **Settings → Add-ons → Add-on Store**
2. Click the **⋮** menu (top-right) → **Repositories**
3. Add this URL: `https://github.com/appslab-it/waha-addon`
4. Find **WAHA WhatsApp** in the store and click **Install**

## Features

- Send text messages to any WhatsApp number
- Send images with captions
- Send videos with captions
- Send files/documents
- REST API on port 3000 for full WAHA capabilities
- QR code pairing via the built-in dashboard
- Session persistence across restarts
- Works on x86_64 (Synology NAS, Intel NUC) and ARM64 (Raspberry Pi 4)

## Addon

| Addon | Description |
|-------|-------------|
| [WAHA WhatsApp](waha-whatsapp/) | WhatsApp sender via WAHA HTTP API |

## Usage with Home Assistant

After starting the addon and pairing your WhatsApp account, add these REST commands to your `configuration.yaml`:

```yaml
rest_command:
  whatsapp_send_message:
    url: "http://localhost:3000/api/default/sendText"
    method: POST
    headers:
      X-Api-Key: "your_api_key_here"
      Content-Type: "application/json"
    payload: '{"chatId": "{{ phone }}@c.us", "text": "{{ message }}"}'

  whatsapp_send_image:
    url: "http://localhost:3000/api/default/sendImage"
    method: POST
    headers:
      X-Api-Key: "your_api_key_here"
      Content-Type: "application/json"
    payload: '{"chatId": "{{ phone }}@c.us", "caption": "{{ caption }}", "file": {"url": "{{ url }}"}}'

  whatsapp_send_video:
    url: "http://localhost:3000/api/default/sendVideo"
    method: POST
    headers:
      X-Api-Key: "your_api_key_here"
      Content-Type: "application/json"
    payload: '{"chatId": "{{ phone }}@c.us", "caption": "{{ caption }}", "file": {"url": "{{ url }}"}}'
```

See [ha-examples/](ha-examples/) for complete automation examples.

## Synology DS218+ Setup

The DS218+ uses an Intel Celeron J3355 (x86_64/amd64), fully supported by this addon. Ensure Docker is installed via **Package Center → Docker**.

## License

MIT
