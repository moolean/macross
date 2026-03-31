#!/usr/bin/env bash
set -euo pipefail
APP_NAME="Macross"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/.local/share/macross"
BIN_DIR="$HOME/.local/bin"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

mkdir -p "$INSTALL_DIR" "$BIN_DIR"

cp "$REPO_DIR/README.md" "$TMP_DIR/"
cp "$REPO_DIR/README.zh-CN.md" "$TMP_DIR/"
cp "$REPO_DIR/LICENSE" "$TMP_DIR/"
cp "$REPO_DIR/install.sh" "$TMP_DIR/"
mkdir -p "$TMP_DIR/bin" "$TMP_DIR/macross"
cp "$REPO_DIR/bin/mx" "$TMP_DIR/bin/"
cp "$REPO_DIR/bin/macross" "$TMP_DIR/bin/"
cp -R "$REPO_DIR/macross/." "$TMP_DIR/macross/"

rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp -R "$TMP_DIR/." "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/install.sh" "$INSTALL_DIR/bin/mx" "$INSTALL_DIR/bin/macross"
ln -sf "$INSTALL_DIR/bin/mx" "$BIN_DIR/mx"
ln -sf "$INSTALL_DIR/bin/macross" "$BIN_DIR/macross"

printf '\n%s installed.\n' "$APP_NAME"
printf 'Commands:\n  %s\n  %s\n' "$BIN_DIR/mx" "$BIN_DIR/macross"
printf '\nIf %s is not on your PATH, add this to ~/.zshrc or ~/.bashrc:\n' "$BIN_DIR"
printf '  export PATH="$HOME/.local/bin:$PATH"\n\n'
printf 'Then run:\n  mx\n\n'
