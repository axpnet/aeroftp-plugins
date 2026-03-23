#!/bin/bash
# File Hasher plugin for AeroFTP
# Reads JSON args from stdin, outputs JSON result

set -euo pipefail

INPUT=$(cat)
FILE=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('path',''))")
ALGO=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('algorithm','sha256'))")

if [ -z "$FILE" ]; then
    echo '{"error": "path parameter is required"}'
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "{\"error\": \"file not found: $FILE\"}"
    exit 1
fi

case "$ALGO" in
    md5)    HASH=$(md5sum "$FILE" | awk '{print $1}') ;;
    sha1)   HASH=$(sha1sum "$FILE" | awk '{print $1}') ;;
    sha256) HASH=$(sha256sum "$FILE" | awk '{print $1}') ;;
    sha512) HASH=$(sha512sum "$FILE" | awk '{print $1}') ;;
    *)      echo "{\"error\": \"unsupported algorithm: $ALGO\"}"; exit 1 ;;
esac

SIZE=$(stat --printf="%s" "$FILE" 2>/dev/null || stat -f "%z" "$FILE" 2>/dev/null)
NAME=$(basename "$FILE")

echo "{\"file\": \"$NAME\", \"algorithm\": \"$ALGO\", \"hash\": \"$HASH\", \"size\": $SIZE}"
