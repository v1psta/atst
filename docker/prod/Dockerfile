FROM python:3.6.5-alpine

# Overridable default config
ARG APP_USER=atst
ARG APP_GROUP=atat
ARG APP_DIR=/opt/atat/atst
ARG APP_PORT=8000
ARG SITE_PACKAGES_DIR=/usr/local/lib/python3.6/site-packages

ENV APP_DIR "${APP_DIR}"
ENV SKIP_PIPENV true

# Copy installed python packages from the tester image
COPY --from=atst-tester:latest "${SITE_PACKAGES_DIR}" "${SITE_PACKAGES_DIR}"

# Copy the app directory contents from the tester image (includes node modules)
COPY --from=atst-tester:latest "${APP_DIR}" "${APP_DIR}"

# Set working dir
WORKDIR ${APP_DIR}

# Add required system packages and app user
RUN set -x ; \
  script/alpine_setup "${APP_USER}" "${APP_GROUP}"

# Update file ownership
RUN set -x ; \
  chown -R atst:atat "${APP_DIR}"

# Set port to open
EXPOSE "${APP_PORT}"

# Run as the unprivileged APP user
USER "${APP_USER}"

# Use dumb-init for proper signal handling
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Default command is to launch the server
CMD ["bash", "-c", "${APP_DIR}/script/server"]
