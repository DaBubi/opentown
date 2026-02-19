#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local"
BIN_DIR="$INSTALL_DIR/bin"
LIB_DIR="$INSTALL_DIR/lib/opentown"

mkdir -p "$BIN_DIR"
rm -rf "$LIB_DIR"
cp -r "$SCRIPT_DIR/opentown" "$LIB_DIR"

cat > "$BIN_DIR/ot" << EOF
#!/bin/bash
exec python3 "$LIB_DIR/cli.py" "\$@"
EOF
chmod +x "$BIN_DIR/ot"

echo "Installed ot to $BIN_DIR/ot"
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "Add to PATH: export PATH=\"\$PATH:$BIN_DIR\""
fi
