# 🔐 Python CLI Password Manager

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Encryption-Fernet%20AES--128-red.svg)]()
[![CLI](https://img.shields.io/badge/Interface-Rich%20CLI-purple.svg)]()

A fully featured, **encrypted command-line password manager** built with Python.  
Stores all passwords locally in an encrypted file secured by a master password.

---

## 📸 Preview

```
╭─────────────────────────────────╮
│    🔐 PYTHON PASSWORD MANAGER   │
│    Secure • Encrypted • Fast    │
╰─────────────────────────────────╯

━━━ MAIN MENU ━━━
1. 📊 Dashboard
2. ➕ Password Add karo
3. 👁️  Password View karo
4. ✏️  Password Edit karo
5. 🗑️  Password Delete karo
6. 🔍 Search & Filter
7. 🎲 Password Generator
8. 📦 Import / Export
0. 🚪 Exit
```

---

## ✨ Features

### 🔒 Security
- **Fernet Symmetric Encryption** (AES-128-CBC + HMAC-SHA256)
- **PBKDF2HMAC Key Derivation** — SHA256, 100,000 iterations
- **Master Password Authentication** — wrong password 3 times = auto exit
- **Auto-logout** after 5 minutes of inactivity (background thread)
- **Password hidden input** using `getpass` (nothing shown on screen)
- **Clipboard auto-clear** after 30 seconds

### 🗂️ Password Management
- Add / Edit / Delete / View passwords
- Fields: `service`, `username`, `password`, `notes`, `category`, `tags`, `favorite`
- Timestamps: `created_at`, `updated_at`, `last_used`
- Password history — last 5 versions stored per entry

### 🎲 Password Utilities
- **Random Password Generator** — customizable length (8–64), uppercase, lowercase, digits, symbols
- **Strength Checker** — score 0–10, levels: Very Weak / Weak / Medium / Strong / Very Strong
- **Duplicate Detection** — warns if same password used in multiple services
- **Weak Password Alert** — warns before saving weak passwords

### 🔍 Search & Filter
- Search by service name, username, notes, tags (partial match, case-insensitive)
- Filter by category: `work` / `personal` / `social` / `banking` / `email` / `other`
- Filter favorites only
- Sort by: name / date created / last used

### 📊 Dashboard & Stats
- Total passwords count
- Weak passwords list
- Duplicate passwords list
- Old passwords (90+ days not updated)
- Favorites count
- Category-wise breakdown

### 📦 Import / Export
- Export to **plain text** (`.txt`) — with unencrypted warning
- Export to **CSV** — Excel compatible
- **Encrypted backup** (`.enc`) — safe, same encryption
- **Import from CSV** — bulk password upload

---

## 📁 Project Structure

```
password_manager/
│
├── manager.py        # Main entry point — menu loop, session, auth
├── crypto.py         # Fernet encryption, PBKDF2 key derivation
├── storage.py        # Encrypted file save/load/backup
├── generator.py      # Password generator + strength checker
├── search.py         # Search, filter, sort logic
├── stats.py          # Dashboard statistics
├── exporter.py       # TXT, CSV, encrypted backup export
├── importer.py       # CSV import logic
├── requirements.txt  # Python dependencies
├── .gitignore        # Git ignored files
└── README.md         # This file
```

---

## ⚙️ Installation

### Step 1 — Python Check karo
```bash
python --version
# Python 3.8 ya usse upar hona chahiye
```

### Step 2 — Repository Clone karo
```bash
git clone https://github.com/YOUR_USERNAME/password-manager.git
cd password-manager
```

### Step 3 — Virtual Environment banao (Recommended)
```bash
# Virtual environment create karo
python -m venv venv

# Activate karo — Windows
venv\Scripts\activate

# Activate karo — Linux / macOS
source venv/bin/activate
```

### Step 4 — Dependencies Install karo
```bash
pip install -r requirements.txt
```

### Step 5 — Run karo!
```bash
python manager.py
```

---

## 🚀 First Run

Pehli baar chalane pe program master password set karne ko kahega:

```
👋 Welcome! Pehli baar setup kar rahe hain.
Ek strong master password set karo.

🔑 Naya master password: ••••••••••••
🔑 Dobara enter karo (confirm): ••••••••••••

Master password strength: Strong
✅ Master password set ho gaya! Login ho rahe hain...
```

> ⚠️ **WARNING:** Master password bhool gaye toh data **recover nahi ho sakta**.  
> Koi backdoor nahi hai — encryption ke by-design.

---

## 📋 Usage Guide

### Password Add karna
```
Main Menu → 2 (Password Add karo)
→ Service naam enter karo (e.g. gmail)
→ Username/Email enter karo
→ Auto-generate ya manually enter karo
→ Category select karo
→ Tags add karo (comma separated)
→ Save ✅
```

### Password Dhundhna
```
Main Menu → 6 (Search & Filter)
→ Option 2: Search karo
→ Query type karo (partial match works)
```

### Encrypted Backup Lena
```
Main Menu → 8 (Import / Export)
→ Option 3: Export encrypted backup
→ backup_YYYYMMDD_HHMMSS.enc file ban jaayegi
```

---

## 🔐 Security Architecture

```
Master Password (user input)
        │
        ▼
PBKDF2HMAC (SHA256, 100,000 iterations, fixed salt)
        │
        ▼
32-byte Derived Key
        │
        ▼
base64.urlsafe_b64encode()
        │
        ▼
Fernet Key
        │
   ┌────┴────┐
   ▼         ▼
encrypt()  decrypt()
   │         │
   ▼         ▼
AES-128-CBC + HMAC-SHA256
        │
        ▼
passwords.enc (binary encrypted file)
```

### Encryption Details
| Property | Value |
|----------|-------|
| Algorithm | AES-128-CBC |
| Authentication | HMAC-SHA256 |
| Key Derivation | PBKDF2HMAC |
| Hash Function | SHA256 |
| KDF Iterations | 100,000 |
| Key Length | 256-bit |
| Storage Format | Fernet Token (Base64) |

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `cryptography` | Latest | Fernet encryption, PBKDF2 |
| `rich` | Latest | Beautiful colored CLI output |
| `pyperclip` | Latest | Clipboard copy/paste |
| `python-dateutil` | Latest | Date parsing utilities |

Install all:
```bash
pip install cryptography rich pyperclip python-dateutil
```

---

## 🗂️ Data Storage

- All passwords stored in **`passwords.enc`** (local file, same directory)
- Format internally: **JSON → UTF-8 encoded → AES-128-CBC encrypted → Base64 Fernet token**
- File is **unreadable without master password** — even if someone copies it

```json
{
  "gmail": {
    "username": "user@gmail.com",
    "password": "Str0ng!Pass#2024",
    "category": "email",
    "tags": ["google", "work"],
    "notes": "Main account",
    "favorite": true,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-20T14:22:00",
    "last_used": "2024-03-19T09:15:00",
    "history": []
  }
}
```
*(This is the internal decrypted structure — actual file is fully encrypted)*

---

## ⚠️ Important Notes

1. **`passwords.enc` file ko GitHub pe push mat karo** — `.gitignore` mein already added hai
2. **Master password** kahi safe jagah note karo — recovery impossible hai
3. **Export TXT/CSV files** encrypted nahi hoti — use karne ke baad delete karo
4. Yeh project **local use** ke liye hai — cloud sync nahi hai

---

## 🛠️ Troubleshooting

### `ModuleNotFoundError: No module named 'cryptography'`
```bash
pip install -r requirements.txt
```

### `pyperclip could not find a copy/paste mechanism`
Linux pe xclip install karo:
```bash
sudo apt-get install xclip
```

### Bhool gaye master password
Koi recovery option nahi hai by design.  
`passwords.enc` delete karo aur fresh start karo:
```bash
rm passwords.enc
python manager.py
```

---

## 🤝 Contributing

1. Fork karo repository
2. Feature branch banao: `git checkout -b feature/new-feature`
3. Changes commit karo: `git commit -m 'Add new feature'`
4. Branch push karo: `git push origin feature/new-feature`
5. Pull Request open karo

---

## 📄 License

MIT License — free to use, modify, distribute.

---

## 👨‍💻 Author

**Aman**  
GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)

---

> 💡 **Tip:** Agar yeh project helpful laga toh ⭐ Star zaroor karo!
