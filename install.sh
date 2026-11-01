#!/usr/bin/env bash
# Al-Fatiem Alarabi website installer for Linux (Debian/Ubuntu LXC) and macOS.
#
#   ./install.sh dev            run locally at http://127.0.0.1:8000 (Linux or macOS)
#   sudo ./install.sh prod      install/update as a systemd service on Linux (gunicorn on 127.0.0.1:8000)
#   sudo ./install.sh backup    copy database + uploaded photos to ./backups/
#   sudo ./install.sh admin     create another admin login
#
# Re-running "prod" updates the site in place and keeps .env, the database and photos.
set -euo pipefail
cd "$(dirname "$0")"
APP_DIR="$(pwd)"
MODE="${1:-dev}"
SERVICE=alfatiem
APP_USER=alfatiem
PORT="${PORT:-8000}"
BIND="${BIND:-127.0.0.1}"   # use BIND=0.0.0.0 only if cloudflared runs outside this container
OS="$(uname -s)"

say() { printf '\n\033[1m%s\033[0m\n' "$*"; }
die() { printf 'Error: %s\n' "$*" >&2; exit 1; }

need_python() {
  if ! command -v python3 >/dev/null || ! python3 -c 'import venv, ensurepip' 2>/dev/null; then
    if [ "$OS" = Linux ] && command -v apt-get >/dev/null && [ "$(id -u)" = 0 ]; then
      say "Installing Python…"
      apt-get update -qq && apt-get install -y -qq python3 python3-venv python3-pip curl >/dev/null
    else
      die "Python 3.10+ with venv is required (Debian/Ubuntu: apt install python3 python3-venv; macOS: python.org)."
    fi
  fi
  python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))' || die "Python 3.10 or newer is required."
}

venv() {
  [ -d .venv ] || python3 -m venv .venv
  .venv/bin/pip install -q --upgrade pip
  .venv/bin/pip install -q -r requirements.txt
}

manage() { .venv/bin/python manage.py "$@"; }

has_admin() {
  manage shell -v0 -c "from django.contrib.auth.models import User;import sys;sys.exit(0 if User.objects.filter(is_superuser=True).exists() else 1)"
}

case "$MODE" in
dev)
  need_python; venv
  manage migrate -v0
  manage seed_site
  has_admin || { say "Create the admin login:"; manage createsuperuser; }
  say "Website: http://127.0.0.1:$PORT    Admin: http://127.0.0.1:$PORT/admin/    (Ctrl+C to stop)"
  ( sleep 2; { [ "$OS" = Darwin ] && open "http://127.0.0.1:$PORT"; } || xdg-open "http://127.0.0.1:$PORT" ) >/dev/null 2>&1 &
  exec .venv/bin/python manage.py runserver "127.0.0.1:$PORT"
  ;;

