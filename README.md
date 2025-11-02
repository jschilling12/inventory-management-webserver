Here’s your content reformatted into clean, production-ready `README.md` Markdown style — with proper code fencing, headings, and indentation preserved for GitHub rendering:

---

````markdown
# 🧱 Static-Site-Server → Flask Deployment
### End-to-End Setup and Run Guide  
**Author:** Jordan Schilling  
**Environment:** Ubuntu 25.04 (DigitalOcean Droplet)  
**Stack:** Flask • Gunicorn • Nginx • systemd • rsync • WSL2  

---

## 📖 Overview

This guide provides a **complete walkthrough** to set up, deploy, and run the connected Flask web application — whether you already have your server configured or are starting fresh.

You’ll learn how to:

- Provision and connect to a remote Ubuntu server  
- Configure SSH access securely  
- Deploy your codebase with `rsync`  
- Serve your Flask app with **Gunicorn + Nginx**  
- Automate everything with a `deploy.sh` script  

By the end, you’ll have a **production-grade setup** running at `http://<your-server-ip>/` or your custom domain.

---

## ⚙️ 1. Prerequisites

### 🖥️ Local Development Environment

You’ll need:

- **Windows 10/11** with **WSL2 (Ubuntu)**  
- Installed tools:
  - `rsync`
  - `ssh`
  - `bash`
- A working Flask codebase (with `app.py`, `templates/`, and `static/`)
- SSH key pair:
  - `SSHKey1_Linux` (private)
  - `SSHKey1_Linux.pub` (public)

---

## ☁️ 2. Server Setup (For New Users)

If you don’t yet have a server:

