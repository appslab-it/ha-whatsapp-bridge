#!/usr/bin/env bash
set -e

CONFIG_PATH=/data/options.json

# Read a value from the HA options JSON
config() {
    local key="$1"
    local default="${2:-}"
    local val
    val=$(jq -r ".${key} // empty" "${CONFIG_PATH}" 2>/dev/null)
    echo "${val:-$default}"
}

echo "[INFO] ============================================"
echo "[INFO]  WAHA WhatsApp Addon starting..."
echo "[INFO] ============================================"

# Read addon options (set defaults if config file absent)
if [ -f "$CONFIG_PATH" ]; then
    API_KEY=$(config 'api_key' '')
    DASHBOARD_USERNAME=$(config 'dashboard_username' 'admin')
    DASHBOARD_PASSWORD=$(config 'dashboard_password' 'admin')
    SESSION_NAME=$(config 'session_name' 'default')
    ENGINE=$(config 'engine' 'NOWEB')
    WEBHOOK_URL=$(config 'webhook_url' '')
    WEBHOOK_EVENTS=$(config 'webhook_events' 'message,session.status')
    LOG_LEVEL=$(config 'log_level' 'INFO')
else
    echo "[WARN] No options.json found, using defaults"
    API_KEY="${WHATSAPP_API_KEY:-}"
    DASHBOARD_USERNAME="${WAHA_DASHBOARD_USERNAME:-admin}"
    DASHBOARD_PASSWORD="${WAHA_DASHBOARD_PASSWORD:-admin}"
    SESSION_NAME="${WAHA_SESSION_NAME:-default}"
    ENGINE="${WHATSAPP_DEFAULT_ENGINE:-NOWEB}"
    WEBHOOK_URL="${WHATSAPP_HOOK_URL:-}"
    WEBHOOK_EVENTS="${WHATSAPP_HOOK_EVENTS:-message,session.status}"
    LOG_LEVEL="${WAHA_LOG_LEVEL:-INFO}"
fi

# Export WAHA environment variables
# Only set API key if non-empty — empty means no authentication required
if [ -n "$API_KEY" ]; then
    export WHATSAPP_API_KEY="$API_KEY"
    echo "[INFO] API key:    set (protected)"
else
    echo "[INFO] API key:    NOT SET — dashboard open, set one after pairing!"
fi
export WAHA_DASHBOARD_USERNAME="$DASHBOARD_USERNAME"
export WAHA_DASHBOARD_PASSWORD="$DASHBOARD_PASSWORD"
export WHATSAPP_SWAGGER_USERNAME="$DASHBOARD_USERNAME"
export WHATSAPP_SWAGGER_PASSWORD="$DASHBOARD_PASSWORD"
export WHATSAPP_DEFAULT_ENGINE="$ENGINE"
export WHATSAPP_HOOK_EVENTS="$WEBHOOK_EVENTS"
export WAHA_LOG_LEVEL="$LOG_LEVEL"
export LOG_LEVEL="$LOG_LEVEL"

if [ -n "$WEBHOOK_URL" ]; then
    export WHATSAPP_HOOK_URL="$WEBHOOK_URL"
fi

# Persist session data and files in /data (HA maps this to addon data dir)
export WHATSAPP_FILES_FOLDER="/data/files"
export WHATSAPP_SESSIONS_FOLDER="/data/sessions"
export WAHA_FILES_FOLDER="/data/files"
export WAHA_SESSIONS_FOLDER="/data/sessions"
mkdir -p /data/files /data/sessions

echo "[INFO] Engine:     $ENGINE"
echo "[INFO] Session:    $SESSION_NAME"
echo "[INFO] Log level:  $LOG_LEVEL"
echo "[INFO] API port:   3000"
if [ -n "$WEBHOOK_URL" ]; then
    echo "[INFO] Webhook:    $WEBHOOK_URL"
fi
echo "[INFO] ============================================"
echo "[INFO]  Open the WAHA dashboard at http://<ha-ip>:3000"
echo "[INFO]  Scan the QR code to pair your WhatsApp account"
echo "[INFO] ============================================"

# Start WAHA (NestJS app)
exec node dist/main.js
