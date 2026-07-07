# 🗳️ Secure E-Voting System

A full-stack electronic voting platform with **blockchain-simulated immutability**, **role-based access control**, **OTP authentication**, and a polished **React** frontend.

> Built with Flask · React 18 · SQLite · Framer Motion

---

## ✨ Features

- **Three-role architecture** — Admin, Election Officer, and Voter portals
- **Blockchain-simulated ledger** — Tamper-proof election records with cryptographic transaction hashes
- **OTP authentication** — 6-digit OTP with expiry and lockout protection for voters
- **Election lifecycle** — Create → Activate → Vote → Close → Archive
- **Real-time vote tallying** — Live candidate vote bars on the admin dashboard
- **Auto-generated Ethereum addresses** — Unique voter identities assigned automatically
- **Responsive cyberpunk UI** — Dark-themed interface with micro-animations

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```
Backend starts at `http://localhost:5000`

### 2. Frontend
```bash
cd frontend
npm install
npm start
```
Frontend starts at `http://localhost:3000`

---

## 🔐 Default Credentials

| Role    | Login                  | Method            |
|---------|------------------------|-------------------|
| Admin   | admin@admin.com        | Password: admin123|
| Officer | officer@admin.com      | Password: officer123|
| Voter   | Voter ID (e.g. V001)  | OTP via phone     |

---

## 🏗️ Project Structure

```
voting-backend/
├── app.py                     ← Flask REST API (main entry)
├── otp_manager.py             ← OTP generation & verification
├── requirements.txt           ← Python dependencies
├── Procfile                   ← Production server config
│
├── database/
│   └── db_setup.py            ← SQLite schema & queries
│
├── utils/
│   └── blockchain_utils.py    ← Blockchain simulator engine
│
├── contracts/
│   ├── SecureVoting.sol        ← Original Solidity smart contract
│   └── SecureVoting_ABI.json   ← Contract ABI reference
│
└── frontend/                  ← React 18 SPA
    └── src/
        ├── api.js             ← API base URL config
        └── pages/
            ├── AdminLogin.js / AdminDashboard.js
            ├── OfficerLogin.js / OfficerDashboard.js
            └── VoterLogin.js / VoterDashboard.js
```

---

## 🔄 Election Lifecycle

```
Admin: Create Election  →  CREATED
Admin: Activate         →  ACTIVE   ← Voters can cast votes
Admin: Close            →  CLOSED   ← Results finalized
Admin: Archive          →  ARCHIVED
```

---

## 🛡️ Security

| Layer              | Implementation                        |
|--------------------|---------------------------------------|
| OTP Authentication | 6-digit, 5-min expiry, 3-attempt lock |
| Blockchain Ledger  | In-memory simulator with SHA-256 hashes|
| Role-Based Access  | Header-based RBAC middleware          |
| Input Sanitization | Regex filtering on all user inputs    |
| CORS Protection    | Configurable origin restriction       |

---

## ⚙️ Deployment

### Backend (Railway / Render)
1. Connect this repository
2. Set environment variables from `.env.example`
3. Deploy — uses `Procfile` for Gunicorn

### Frontend (Netlify)
1. Base directory: `frontend`
2. Build command: `npm install --legacy-peer-deps && npm run build`
3. Set `REACT_APP_API_URL` to your backend URL

---

## 📦 Tech Stack

| Layer     | Technologies                         |
|-----------|--------------------------------------|
| Backend   | Python · Flask · SQLite · Gunicorn   |
| Frontend  | React 18 · Framer Motion · Axios     |
| Blockchain| In-memory simulator (Solidity-based) |
| Auth      | OTP · Password hashing (SHA-256)     |

---

## 📄 API Endpoints

| Method | Endpoint                              | Role    |
|--------|---------------------------------------|---------|
| GET    | `/api/health`                         | Public  |
| POST   | `/api/login`                          | Public  |
| POST   | `/api/voter/request-otp`              | Public  |
| POST   | `/api/voter/verify-otp`               | Public  |
| GET    | `/api/generate-eth-address`           | Public  |
| GET    | `/api/admin/stats`                    | Admin   |
| POST   | `/api/admin/create-election`          | Admin   |
| POST   | `/api/admin/activate-election/:id`    | Admin   |
| POST   | `/api/admin/close-election/:id`       | Admin   |
| GET    | `/api/admin/elections`                | Admin   |
| GET    | `/api/officer/voters`                 | Officer |
| POST   | `/api/officer/add-voter`              | Officer |
| PUT    | `/api/officer/update-voter/:id`       | Officer |
| DELETE | `/api/officer/delete-voter/:id`       | Officer |
| GET    | `/api/elections`                      | Voter   |
| POST   | `/api/cast-vote`                      | Voter   |

---

## 📝 License

This project is for educational and demonstration purposes.
