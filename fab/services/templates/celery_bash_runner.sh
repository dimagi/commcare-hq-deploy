# Catch any TERM or INT signals and propagate
# to the Celery process. Upon catching of the signal
# the 'wait' command below will terminate and thus will
# exit the bash process.
#
# > When Bash is waiting for an asynchronous command via the wait
# > built-in, the reception of a signal for which a trap has
# > been set will cause the wait built-in to return immediately
# > with an exit status greater than 128, immediately after which
# > the trap is executed.
#
# See Section 12.2.2 of http://tldp.org/LDP/Bash-Beginners-Guide/html/sect_12_02.html
#
# Effectively we've orphaned
# the Celery process to do a warm shutdown and we are
# free to start another bash process under supervisor.
trap 'echo "Killing: $PID"; kill -TERM $PID; echo "Killed: $PID";' TERM INT

HOSTNAME=""
ARGS=""
for i in "$@"
do
    case $i in
        # Note this pattern will break if we use --hostname <hostname> (no = sign)
        # because $@ space separates arguments
        --hostname=*|-n=*)
        HOSTNAME="$1"
        shift 1
        ;;
        *)  # Default case
        ARGS+=" $1"
        shift 1
        ;;
esac
done

TIMESTAMP=`date +%s`
HOSTNAME+=".${TIMESTAMP}_timestamp"
{{ new_relic_command }}{{ virtualenv_current }}/bin/python {{ code_current }}/manage.py celery worker ${HOSTNAME} ${ARGS}  &
PID=$!
BASH_PID=$$
echo "Started ${HOSTNAME} on PID: ${PID}"
wait $PID
echo "Exiting Bash Process: ${BASH_PID}"