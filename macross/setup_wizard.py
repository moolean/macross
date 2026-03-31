from __future__ import annotations

import shutil
import subprocess

from .config import APP_NAME, CONFIG_DIR, CONFIG_FILE, DEFAULT_CONFIG, EXAMPLES_DIR, INVENTORY_FILE, DEFAULT_INVENTORY, ensure_dirs
from .utils import ask_yes_no, command_exists


class SetupWizard:
    def run(self) -> int:
        print(f"Welcome to {APP_NAME}.")
        print("We'll prepare your local Macross workspace.\n")
        self.ensure_dependencies()
        ensure_dirs()
        self.write_defaults()
        print(f"\n{APP_NAME} is ready.")
        print("\nNext steps:")
        print("  mx add-host   # add your first machine")
        print("  mx doctor     # check your environment")
        print("  mx            # start the shell once you have hosts")
        return 0

    def ensure_dependencies(self) -> None:
        if not command_exists("python3"):
            raise SystemExit("python3 is required. Please install Python 3 first.")
        if not command_exists("ssh"):
            raise SystemExit("ssh is required. Please install OpenSSH first.")
        if not command_exists("ansible"):
            print("ansible not found.")
            if ask_yes_no("Install ansible with Homebrew now?", default=True):
                result = subprocess.run(["brew", "install", "ansible"], text=True)
                if result.returncode != 0 or not command_exists("ansible"):
                    print("\nAutomatic install failed.")
                    print("Run:")
                    print("  brew install ansible")
            else:
                print("You can install it later with:")
                print("  brew install ansible")

    def write_defaults(self) -> None:
        if not CONFIG_FILE.exists():
            CONFIG_FILE.write_text(DEFAULT_CONFIG, encoding="utf-8")
        if not INVENTORY_FILE.exists():
            INVENTORY_FILE.write_text(DEFAULT_INVENTORY, encoding="utf-8")
        example = EXAMPLES_DIR / "inventory.ini"
        if not example.exists():
            example.write_text(DEFAULT_INVENTORY, encoding="utf-8")
