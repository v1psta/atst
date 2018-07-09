#!/bin/sh

# alpine_setup_functions: Functions used by the run_alpine_setup script

update_system_packages() {
  apk update
  apk upgrade
}

install_package() {
  local package_name=${1}

  apk add ${1}
  return $?
}

add_group() {
  local group_name="${1}"
  local gid="${2}"

  addgroup -g "${gid}" -S "${group_name}"
  return $?
}

add_user() {
  local username="${1}"
  local primary_group="${2}"
  local uid="${3}"

  adduser -u "${3}" -D -S -G "${primary_group}" "${username}"
  return $?
}
