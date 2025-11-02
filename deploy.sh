#!/usr/bin/env bash
set -euo pipefail

# --- Defaults (override with flags or env vars) ---
HOST="${HOST:-138.197.38.114}"
USER="${USER:-root}"
PORT="${PORT:-22}"
KEY="${KEY:-$HOME/.ssh/SSHKey1_Linux}"
SRC="${SRC:-$(pwd)/}"
DEST="${DEST:-/root/static-site-server/}"
EXCLUDE_FILE="${EXCLUDE_FILE:-$(pwd)/.rsync-exclude}"
DELETE="${DELETE:-0}"     # 1 = enable --delete
LIVE="${LIVE:-0}"         # 1 = live (otherwise dry-run)
BWLIMIT="${BWLIMIT:-}"    # e.g. 2m

usage(){ cat <<USAGE
Usage: $(basename "$0") [options]
  --host HOST          Remote host/IP (default: $HOST)
  --user USER          SSH user (default: $USER)
  --port PORT          SSH port (default: $PORT)
  --key PATH           Private key path (default: $KEY)
  --src PATH           Local source dir (default: $SRC)
  --dest PATH          Remote destination (default: $DEST)
  --exclude PATH       Exclude file (default: $EXCLUDE_FILE if exists)
  --delete             Mirror with rsync --delete (CAUTION)
  --live               Perform real sync (default is --dry-run)
  --bwlimit RATE       Limit bandwidth (e.g. 2m, 500k)
  --preview            Print the rsync cmd and exit
  -h|--help            Show help
USAGE
}

preview=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --host) HOST="$2"; shift 2;;
    --user) USER="$2"; shift 2;;
    --port) PORT="$2"; shift 2;;
    --key) KEY="$2"; shift 2;;
    --src) SRC="$2"; shift 2;;
    --dest) DEST="$2"; shift 2;;
    --exclude) EXCLUDE_FILE="$2"; shift 2;;
    --delete) DELETE=1; shift;;
    --live) LIVE=1; shift;;
    --bwlimit) BWLIMIT="$2"; shift 2;;
    --preview) preview=1; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown option: $1"; usage; exit 2;;
  esac
done

command -v rsync >/dev/null || { echo "rsync not found"; exit 1; }
command -v ssh   >/dev/null || { echo "ssh not found"; exit 1; }

if [[ ! -r "$KEY" ]]; then
  echo "Private key not readable: $KEY"
  exit 1
fi

# Ensure SRC has trailing slash (sync contents)
[[ "$SRC" == */ ]] || SRC="${SRC}/"

# Build SSH bits (keep pieces separate to avoid quoting bugs)
ssh_bin=ssh
ssh_opts=(-i "$KEY" -o IdentitiesOnly=yes -p "$PORT")

# Build rsync command
rsync_opts=(-avzP -e "$ssh_bin -i $KEY -o IdentitiesOnly=yes -p $PORT")
[[ -f "$EXCLUDE_FILE" ]] && rsync_opts+=(--exclude-from="$EXCLUDE_FILE")
[[ "$DELETE" == "1" ]] && rsync_opts+=(--delete)
[[ "$LIVE" != "1" ]] && { rsync_opts+=(--dry-run); echo "[DRY-RUN] Use --live to deploy."; }
[[ -n "$BWLIMIT" ]] && rsync_opts+=(--bwlimit="$BWLIMIT")

if [[ "$preview" == "1" ]]; then
  printf 'rsync %q ' "${rsync_opts[@]}"; printf ' %q ' "$SRC" "${USER}@${HOST}:${DEST}"; echo; exit 0
fi

# Ensure destination exists (this is where the previous script went wrong)
$ssh_bin "${ssh_opts[@]}" "${USER}@${HOST}" "mkdir -p '$DEST'"

echo "Deploying: $SRC  -->  ${USER}@${HOST}:${DEST}"
rsync "${rsync_opts[@]}" "$SRC" "${USER}@${HOST}:${DEST}"
echo "Done."
