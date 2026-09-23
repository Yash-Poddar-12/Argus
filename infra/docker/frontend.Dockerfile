FROM node:22-alpine
ARG APP=operator
ENV APP=${APP} NEXT_TELEMETRY_DISABLED=1
RUN corepack enable && corepack prepare pnpm@9 --activate
WORKDIR /web
COPY . .
RUN pnpm install --frozen-lockfile
CMD ["sh", "-c", "pnpm --filter @argus/${APP} dev"]
