"""
Authentication module — phone + OTP login, user profile storage.
OTPs are simulated (printed to terminal) since no SMS gateway is configured.
"""
import json
import random
import time
import hashlib
from pathlib import Path

USERS_FILE = Path(__file__).parent.parent.parent / "data" / "users.json"


def _load_users() -> dict:
    if USERS_FILE.exists():
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}


def _save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def generate_otp(phone: str) -> str:
    """Generate a 6-digit OTP and store it against the phone number."""
    otp = str(random.randint(100000, 999999))
    users = _load_users()
    if phone not in users:
        users[phone] = {"phone": phone, "name": "", "role": "", "otp": otp, "otp_time": time.time(), "verified": False}
    else:
        users[phone]["otp"] = otp
        users[phone]["otp_time"] = time.time()
        users[phone]["verified"] = False
    _save_users(users)
    # In production, send via SMS. Here we print to terminal.
    print(f"\n{'='*40}")
    print(f"  OTP for {phone}: {otp}")
    print(f"{'='*40}\n")
    return otp  # returned so Streamlit can show it in dev mode


def verify_otp(phone: str, entered_otp: str) -> bool:
    """Verify OTP — valid for 5 minutes."""
    users = _load_users()
    if phone not in users:
        return False
    user = users[phone]
    if str(user.get("otp")) != str(entered_otp).strip():
        return False
    if time.time() - user.get("otp_time", 0) > 300:  # 5 min expiry
        return False
    users[phone]["verified"] = True
    _save_users(users)
    return True


def register_user(phone: str, name: str, role: str):
    """Save user profile after successful OTP verification."""
    users = _load_users()
    if phone in users:
        users[phone]["name"] = name
        users[phone]["role"] = role
    _save_users(users)


def get_user(phone: str) -> dict:
    users = _load_users()
    return users.get(phone, {})


def is_registered(phone: str) -> bool:
    user = get_user(phone)
    return bool(user.get("name") and user.get("role"))


def save_farmer_submission(phone: str, submission: dict):
    """Save a farmer's land valuation record."""
    users = _load_users()
    if phone in users:
        if "submissions" not in users[phone]:
            users[phone]["submissions"] = []
        submission["timestamp"] = time.strftime("%Y-%m-%d %H:%M")
        users[phone]["submissions"].append(submission)
        _save_users(users)


def get_farmer_submissions(phone: str) -> list:
    user = get_user(phone)
    return user.get("submissions", [])
