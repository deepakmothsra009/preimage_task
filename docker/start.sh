cp docker/supervisord.conf /etc/supervisor/conf.d/
supervisord -c /etc/supervisor/supervisord.conf
python3 /preimage_task/db_helper.py
declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env
tail -f /dev/null
