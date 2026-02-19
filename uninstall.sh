#!/bin/bash
set -e

INSTALL_DIR="$HOME/.local"
BIN_DIR="$INSTALL_DIR/bin"
LIB_DIR="$INSTALL_DIR/lib/opentown"

rm -f "$BIN_DIR/ot"
rm -rf "$LIB_DIR"

echo "Uninstalled opentown"
