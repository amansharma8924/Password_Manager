# Python CLI Password Manager

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Encryption](https://img.shields.io/badge/Encryption-AES--128--CBC-red.svg)]()
[![CLI](https://img.shields.io/badge/Interface-Rich%20CLI-purple.svg)]()

A local, encrypted command-line password manager written in Python. All your passwords are stored in a single encrypted file on your machine — no cloud, no third-party servers, no accounts required.

---

## Why I Built This

I wanted a password manager that I fully understood and controlled. Most tools are either too complex, require an internet connection, or are closed source. This one is straightforward — a single encrypted file, one master password, and a clean terminal interface. Everything runs locally on your machine.

---

## Features

**Security**
- Fernet encryption (AES-128-CBC + HMAC-SHA256) for all stored data
- PBKDF2HMAC key derivation with SHA256 and 100,000 iterations — makes brute force attacks computationally expensive
- Master password is never stored anywhere — only used to derive the encryption key at runtime
- 3 incorrect password attempts exits the program automatically
- Auto-logout after 5 minutes of inactivity
- Clipboard automatically cleared 30 seconds after copying a password

**Password Management**
- Add, edit, delete, and view entries
- Each entry stores: service name, username, password, notes, category, tags, and a favorite flag
- Timestamps tracked for: date created, last modified, and last used
- Keeps the last 5 historical versions of each password per entry

**Password Tools**
- Password generator with configurable length (8–64 characters), uppercase, lowercase, digits, and symbols
- Strength checker rated 0–10 with labels: Very Weak / Weak / Medium / Strong / Very Strong
- Warns if you are reusing a password across multiple services
- Warns before saving any password rated below Medium strength

**Search and Organization**
- Search across service name, username, notes, and tags — partial match, case-insensitive
- Filter by category: work, personal, social, banking, email, other
- Filter to show favorites only
- Sort by name, date created, or last used

**Dashboard**
- Total number of saved passwords
- List of weak passwords
- List of reused (duplicate) passwords
- Passwords not updated in over 90 days
- Count of favorites
- Breakdown by category

**Import and Export**
- Export to plain text (.txt) — clearly warned as unencrypted
- Export to CSV — opens in Excel or Google Sheets
- Encrypted backup (.enc) — safe to store or transfer
- Import from CSV for bulk adding entries

---

## Project Structure

```
password_manager/
├── manager.py        # Entry point — authentication, menus, session handling
├── crypto.py         # Encryption and decryption using Fernet + PBKDF2
├── storage.py        # Reading and writing the encrypted data file
├── generator.py      # Password generation and strength checking
├── search.py         # Search, filter, and sort logic
├── stats.py          # Dashboard statistics
├── exporter.py       # Export to TXT, CSV, and encrypted backup
├── importer.py       # Import from CSV
├── requirements.txt  # Python dependencies
├── .gitignore        # Files excluded from version control
└── README.md         # This file
```

---

## Getting Started

**Requirement:** Python 3.8 or higher

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/password-manager.git
cd password-manager
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the program

```bash
python manager.py
```

---

## First Run

The first time you run the program, it will ask you to set a master password. Every subsequent run will ask you to enter it to unlock the vault.

```
Welcome! Setting up for the first time.

New master password: ••••••••••••
Confirm master password: ••••••••••••

Master password strength: Strong
Setup complete. Logging you in...
```

> **Important:** If you forget your master password, your data cannot be recovered. There is no reset option — this is by design. The encryption key is derived entirely from your master password and is never stored anywhere.

---

## How the Encryption Works

```
Master Password (user input)
        │
        ▼
PBKDF2HMAC — SHA256, 100,000 iterations, fixed salt
        │
        ▼
32-byte derived key
        │
        ▼
Base64 URL-safe encoding
        │
        ▼
Fernet cipher object
        │
        ▼
AES-128-CBC encryption + HMAC-SHA256 authentication
        │
        ▼
passwords.enc (binary encrypted file saved to disk)
```

The data file contains nothing readable without the correct master password. Even the internal JSON structure is completely hidden.

| Property | Value |
|----------|-------|
| Cipher | AES-128-CBC |
| Authentication | HMAC-SHA256 |
| Key Derivation | PBKDF2HMAC |
| Hash Function | SHA256 |
| KDF Iterations | 100,000 |
| Key Length | 256-bit |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `cryptography` | Fernet encryption, PBKDF2 key derivation |
| `rich` | Terminal formatting and colored output |
| `pyperclip` | Clipboard read and write |
| `python-dateutil` | Date parsing utilities |

---

## Security Notes

- `passwords.enc` is excluded from version control via `.gitignore` — do not commit it manually either
- Exported TXT and CSV files are **not encrypted** — delete them after use
- This tool is designed for local personal use — there is no network functionality or sync
- The salt used in key derivation is fixed in the source code. For a production-grade system, a randomly generated salt stored alongside the vault file would be more appropriate

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'cryptography'`**
```bash
pip install -r requirements.txt
```

**`pyperclip could not find a copy/paste mechanism`** (Linux only)
```bash
sudo apt-get install xclip
```

**Forgot your master password**

There is no recovery option. You will need to delete the vault file and start over.
```bash
rm passwords.enc
python manager.py
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Author

**Aman**
GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)
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
