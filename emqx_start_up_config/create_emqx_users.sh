#!/bin/bash

until curl -fs http://localhost:18083/api/v5/status >/dev/null; do
  echo "Waiting for EMQX to be ready..."
  sleep 5
done

EMQX_USERNAME="${EMQX_DASHBOARD__DEFAULT_USERNAME:-admin}"
EMQX_PASSWORD="${EMQX_DASHBOARD__DEFAULT_PASSWORD:-public}"

LOGIN_RESPONSE=$(curl -s -u "$EMQX_USERNAME:$EMQX_PASSWORD" -X POST "http://localhost:18083/api/v5/login")
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token')

if [ -z "$TOKEN" ]; then
  echo "ERROR: Failed to authenticate with EMQX"
  exit 1
fi

NEW_USER="your_username"
NEW_PASS="your_password"

curl -X POST "http://localhost:18083/api/v5/authentication/password_based:built_in_database/users" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"user_id\":\"$NEW_USER\", \"password\":\"$NEW_PASS\"}"

exec "$@"