prod)
  [ "$OS" = Linux ] || die "prod mode is for the Linux server. Use ./install.sh dev on a Mac."
  [ "$(id -u)" = 0 ] || die "run with sudo (or as root in the LXC)."
  command -v systemctl >/dev/null || die "systemd is required."
  need_python
  id "$APP_USER" >/dev/null 2>&1 || useradd --system --home "$APP_DIR" --shell /usr/sbin/nologin "$APP_USER"

  if [ ! -f .env ]; then
    say "First install: a few questions"
    read -rp "Public host name(s), comma separated (e.g. alfatim-demo.example.com): " HOSTS
    [ -n "$HOSTS" ] || die "a host name is needed."
    read -rp "Admin URL path [admin]: " ADMIN; ADMIN="${ADMIN:-admin}"
    read -rp "Demo copy? Hide it from Google [y/N]: " NOIDX
    case "$NOIDX" in y|Y) NOIDX=1 ;; *) NOIDX=0 ;; esac
    ORIGINS=$(echo "$HOSTS" | tr -d ' ' | sed 's#\([^,]*\)#https://\1#g')
    umask 077
    cat > .env <<ENV
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=$(python3 -c 'import secrets;print(secrets.token_urlsafe(50))')
DJANGO_ALLOWED_HOSTS=$(echo "$HOSTS" | tr -d ' '),localhost,127.0.0.1
DJANGO_CSRF_ORIGINS=$ORIGINS
DJANGO_ADMIN_PATH=$ADMIN
DJANGO_NOINDEX=$NOIDX
DJANGO_DB_PATH=$APP_DIR/data/db.sqlite3
DJANGO_CACHE_DIR=$APP_DIR/data/cache
ENV
    umask 022
  fi

  say "Installing packages…"; venv
  chown -R root:root "$APP_DIR"
  mkdir -p data/cache media backups staticfiles
  chown -R "$APP_USER":"$APP_USER" data media      # the only folders the site can write to
  chown root:"$APP_USER" .env && chmod 640 .env
  chmod 700 backups
  asapp() { runuser -u "$APP_USER" -- .venv/bin/python manage.py "$@"; }
  asapp migrate --noinput -v0
  manage collectstatic --noinput -v0
  asapp seed_site
  asapp shell -v0 -c "from django.contrib.auth.models import User;import sys;sys.exit(0 if User.objects.filter(is_superuser=True).exists() else 1)" \
    || { say "Create the admin login:"
         if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
           asapp createsuperuser --noinput --email "${DJANGO_SUPERUSER_EMAIL:-admin@localhost}"
         else asapp createsuperuser; fi; }

  chmod 750 data data/cache media; find data -type f -exec chmod 640 {} +
  cat > /etc/systemd/system/$SERVICE.service <<UNIT
[Unit]
Description=Al-Fatiem Alarabi website
After=network.target

[Service]
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/.venv/bin/gunicorn config.wsgi:application --bind $BIND:$PORT --workers 3 --timeout 60 --access-logfile -
Restart=always
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR/data $APP_DIR/media
UMask=0027

[Install]
WantedBy=multi-user.target
UNIT
  systemctl daemon-reload
  systemctl enable --now $SERVICE >/dev/null
  systemctl restart $SERVICE
  sleep 2
  CODE=$(curl -s -o /dev/null -w '%{http_code}' -H "X-Forwarded-Proto: https" -H "Host: localhost" "http://127.0.0.1:$PORT/" || true)
  [ "$CODE" = 200 ] || die "site answered $CODE. Check: journalctl -u $SERVICE -n 50"
  ADMIN=$(grep DJANGO_ADMIN_PATH .env | cut -d= -f2)
  say "Done. The site runs on http://127.0.0.1:$PORT (point your Cloudflare Tunnel there)."
  echo "Admin: https://<your host>/$ADMIN/    Logs: journalctl -u $SERVICE -f    Update: git pull && sudo ./install.sh prod"
  ;;

backup)
  STAMP=$(date +%Y%m%d-%H%M%S)
  mkdir -p backups
  manage shell -v0 -c "import sqlite3;from django.conf import settings as s;a=sqlite3.connect(s.DATABASES['default']['NAME']);b=sqlite3.connect('backups/db-$STAMP.sqlite3');a.backup(b);b.close()"
  tar -czf "backups/media-$STAMP.tar.gz" media
  ls -1t backups | tail -n +29 | sed 's#^#backups/#' | xargs -r rm -f   # keep the newest 14 pairs
  say "Saved backups/db-$STAMP.sqlite3 and backups/media-$STAMP.tar.gz"
  ;;

admin)
  if [ "$OS" = Linux ] && id "$APP_USER" >/dev/null 2>&1 && [ -f .env ]; then
    runuser -u "$APP_USER" -- .venv/bin/python manage.py createsuperuser
  else
    manage createsuperuser
  fi
  ;;

*) die "usage: ./install.sh [dev|prod|backup|admin]" ;;
esac
