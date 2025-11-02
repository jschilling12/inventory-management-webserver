# 🧱 Static-Site-Server → Flask Deployment  
### End-to-End Setup and Run Guide    
**Environment:** Ubuntu 25.04 (DigitalOcean Droplet)  
**Stack:** Flask • Gunicorn • Nginx • systemd • rsync • WSL2

https://roadmap.sh/projects/static-site-server

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
  - `SSHKey1` (private) example
  - `SSHKey1.pub` (public) example

---

## ☁️ 2. Server Setup (For New Users)

If you don’t yet have a server:

1. **Create a new Droplet** on [DigitalOcean](https://digitalocean.com) using Ubuntu 25.04.  
2. **Get your IP address** (e.g., `139.197.39.111`) and log in:

   ```bash
   ssh root@<linux ip>


## 🧩 Credits / Sources

This project incorporates UI templates from the open-source repository [gavindsouza/inventory-management-system](https://github.com/gavindsouza/inventory-management-system/tree/main/inventory/templates).  
Special thanks to @gavindsouza for the foundation provided by those templates and some inspiration from the app.py and [starter kit](https://github.com/pallets/flask/tree/main/examples/tutorial) for Flask.

