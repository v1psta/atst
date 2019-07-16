# dev_server_functions.inc.sh: Functions used by the dev_server script

# Used to ensure a SIGTERM is sent to all process in the current process group
reap() {
   kill -s SIGTERM -- "-$$"
   sleep 0.1
   exit
}
