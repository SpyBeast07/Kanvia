# Kanvia - Team Task Manager

Kanvia is a premium, Kanban-style team task management application built for high performance and modern aesthetics. It features a robust FastAPI backend and a dynamic Svelte 5 frontend, all orchestrated with Docker.

## ✨ Features

- **Project Management**: Create and manage multiple projects with ease.
- **Dynamic Board**: Intuitive Kanban board with automatic column creation.
- **Role-Based Access**: Secure admin and member roles.
- **Task Assignment**: Assign tasks to team members and track progress.
- **Modern UI**: Sleek, responsive design built with Svelte 5 and vanilla CSS.
- **Auto-Columns**: Every new project automatically receives "Not Now", "Maybe?", and "Done" columns.

## 🚀 Quick Start

The entire stack is containerized for a seamless setup.

### 1. Start the services
Run the following command in the root directory:
```bash
docker-compose up --build
```
This starts:
- **Caddy**: Reverse proxy (Entry point)
- **Frontend**: SvelteKit application
- **Backend**: FastAPI API
- **Database**: PostgreSQL 15

### 2. Initialize the Database
Once the containers are running, you need to set up the database schema and seed initial data:

**Reset the database (optional, for a clean start):**
```bash
docker-compose exec backend python reset_db.py
```

**Seed the database:**
```bash
docker-compose exec backend python seed.py
```

### 3. Access the Application
- **Web App**: [http://localhost:8081](http://localhost:8081)
- **API Docs**: [http://localhost:8081/docs](http://localhost:8081/docs)

## 🔐 Default Accounts

| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@example.com` | `admin123` |
| **Member** | `mem1@example.com` | `mem1123` |

## 🛠 Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ORM**: [SQLModel](https://sqlmodel.tiangolo.com/) (SQLAlchemy + Pydantic)
- **Auth**: JWT (JSON Web Tokens)
- **Database**: PostgreSQL 15

### Frontend
- **Framework**: [Svelte 5](https://svelte.dev/)
- **Meta-framework**: [SvelteKit](https://kit.svelte.dev/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Language**: TypeScript

### Infrastructure
- **Proxy**: Caddy
- **Containerization**: Docker & Docker Compose

## 📁 Project Structure

- `backend/`: FastAPI source code, database models, and seeding scripts.
- `frontend/`: SvelteKit source code and assets.
- `Caddyfile`: Configuration for the reverse proxy.
- `docker-compose.yml`: Service orchestration.

## 🔧 Development Notes

- **Automatic Columns**: Projects are automatically initialized with default columns via a SQLAlchemy listener in `backend/app/models.py`.
- **Permissions**: Admins have full access to create projects and manage users. Members can view projects they are part of and manage tasks.
- **CORS**: Configured to allow all origins in development (see `backend/app/main.py`).

---
