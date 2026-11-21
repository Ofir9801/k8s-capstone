# syntax=docker/dockerfile:1

# -----------------------------------------------
# Build stage: install dependencies, build Nuxt
# -----------------------------------------------
FROM node:24-alpine AS build

WORKDIR /app

# Install dependencies first (better layer caching). The postinstall step
# (nuxt prepare) needs nuxt.config.ts, so copy it along with the lockfile.
COPY package.json package-lock.json nuxt.config.ts ./
RUN npm ci

# Copy source and build. The result is .output/: a self-contained Node server
# (with only the node_modules it needs) plus the browser assets.
COPY . .
RUN npm run build

# --------------------------------
# Runtime stage: run the server
# --------------------------------
FROM node:24-alpine AS runtime

WORKDIR /app

LABEL org.opencontainers.image.title="TodoList Nuxt Frontend" \
    org.opencontainers.image.description="Server-side rendered Nuxt app for the TodoList API" \
    org.opencontainers.image.source="todolist/todolist-nuxt" \
    org.opencontainers.image.licenses="MIT"

ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3000

# Runtime configuration (override with -e or a Kubernetes ConfigMap):
#   NUXT_API_BASE_URL  where the server reaches the API (default http://localhost:8080)
#   NUXT_PUBLIC_USER   optional name shown in the title

COPY --from=build --chown=node:node /app/.output ./.output

# The node image ships an unprivileged "node" user (uid 1000).
USER node

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
