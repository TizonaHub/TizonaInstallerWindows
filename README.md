# TizonaHub Windows Installer

## 🖥️ What is the TizonaHub Windows Installer?

The TizonaHub Windows Installer is an easy-to-use assistant that helps you install and configure [TizonaHub](https://github.com/TizonaHub) on Windows systems.  
It takes care of all prerequisites, so you don't have to worry about dependencies or manual setup steps.

**Main features:**
- Checks if Node.js, MySQL, and Python are installed.
- If any component is missing, the installer will guide you to install it.
- Verifies that your Node.js, MySQL, and Python versions are compatible with TizonaHub. If not, it offers to update them.
- Automatically generates the `.env` configuration file needed for TizonaHub.
- Prepares the MySQL database.

This ensures your TizonaHub installation is always up to date and ready to use, even if you're not an advanced user!

---

## ⚒️ Developing

To contribute or modify the installer, follow these steps:

### 1. Clone the repository

```bash
git clone https://github.com/TizonaHub/TizonaInstaller.git
cd TizonaInstaller
```
### 2. Clone the repository
```
python -m venv venv
venv\Scripts\activate
``` 

### 3. Install dependencies
```
pip install -r requirements.txt
```
### 4. Start developing!

- The main script is typically `main.py` (or as specified in your repo).
- All installation logic is handled in Python.
- You can customize checks, installation steps, and user prompts as needed.

---
## Generating .exe
```bash
pyinstaller main.spec
```
---
## 📃 Notes

- The installer must be run with administrator privileges to install or update system components like Node.js, Python, or MySQL.
- For advanced usage or troubleshooting, please check the source code and documentation comments.

---

## 📫 Feedback & Issues

If you encounter any problems or have suggestions for improvements, feel free to open an [issue](https://github.com/TizonaHub/TizonaInstallerWindows/issues) on GitHub.

---

