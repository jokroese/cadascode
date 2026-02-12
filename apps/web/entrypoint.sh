#!/bin/sh
set -eu

# These are the mount points that may be root-owned when coming from named volumes
fix_paths="
/app/node_modules
/app/apps/web/node_modules
/home/node/.local/share/pnpm/store
"

if [ "$(id -u)" = "0" ]; then
  for p in $fix_paths; do
    mkdir -p "$p"
    chown -R node:node "$p" || true
  done

  # Drop privileges and run the CMD
  exec su-exec node "$@"
fi

exec "$@"