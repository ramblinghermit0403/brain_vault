import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from pydantic_settings import BaseSettings, SettingsConfigDict
# We need BASE_DIR. Let's replicate what config.py does.
# config.py: BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# But __file__ here is verify_settings.py in backend.
# config.py is in backend/app/core/config.py
# So config.py's BASE_DIR points to backend directory.
# Let's assume backend is current dir.
BASE_DIR = os.getcwd()
env_path = os.path.join(BASE_DIR, ".env")

print(f"Base Dir: {BASE_DIR}")
print(f"Env Path: {env_path}")
print(f"Exists: {os.path.exists(env_path)}")

class TestSettings(BaseSettings):
    GEMINI_API_KEY: str | None = None
    model_config = SettingsConfigDict(env_file=env_path, extra='ignore')

try:
    t = TestSettings()
    print(f"Test GEMINI: {'Set' if t.GEMINI_API_KEY else 'Unset'}")
    print(f"Value (len): {len(t.GEMINI_API_KEY) if t.GEMINI_API_KEY else 0}")
except Exception as e:
    print(f"Error: {e}")
