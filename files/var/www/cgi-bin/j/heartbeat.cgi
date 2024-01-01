#!/bin/sh
# shellcheck disable=SC2039

vendor=$(ipcinfo --vendor)

soc_temp=$(ipcinfo --temp 2>/dev/null)
if [ -n "$soc_temp" ]; then
	soc_temp="${soc_temp}°C"
else
	soc_temp=""
fi

case "$vendor" in
	ingenic)
		daynight_value=$(imp-control.sh gettotalgain)
		;;
	sigmastar)
		echo 2 >/sys/devices/virtual/mstar/sar/channel
		daynight_value=$(cat /sys/devices/virtual/mstar/sar/value)
		;;
	*)
		daynight_value=-1
		;;
esac

mem_total=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
mem_free=$(awk '/MemFree/ {print $2}' /proc/meminfo)
mem_used=$(( 100 - (mem_free / (mem_total / 100)) ))
overlay_used=$(df | grep /overlay | xargs | cut -d' ' -f5)
payload=$(printf '{"soc_temp":"%s","time_now":"%s","timezone":"%s","mem_used":"%d","overlay_used":"%d","daynight_value":"%d"}' \
 	"$soc_temp" "$(date +%s)" "$(cat /etc/timezone)" "$mem_used" "${overlay_used//%/}" "$daynight_value")

echo "HTTP/1.1 200 OK
Content-type: application/json
Pragma: no-cache
Expires: $(TZ=GMT0 date +'%a, %d %b %Y %T %Z')
Etag: \"$(cat /proc/sys/kernel/random/uuid)\"

${payload}
"
