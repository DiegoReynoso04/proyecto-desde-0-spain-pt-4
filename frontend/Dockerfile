# syntax=docker/dockerfile:1

# ---------------------------------------------------------------- base
FROM node:26-alpine AS base
ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /app

# ---------------------------------------------------------------- dependencias
FROM base AS deps
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

# ---------------------------------------------------------------- desarrollo (hot reload)
FROM base AS dev
ENV NODE_ENV=development
COPY --from=deps --chown=node:node /app/node_modules ./node_modules
COPY --chown=node:node . .
# .next existe con el propietario correcto para que el volumen anónimo lo herede.
RUN mkdir -p .next && chown node:node /app .next
USER node
EXPOSE 3000
CMD ["npm", "run", "dev"]

# ---------------------------------------------------------------- build de producción
FROM base AS builder
# Las NEXT_PUBLIC_* y los rewrites se fijan en el build.
ARG NEXT_PUBLIC_SITE_URL=http://localhost:3000
ARG NEXT_PUBLIC_API_BASE=/api/v1
ARG API_INTERNAL_URL=http://backend:8000
ENV NEXT_PUBLIC_SITE_URL=$NEXT_PUBLIC_SITE_URL \
    NEXT_PUBLIC_API_BASE=$NEXT_PUBLIC_API_BASE \
    API_INTERNAL_URL=$API_INTERNAL_URL
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ---------------------------------------------------------------- producción (standalone)
FROM base AS prod
ENV NODE_ENV=production \
    HOSTNAME=0.0.0.0 \
    PORT=3000
COPY --from=builder --chown=node:node /app/public ./public
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static
USER node
EXPOSE 3000
CMD ["node", "server.js"]
