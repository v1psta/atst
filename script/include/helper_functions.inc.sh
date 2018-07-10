# helper_functions.inc.sh: General helper functions

# Check pip to see if the given package is installed
# (returns 0 if installed, 2 if not installed)
check_system_pip_for () {
  local package_name="${1}"

  # Use 'pip list' to see if the requested package is already installed
  pip list --format=columns --disable-pip-version-check | \
    grep -Fe "${package_name}" >/dev/null 2>&1
  return $?
}

# Used whenever an environment sensitive command is being run
run_command () {
  local cmd="${1}"

  pipenv run ${cmd}
  return $?
}
