#!/bin/sh
commit_msg_file=$1
commit_msg=$(head -n1 "$commit_msg_file")

pattern='^(FEAT|FIX|DOC|CHORE|TEST|REFACTOR): .+'

if ! echo "$commit_msg" | grep -qE "$pattern"; then
  echo "❌ Error: Commit message must start with one of these prefixes: FEAT:, FIX:, DOC:, CHORE:, TEST:, REFACTOR:"
  exit 1
fi
