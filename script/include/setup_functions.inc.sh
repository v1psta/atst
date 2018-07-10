# setup_functions.inc.sh: Functions used by the setup script

install_pipenv() {
  return_code=0

  # Ensure we are not in a virtual env already
  if [ -z "${VIRTUAL_ENV+is_set}" ]; then
    if ! check_system_pip_for pipenv; then
      # pipenv is not installed, so install it
      echo "Installing pipenv..."
      pip install pipenv
      # Capture pip exit code
      return_code="${?}"
    fi
  fi

  return "${return_code}"
}

create_virtual_environment() {
  default_python_version=3.6
  # Parse out the required Python version from the Pipfile
  python_version=$(grep python_version ./Pipfile | cut -d '"' -f 2)

  # If we ended up with an empty string for the required Python version,
  # specify the default version
  if [ -z "${python_version}" ]; then
    python_version="${default_python_version}"
  fi

  # Create a new virtual environment for the app
  # The environment will be in a directory called .venv off the app
  # root directory
  echo "Creating virtual environment using Python version ${python_version}..."
  PIPENV_VENV_IN_PROJECT=true pipenv --python "${python_version}"
  return $?
}

install_sass() {
  if ! type sass >/dev/null; then
    if type gem >/dev/null; then
      echo 'Installing a sass compiler (gem)...'
      gem install sass
    else
      echo 'Could not install a sass compiler. Please install a version of sass.'
    fi
  fi
}
