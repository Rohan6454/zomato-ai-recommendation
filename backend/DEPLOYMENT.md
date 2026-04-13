## Backend Deployment Notes

### Run with Docker

From `backend/`:

```bash
docker build -t zomato-backend:latest .
docker run --rm -p 8000:8000 --env-file ../.env zomato-backend:latest
```

### Recommended production hardening

- Put API behind a reverse proxy/load balancer.
- Enforce HTTPS at ingress.
- Add authentication if exposing publicly.
- Externalize cache (Redis) and database (Postgres) for scale.
- Export `/metrics` to monitoring stack (Prometheus/Grafana).

### Useful endpoints

- `GET /health`
- `GET /metrics`
- `GET /localities`
- `POST /recommendations`
- `POST /feedback`
- `GET /feedback`

