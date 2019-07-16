# set_db_env_vars.inc.sh: Functions used by the set_db_env_vars script

set_db_env_vars () {
    local config_file="${1}"

    # Read in and export all name=value pairs where the name starts with PG
    # unless we already have an env var with that value
    # (NOTE: all whitespaces are removed from each line)
    while read -r DBVAR
    do
	if ! $(env | grep -qFle "${DBVAR%%=*}"); then
            eval "export ${DBVAR}"
	fi
    done < <(grep -Ee '^PG' "${config_file}" | sed 's/ //g')
}
