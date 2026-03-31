#!/usr/bin/env bash
set -euo pipefail
APP_NAME="Macross"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/.local/share/macross"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR" "$BIN_DIR"
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp -R "$REPO_DIR"/* "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/bin/mx" "$INSTALL_DIR/bin/macross"
ln -sf "$INSTALL_DIR/bin/mx" "$BIN_DIR/mx"
ln -sf "$INSTALL_DIR/bin/macross" "$BIN_DIR/macross"
printf '\n%s installed.\n' "$APP_NAME"
printf 'Commands:\n  %s\n  %s\n' "$BIN_DIR/mx" "$BIN_DIR/macross"
printf '\nIf %s is not on your PATH, add this to ~/.zshrc or ~/.bashrc:\n' "$BIN_DIR"
printf '  export PATH="$HOME/.local/bin:$PATH"\n\n'
