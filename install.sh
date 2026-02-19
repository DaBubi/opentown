#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local"
BIN_DIR="$INSTALL_DIR/bin"

mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/ot" << 'WRAPPER'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$(dirname "$SCRIPT_DIR")/lib/opentown"
exec python3 "$LIB_DIR/cli.py" "$@"
WRAPPER
chmod +x "$BIN_DIR/ot"

pip install --target="$INSTALL_DIR/lib/opentown" "$SCRIPT_DIR" -q

echo "Installed ot to $BIN_DIR/ot"
echo "Make sure $BIN_DIR is in your PATH"
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "Add to PATH: export PATH=\"\$PATH:$BIN_DIR\""
fi
