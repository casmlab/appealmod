#!/bin/bash

exec python3 core/bin/run_recent_convs.py &
exec python3 core/bin/run_started_convs.py
