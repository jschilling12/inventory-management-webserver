#!/usr/bin/env bash
set -e

HOST=${1:-root@174.138.80.251}
KEY=${2:-~/.ssh/warehousingdroplet}
REMOTE_DIR=/var/www/static-site-server

echo "🚀 Deploying to $HOST..."

rsync -avzP \
  -e "ssh -i $KEY -o IdentitiesOnly=yes" \
  --exclude-from="./.rsync-exclude" \
  ./ \
  $HOST:$REMOTE_DIR

ssh -i $KEY $HOST "systemctl restart gunicorn && systemctl reload nginx"