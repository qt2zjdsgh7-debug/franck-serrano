#!/usr/bin/env python3
"""
Upload Zervos sales agent files to iCloud Drive.
Usage: python upload_to_icloud.py --username your@apple.com
"""

import argparse
import getpass
import sys
from pathlib import Path

from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudFailedLoginException

FILES = [
    Path("zervos_sales_agent.md"),
    Path("zervos_sales_agent_prompt.pdf"),
]
ICLOUD_FOLDER = "Zervos"   # folder created in iCloud Drive root


def get_args():
    parser = argparse.ArgumentParser(description="Upload Zervos files to iCloud Drive")
    parser.add_argument("--username", "-u", required=True, help="Apple ID email")
    parser.add_argument("--password", "-p", default=None, help="Apple ID password (prompted if omitted)")
    return parser.parse_args()


def authenticate(username: str, password: str) -> PyiCloudService:
    print(f"Connecting to iCloud as {username} …")
    api = PyiCloudService(username, password)

    if api.requires_2fa:
        code = input("Two-factor code (from your Apple device): ").strip()
        result = api.validate_2fa_code(code)
        if not result:
            print("Invalid 2FA code.")
            sys.exit(1)
        if not api.is_trusted_session:
            api.trust_session()

    elif api.requires_2sa:
        devices = api.trusted_devices
        for i, dev in enumerate(devices):
            print(f"  [{i}] {dev.get('deviceName', 'Unknown device')}")
        idx = int(input("Select device: "))
        device = devices[idx]
        if not api.send_verification_code(device):
            print("Failed to send code.")
            sys.exit(1)
        code = input("Verification code: ").strip()
        if not api.validate_verification_code(device, code):
            print("Invalid code.")
            sys.exit(1)

    return api


def ensure_folder(drive_root, folder_name: str):
    """Return the iCloud Drive folder, creating it if needed."""
    try:
        return drive_root[folder_name]
    except KeyError:
        drive_root.mkdir(folder_name)
        return drive_root[folder_name]


def upload_files(api: PyiCloudService):
    drive = api.drive
    folder = ensure_folder(drive.root, ICLOUD_FOLDER)
    print(f"Uploading to iCloud Drive / {ICLOUD_FOLDER} /")

    for path in FILES:
        if not path.exists():
            print(f"  [SKIP] {path.name} — file not found locally")
            continue
        with open(path, "rb") as fh:
            folder.upload(fh)
        print(f"  [OK]   {path.name}")

    print("\nDone. Open the Files app on iPhone/iPad or Finder on Mac")
    print(f"→ iCloud Drive / {ICLOUD_FOLDER} /")


def main():
    args = get_args()
    password = args.password or getpass.getpass("Apple ID password: ")

    try:
        api = authenticate(args.username, password)
    except PyiCloudFailedLoginException:
        print("Login failed — check your Apple ID and password.")
        sys.exit(1)

    upload_files(api)


if __name__ == "__main__":
    main()
