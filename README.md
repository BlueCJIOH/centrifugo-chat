# Django + Centrifugo chat backend

This repository provides the backend and Centrifugo setup for a real-time chat service. The original React frontend was removed so the API can be consumed from another application.

## Running locally

Docker and Docker Compose are required:

```sh
docker compose up
```

After containers start, create an admin user to manage rooms:

```sh
docker compose exec backend python manage.py createsuperuser
```
Use the Django admin at [http://localhost:9000/admin](http://localhost:9000/admin) to create chat rooms.

## Authentication

The API uses JWT authentication. Every request must include an `Authorization: Bearer <token>` header. Tokens are verified using the secret specified in the `JWT_SECRET` environment variable (falls back to the Django `SECRET_KEY`) and must contain a `sub` claim with the user ID. At the moment token validity is only checked locally; integrate with your `/auth/verify` endpoint in `app/authentication.py` as needed.

Example: obtain a Centrifugo connection token for the current user.

```sh
curl -H "Authorization: Bearer <jwt>" http://localhost:9000/api/token/connection/
```

Subscribe to a personal channel:

```sh
curl -H "Authorization: Bearer <jwt>" "http://localhost:9000/api/token/subscription/?channel=personal:<user_id>"
```

The Centrifugo WebSocket endpoint is exposed at `http://localhost:8000/connection/websocket`.

### Sending a message

Assuming user A and user B are members of room `42`, user A can post a message using their JWT:

```sh
curl -X POST \
  -H "Authorization: Bearer <jwt_of_user_A>" \
  -H "Content-Type: application/json" \
  -d '{"content": "hello"}' \
  http://localhost:9000/api/rooms/42/messages/
```

All room members (including user B) who are subscribed to their personal channels will receive the message through Centrifugo.

## Integrating with another service

Your primary service should authenticate users and issue JWTs. Use those tokens to call the endpoints under `/api/` of this project to manage chat rooms and messages.
