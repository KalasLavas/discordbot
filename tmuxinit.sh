#!/bin/sh

#python3 Space ~/discordbot-timezone/bot.py C-m

# set up tmux
tmux start-server

sleep 1
# - DISCORD -
# create new detached(-d) tmux session(-s)
tmux new-session -d -s "discordbot"
# send command
tmux send-keys -t "discordbot" "~/discordbot-timezone/botinit.sh" C-m

sleep 1
# - NGROK -
# create new detached(-d) tmux session(-s)
tmux new-session -d -s "ngrok"
# send command
tmux send-keys -t "ngrok" "ngrok tcp 22" C-m