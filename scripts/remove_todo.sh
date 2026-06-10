#!/usr/bin/env bash
if [ -f TODO.md ]; then
  rm TODO.md
  echo "TODO.md removed from working directory. Commit changes if desired."
else
  echo "TODO.md not found."
fi
