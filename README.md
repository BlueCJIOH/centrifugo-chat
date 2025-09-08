# Django + Centrifugo chat backend

This repository provides the backend and Centrifugo setup for a real-time chat service. The original React frontend was removed so the API can be consumed from another application.

## Running locally

Docker and Docker Compose are required:

```sh
docker compose up
```

After containers start, create an admin user to manage rooms and users:

```sh
docker compose exec backend python manage.py createsuperuser
```

Use the Django admin at [http://localhost:9000/admin](http://localhost:9000/admin) to create rooms or populate demo data from the shell:

```sh
docker compose exec backend python manage.py shell
```

```python
from app.utils import setup_dev
setup_dev()
```

## Authentication

The API uses JWT authentication. Every request must include an `Authorization: Bearer <token>` header. Tokens are verified using the secret specified in the `JWT_SECRET` environment variable (falls back to the Django `SECRET_KEY`) and must contain a `sub` claim with the user ID.

Example: obtain a Centrifugo connection token for the current user.

```sh
curl -H "Authorization: Bearer <jwt>" http://localhost:9000/api/token/connection/
```

Subscribe to a personal channel:

```sh
curl -H "Authorization: Bearer <jwt>" "http://localhost:9000/api/token/subscription/?channel=personal:<user_id>"
```

The Centrifugo WebSocket endpoint is exposed at `http://localhost:8000/connection/websocket`.

## Integrating with another service

Your primary service should authenticate users and issue JWTs. Use those tokens to call the endpoints under `/api/` of this project to manage chat rooms and messages.
