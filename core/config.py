"""
Secure Configuration & Credential Store.
Safely loads .env without leaking secrets into logs or console stdout.
"""
import os
from pathlib import Path
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        pass

# Search locations for .env
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_LOCATIONS = [
    PROJECT_ROOT / ".env",
    Path.home() / ".env"
]

_loaded = False
for env_path in ENV_LOCATIONS:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        _loaded = True
        break

class Config:
    @staticmethod
    def is_configured(var_name: str) -> bool:
        val = os.getenv(var_name, "").strip()
        return bool(val and not val.startswith("your_"))

    @staticmethod
    def get(var_name: str, default: str = "") -> str:
        return os.getenv(var_name, default)

    @classmethod
    def get_credential_status(cls) -> dict:
        """Returns boolean status of each platform credential (NEVER the actual value)."""
        return {
            "Gumroad": cls.is_configured("GUMROAD_ACCESS_TOKEN"),
            "Lemon Squeezy": cls.is_configured("LEMON_SQUEEZY_API_KEY") and cls.is_configured("LEMON_SQUEEZY_STORE_ID"),
            "Whop": cls.is_configured("WHOP_API_KEY"),
            "Payhip": cls.is_configured("PAYHIP_API_KEY"),
            "Custom Website": cls.is_configured("CUSTOM_STORE_ENDPOINT"),
            "Telegram Alerts": cls.is_configured("TELEGRAM_BOT_TOKEN"),
        }

if __name__ == "__main__":
    print("=" * 70)
    print(" CREDENTIAL STATUS OVERVIEW")
    print("=" * 70)
    status = Config.get_credential_status()
    for name, ok in status.items():
        state = "[CONFIGURED]" if ok else "[NOT SET]"
        print(f"  {name:<22}: {state}")
    print("=" * 70)
    print(f"Env file path: {PROJECT_ROOT / '.env'}")
    print("To configure, edit the .env file or copy from .env.example.")

