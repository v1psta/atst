FROM alpine:3.8

### Very low chance of changing
###############################
# Overridable default config
ARG APP_USER=atst
ARG APP_GROUP=atat
ARG APP_DIR=/opt/atat/atst
ARG APP_PORT=8000
ARG LOCAL_BIN_DIR=/usr/bin
ARG SITE_PACKAGES_DIR=/usr/lib/python3.6/site-packages

ENV APP_USER "${APP_USER}"
ENV APP_GROUP "${APP_GROUP}"
ENV APP_DIR "${APP_DIR}"

# Set port to open
EXPOSE "${APP_PORT}"

# Use dumb-init for proper signal handling
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Default command is to launch the server
CMD ["bash", "-c", "crond -b && ${APP_DIR}/script/uwsgi_server"]

### Items that will change almost every build
#############################################
# Copy installed python packages from the tester image
COPY --from=atst-tester:latest "${SITE_PACKAGES_DIR}" "${SITE_PACKAGES_DIR}"

# Copy local bin directory (contains python system package wrappers)
COPY --from=atst-tester:latest "${LOCAL_BIN_DIR}" "${LOCAL_BIN_DIR}"

# Copy the app directory contents from the tester image (includes node modules)
COPY --from=atst-tester:latest "${APP_DIR}" "${APP_DIR}"

# Set working dir
WORKDIR ${APP_DIR}

# Add required system packages and app user
RUN set -x ; \
  script/alpine_setup "${APP_USER}" "${APP_GROUP}"

# add sync-crl cronjob for atst user
RUN echo "1 */6 * * * /opt/atat/atst/script/sync-crls tests/crl-tmp" >> /etc/crontabs/atst

# Update file ownership
RUN set -x ; \
  for subdir in $(find . -type d -maxdepth 1 | grep -Ee '.[^/]' | grep -Fve 'node_modules'); do chown atst:atat -R ${subdir}; done

# Run as the unprivileged APP user
USER "${APP_USER}"
