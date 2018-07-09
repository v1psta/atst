# test_functions.inc.sh: Functions used by the run_test script

run_python_lint() {
  local python_files="${1}"
  run_command "pylint ${python_files}"
  return $?
}

run_python_static_analysis() {
  local python_files="${1}"
  run_command "bandit -c ./.bandit_config -r ${python_files}"
  return $?
}

run_python_unit_tests() {
  run_command "python -m pytest -s"
  return $?
}
