# Desktop Todo List client in a container.
# It is a GUI app: the container draws on the host's X11 display (see README).
FROM python:3.12-slim

LABEL org.opencontainers.image.title="TodoList Desktop Client" \
    org.opencontainers.image.description="Tkinter fat client for the TodoList API" \
    org.opencontainers.image.source="todolist/todolist-tk" \
    org.opencontainers.image.licenses="MIT"

# The slim image ships Python's tkinter module but not the Tk libraries or fonts it needs
RUN apt-get update \
    && apt-get install -y --no-install-recommends libtk8.6 fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY todolist.py .

# Run as an unprivileged user
RUN useradd --create-home --uid 1000 app
USER app

# Override with -e TODO_API_URL=... or by passing --api-url
ENV TODO_API_URL=http://localhost:8080

ENTRYPOINT ["python", "/app/todolist.py"]
