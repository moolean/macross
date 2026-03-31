#!/usr/bin/env bash
set -euo pipefail

APP_NAME="Macross"
REPO_OWNER="moolean"
REPO_NAME="macross"
REPO_BRANCH="main"
INSTALL_DIR="$HOME/.local/share/macross"
BIN_DIR="$HOME/.local/bin"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: required command not found: $1" >&2
    exit 1
  fi
}

copy_repo_files() {
  local src="$1"
  cp "$src/README.md" "$TMP_DIR/"
  cp "$src/README.zh-CN.md" "$TMP_DIR/"
  cp "$src/LICENSE" "$TMP_DIR/"
  cp "$src/install.sh" "$TMP_DIR/"
  mkdir -p "$TMP_DIR/bin" "$TMP_DIR/macross"
  cp "$src/bin/mx" "$TMP_DIR/bin/"
  cp "$src/bin/macross" "$TMP_DIR/bin/"
  cp -R "$src/macross/." "$TMP_DIR/macross/"
}

fetch_remote_repo() {
  need_cmd curl
  need_cmd tar
  local archive_url="https://codeload.github.com/${REPO_OWNER}/${REPO_NAME}/tar.gz/refs/heads/${REPO_BRANCH}"
  local archive_path="$TMP_DIR/repo.tar.gz"
  curl -fsSL "$archive_url" -o "$archive_path"
  tar -xzf "$archive_path" -C "$TMP_DIR"
  local extracted="$TMP_DIR/${REPO_NAME}-${REPO_BRANCH}"
  if [ ! -d "$extracted" ]; then
    echo "Error: failed to unpack repository archive." >&2
    exit 1
  fi
  copy_repo_files "$extracted"
}

local_repo_dir() {
  local source="${BASH_SOURCE[0]:-}"
  if [ -z "$source" ]; then
    return 1
  fi
  if [ ! -e "$source" ]; then
    return 1
  fi
  if [ "$(basename "$source")" != "install.sh" ]; then
    return 1
  fi
  local dir
  dir="$(cd "$(dirname "$source")" && pwd)"
  if [ -f "$dir/README.md" ] && [ -d "$dir/macross" ] && [ -f "$dir/bin/mx" ]; then
    printf '%s\n' "$dir"
    return 0
  fi
  return 1
}

main() {
  mkdir -p "$INSTALL_DIR" "$BIN_DIR"

  if repo_dir="$(local_repo_dir)"; then
    copy_repo_files "$repo_dir"
  else
    fetch_remote_repo
  fi

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
}

main "$@"
