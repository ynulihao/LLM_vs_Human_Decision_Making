#!/bin/bash

PIDS=$(ps aux | grep otree | grep -v grep | awk '{print $2}' | tr '\n' ' ')

if [ -n "$PIDS" ]; then
  echo "Found otree processes: $PIDS"
  echo "Attempting to kill otree processes..."

  SUCCESS_COUNT=0
  FAILURE_COUNT=0

  for PID in $PIDS; do
    kill $PID 2>/tmp/kill_otree_error.log
    if [ $? -eq 0 ]; then
      echo "Successfully killed process $PID"
      SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
      echo "Failed to kill process $PID. Check /tmp/kill_otree_error.log for details."
      FAILURE_COUNT=$((FAILURE_COUNT + 1))
    fi
  done

  echo "Summary: Successfully killed $SUCCESS_COUNT processes. Failed to kill $FAILURE_COUNT processes."

else
  echo "No otree processes found."
fi
