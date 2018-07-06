#!/bin/bash

# helper_functions.inc.sh: General helper functions

# Check pip to see if the given package is installed
# (returns 0 if installed, 2 if not installed)
check_pip_for () {
  return $(pip list --format=columns --disable-pip-version-check | \
	  grep -Fe "${1}" >/dev/null 2>&1)
}
