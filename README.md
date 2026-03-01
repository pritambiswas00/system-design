# System Design - Auth Service

Simple authentication service built with Flask + MySQL.

## Features

- `POST /login` using Basic Auth credentials
- JWT generation on successful login
- `POST /validate` to validate a bearer token
- Dockerized app and MySQL with `docker-compose`
- GitHub Actions pipeline to build and push image to Docker Hub

## Project Structure

- `auth-service/server.py` - Flask API
- `auth-service/init.sql` - MySQL schema and seed data
- `DockerFile` - app image build
- `docker-compose.yml` - local app + MySQL stack
- `apitest.http` - request file for local endpoint testing
- `.github/workflows/docker-image.yml` - CI build/push pipeline

## Prerequisites

- Docker + Docker Compose

## Run Locally (Docker Compose)

```bash
docker compose up -d --build
```

Service endpoints:

- App: `http://localhost:5000`
- MySQL: `localhost:3306`

Stop stack:

```bash
docker compose down
```

Reset DB volume:

```bash
docker compose down -v
```

## Seeded Test Credentials

`auth-service/init.sql` inserts a default user:

- Email: `email@mail.com`
- Password: `password123`

## API Usage

### 1) Login

Request:

```http
POST /login
Authorization: Basic ZW1haWxAbWFpbC5jb206cGFzc3dvcmQxMjM=
```

Success response: JWT token string.

### 2) Validate Token

Request:

```http
POST /validate
Authorization: Bearer <jwt-token>
```

Success response: decoded JWT payload.

## Test via `apitest.http`

Open `apitest.http` in VS Code REST Client and run:

1. `Login (Basic Auth)`
2. Copy token into `@jwt`
3. Run `Validate JWT`

## Environment Variables

Used by `auth-service/server.py`:

- `MYSQL_HOST` (default: `localhost`)
- `MYSQL_USER` (default: `myuser`)
- `MYSQL_PASSWORD` (default: `mypassword`)
- `MYSQL_DB` (default: `mydb`)
- `JWT_SECRET` (default: `mysecret`)

In Compose, these are set for you.

## CI/CD: GitHub Actions -> Docker Hub

Workflow: `.github/workflows/docker-image.yml`

Triggers:

- Push to `master`
- Tags like `v*`
- Manual `workflow_dispatch`

Required GitHub repository secrets:

- `DOCKER_USERNAME`
- `DOCKER_SECRET`

Published image name format:

- `<DOCKER_USERNAME>/<repo-name>`

## Build Image Manually

```bash
docker build -f DockerFile -t system-design-auth .
```
