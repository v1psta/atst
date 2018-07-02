FROM atat-app-builder-builder:latest as app-builder

ARG APP_USER=atst
ARG APP_GROUP=atat
ARG APP_DIR=/opt/atat/atst
ARG CIBUILD=true

ENV SKIP_PIPENV true

# Create application directory
RUN set -x ; \
  mkdir -p ${APP_DIR}

# Set working dir
WORKDIR ${APP_DIR}

# Copy app and module files
COPY . .

# Add required system packages and app user
RUN set -x ; \
  script/alpine_setup "${APP_USER}" "${APP_GROUP}"

# Install app dependencies
RUN set -x ; \
  script/setup

# Use dumb-init for proper signal handling
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Default command is to run all the tests
CMD ["${APP_DIR}/script/cibuild"]
