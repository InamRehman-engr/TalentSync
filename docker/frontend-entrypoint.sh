#!/bin/sh
set -eu

# Runs automatically via nginx's /docker-entrypoint.d mechanism before nginx starts.
# Regenerates runtime config from env vars on every container start (down/up, restart).
CONFIG_PATH="/usr/share/nginx/html/runtime-config.js"

cat > "$CONFIG_PATH" <<EOF
window.__TALENTSYNC_CONFIG__ = {
  "VITE_SHOW_EMPLOYEE_DASHBOARD": "${VITE_SHOW_EMPLOYEE_DASHBOARD:-true}",
  "VITE_SHOW_QUICK_DEMO": "${VITE_SHOW_QUICK_DEMO:-true}",
  "VITE_SHOW_PRICING_CONTACT_OVERLAY": "${VITE_SHOW_PRICING_CONTACT_OVERLAY:-true}",
  "VITE_PRICING_CONTACT_EMAIL": "${VITE_PRICING_CONTACT_EMAIL:-hello@talentsync.com}"
};
EOF
