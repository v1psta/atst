# get_db_settings: Reads postgres related settings from all of the relevant
#                  config files and then sets them as environment variables

# Load get_db_settings_functions functions
source ./script/include/get_db_settings_functions.inc.sh


# If an OVERRIDE config has been specified, and the file is present, 
# read those values first
if [ ! -z "${OVERRIDE_CONFIG_FULLPATH+is_not_set}" ] && 
   [ -f "${OVERRIDE_CONFIG_FULLPATH}" ]; then
    set_db_env_vars "${OVERRIDE_CONFIG_FULLPATH}"
fi

# If FLASK_ENV is set, and a config file exists for it,
# allow it to set anything not already defined
if [ "${FLASK_ENV}x" != "x" ]; then
    flask_env_config_file="./config/${FLASK_ENV}.ini"

    if [ -f "${flask_env_config_file}" ]; then
        set_db_env_vars "${flask_env_config_file}"
    fi
fi

# Finish with the base config file, setting anything that is still unset
set_db_env_vars "./config/base.ini"
