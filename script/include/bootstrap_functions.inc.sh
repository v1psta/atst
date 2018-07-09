# bootstrap_functions.inc.sh: Functions used by the bootstrap script

install_python_packages() {
  local install_flags="${1}"
  pipenv install ${install_flags}
  return $?
}

install_node_packages() {
  npm install
  return $?
}
