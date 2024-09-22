#!/bin/bash

exec python3 bot/bin/run_recent_convs.py &
exec python3 bot/bin/run_started_convs.py
