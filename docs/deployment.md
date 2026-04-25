# VPS Deployment Guide

This project can be deployed to a VPS directory like `/var/www/app`.

The steps below assume:

- Ubuntu VPS
- project path: `/var/www/app`
- FastAPI served by `uvicorn`
- MySQL running with `docker compose`
- Nginx used as the public reverse proxy
- `systemd` used to keep the API running

## 1. Connect to the server

```bash
ssh your-user@your-server-ip
```

## 2. Install system packages

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx git docker.io docker-compose-plugin
```

Enable Docker and Nginx:

```bash
sudo systemctl enable --now docker
sudo systemctl enable --now nginx
```

Optional but recommended:

```bash
sudo usermod -aG docker $USER
```

After this command, log out and log back in before using Docker without `sudo`.

## 3. Create the app directory

```bash
sudo mkdir -p /var/www/app
sudo chown -R $USER:$USER /var/www/app
cd /var/www/app
```

## 4. Upload or clone the project

If your code is in Git:

```bash
git clone <your-repository-url> /var/www/app
cd /var/www/app
```

If the files already exist on the server, just move into the directory:

```bash
cd /var/www/app
```

## 5. Create the Python environment

```bash
cd /var/www/app
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 6. Configure environment variables

Create or update `.env` in `/var/www/app`.

Example:

```env
DB_HOST=127.0.0.1
DB_PORT=3307
DB_NAME=fast_api
DB_USER=root
DB_PASSWORD=change-this-password
```

Notes:

- Keep `DB_HOST=127.0.0.1` because the app connects to MySQL through the VPS itself.
- Keep `DB_PORT=3307` if you use the current `docker-compose.yml` unchanged.
- Do not leave `DB_PASSWORD` empty on production.

## 7. Start MySQL with Docker Compose

This project already includes `docker-compose.yml` for MySQL.

```bash
cd /var/www/app
docker compose up -d
```

Check that the container is running:

```bash
docker compose ps
```

Check database logs if needed:

```bash
docker compose logs mysql
```

## 8. Run database migrations

Activate the virtual environment and apply Alembic migrations:

```bash
cd /var/www/app
source .venv/bin/activate
alembic upgrade head
```

## 9. Create required storage directories

The app writes files under the local `storage/` folder, so make sure it exists:

```bash
mkdir -p /var/www/app/storage/docs
mkdir -p /var/www/app/storage/cv
mkdir -p /var/www/app/storage/uploads
mkdir -p /var/www/app/storage/temp
mkdir -p /var/www/app/storage/images
```

If your deployment user and service user are the same, this is enough.

## 10. Test the app manually

Before creating a service, confirm the app starts:

```bash
cd /var/www/app
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open another terminal and test:

```bash
curl http://127.0.0.1:8000/
```

You should get:

```json
{"message":"FastAPI Async CRUD with MySQL is running"}
```

Press `Ctrl+C` after confirming it works.

## 11. Create a systemd service

Create `/etc/systemd/system/fastapi-docs.service`:

```ini
[Unit]
Description=FastAPI Docs App
After=network.target docker.service
Requires=docker.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/app
EnvironmentFile=/var/www/app/.env
ExecStart=/var/www/app/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Important:

- If your project files are owned by another user, either give `www-data` access or change `User` and `Group` to your deploy user.
- The service must be able to read `.env` and write into `/var/www/app/storage`.

Set permissions if you keep `www-data`:

```bash
sudo chown -R www-data:www-data /var/www/app
```

Then enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now fastapi-docs
```

Check service status:

```bash
sudo systemctl status fastapi-docs
```

Read logs:

```bash
sudo journalctl -u fastapi-docs -f
```

## 12. Configure Nginx

Create `/etc/nginx/sites-available/fastapi-docs`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/fastapi-docs /etc/nginx/sites-enabled/fastapi-docs
sudo nginx -t
sudo systemctl reload nginx
```

If the default site conflicts, remove it:

```bash
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

## 13. Open the firewall

If `ufw` is enabled:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## 14. Optional: add HTTPS with Let's Encrypt

Install Certbot:

```bash
sudo apt install -y certbot python3-certbot-nginx
```

Request a certificate:

```bash
sudo certbot --nginx -d your-domain.com
```

## 15. Deployment update flow

When you push a new version:

```bash
cd /var/www/app
git pull
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart fastapi-docs
```

If your database service was changed too:

```bash
docker compose up -d
```

## 16. Quick verification checklist

- `docker compose ps` shows MySQL running
- `sudo systemctl status fastapi-docs` is active
- `sudo nginx -t` passes
- `curl http://127.0.0.1:8000/` returns the app message
- opening `http://your-domain.com/docs` loads Swagger UI

## Common notes for this project

- The application reads database settings from `.env` through `app/core/config.py`.
- Uploaded and generated files are stored inside `/var/www/app/storage`.
- Alembic is already configured to read the same `.env` database values.
- The included Docker Compose file exposes MySQL on host port `3307`, so your `.env` should match that unless you change the compose file.
