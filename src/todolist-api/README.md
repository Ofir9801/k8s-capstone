# API Service for Todo List demo App

## Go REST API service (api)

This repo also includes a lightweight Go service that provides RESTful APIs for todolist application 

Endpoints:
- `GET /todos` (list), 
- `GET /todos/{id}` (fetch one)
- `POST /todos` (create; body: `{ "task": "..." }`, status defaults to `"Todo"`, id generated as `MAX(id)+1` within a transaction)
- `PUT/PATCH /todos/{id}` (update `task` and/or `status`; valid statuses: `"Todo"`, `"In Progress"`, `"Complete"`; response shows `updated_fields` or `"no changes"`)
- `DELETE /todos/{id}` (remove)
- `GET /livez`, `GET /readyz` health probes

## API Usage Examples with curl, assuming service is running locally 

### List all todos

```bash
curl http://localhost:8080/todos
```

### Get a specific todo

```bash
curl http://localhost:8080/todos/1
```

### Create a new todo

```bash
curl -X POST http://localhost:8080/todos \
  -H "Content-Type: application/json" \
  -d '{"task": "Buy groceries"}'
```

### Update a todo (PUT)

```bash
# Update both task and status
curl -X PUT http://localhost:8080/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"task": "Buy groceries and cook", "status": "In Progress"}'
```

### Update a todo (PATCH)

```bash
# Update only status
curl -X PATCH http://localhost:8080/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "Complete"}'

# Update only task
curl -X PATCH http://localhost:8080/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"task": "Buy organic groceries"}'
```

### Delete a todo

```bash
curl -X DELETE http://localhost:8080/todos/1
```

## Running the API

Run locally:

```bash
cd api
export MYSQL_USER=<user>
export MYSQL_PASSWORD=<password>
export MYSQL_DB=<database>
export MYSQL_HOST=<host-or-host:port>
export PORT=8080  # optional
go run .
```

Initialize the configured todo table during startup only when needed:

```bash
go run . --init-schema
```

Build and run the Go API as a container:

```bash
cd api
docker build -t todos-go-api .
docker run --rm -p 8080:8080 \
  -e MYSQL_USER=<user> \
  -e MYSQL_PASSWORD=<password> \
  -e MYSQL_DB=<database> \
  -e MYSQL_HOST=<host-or-host:port> \
  todos-go-api
```

## Building and Pushing the Container Image

Build and push with `docker` or `podman` (the commands are the same), from the capstone project folder (the one that contains `src/`):

```bash
docker build -t ghcr.io/<you>/todolist-api:1.0 src/todolist-api
docker push ghcr.io/<you>/todolist-api:1.0
```

Or use the `Makefile` in this folder, which runs the same two commands
(`podman` by default, `CONTAINER_TOOL=docker` to switch):

```bash
OWNER=<you> VERSION=1.0 make -C src/todolist-api push     # build + push
OWNER=<you> VERSION=1.0 make -C src/todolist-api build    # build only
make -C src/todolist-api                                  # show settings and targets
```

| Setting | Meaning | Default |
| --- | --- | --- |
| `OWNER` | registry owner/namespace (your GitHub user for ghcr.io) | required |
| `VERSION` | image tag | required |
| `REGISTRY` | registry host | `ghcr.io` |
| `CONTAINER_TOOL` | `podman` or `docker` | `podman` |

The image is tagged `$REGISTRY/$OWNER/todolist-api:$VERSION`, e.g. `ghcr.io/<you>/todolist-api:1.0`.

## License

[MIT License](LICENSE)
