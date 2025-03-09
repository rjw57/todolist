ARG PYTHON_VERSION=3.12
ARG NODE_VERSION=lts

###############################################################################
# Base image for all *production* images to build upon.
#
# If you change the version here, update pyproject.toml and the version used in
# CI. We explicitly specify the platform here so that it matches the platform
# used in deployment.
FROM --platform=linux/amd64 registry.gitlab.developers.cam.ac.uk/uis/devops/infra/dockerimages/python:${PYTHON_VERSION}-slim AS base

# Some performance and disk-usage optimisations for Python within a docker container.
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

# Do everything relative to /usr/src/app which is where we install our
# application.
WORKDIR /usr/src/app

# Pretty much everything from here on needs poetry.
RUN pip install --no-cache-dir poetry && poetry self add poetry-plugin-export

###############################################################################
# Node container. We simply copy the entire contents of the node container into the installed deps
# container to "install" node within it. This container exists so that the version of node we use
# only has to be specified once.
FROM --platform=linux/amd64 node:$NODE_VERSION AS node-base

###############################################################################
# Node container for running on the local machine. On arm64 platforms, this will be basically the
# same as the "base" image but this image will run as an aarch64 image on Apple Silicon machines.
FROM node:$NODE_VERSION AS node-base-dev

###############################################################################
# Base image for all *development* images to build upon.
#
# If you change the version here, update pyproject.toml and the version used in
# CI. On arm64 platforms, this will be basically the same as the "base" image but this image will
# run as an aarch64 image on Apple Silicon machines which means that the app will be far snappier.
FROM registry.gitlab.developers.cam.ac.uk/uis/devops/infra/dockerimages/python:${PYTHON_VERSION}-slim AS dev-base

# Do everything relative to /usr/src/app which is where we install our application.
WORKDIR /usr/src/app

# "Install" node by copying content of node base image.
COPY --from=node-base-dev / /

# Some performance and disk-usage optimisations for Python within a docker container.
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

# Pretty much everything from here on needs poetry.
RUN pip install --no-cache-dir poetry && poetry self add poetry-plugin-export

###############################################################################
# Install frontend dependencies within a dedicated container. Note that for consistency we use the
# same version of node installed into the "installed-deps" container, not that it *should* matter as
# the build artefacts should be identical.
FROM node-base-dev AS frontend-deps

# Do everything relative to /usr/src/app which is where we install our
# application.
WORKDIR /usr/src/app/frontend/

# Install packages and build frontend
ADD ./frontend/package.json ./frontend/yarn.lock ./
RUN yarn install

# Copy remaining files (such as tsconfig.json, etc) but do not build the
# frontend yet.
ADD ./frontend/ ./

###############################################################################
# Use the frontend-deps container to build the frontend itself.
FROM frontend-deps AS frontend-builder
RUN yarn run build

###############################################################################
# Just enough to run tox. Tox will install any other dependencies it needs.
# Note that tox runs from the base *production* container so that it uses
# the same platform as will be running in production. This is to provide some
# easy way for developers on Apple Silicon to run tests on the platform used in
# production.
FROM base AS tox

RUN pip install tox
ENTRYPOINT ["tox"]
CMD []

###############################################################################
# Install requirements.
FROM base AS installed-deps

# "Install" node.
COPY --from=node-base / /

COPY pyproject.toml poetry.lock ./
RUN set -e; \
  poetry export --format=requirements.txt --output=.tmp-requirements.txt; \
  pip install --no-cache-dir -r .tmp-requirements.txt; \
  rm .tmp-requirements.txt

# Default environment for image. By default, we use the settings module
# bundled with this repo. Change DJANGO_SETTINGS_MODULE to use custom settings.
ENV DJANGO_SETTINGS_MODULE=project.settings

###############################################################################
# A development-focussed image. This does not include the actual application
# code since that will be mounted in as a volume.
FROM dev-base AS development

# Install the base requirements as in the production image.
COPY pyproject.toml poetry.lock ./
RUN set -e; \
  poetry export --format=requirements.txt --output=.tmp-requirements.txt; \
  pip install --no-cache-dir -r .tmp-requirements.txt; \
  rm .tmp-requirements.txt

# Additionally, install local development requirements.
RUN set -e; \
  poetry export --only=dev --format=requirements.txt --output=.tmp-requirements.txt; \
  pip install --no-cache-dir -r .tmp-requirements.txt; \
  rm .tmp-requirements.txt

ENV DJANGO_SETTINGS_MODULE=project.settings.developer

EXPOSE 8000
CMD ["./manage.py", "runserver", "0.0.0.0:8000"]

###############################################################################
# The last target in the file is the "default" one. In our case it is the
# production image.
#
# KEEP THIS AS THE FINAL TARGET OR ELSE DEPLOYMENTS WILL BREAK.
FROM installed-deps AS production

# The production target includes the application code.
COPY . .

# Copy the frontend application code which was built by the frontend builder.
COPY --from=frontend-builder /usr/src/app/frontend/ /usr/src/app/frontend/
ENV EXTERNAL_SETTING_FRONTEND_SERVER_ENTRY_POINT=/usr/src/app/frontend/run-server.mjs
ENV EXTERNAL_SETTING_FRONTEND_STATIC_DIR=/usr/src/app/frontend/dist/client/

# Collect any static files
RUN \
  EXTERNAL_SETTING_SECRET_KEY=fake \
  EXTERNAL_SETTING_DATABASES={} \
  EXTERNAL_SETTING_SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=fake \
  EXTERNAL_SETTING_SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=fake \
  ./manage.py collectstatic --noinput

# We start a server on a port provided to us via the PORT environment variable.
ENV PORT=8000
ENTRYPOINT ["sh", "-c"]
CMD ["exec gunicorn \
  --name 'todolist' \
  --bind 0.0.0.0:$PORT \
  --worker-class gthread \
  --workers 4 --threads 1 \
  --log-level=info \
  --log-file=- \
  --access-logfile=- \
  --capture-output \
  project.wsgi" \
]
