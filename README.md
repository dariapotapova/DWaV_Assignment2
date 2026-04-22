## `DOCKER.md`

```markdown
# Docker setup for Traffic Visualizer

## Build and run

### 1. Build all containers

```bash
docker-compose build
```

### 2. Start all services

```bash
docker-compose up
```

To run in background:

```bash
docker-compose up -d
```

### 3. Stop everything

```bash
docker-compose down
```

## Access the application

After running `docker-compose up`, open in your browser:

| Service | URL |
|---------|-----|
| Frontend (globe) | http://localhost:8080 |
| Backend API | http://localhost:5000 |
| Backend status | http://localhost:5000/api/status |

## What happens when you run

1. **Backend container** starts Flask server on port 5000
2. **Frontend container** serves index.html on port 8080
3. **Sender container** reads CSV and sends all packages to backend, then exits

## Check if everything works

### Backend is running

Open `http://localhost:5000/api/status`

Should see: `{"packages_received":0,"is_active":true,"time_elapsed":0}`

### Frontend is running

Open `http://localhost:8080`

Should see a 3D globe

### Sender did its job

Check backend logs:

```bash
docker-compose logs backend
```

Should see `Added: IP at (lat, lon)` messages
