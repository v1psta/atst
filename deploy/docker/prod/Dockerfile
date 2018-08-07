FROM python:3.6.5-alpine

### Very low chance of changing
###############################
# Overridable default config
ARG APP_USER=atst
ARG APP_GROUP=atat
ARG APP_DIR=/opt/atat/atst
ARG APP_PORT=8000
ARG SITE_PACKAGES_DIR=/usr/local/lib/python3.6/site-packages

ENV APP_USER "${APP_USER}"
ENV APP_GROUP "${APP_GROUP}"
ENV APP_DIR "${APP_DIR}"
ENV SKIP_PIPENV true

# Set port to open
EXPOSE "${APP_PORT}"

# Use dumb-init for proper signal handling
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Default command is to launch the server
CMD ["bash", "-c", "${APP_DIR}/script/uwsgi_server"]

### Items that will change almost every build
#############################################
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
  for subdir in $(find . -type d -maxdepth 1 | grep -Ee '.[^/]' | grep -Fve 'node_modules'); do chown atst:atat -R ${subdir}; done

# Run as the unprivileged APP user
USER "${APP_USER}"
