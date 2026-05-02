# Kanvia Docker Deployment

This project is fully dockerized with a production-ready setup using Caddy as a reverse proxy.

## Prerequisites
- Docker
- Docker Compose

## Running the application

To start the entire stack (Frontend, Backend, Database, and Caddy), run:

```bash
docker-compose up --build
```

The application will be available at:
**http://localhost:8081**

## Services
- **Caddy**: Reverse proxy listening on port `8081`.
- **Frontend**: SvelteKit application running on Node.js.
- **Backend**: FastAPI application.
- **Database**: PostgreSQL 15.

## Environment Variables
You can customize the setup by modifying the `environment` sections in `docker-compose.yml`.
- `SECRET_KEY`: Used for JWT signing.
- `DATABASE_URL`: Connection string for the backend to find the database.
