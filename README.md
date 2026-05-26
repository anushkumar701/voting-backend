# 🗳️ E-Voting Meets Blockchain

A secure, full-stack electronic voting system combining **Flask**, **React**, **Ethereum Blockchain**, **Face Recognition**, and **OTP Authentication**.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Ganache](https://trufflesuite.com/ganache/) running on port **7545**
- Contract deployed via [Remix IDE](https://remix.ethereum.org)

### Run the System
```
Double-click → START_BOTH.bat
```
Opens backend on `http://localhost:5000` and frontend on `http://localhost:3000`.

---

## 🔐 Login Credentials

| Role    | Email / ID             | Password / Method |
|---------|------------------------|-------------------|
| Admin   | admin@admin.com        | admin123          |
| Officer | officer@admin.com      | officer123        |
| Voter   | Voter ID (e.g. V001)   | OTP via phone     |

---

## 🏗️ Project Structure

```
voting-backend/
├── app.py                    ← Flask REST API (main entry point)
├── otp_manager.py            ← OTP generation & verification
├── face_recognition_system.py← Face registration & live verification
├── requirements.txt          ← Python dependencies
├── START_BOTH.bat            ← One-click startup script
│
├── database/
│   └── db_setup.py           ← SQLite schema & queries
│
├── utils/
│   ├── blockchain_utils.py   ← Web3 / Ganache integration
│   ├── load_contract.py      ← Contract loader helper
│   └── ...
│
├── contracts/
│   └── SecureVoting_ABI.json ← Deployed Solidity contract ABI
│
├── face_data/                ← Voter face encodings (auto-generated)
├── face/                     ← Sample face images
│
└── frontend/                 ← React 18 SPA
    └── src/pages/
        ├── AdminLogin.js / AdminDashboard.js
        ├── OfficerLogin.js / OfficerDashboard.js
        └── VoterLogin.js / VoterDashboard.js
```

---

## ⚙️ Setup Steps

1. **Start Ganache** — set port to 7545
2. **Deploy contract** via Remix IDE using `contracts/SecureVoting_ABI.json`
3. **Copy contract address** → paste into `contract_address.txt`
4. **Install Python deps:**
   ```
   pip install -r requirements.txt
   ```
5. **Install frontend deps:**
   ```
   cd frontend && npm install
   ```
6. **Run:** `START_BOTH.bat`

---

## 🔄 Election Lifecycle

```
Admin: Create Election  →  CREATED
Admin: Activate         →  ACTIVE   ← Voters can vote
Admin: Close            →  CLOSED
Admin: Archive          →  ARCHIVED
```

---

## 🛡️ Security Layers

| Layer            | Technology                      |
|------------------|---------------------------------|
| OTP Auth         | 6-digit, 5-min expiry, lockout  |
| Face Recognition | OpenCV + face_recognition lib   |
| Blockchain       | Ethereum / Ganache (immutable)  |
| Role Access      | Header-based RBAC               |
| Input Sanitize   | Regex filtering on all inputs   |

---

## 📦 Tech Stack

**Backend:** Python · Flask · SQLite · Web3.py  
**Frontend:** React 18 · Framer Motion · Axios  
**Blockchain:** Ethereum · Solidity · Ganache  
**AI/Vision:** OpenCV · face_recognition · NumPy
