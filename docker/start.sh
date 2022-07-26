cp docker/supervisord.conf /etc/supervisor/conf.d/
supervisord -c /etc/supervisor/supervisord.conf
declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env
tail -f /dev/null