1. **Create a new Droplet** on [DigitalOcean](https://digitalocean.com) using Ubuntu 25.04.  
2. **Get your IP address** (e.g., `138.197.38.114`) and log in:

   ```bash
   ssh root@138.197.38.114
````

3. **Install base packages:**

   ```bash
   apt update && apt install -y nginx openssh-server python3-venv python3-pip rsync ufw
   ```

4. **Enable services:**

   ```bash
   systemctl enable --now ssh
   systemctl enable --now nginx
   ```

5. **Set up firewall:**

   ```bash
   ufw allow OpenSSH
   ufw allow 'Nginx Full'
   ufw enable
   ```

6. **Create your project directory:**

   ```bash
   mkdir -p /var/www/static-site-server
   ```

---

## 🔑 3. SSH Configuration (Local Machine)

Edit your SSH configuration file at:

**Windows path:**

```
C:\Users\<youruser>\.ssh\config
```

**Content:**

```bash
Host myserver
    HostName 138.197.38.114
    User root
    IdentityFile C:/Users/jorda/SSHKey1_Linux
    IdentitiesOnly yes
```

Then test your connection:

```bash
ssh myserver
```

✅ You should now connect directly as root.

---

## 🧰 4. Flask App Environment (on Server)

SSH into your server:

```bash
ssh myserver
```

Then set up your Flask app:

```bash
cd /var/www/static-site-server
python3 -m venv .venv
source .venv/bin/activate
pip install flask gunicorn
```

Test your app manually:

```bash
gunicorn -w 2 -b 127.0.0.1:8000 app:app
curl -I http://127.0.0.1:8000/
```

✅ If you see `HTTP/1.1 200 OK`, your Flask app is running.

---

## ⚙️ 5. Create Gunicorn Service

Make it persistent with systemd:

```bash
sudo tee /etc/systemd/system/gunicorn.service >/dev/null <<'UNIT'
[Unit]
Description=Gunicorn for Flask app
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/static-site-server
Environment="PATH=/var/www/static-site-server/.venv/bin"
RuntimeDirectory=gunicorn
RuntimeDirectoryMode=0755
UMask=007
ExecStart=/var/www/static-site-server/.venv/bin/gunicorn --workers 3 --bind unix:/run/gunicorn/flaskapp.sock app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
UNIT
```

Enable and verify:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn
sudo systemctl status gunicorn
```

✅ If you see “active (running)”, you’re good.

---

## 🌐 6. Configure Nginx as Reverse Proxy

Create and link the configuration:

```bash
sudo tee /etc/nginx/sites-available/static-site-server >/dev/null <<'NGINX'
server {
    listen 80;
    server_name 138.197.38.114;

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn/flaskapp.sock;
    }

    location /static/ {
        alias /var/www/static-site-server/static/;
        expires 30d;
        access_log off;
    }
}
NGINX
```

Activate it:

```bash
sudo ln -sf /etc/nginx/sites-available/static-site-server /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

✅ Your Flask app is now served at:
👉 [http://138.197.38.114](http://138.197.38.114)

---

## 🚀 7. Automated Deployment with deploy.sh

Create a `deploy.sh` script in your local project root:

```bash
#!/usr/bin/env bash
set -e

HOST=${1:-root@138.197.38.114}
KEY=${2:-~/.ssh/SSHKey1_Linux}
REMOTE_DIR=/var/www/static-site-server

echo "🚀 Deploying to $HOST..."

rsync -avzP \
  -e "ssh -i $KEY -o IdentitiesOnly=yes" \
  --exclude-from="./.rsync-exclude" \
  ./ \
  $HOST:$REMOTE_DIR

ssh -i $KEY $HOST "systemctl restart gunicorn && systemctl reload nginx"

echo "✅ Deployment complete!"
```

Make it executable:

```bash
chmod +x deploy.sh
```

Deploy your code:

```bash
./deploy.sh
```

✅ Automatically syncs code and restarts the app.

---

## 📂 8. .rsync-exclude File

To skip unnecessary files during deploy:

```bash
node_modules/
.git/
.env
.env.*
.DS_Store
*.log
dist/
build/
```

---

## ✅ 9. Verification Checklist

Open your browser to:
👉 [http://138.197.38.114](http://138.197.38.114)

You should see your Flask-rendered app.

If not, check logs:

```bash
sudo journalctl -u gunicorn --no-pager -n 20
sudo tail -n 20 /var/log/nginx/error.log
```

---

## 🔁 10. Redeploy Anytime

Once configured, every future update is one line:

```bash
./deploy.sh
```

This will:

* Sync code with rsync
* Restart Gunicorn
* Reload Nginx

---

## 🩺 Troubleshooting

| Problem                  | Symptom                                 | Fix                                  |
| ------------------------ | --------------------------------------- | ------------------------------------ |
| 🔒 SSH Permission denied | Wrong user/key                          | Use User root + chmod 600            |
| 🚫 Connection refused    | Port 22 closed                          | `sudo systemctl enable --now ssh`    |
| 🧱 Nginx 403             | Only default page loads                 | Ensure proxy_pass → Gunicorn         |
| 🧩 Missing socket        | `/run/gunicorn/flaskapp.sock` not found | Restart Gunicorn service             |
| ⚙️ rsync fails           | Missing exclude or path                 | Check `.rsync-exclude` + permissions |

---

## 🧠 Local Testing (Optional)

You can run locally before deployment:

```bash
source .venv/bin/activate
flask run
# or
gunicorn -w 2 -b 127.0.0.1:8000 app:app
```

Then open:
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🔐 Optional: Add SSL (Let’s Encrypt)

Once live, secure with HTTPS:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

Auto-renew every 90 days:

```bash
sudo systemctl enable certbot.timer
```

---

## 🏗️ Architecture Summary

| Layer           | Component             | Purpose                 |
| --------------- | --------------------- | ----------------------- |
| Web Server      | Nginx                 | Reverse proxy for Flask |
| Application     | Gunicorn              | WSGI server for Flask   |
| Process Manager | systemd               | Keeps Gunicorn running  |
| Deployment      | rsync + deploy.sh     | Fast updates from local |
| Environment     | Ubuntu (DigitalOcean) | Production host         |

---

## 💡 Pro Tips

Create a `requirements.txt`:

```bash
pip freeze > requirements.txt
```

Backup configs before editing:

```bash
/etc/nginx/sites-available/
/etc/systemd/system/
```

For custom domains → update `server_name` in Nginx.

---

## 🧾 Final Run Commands Recap

```bash
# From Local Machine
./deploy.sh

# From Server
sudo systemctl status gunicorn
sudo systemctl reload nginx

# Check App
curl -I http://138.197.38.114
```

---

## 🧩 If You’re Starting Fresh

1. Create server (DigitalOcean / AWS)
2. SSH into it and install packages
3. Clone or rsync your app
4. Setup Gunicorn + Nginx
5. Run `./deploy.sh`
6. Open `http://<server-ip>` 🎉

---

## 🏁 Summary

You now have:

* Fully automated deployment via rsync
* Reverse-proxy Flask hosting via Nginx
* Persistent uptime via systemd
* Modular, production-ready architecture

**Maintainer:** Jordan Schilling
**Repository Purpose:** End-to-end demonstration of static → Flask deployment using modern DevOps tooling.
**Server Path:** `/var/www/static-site-server`

```

---

Would you like me to export this as a ready-to-download `README.md` file next (with UTF-8 formatting and emoji preserved)?
```


## 🧩 Credits / Sources

This project incorporates UI templates from the open-source repository [gavindsouza/inventory-management-system](https://github.com/gavindsouza/inventory-management-system/tree/main/inventory/templates).  
Special thanks to @gavindsouza for the foundation provided by those templates and some inspiration from the app.py and [starter kit](https://github.com/pallets/flask/tree/main/examples/tutorial) for Flask.

