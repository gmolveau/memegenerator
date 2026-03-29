FROM node:trixie-slim AS base

SHELL ["/bin/bash", "-c"]

FROM base AS dev_base

COPY --from=ghcr.io/casey/just:latest /just /usr/local/bin/

RUN npm install -g pnpm@latest-10

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

COPY . /app
WORKDIR /app

FROM dev_base AS dev
RUN --mount=type=cache,id=pnpm,target=/pnpm/store just install-dev
EXPOSE 5173
CMD [ "just", "run-dev" ]

FROM dev_base AS build-prod
RUN --mount=type=cache,id=pnpm,target=/pnpm/store just install-prod && just build

FROM base AS prod
WORKDIR /app
COPY --from=build-prod /app/build /app/build
COPY --from=build-prod /app/package.json /app/package.json
RUN npm install dotenv@17.3.1
EXPOSE 3000
CMD [ "node", "-r", "dotenv/config", "build" ]
