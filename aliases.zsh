# mac_fleet aliases
export MAC_FLEET_DIR="$HOME/Documents/workspace/mac_fleet"

mf='cd "$MAC_FLEET_DIR"'
alias mfc='cd "$MAC_FLEET_DIR"'
alias mfp='cd "$MAC_FLEET_DIR" && ansible all -m ping'
alias mfh='cd "$MAC_FLEET_DIR" && ansible all -a "hostname"'
alias mfu='cd "$MAC_FLEET_DIR" && ansible all -a "uptime"'
alias mfd='cd "$MAC_FLEET_DIR" && ansible all -a "df -h /"'
alias mfv='cd "$MAC_FLEET_DIR" && ansible all -a "sw_vers"'
alias mfw='cd "$MAC_FLEET_DIR" && ansible all -a "whoami"'
alias mfls='cd "$MAC_FLEET_DIR" && ansible all -a "ls"'
alias mfsync='cd "$MAC_FLEET_DIR" && ansible all -m shell -a "mkdir -p ~/test_sync"'
alias mfcat='cd "$MAC_FLEET_DIR" && ansible all -m shell -a "cat ~/test_sync/hello.txt"'
alias mfinv='cd "$MAC_FLEET_DIR" && cat inventory.ini'
alias fleet='$MAC_FLEET_DIR/bin/fleet'
alias mx='$MAC_FLEET_DIR/bin/mx'
alias macross='$MAC_FLEET_DIR/bin/macross'

mfrun() {
  cd "$MAC_FLEET_DIR" || return 1
  ansible all -m shell -a "$*"
}

mfcmd() {
  cd "$MAC_FLEET_DIR" || return 1
  ansible all -a "$*"
}

mfcopy() {
  if [ "$#" -ne 2 ]; then
    echo "用法: mfcopy <本地文件> <远程绝对路径>"
    return 1
  fi
  cd "$MAC_FLEET_DIR" || return 1
  ansible all -m copy -a "src=$1 dest=$2"
}

mfplay() {
  cd "$MAC_FLEET_DIR" || return 1
  ansible-playbook "$@"
}
