# NovaPay ERP

A monorepo scaffold containing a FastAPI backend and a Next.js frontend.

## Structure

```
novapay-erp/
├── backend/                # FastAPI Python application
│   ├── main.py             # FastAPI app entry point (CORS enabled for localhost:3000)
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variable template
├── frontend/               # Next.js application (TypeScript + Tailwind CSS)
├── docker-compose.yml      # PostgreSQL 15 service
└── README.md               # This file
```

## Prerequisites

- Python 3.11+ (for the backend)
- Node.js 18+ and npm (for the frontend)
- Docker and Docker Compose (for the database)

## Setup

### 1. Database (Docker)

Start the PostgreSQL service:

```bash
docker compose up -d
```

This creates a database named `novapay_db` with user `postgres` and password `password`, exposed on `localhost:5432`.

### 2. Backend

```bash
cd backend
cp .env.example .env
# Edit .env with your JWT secret and environment settings
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend runs on `http://localhost:8000` (interactive docs at `/docs`).

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:3000`.

## Notes

- No business logic has been written yet — this is a scaffold only.
- The backend's `DATABASE_URL` points at the docker-compose PostgreSQL service.
- Copy `.env.example` to `.env` and fill in your own `JWT_SECRET_KEY` before running.