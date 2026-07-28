import os


# Unit and integration tests use fixtures and deterministic fallbacks. External
# providers must never be enabled implicitly by a developer's local .env file.
os.environ["GEMINI_ENABLED"] = "false"
