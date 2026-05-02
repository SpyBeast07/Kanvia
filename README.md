# Kanvia - Team Task Manager

A Kanban-style team task manager built with SvelteKit and FastAPI.

## Project Structure

- `frontend/`: SvelteKit (Frontend)
- `backend/`: FastAPI (Backend)

## Tech Stack

- **Frontend**: SvelteKit, TypeScript, Vite
- **Backend**: FastAPI, Python 3.14+
- **Database**: PostgreSQL
- **Styling**: Vanilla CSS (Custom design)

## Setup Instructions

### Database Setup (Docker)

1. Ensure you have Docker installed.
2. Navigate to the `db` directory:
   ```bash
   cd db
   ```
3. Start the PostgreSQL container:
   ```bash
   docker-compose up -d
   ```
   *This will automatically initialize the schema using `init.sql`.*

### Prerequisites

- Node.js (v18+)
- Python (3.10+)
- Docker (for PostgreSQL)

### Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables in `.env`.
5. Run the development server:
   ```bash
   python3 main.py
   ```

### Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## API Documentation

Once the backend is running, you can access the interactive API docs at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
