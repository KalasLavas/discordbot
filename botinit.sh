#!/bin/sh

IP="8.8.8.8"

echo -n Waiting for internet connection. 

while true
do
	if ping -c 1 $IP > /dev/null 2>&1
	then
		break
	else
		echo -n .
	fi
done

echo !

cd ~/discordbot-timezone/

python3 bot.py