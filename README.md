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

## Тестирование без основного сервиса авторизации

Если у вас нет отдельного сервиса, который выдаёт JWT, можно сгенерировать токен вручную и протестировать защищённые URL этого бэкенда.

Критерии токена:
- Алгоритм: HS256
- Секрет: значение `JWT_SECRET` (если не задан, берётся `SECRET_KEY` из Django). В локальном `docker compose` по умолчанию используется:
  - `SECRET_KEY = 'django-insecure-x7gca%3()9-8a!mo%v+x2_f4to#yvo(d1+@g8*sv4bz$-y1ya7'`
- Обязательная claim: `sub` — строковый идентификатор пользователя
- Для сервисных операций (создание комнаты, управление участниками) нужен либо `role: "service"`, либо scope `chat.manage` в `scp`/`scope`.

### Вариант A: сгенерировать токен внутри контейнера (PyJWT уже установлен)

Пользовательский токен (для обычных запросов от имени пользователя `u123`):

```sh
TOKEN=$(docker compose exec -T backend python -c "import jwt,time; print(jwt.encode({'sub':'u123','exp':int(time.time())+3600}, 'django-insecure-x7gca%3()9-8a!mo%v+x2_f4to#yvo(d1+@g8*sv4bz$-y1ya7', algorithm='HS256')))")
echo $TOKEN
```

Сервисный токен (для эндпоинтов, требующих сервисных прав):

```sh
SERVICE_TOKEN=$(docker compose exec -T backend python -c "import jwt,time; print(jwt.encode({'sub':'system','role':'service','exp':int(time.time())+3600}, 'django-insecure-x7gca%3()9-8a!mo%v+x2_f4to#yvo(d1+@g8*sv4bz$-y1ya7', algorithm='HS256')))")
echo $SERVICE_TOKEN
```

Альтернативно вместо `role` можно использовать scope:

```sh
SERVICE_TOKEN=$(docker compose exec -T backend python -c "import jwt,time; print(jwt.encode({'sub':'system','scp':'chat.manage','exp':int(time.time())+3600}, 'django-insecure-x7gca%3()9-8a!mo%v+x2_f4to#yvo(d1+@g8*sv4bz$-y1ya7', algorithm='HS256')))")
```

Если вы переопределили `JWT_SECRET` через переменные окружения — используйте его вместо `SECRET_KEY` в примерах.

### Вариант B: сгенерировать токен локально

Установите PyJWT и сгенерируйте токен:

```sh
pip install pyjwt
python -c "import jwt,time; print(jwt.encode({'sub':'u123','exp':int(time.time())+3600}, 'django-insecure-x7gca%3()9-8a!mo%v+x2_f4to#yvo(d1+@g8*sv4bz$-y1ya7', algorithm='HS256')))"
```

### Примеры запросов с авторизацией

1) Получить список комнат текущего пользователя:

```sh
curl -H "Authorization: Bearer $TOKEN" http://localhost:9000/api/rooms/
```

2) Создать комнату (сервисный вызов) и сразу задать участников:

 python -c "import jwt,time; print(jwt.encode({'sub':'system','role':'service','exp':int(time.time())+3600}, 'django-insecure-x7gca%3()9-8a!mo%v+x2_f4to#yvo(d1+@g8*sv4bz$-y1ya7', algorithm='HS256')))

```sh
curl -X POST \
  -H "Authorization: Bearer $SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"general","members":["u123","u456"]}' \
  http://localhost:9000/api/rooms/
```

3) Получить Centrifugo-токены для WebSocket/подписок (от имени пользователя `u123`):

```sh
# Connection token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:9000/api/token/connection/

# Subscription token (для личного канала)
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9000/api/token/subscription/?channel=personal:u123"
```

4) Отправить сообщение в комнату (если `u123` — участник комнаты `1`):

```sh
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"hello"}' \
  http://localhost:9000/api/rooms/1/messages/
```

Подсказка: почти все эндпоинты требуют, чтобы пользователь уже был участником комнаты. Для начальной инициализации удобно использовать сервисный токен — создать комнату и добавить нужных пользователей, затем тестировать пользовательскими токенами.

## API Endpoints

- `GET /api/rooms/`: List rooms where the current user is a member. Returns each room with `member_count`, `bumped_at`, and `last_message`.
- `GET /api/rooms/{id}/`: Get details for a room if the current user is a member.
- `GET /api/search/`: Search rooms by name, includes `is_member` for the current user.
- `GET /api/rooms/{room_id}/messages/`: List messages in a room (requires membership).
- `POST /api/rooms/{room_id}/messages/`: Create a message in a room (requires membership). Body: `{ "content": "..." }`.
- `POST /api/rooms/{room_id}/join/`: Join the room as the current user.
- `POST /api/rooms/{room_id}/leave/`: Leave the room as the current user.
- `GET /api/rooms/{room_id}/members/`: List room members (requires membership).
- `POST /api/rooms/`: Create a room and optionally set initial members. Service-only, see below.
- `POST /api/rooms/{room_id}/members/`: Add members by external user IDs. Service-only.
- `DELETE /api/rooms/{room_id}/members/{user_id}/`: Remove a member by external user ID. Service-only.

Notes:
- The `user` fields in messages and room memberships store the external user ID (from JWT `sub`) as a string. There is no local user table dependency.
- All real-time notifications are broadcast to personal channels `personal:<user_id>` of current room members.

### Service-only endpoints

Some operations are intended to be called by your monolith (or another trusted backend), not by end users:

- `POST /api/rooms/`
  - Body: `{ "name": "general", "members": ["123", "456"] }`
  - Creates a room and adds the specified members (by external IDs). Broadcasts `user_joined` events for each added member.

- `POST /api/rooms/{room_id}/members/`
  - Body: `{ "users": ["123", "456"] }`
  - Adds users to the room (idempotent). Broadcasts `user_joined` per added user.

- `DELETE /api/rooms/{room_id}/members/{user_id}/`
  - Removes the specified user from the room. Broadcasts `user_left`.

Authentication for service-only endpoints is enforced via JWT claims in the same `Authorization` header. The token must include either `role=service` or a scope containing `chat.manage` (space-separated string or list in claims `scp`/`scope`). See `app/permissions.py`.

### Centrifugo tokens

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
