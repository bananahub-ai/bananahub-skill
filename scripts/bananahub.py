#!/usr/bin/env python3
"""BananaHub - Gemini image generation CLI tool."""

import argparse
import base64
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib import error as urlerror, request as urlrequest
from urllib.parse import urlparse, urlunparse
from uuid import uuid4


def load_dotenv(env_path):
    """Parse a .env file into a dict."""
    config = {}
    if not env_path.exists():
        return config
    for line in env_path.read_text().strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()
    return config


SKILL_CONFIG_DIR = Path.home() / ".config" / "bananahub"
SKILL_CONFIG_PATH = SKILL_CONFIG_DIR / "config.json"
TELEMETRY_STATE_PATH = SKILL_CONFIG_DIR / "telemetry.json"
HUB_API_BASE = os.environ.get("BANANAHUB_HUB_API", "https://worker.bananahub.ai/api")
DEFAULT_TEMPLATE_REPO = "bananahub-ai/bananahub-skill"
VALID_TEMPLATE_DISTRIBUTIONS = {"bundled", "remote"}
VALID_CATALOG_SOURCES = {"curated", "discovered"}
VALID_TELEMETRY_EVENTS = {"selected", "generate_success", "edit_success"}

PROVIDER_GOOGLE_AI_STUDIO = "google-ai-studio"
PROVIDER_GEMINI_COMPATIBLE = "gemini-compatible"
PROVIDER_VERTEX_AI = "vertex-ai"
PROVIDER_OPENAI_COMPATIBLE = "openai-compatible"
SUPPORTED_PROVIDERS = {
    PROVIDER_GOOGLE_AI_STUDIO,
    PROVIDER_GEMINI_COMPATIBLE,
    PROVIDER_VERTEX_AI,
    PROVIDER_OPENAI_COMPATIBLE,
}
SUPPORTED_RUNTIME_PROVIDERS = {
    PROVIDER_GOOGLE_AI_STUDIO,
    PROVIDER_GEMINI_COMPATIBLE,
    PROVIDER_VERTEX_AI,
    PROVIDER_OPENAI_COMPATIBLE,
}
DEFAULT_PROVIDER = PROVIDER_GOOGLE_AI_STUDIO
DEFAULT_LOCATION = "global"

TRANSPORT_GENAI = "genai"
TRANSPORT_GEMINI_REST = "gemini-rest"
TRANSPORT_OPENAI_REST = "openai-rest"
SUPPORTED_TRANSPORTS = {
    TRANSPORT_GENAI,
    TRANSPORT_GEMINI_REST,
    TRANSPORT_OPENAI_REST,
}

AUTH_MODE_API_KEY = "api_key"
AUTH_MODE_ADC = "adc"
SUPPORTED_AUTH_MODES = {AUTH_MODE_API_KEY, AUTH_MODE_ADC}

PROVIDER_ALIASES = {
    "google": PROVIDER_GOOGLE_AI_STUDIO,
    "google-ai": PROVIDER_GOOGLE_AI_STUDIO,
    "google-ai-studio": PROVIDER_GOOGLE_AI_STUDIO,
    "ai-studio": PROVIDER_GOOGLE_AI_STUDIO,
    "gemini-developer-api": PROVIDER_GOOGLE_AI_STUDIO,
    "developer-api": PROVIDER_GOOGLE_AI_STUDIO,
    "gemini-compatible": PROVIDER_GEMINI_COMPATIBLE,
    "compatible": PROVIDER_GEMINI_COMPATIBLE,
    "proxy": PROVIDER_GEMINI_COMPATIBLE,
    "relay": PROVIDER_GEMINI_COMPATIBLE,
    "custom-endpoint": PROVIDER_GEMINI_COMPATIBLE,
    "vertex": PROVIDER_VERTEX_AI,
    "vertex-ai": PROVIDER_VERTEX_AI,
    "openai": PROVIDER_OPENAI_COMPATIBLE,
    "openai-compatible": PROVIDER_OPENAI_COMPATIBLE,
}
TRANSPORT_ALIASES = {
    "genai": TRANSPORT_GENAI,
    "gemini": TRANSPORT_GEMINI_REST,
    "gemini-rest": TRANSPORT_GEMINI_REST,
    "openai": TRANSPORT_OPENAI_REST,
    "openai-rest": TRANSPORT_OPENAI_REST,
}
AUTH_MODE_ALIASES = {
    "api_key": AUTH_MODE_API_KEY,
    "apikey": AUTH_MODE_API_KEY,
    "key": AUTH_MODE_API_KEY,
    "adc": AUTH_MODE_ADC,
}
DEFAULT_TRANSPORT_BY_PROVIDER = {
    PROVIDER_GOOGLE_AI_STUDIO: TRANSPORT_GENAI,
    PROVIDER_GEMINI_COMPATIBLE: TRANSPORT_GENAI,
    PROVIDER_VERTEX_AI: TRANSPORT_GENAI,
    PROVIDER_OPENAI_COMPATIBLE: TRANSPORT_OPENAI_REST,
}

# Mapping from config.json keys to internal config keys
CONFIG_KEY_MAP = {
    "provider": "BANANAHUB_PROVIDER",
    "transport": "BANANAHUB_TRANSPORT",
    "auth_mode": "BANANAHUB_AUTH_MODE",
    "api_key": "GEMINI_API_KEY",
    "google_api_key": "GEMINI_API_KEY",
    "gemini_api_key": "GEMINI_API_KEY",
    "base_url": "GOOGLE_GEMINI_BASE_URL",
    "gemini_base_url": "GOOGLE_GEMINI_BASE_URL",
    "project": "GOOGLE_CLOUD_PROJECT",
    "location": "GOOGLE_CLOUD_LOCATION",
    "model": "BANANAHUB_MODEL",
    "use_vertexai": "GOOGLE_GENAI_USE_VERTEXAI",
}

ENV_KEY_ALIASES = {
    "BANANAHUB_PROVIDER": ("BANANAHUB_PROVIDER",),
    "BANANAHUB_TRANSPORT": ("BANANAHUB_TRANSPORT",),
    "BANANAHUB_AUTH_MODE": ("BANANAHUB_AUTH_MODE",),
    "BANANAHUB_MODEL": ("BANANAHUB_MODEL",),
    "GEMINI_API_KEY": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    "GOOGLE_GEMINI_BASE_URL": (
        "GOOGLE_GEMINI_BASE_URL",
        "GEMINI_BASE_URL",
        "BANANAHUB_BASE_URL",
    ),
    "GOOGLE_CLOUD_PROJECT": ("GOOGLE_CLOUD_PROJECT",),
    "GOOGLE_CLOUD_LOCATION": ("GOOGLE_CLOUD_LOCATION", "GOOGLE_CLOUD_REGION"),
    "GOOGLE_GENAI_USE_VERTEXAI": ("GOOGLE_GENAI_USE_VERTEXAI",),
}

def _mask_secret(value):
    """Return a masked representation for API keys."""
    if not value:
        return ""
    if len(value) <= 12:
        return "***"
    return value[:8] + "..." + value[-4:]


def _normalize_base_url(value):
    """Normalize a custom base URL for Gemini-compatible endpoints."""
    if value is None:
        return None

    normalized = str(value).strip()
    if not normalized:
        return None
    if not re.match(r"^https?://", normalized):
        raise ValueError("base_url must start with http:// or https://")

    return normalized.rstrip("/")


def _split_trailing_api_version(base_url, default_api_version="v1beta"):
    """Split a trailing API version suffix from a base URL when present."""
    normalized = _normalize_base_url(base_url)
    if not normalized:
        return None, default_api_version, False

    parsed = urlparse(normalized)
    path = parsed.path.rstrip("/")
    match = re.search(r"/(v\d+(?:beta\d*|alpha\d*)?)$", path)
    if not match:
        return normalized, default_api_version, False

    api_version = match.group(1)
    base_path = path[: -(len(api_version) + 1)]
    rebuilt = urlunparse(parsed._replace(path=base_path))
    return rebuilt.rstrip("/"), api_version, True


def _resolve_genai_endpoint(base_url):
    """Resolve a Gemini-style endpoint into base_url + api_version parts."""
    if not base_url:
        return {
            "configured_base_url": None,
            "resolved_base_url": None,
            "api_version": "v1beta",
            "warnings": [],
        }

    resolved_base_url, api_version, stripped_version = _split_trailing_api_version(base_url)
    warnings = []
    if stripped_version:
        warnings.append(
            f"Detected trailing `/{api_version}` in base_url and normalized it to avoid duplicating the API version."
        )

    return {
        "configured_base_url": _normalize_base_url(base_url),
        "resolved_base_url": resolved_base_url,
        "api_version": api_version,
        "warnings": warnings,
    }


def _resolve_openai_endpoint(base_url):
    """Resolve an OpenAI-compatible endpoint into the URL used by runtime calls."""
    configured = _normalize_base_url(base_url)
    parsed = urlparse(configured)
    path = parsed.path.rstrip("/")
    warnings = []

    if parsed.netloc == "generativelanguage.googleapis.com":
        if path in {"", "/v1beta", "/v1beta1", "/v1"}:
            suffix = "/v1beta/openai"
            warnings.append("Expanded the official Gemini OpenAI-compatible endpoint to `/v1beta/openai`.")
        elif path == "/openai":
            suffix = "/v1beta/openai"
            warnings.append("Expanded `/openai` to the official Gemini path `/v1beta/openai`.")
        else:
            suffix = path or "/v1beta/openai"
        resolved = urlunparse(parsed._replace(path=suffix))
        return {
            "configured_base_url": configured,
            "resolved_base_url": resolved.rstrip("/"),
            "warnings": warnings,
        }

    if path in {"", "/"}:
        resolved = urlunparse(parsed._replace(path="/v1"))
        warnings.append("Appended `/v1` to the OpenAI-compatible base_url.")
        return {
            "configured_base_url": configured,
            "resolved_base_url": resolved.rstrip("/"),
            "warnings": warnings,
        }

    if path == "/openai":
        resolved = urlunparse(parsed._replace(path="/openai/v1"))
        warnings.append("Appended `/v1` to the OpenAI-compatible `/openai` base_url.")
        return {
            "configured_base_url": configured,
            "resolved_base_url": resolved.rstrip("/"),
            "warnings": warnings,
        }

    return {
        "configured_base_url": configured,
        "resolved_base_url": configured,
        "warnings": warnings,
    }


def _normalize_provider(value):
    """Normalize provider ids accepted by BananaHub config."""
    if value is None:
        return None

    normalized = str(value).strip().lower()
    if not normalized:
        return None
    normalized = PROVIDER_ALIASES.get(normalized, normalized)
    if normalized not in SUPPORTED_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
        raise ValueError(f"provider must be one of: {supported}")
    return normalized


def _normalize_transport(value):
    """Normalize transport ids accepted by BananaHub config."""
    if value is None:
        return None

    normalized = str(value).strip().lower()
    if not normalized:
        return None
    normalized = TRANSPORT_ALIASES.get(normalized, normalized)
    if normalized not in SUPPORTED_TRANSPORTS:
        supported = ", ".join(sorted(SUPPORTED_TRANSPORTS))
        raise ValueError(f"transport must be one of: {supported}")
    return normalized


def _normalize_auth_mode(value):
    """Normalize auth-mode values accepted by BananaHub config."""
    if value is None:
        return None

    normalized = str(value).strip().lower()
    if not normalized:
        return None
    normalized = AUTH_MODE_ALIASES.get(normalized, normalized)
    if normalized not in SUPPORTED_AUTH_MODES:
        supported = ", ".join(sorted(SUPPORTED_AUTH_MODES))
        raise ValueError(f"auth_mode must be one of: {supported}")
    return normalized


def _normalize_model(value):
    """Normalize optional default model ids."""
    if value is None:
        return None

    normalized = str(value).strip()
    if not normalized:
        return None
    return _canonicalize_model(normalized)


def _is_truthy(value):
    """Return True for common truthy env/config values."""
    normalized = str(value or "").strip().lower()
    return normalized in {"1", "true", "yes", "on"}


def _normalize_config_value(env_key, value):
    """Normalize raw config values based on the canonical internal key."""
    if env_key == "GOOGLE_GEMINI_BASE_URL":
        return _normalize_base_url(value)
    if env_key == "BANANAHUB_PROVIDER":
        return _normalize_provider(value)
    if env_key == "BANANAHUB_TRANSPORT":
        return _normalize_transport(value)
    if env_key == "BANANAHUB_AUTH_MODE":
        return _normalize_auth_mode(value)
    if env_key == "BANANAHUB_MODEL":
        return _normalize_model(value)
    if env_key == "GOOGLE_GENAI_USE_VERTEXAI":
        return "true" if _is_truthy(value) else None

    normalized = str(value).strip()
    if not normalized:
        return None
    return normalized


def _read_json_file(path, required=False):
    """Read a JSON file and return a dict."""
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        if required:
            raise ValueError(f"Invalid JSON config: {exc}") from exc
        return {}

    if not isinstance(data, dict):
        if required:
            raise ValueError(f"Invalid JSON config: expected object at {path}")
        return {}

    return data


def _write_json_file(path, data):
    """Write JSON with stable formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def _normalize_template_repo(value):
    """Normalize template repo values."""
    normalized = str(value or "").strip()
    if not normalized or "/" not in normalized:
        return DEFAULT_TEMPLATE_REPO
    return normalized


def _normalize_template_distribution(value):
    """Normalize bundled vs remote template distribution values."""
    normalized = str(value or "").strip().lower()
    if not normalized:
        return ""
    if normalized not in VALID_TEMPLATE_DISTRIBUTIONS:
        raise ValueError("template distribution must be bundled or remote")
    return normalized


def _normalize_catalog_source(value):
    """Normalize curated vs discovered catalog source values."""
    normalized = str(value or "").strip().lower()
    if not normalized:
        return ""
    if normalized not in VALID_CATALOG_SOURCES:
        raise ValueError("template source must be curated or discovered")
    return normalized


def _normalize_telemetry_event(value):
    """Validate telemetry event names accepted by the Hub API."""
    normalized = str(value or "").strip().lower()
    if normalized not in VALID_TELEMETRY_EVENTS:
        supported = ", ".join(sorted(VALID_TELEMETRY_EVENTS))
        raise ValueError(f"invalid telemetry event: {value}. Use one of: {supported}")
    return normalized


def _telemetry_disabled():
    """Allow local opt-out via environment flag."""
    raw = str(os.environ.get("BANANAHUB_DISABLE_TELEMETRY", "")).strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _load_telemetry_state(create=False):
    """Load or create local anonymous telemetry identity."""
    state = _read_json_file(TELEMETRY_STATE_PATH)
    if not isinstance(state, dict):
        state = {}

    anonymous_id = str(state.get("anonymous_id", "")).strip()
    if anonymous_id:
        return state

    if not create:
        return state

    state["anonymous_id"] = uuid4().hex
    state["created_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    _write_json_file(TELEMETRY_STATE_PATH, state)
    return state


def _get_anonymous_id():
    """Return a stable anonymous telemetry identifier."""
    state = _load_telemetry_state(create=True)
    return str(state.get("anonymous_id", "")).strip()


def _track_template_usage(
    event,
    template_id,
    template_repo="",
    template_distribution="",
    template_source="",
    command="",
):
    """Best-effort usage telemetry for bundled or installed templates."""
    if _telemetry_disabled():
        return {
            "enabled": False,
            "sent": False,
            "reason": "disabled_via_env",
        }

    normalized_template_id = str(template_id or "").strip()
    if not normalized_template_id:
        return {
            "enabled": True,
            "sent": False,
            "reason": "missing_template_id",
        }

    try:
        normalized_event = _normalize_telemetry_event(event)
        normalized_distribution = _normalize_template_distribution(template_distribution)
        normalized_source = _normalize_catalog_source(template_source)
    except ValueError as exc:
        return {
            "enabled": True,
            "sent": False,
            "reason": str(exc),
        }

    payload = {
        "event": normalized_event,
        "repo": _normalize_template_repo(template_repo),
        "template_id": normalized_template_id,
        "anonymous_id": _get_anonymous_id(),
        "distribution": normalized_distribution,
        "catalog_source": normalized_source,
        "command": str(command or "").strip(),
        "client_ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }

    req = urlrequest.Request(
        f"{HUB_API_BASE}/usage",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlrequest.urlopen(req, timeout=3) as resp:
            ok = 200 <= getattr(resp, "status", 200) < 300
    except (urlerror.URLError, TimeoutError, OSError) as exc:
        return {
            "enabled": True,
            "sent": False,
            "event": normalized_event,
            "template_id": normalized_template_id,
            "error": str(exc),
        }

    result = {
        "enabled": True,
        "sent": bool(ok),
        "event": normalized_event,
        "template_id": normalized_template_id,
        "repo": payload["repo"],
    }
    if normalized_distribution:
        result["distribution"] = normalized_distribution
    if normalized_source:
        result["catalog_source"] = normalized_source
    return result


def _track_template_usage_from_args(args, event, command):
    """Track usage from optional template telemetry flags on generate/edit."""
    template_id = getattr(args, "template_id", None)
    if not template_id or getattr(args, "no_telemetry", False):
        return None

    return _track_template_usage(
        event=event,
        template_id=template_id,
        template_repo=getattr(args, "template_repo", "") or DEFAULT_TEMPLATE_REPO,
        template_distribution=getattr(args, "template_distribution", ""),
        template_source=getattr(args, "template_source", ""),
        command=command,
    )


def _apply_json_config(config, resolved_from, data, source):
    """Merge config.json-style keys into the canonical config dict."""
    for json_key, env_key in CONFIG_KEY_MAP.items():
        value = data.get(json_key)
        if value in (None, ""):
            continue
        try:
            value = _normalize_config_value(env_key, value)
        except ValueError:
            continue
        if value in (None, ""):
            continue
        config[env_key] = value
        resolved_from[env_key] = source


def _apply_env_config(config, resolved_from):
    """Merge supported environment variables into the canonical config dict."""
    for env_key, aliases in ENV_KEY_ALIASES.items():
        for alias in aliases:
            value = os.environ.get(alias)
            if not value:
                continue
            try:
                value = _normalize_config_value(env_key, value)
            except ValueError:
                continue
            if value in (None, ""):
                continue
            config[env_key] = value
            resolved_from[env_key] = f"env:{alias}"
            break


def _apply_dotenv_values(config, resolved_from, dotenv_values, source):
    """Merge supported dotenv keys into the canonical config dict."""
    for env_key, aliases in ENV_KEY_ALIASES.items():
        for alias in aliases:
            value = dotenv_values.get(alias)
            if not value:
                continue
            try:
                value = _normalize_config_value(env_key, value)
            except ValueError:
                continue
            if value in (None, ""):
                continue
            config[env_key] = value
            resolved_from[env_key] = source
            break


def _finalize_config(config, resolved_from):
    """Infer provider-related defaults after merging explicit config sources."""
    provider = config.get("BANANAHUB_PROVIDER")
    if not provider:
        if _is_truthy(config.get("GOOGLE_GENAI_USE_VERTEXAI")):
            provider = PROVIDER_VERTEX_AI
            provider_source = "inferred:GOOGLE_GENAI_USE_VERTEXAI"
        elif config.get("GOOGLE_CLOUD_PROJECT") or config.get("GOOGLE_CLOUD_LOCATION"):
            provider = PROVIDER_VERTEX_AI
            provider_source = "inferred:google-cloud"
        elif config.get("GOOGLE_GEMINI_BASE_URL"):
            provider = PROVIDER_GEMINI_COMPATIBLE
            provider_source = "inferred:base_url"
        else:
            provider = DEFAULT_PROVIDER
            provider_source = "default"
        config["BANANAHUB_PROVIDER"] = provider
        resolved_from.setdefault("BANANAHUB_PROVIDER", provider_source)

    transport = config.get("BANANAHUB_TRANSPORT")
    if not transport:
        config["BANANAHUB_TRANSPORT"] = DEFAULT_TRANSPORT_BY_PROVIDER.get(provider, TRANSPORT_GENAI)
        resolved_from.setdefault("BANANAHUB_TRANSPORT", f"default:{provider}")

    auth_mode = config.get("BANANAHUB_AUTH_MODE")
    if not auth_mode:
        if provider == PROVIDER_VERTEX_AI and not config.get("GEMINI_API_KEY"):
            auth_mode = AUTH_MODE_ADC
        else:
            auth_mode = AUTH_MODE_API_KEY
        config["BANANAHUB_AUTH_MODE"] = auth_mode
        resolved_from.setdefault("BANANAHUB_AUTH_MODE", f"default:{provider}")

    if provider == PROVIDER_VERTEX_AI and not config.get("GOOGLE_CLOUD_LOCATION"):
        config["GOOGLE_CLOUD_LOCATION"] = DEFAULT_LOCATION
        resolved_from.setdefault("GOOGLE_CLOUD_LOCATION", "default:vertex-ai")


def _runtime_support_status(config):
    """Return whether the current runtime can execute the configured provider."""
    provider = config.get("BANANAHUB_PROVIDER", DEFAULT_PROVIDER)
    transport = config.get("BANANAHUB_TRANSPORT", DEFAULT_TRANSPORT_BY_PROVIDER.get(provider, TRANSPORT_GENAI))
    auth_mode = config.get("BANANAHUB_AUTH_MODE", AUTH_MODE_API_KEY)
    reasons = []
    capabilities = {
        "generate": True,
        "edit": True,
        "models": True,
        "healthcheck": True,
    }

    if provider in {PROVIDER_GOOGLE_AI_STUDIO, PROVIDER_GEMINI_COMPATIBLE}:
        if transport != TRANSPORT_GENAI:
            reasons.append(
                f"provider '{provider}' requires transport '{TRANSPORT_GENAI}', not '{transport}'."
            )
        if auth_mode != AUTH_MODE_API_KEY:
            reasons.append(
                f"provider '{provider}' requires auth_mode '{AUTH_MODE_API_KEY}', not '{auth_mode}'."
            )
    elif provider == PROVIDER_VERTEX_AI:
        if transport != TRANSPORT_GENAI:
            reasons.append(
                f"provider '{provider}' requires transport '{TRANSPORT_GENAI}', not '{transport}'."
            )
        if auth_mode not in {AUTH_MODE_API_KEY, AUTH_MODE_ADC}:
            reasons.append(
                f"provider '{provider}' requires auth_mode '{AUTH_MODE_API_KEY}' or '{AUTH_MODE_ADC}', not '{auth_mode}'."
            )
    elif provider == PROVIDER_OPENAI_COMPATIBLE:
        if transport != TRANSPORT_OPENAI_REST:
            reasons.append(
                f"provider '{provider}' requires transport '{TRANSPORT_OPENAI_REST}', not '{transport}'."
            )
        if auth_mode != AUTH_MODE_API_KEY:
            reasons.append(
                f"provider '{provider}' requires auth_mode '{AUTH_MODE_API_KEY}', not '{auth_mode}'."
            )
        capabilities["edit"] = False
    else:
        reasons.append(
            f"provider '{provider}' is not recognized by this BananaHub runtime."
        )

    return {
        "supported": not reasons,
        "provider": provider,
        "transport": transport,
        "auth_mode": auth_mode,
        "reasons": reasons,
        "capabilities": capabilities,
    }


def _config_validation_errors(config):
    """Return configuration issues that block runtime execution."""
    errors = []
    runtime_support = _runtime_support_status(config)
    errors.extend(runtime_support["reasons"])

    if runtime_support["auth_mode"] == AUTH_MODE_API_KEY and not config.get("GEMINI_API_KEY"):
        errors.append("API key not found. Set GEMINI_API_KEY or GOOGLE_API_KEY, or persist api_key in BananaHub config.")

    if runtime_support["provider"] == PROVIDER_GEMINI_COMPATIBLE and not config.get("GOOGLE_GEMINI_BASE_URL"):
        errors.append("provider 'gemini-compatible' requires a base_url.")
    if runtime_support["provider"] == PROVIDER_OPENAI_COMPATIBLE and not config.get("GOOGLE_GEMINI_BASE_URL"):
        errors.append("provider 'openai-compatible' requires a base_url.")

    return errors


def _resolve_default_model(config, cli_model=None):
    """Resolve the effective model with CLI args taking precedence over config."""
    if cli_model:
        return cli_model
    configured = config.get("BANANAHUB_MODEL")
    if configured:
        return configured
    return DEFAULT_MODEL


def _load_explicit_config(path):
    """Load a user-provided config file, either JSON or .env style."""
    config = {}
    resolved_from = {}
    raw_text = path.read_text()
    stripped = raw_text.lstrip()

    if path.suffix == ".json" or stripped.startswith("{"):
        data = _read_json_file(path, required=True)
        _apply_json_config(config, resolved_from, data, str(path))
        return config, resolved_from

    _apply_dotenv_values(config, resolved_from, load_dotenv(path), str(path))

    return config, resolved_from


def _load_merged_config(config_file=None):
    """Load effective config and return config plus source metadata."""
    config = {}
    resolved_from = {}
    explicit_resolved_from = {}
    existing_sources = []

    if SKILL_CONFIG_PATH.exists():
        existing_sources.append(str(SKILL_CONFIG_PATH))
        data = _read_json_file(SKILL_CONFIG_PATH)
        _apply_json_config(config, resolved_from, data, str(SKILL_CONFIG_PATH))

    _apply_env_config(config, resolved_from)

    if config_file:
        cf = Path(config_file)
        if not cf.exists():
            print(json.dumps({"status": "error", "error": f"Config file not found: {cf}"}))
            sys.exit(1)
        try:
            explicit_config, explicit_resolved_from = _load_explicit_config(cf)
        except ValueError as exc:
            print(json.dumps({"status": "error", "error": str(exc)}))
            sys.exit(1)
        config.update(explicit_config)
        resolved_from.update(explicit_resolved_from)
        existing_sources.append(str(cf))

    explicit_resolved_from.update(resolved_from)
    _finalize_config(config, resolved_from)

    deduped_sources = []
    for source in existing_sources:
        if source not in deduped_sources:
            deduped_sources.append(source)

    return config, resolved_from, deduped_sources, explicit_resolved_from


def _load_persisted_config_for_write():
    """Load the preferred writable BananaHub config."""
    if SKILL_CONFIG_PATH.exists():
        return _read_json_file(SKILL_CONFIG_PATH, required=True)
    return {}


def _write_persisted_config(data):
    """Write BananaHub config.json with stable formatting."""
    _write_json_file(SKILL_CONFIG_PATH, data)


def load_config(config_file=None):
    """Load API config with priority chain:
    1. Explicit --config file (JSON or .env)
    2. Environment variables
    3. Skill config: ~/.config/bananahub/config.json
    """
    config, _, _, _ = _load_merged_config(config_file=config_file)
    errors = _config_validation_errors(config)
    if errors:
        sources = [
            f"  --config <file>",
            f"  env GEMINI_API_KEY / GOOGLE_API_KEY",
            f"  env BANANAHUB_PROVIDER / BANANAHUB_AUTH_MODE / BANANAHUB_MODEL",
            f"  env GOOGLE_GEMINI_BASE_URL / GEMINI_BASE_URL / BANANAHUB_BASE_URL",
            f"  env GOOGLE_CLOUD_PROJECT / GOOGLE_CLOUD_LOCATION",
            f"  {SKILL_CONFIG_PATH}",
        ]
        print(json.dumps({
            "status": "error",
            "error": errors[0],
            "details": errors,
            "searched": sources,
        }, ensure_ascii=False))
        sys.exit(1)

    return config


def get_client(config):
    """Create Gemini client from config."""
    from google import genai

    runtime_support = _runtime_support_status(config)
    if not runtime_support["supported"]:
        print(json.dumps({
            "status": "error",
            "error": runtime_support["reasons"][0],
            "details": runtime_support["reasons"],
        }, ensure_ascii=False))
        sys.exit(1)

    api_key = config.get("GEMINI_API_KEY", "")
    base_url = config.get("GOOGLE_GEMINI_BASE_URL", "")
    provider = runtime_support["provider"]
    auth_mode = runtime_support["auth_mode"]

    if auth_mode == AUTH_MODE_API_KEY and not api_key:
        print(json.dumps({"status": "error", "error": "API key not found in config"}))
        sys.exit(1)

    if provider == PROVIDER_VERTEX_AI:
        client_kwargs = {"vertexai": True}
        if auth_mode == AUTH_MODE_API_KEY:
            client_kwargs["api_key"] = api_key
        else:
            if config.get("GOOGLE_CLOUD_PROJECT"):
                client_kwargs["project"] = config.get("GOOGLE_CLOUD_PROJECT")
            if config.get("GOOGLE_CLOUD_LOCATION"):
                client_kwargs["location"] = config.get("GOOGLE_CLOUD_LOCATION")
        return genai.Client(**client_kwargs)

    endpoint_resolution = _resolve_genai_endpoint(base_url)
    http_options = {"api_version": endpoint_resolution["api_version"]}
    if base_url:
        http_options["base_url"] = endpoint_resolution["resolved_base_url"]

    return genai.Client(api_key=api_key, http_options=http_options)


def _list_config_sources(config_sources, explicit_resolved_from):
    """Return a deduped human-readable list of actual config sources."""
    ordered = list(config_sources)
    for source in sorted(set(explicit_resolved_from.values())):
        if source not in ordered:
            ordered.append(source)
    return ordered


def _serialize_effective_config(config):
    """Return a display-friendly config snapshot."""
    runtime_support = _runtime_support_status(config)
    endpoint_resolution = None
    if runtime_support["transport"] == TRANSPORT_OPENAI_REST and config.get("GOOGLE_GEMINI_BASE_URL"):
        endpoint_resolution = _resolve_openai_endpoint(config.get("GOOGLE_GEMINI_BASE_URL"))
    elif config.get("GOOGLE_GEMINI_BASE_URL"):
        endpoint_resolution = _resolve_genai_endpoint(config.get("GOOGLE_GEMINI_BASE_URL"))
    return {
        "provider": config.get("BANANAHUB_PROVIDER"),
        "transport": config.get("BANANAHUB_TRANSPORT"),
        "auth_mode": config.get("BANANAHUB_AUTH_MODE"),
        "api_key": _mask_secret(config.get("GEMINI_API_KEY", "")) if config.get("GEMINI_API_KEY") else None,
        "base_url": config.get("GOOGLE_GEMINI_BASE_URL") or None,
        "model": config.get("BANANAHUB_MODEL") or None,
        "project": config.get("GOOGLE_CLOUD_PROJECT") or None,
        "location": config.get("GOOGLE_CLOUD_LOCATION") or None,
        "capabilities": runtime_support["capabilities"],
        "endpoint_resolution": endpoint_resolution,
    }


def _serialize_resolved_from(resolved_from):
    """Map internal config keys to stable public field names."""
    return {
        "provider": resolved_from.get("BANANAHUB_PROVIDER"),
        "transport": resolved_from.get("BANANAHUB_TRANSPORT"),
        "auth_mode": resolved_from.get("BANANAHUB_AUTH_MODE"),
        "api_key": resolved_from.get("GEMINI_API_KEY"),
        "base_url": resolved_from.get("GOOGLE_GEMINI_BASE_URL"),
        "model": resolved_from.get("BANANAHUB_MODEL"),
        "project": resolved_from.get("GOOGLE_CLOUD_PROJECT"),
        "location": resolved_from.get("GOOGLE_CLOUD_LOCATION"),
    }


def _load_persisted_config_snapshot():
    """Return persisted config.json interpreted through the current config schema."""
    if not SKILL_CONFIG_PATH.exists():
        return None

    stored = _read_json_file(SKILL_CONFIG_PATH)
    persisted_config = {}
    persisted_resolved_from = {}
    _apply_json_config(persisted_config, persisted_resolved_from, stored, str(SKILL_CONFIG_PATH))
    _finalize_config(persisted_config, persisted_resolved_from)
    return _serialize_effective_config(persisted_config)


def _join_endpoint(base_url, path):
    """Join a configured base URL with a relative API path."""
    return base_url.rstrip("/") + "/" + path.lstrip("/")


def _extract_error_message_from_payload(payload, fallback):
    """Extract a concise error message from a JSON API error payload."""
    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict):
            message = error.get("message") or error.get("code")
            if message:
                return str(message)
        if isinstance(error, str) and error.strip():
            return error.strip()
        message = payload.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()
    return fallback


def _http_json_request(method, url, headers=None, payload=None, timeout=60):
    """Send a JSON HTTP request and parse the JSON response."""
    body = None
    request_headers = dict(headers or {})
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")

    req = urlrequest.Request(url, data=body, headers=request_headers, method=method.upper())
    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            if not raw:
                return {}
            return json.loads(raw.decode("utf-8"))
    except urlerror.HTTPError as exc:
        raw = exc.read()
        fallback = f"{exc.code} {exc.reason}"
        if raw:
            try:
                payload = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                payload = None
            fallback = _extract_error_message_from_payload(payload, fallback)
        raise RuntimeError(f"HTTP {exc.code}: {fallback}") from exc
    except urlerror.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc


def _http_fetch_bytes(url, headers=None, timeout=60):
    """Fetch raw bytes from an HTTP endpoint."""
    req = urlrequest.Request(url, headers=headers or {}, method="GET")
    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urlerror.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}: failed to fetch binary response") from exc
    except urlerror.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc


def _openai_headers(config):
    """Return auth headers for OpenAI-compatible endpoints."""
    api_key = config.get("GEMINI_API_KEY", "")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _provider_error_hint(config, error_msg):
    """Return a provider-specific hint for common endpoint/config mistakes."""
    runtime_support = _runtime_support_status(config)
    provider = runtime_support["provider"]
    upper = str(error_msg).upper()

    if provider == PROVIDER_GEMINI_COMPATIBLE:
        if "404" in str(error_msg) or "NOT FOUND" in upper:
            return (
                "Check the gemini-compatible base_url. If the vendor docs show a `/v1beta` suffix, "
                "you can paste it directly; BananaHub now normalizes the trailing API version automatically."
            )
        if "401" in str(error_msg) or "403" in str(error_msg):
            return "Authentication failed. Check the gemini-compatible key and whether the relay expects a different auth header."

    if provider == PROVIDER_OPENAI_COMPATIBLE:
        if "404" in str(error_msg) or "NOT FOUND" in upper:
            return (
                "Check the openai-compatible base_url. Many gateways expect a `/v1` suffix. "
                "For Google's official endpoint, use `https://generativelanguage.googleapis.com/v1beta/openai`."
            )
        if "401" in str(error_msg) or "403" in str(error_msg):
            return "Authentication failed. Check the openai-compatible key and whether the endpoint expects a Bearer token."

    if provider == PROVIDER_VERTEX_AI:
        if "401" in str(error_msg) or "403" in str(error_msg):
            return "Authentication failed. Check Vertex AI auth mode, ADC readiness, or project/location permissions."
        if "404" in str(error_msg) or "NOT FOUND" in upper:
            return "Check the Vertex AI location and model availability in that project/region."

    if "401" in str(error_msg) or "403" in str(error_msg):
        return "Authentication failed. Check your provider and API key config."
    if "TIMEOUT" in upper or "CONNECT" in upper:
        return "Network error. Check your connection and provider endpoint settings."
    return ""


def _build_openai_generation_payload(model, prompt, aspect_ratio, native_image_size=None):
    """Build an OpenAI-compatible image generation payload."""
    payload = {
        "model": model,
        "prompt": prompt,
        "response_format": "b64_json",
    }
    warnings = []

    if aspect_ratio and aspect_ratio != "1:1":
        payload["extra_body"] = {"google": {"aspect_ratio": aspect_ratio}}

    if native_image_size:
        size_map = {
            "1K": "1024x1024",
            "2K": "2048x2048",
            "4K": "4096x4096",
        }
        if aspect_ratio and aspect_ratio != "1:1":
            warnings.append(
                f"`--image-size {native_image_size}` is ignored for openai-compatible generation when aspect ratio is not 1:1."
            )
        else:
            payload["size"] = size_map[native_image_size]

    return payload, warnings


def _list_openai_models(config):
    """List models from an OpenAI-compatible endpoint."""
    endpoint_resolution = _resolve_openai_endpoint(config.get("GOOGLE_GEMINI_BASE_URL", ""))
    base_url = endpoint_resolution["resolved_base_url"]
    payload = _http_json_request(
        "GET",
        _join_endpoint(base_url, "models"),
        headers=_openai_headers(config),
    )
    entries = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(entries, list):
        return []

    models = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        raw_model_id = str(item.get("id", "")).strip()
        if not raw_model_id:
            continue
        model_id = _canonicalize_model(raw_model_id.removeprefix("models/"))
        models.append({
            "id": model_id,
            "display_name": model_id,
            "description": f"owned_by={item.get('owned_by', 'unknown')}",
            "default": model_id == DEFAULT_MODEL,
        })
        if raw_model_id != model_id:
            models[-1]["aliases"] = [raw_model_id]
    return models


def _openai_try_generate(config, model, prompt, aspect_ratio, image_size=None):
    """Attempt image generation against an OpenAI-compatible endpoint."""
    payload, warnings = _build_openai_generation_payload(model, prompt, aspect_ratio, native_image_size=image_size)
    endpoint_resolution = _resolve_openai_endpoint(config.get("GOOGLE_GEMINI_BASE_URL", ""))
    warnings = endpoint_resolution["warnings"] + warnings
    response = _http_json_request(
        "POST",
        _join_endpoint(endpoint_resolution["resolved_base_url"], "images/generations"),
        headers=_openai_headers(config),
        payload=payload,
        timeout=120,
    )

    items = response.get("data") if isinstance(response, dict) else None
    if not isinstance(items, list) or not items:
        return None, warnings, "No image generated. The endpoint returned an empty response."

    first = items[0]
    if not isinstance(first, dict):
        return None, warnings, "No image generated. The endpoint returned an invalid payload."

    b64_json = first.get("b64_json")
    if b64_json:
        try:
            return base64.b64decode(b64_json), warnings, None
        except Exception as exc:
            return None, warnings, f"Failed to decode image bytes: {exc}"

    image_url = first.get("url")
    if image_url:
        return _http_fetch_bytes(image_url), warnings, None

    return None, warnings, "No image found in response."


def _provider_healthcheck(config):
    """Run a low-cost provider-aware healthcheck."""
    runtime_support = _runtime_support_status(config)
    if not runtime_support["supported"]:
        raise RuntimeError(runtime_support["reasons"][0])

    if runtime_support["transport"] == TRANSPORT_OPENAI_REST:
        models = _list_openai_models(config)
        return {
            "mode": "models.list",
            "response": f"{len(models)} model(s) visible",
        }

    client = get_client(config)
    response = client.models.generate_content(
        model=_resolve_default_model(config),
        contents="Say OK",
    )
    text = ""
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                text = part.text
                break
    return {
        "mode": "generate_content",
        "response": text[:100],
    }


def cmd_init(args):
    """Check environment readiness and guide user through setup."""
    checks = []

    # 1. Check config sources
    config, resolved_from, config_sources, explicit_resolved_from = _load_merged_config(
        config_file=getattr(args, "config", None)
    )
    actual_sources = _list_config_sources(config_sources, explicit_resolved_from)

    if actual_sources:
        checks.append({
            "name": "config_source",
            "ok": True,
            "sources": actual_sources,
            "preferred_path": str(SKILL_CONFIG_PATH),
        })
    else:
        checks.append({
            "name": "config_source",
            "ok": False,
            "error": f"No config found. Create {SKILL_CONFIG_PATH} or use environment variables.",
        })

    # 2. Check provider resolution and runtime support
    runtime_support = _runtime_support_status(config)
    checks.append({
        "name": "provider",
        "ok": True,
        "value": config.get("BANANAHUB_PROVIDER"),
        "transport": runtime_support["transport"],
        "auth_mode": runtime_support["auth_mode"],
        "source": resolved_from.get("BANANAHUB_PROVIDER"),
    })
    checks.append({
        "name": "runtime_support",
        "ok": runtime_support["supported"],
        "provider": runtime_support["provider"],
        "transport": runtime_support["transport"],
        "auth_mode": runtime_support["auth_mode"],
        "capabilities": runtime_support["capabilities"],
        "detail": runtime_support["reasons"] or ["ready"],
    })

    # 3. Check API key
    api_key = config.get("GEMINI_API_KEY", "")
    if runtime_support["auth_mode"] != AUTH_MODE_API_KEY:
        checks.append({
            "name": "api_key",
            "ok": True,
            "value": "(not required for current auth_mode)",
            "source": resolved_from.get("GEMINI_API_KEY"),
        })
    elif api_key:
        checks.append({
            "name": "api_key",
            "ok": True,
            "value": _mask_secret(api_key),
            "source": resolved_from.get("GEMINI_API_KEY"),
        })
    else:
        checks.append({
            "name": "api_key",
            "ok": False,
            "error": "API key not found in any config source. Set GEMINI_API_KEY or GOOGLE_API_KEY.",
        })

    # 4. Check endpoint / base URL
    base_url = config.get("GOOGLE_GEMINI_BASE_URL", "")
    if runtime_support["provider"] == PROVIDER_GEMINI_COMPATIBLE and not base_url:
        checks.append({
            "name": "base_url",
            "ok": False,
            "error": "provider 'gemini-compatible' requires a base_url.",
        })
    elif base_url:
        endpoint_resolution = (
            _resolve_openai_endpoint(base_url)
            if runtime_support["transport"] == TRANSPORT_OPENAI_REST
            else _resolve_genai_endpoint(base_url)
        )
        checks.append({
            "name": "base_url",
            "ok": True,
            "value": base_url,
            "source": resolved_from.get("GOOGLE_GEMINI_BASE_URL"),
            "mode": "custom_endpoint" if runtime_support["provider"] != PROVIDER_GOOGLE_AI_STUDIO else "override_endpoint",
            "resolved_base_url": endpoint_resolution.get("resolved_base_url"),
            "api_version": endpoint_resolution.get("api_version"),
            "warnings": endpoint_resolution.get("warnings"),
        })
    else:
        checks.append({"name": "base_url", "ok": True, "value": "(default Google endpoint)", "mode": "google_default"})

    # 5. Show configured default model when present
    model = config.get("BANANAHUB_MODEL", "")
    checks.append({
        "name": "default_model",
        "ok": True,
        "value": model or DEFAULT_MODEL,
        "source": resolved_from.get("BANANAHUB_MODEL") if model else f"default:{DEFAULT_MODEL}",
    })

    # 6. Check Python dependencies
    deps = {}
    for pkg, import_name in [("google-genai", "google.genai"), ("pillow", "PIL")]:
        try:
            __import__(import_name)
            deps[pkg] = True
        except ImportError:
            deps[pkg] = False
    checks.append({"name": "dependencies", "ok": all(deps.values()), "detail": deps})

    all_ok = all(c["ok"] for c in checks)

    # 7. API connectivity test (only if basic checks pass)
    if all_ok and not args.skip_test:
        try:
            healthcheck = _provider_healthcheck(config)
            checks.append({"name": "api_test", "ok": True, **healthcheck})
        except Exception as e:
            checks.append({"name": "api_test", "ok": False, "error": str(e)[:200]})

    all_ok = all(c["ok"] for c in checks)

    setup_guide = None
    if not all_ok:
        setup_guide = {
            "steps": [
                "Option A (recommended): Google AI Studio / Gemini Developer API:",
                "  1. Create or manage a key in Google AI Studio: https://aistudio.google.com/apikey",
                "  2. python3 bananahub.py config set --provider google-ai-studio --api-key <your_api_key>",
                "  3. Optional default model: python3 bananahub.py config set --model gemini-3.1-flash-image-preview",
                f"  4. Review effective config: python3 bananahub.py config show",
                "Option B: Gemini-compatible relay / proxy:",
                "  1. python3 bananahub.py config set --provider gemini-compatible --base-url https://your-gemini-compatible-endpoint --api-key <your_proxy_key>",
                "  2. Optional default model: python3 bananahub.py config set --model gemini-2.5-flash-image",
                f"  3. Review effective config: python3 bananahub.py config show",
                "Option C: OpenAI-compatible endpoint:",
                "  1. python3 bananahub.py config set --provider openai-compatible --base-url https://your-openai-compatible-endpoint --api-key <your_api_key>",
                "  2. Optional default model: python3 bananahub.py config set --model gemini-2.0-flash-preview-image-generation",
                f"  3. Review effective config: python3 bananahub.py config show",
                "Option D: Vertex AI:",
                "  1. ADC mode: python3 bananahub.py config set --provider vertex-ai --auth-mode adc --project <gcp-project> --location global",
                "  2. Express mode key: python3 bananahub.py config set --provider vertex-ai --auth-mode api_key --api-key <vertex_api_key>",
                f"  3. Review effective config: python3 bananahub.py config show",
                "Option E: Create BananaHub config manually:",
                f"  1. mkdir -p {SKILL_CONFIG_DIR}",
                f'  2. Create {SKILL_CONFIG_PATH} with:',
                '     {"provider": "google-ai-studio", "api_key": "your_api_key_here", "model": "gemini-3-pro-image-preview"}',
                "     or",
                '     {"provider": "gemini-compatible", "api_key": "your_proxy_key_here", "base_url": "https://your-endpoint"}',
                "     or",
                '     {"provider": "openai-compatible", "api_key": "your_api_key_here", "base_url": "https://your-openai-endpoint"}',
                "     or",
                '     {"provider": "vertex-ai", "auth_mode": "adc", "project": "your-gcp-project", "location": "global"}',
                "Option F: Use environment variables:",
                "  export GOOGLE_API_KEY=your_api_key_here  # or GEMINI_API_KEY",
                "  export BANANAHUB_PROVIDER=google-ai-studio",
                "  export BANANAHUB_MODEL=gemini-3-pro-image-preview  # optional",
                "  export BANANAHUB_PROVIDER=gemini-compatible        # for relay/proxy users",
                "  export GOOGLE_GEMINI_BASE_URL=https://your-gemini-compatible-endpoint",
                "  export BANANAHUB_PROVIDER=openai-compatible       # for OpenAI-style endpoints",
                "  export BANANAHUB_PROVIDER=vertex-ai",
                "  export BANANAHUB_AUTH_MODE=adc                     # or api_key",
                "  export GOOGLE_CLOUD_PROJECT=your-gcp-project       # Vertex AI",
                "  export GOOGLE_CLOUD_LOCATION=global                # Vertex AI",
                "",
                "OpenAI-compatible currently supports generate/models/init healthcheck.",
                "Image edit is still only available on genai-backed providers.",
                "Google pricing and quota policy may apply depending on model/account/region.",
                "Install dependencies: pip install google-genai pillow",
                f"Run again: python3 bananahub.py init",
            ]
        }

    print(json.dumps({
        "status": "ok" if all_ok else "incomplete",
        "checks": checks,
        "setup_guide": setup_guide,
    }, ensure_ascii=False, indent=2))

    if not all_ok:
        sys.exit(1)


def cmd_config_show(args):
    """Show effective and persisted config state."""
    config, resolved_from, config_sources, explicit_resolved_from = _load_merged_config(
        config_file=getattr(args, "config", None)
    )
    runtime_support = _runtime_support_status(config)

    response = {
        "status": "ok",
        "preferred_path": str(SKILL_CONFIG_PATH),
        "existing_sources": _list_config_sources(config_sources, explicit_resolved_from),
        "effective_config": _serialize_effective_config(config),
        "resolved_from": _serialize_resolved_from(resolved_from),
        "runtime_support": runtime_support,
        "custom_endpoint_enabled": bool(config.get("GOOGLE_GEMINI_BASE_URL")),
        "telemetry": {
            "enabled": not _telemetry_disabled(),
            "endpoint": f"{HUB_API_BASE}/usage",
            "state_file": str(TELEMETRY_STATE_PATH),
            "anonymous_id": _load_telemetry_state(create=not _telemetry_disabled()).get("anonymous_id")
            if not _telemetry_disabled()
            else None,
        },
    }

    response["persisted_config"] = _load_persisted_config_snapshot()

    print(json.dumps(response, ensure_ascii=False, indent=2))


def cmd_config_set(args):
    """Persist BananaHub config under ~/.config/bananahub/config.json."""
    if (
        not args.api_key
        and not args.provider
        and not args.auth_mode
        and not args.model
        and args.project is None
        and args.location is None
        and args.base_url is None
        and not args.clear_base_url
        and not args.clear_model
        and not args.clear_project
        and not args.clear_location
    ):
        print(json.dumps({
            "status": "error",
            "error": "Nothing to update. Use --api-key, --provider, --auth-mode, --project, --location, --model, --base-url, or the clear-* flags.",
        }, ensure_ascii=False))
        sys.exit(1)

    try:
        persisted_config = _load_persisted_config_for_write()
    except ValueError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
        sys.exit(1)

    if args.api_key:
        persisted_config["api_key"] = args.api_key.strip()

    explicit_provider = None
    if args.provider:
        try:
            explicit_provider = _normalize_provider(args.provider)
        except ValueError as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
            sys.exit(1)
        persisted_config["provider"] = explicit_provider

    if args.auth_mode:
        try:
            persisted_config["auth_mode"] = _normalize_auth_mode(args.auth_mode)
        except ValueError as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
            sys.exit(1)

    if args.clear_model:
        persisted_config.pop("model", None)
    elif args.model is not None:
        normalized_model = _normalize_model(args.model)
        if normalized_model:
            persisted_config["model"] = normalized_model
        else:
            persisted_config.pop("model", None)

    if args.clear_project:
        persisted_config.pop("project", None)
    elif args.project is not None:
        normalized_project = str(args.project).strip()
        if normalized_project:
            persisted_config["project"] = normalized_project
        else:
            persisted_config.pop("project", None)

    if args.clear_location:
        persisted_config.pop("location", None)
    elif args.location is not None:
        normalized_location = str(args.location).strip()
        if normalized_location:
            persisted_config["location"] = normalized_location
        else:
            persisted_config.pop("location", None)

    if args.clear_base_url:
        persisted_config.pop("base_url", None)
    elif args.base_url is not None:
        try:
            normalized_base_url = _normalize_base_url(args.base_url)
        except ValueError as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
            sys.exit(1)
        if normalized_base_url:
            persisted_config["base_url"] = normalized_base_url
        else:
            persisted_config.pop("base_url", None)

    if "provider" not in persisted_config:
        persisted_config["provider"] = (
            PROVIDER_GEMINI_COMPATIBLE if persisted_config.get("base_url") else PROVIDER_GOOGLE_AI_STUDIO
        )

    if args.base_url is not None and not explicit_provider and persisted_config.get("base_url"):
        persisted_config["provider"] = PROVIDER_GEMINI_COMPATIBLE

    if args.clear_base_url and not explicit_provider and persisted_config.get("provider") == PROVIDER_GEMINI_COMPATIBLE:
        persisted_config["provider"] = PROVIDER_GOOGLE_AI_STUDIO

    if persisted_config.get("provider") == PROVIDER_GEMINI_COMPATIBLE and not persisted_config.get("base_url"):
        print(json.dumps({
            "status": "error",
            "error": "provider 'gemini-compatible' requires a base_url. Use --base-url or switch --provider google-ai-studio.",
        }, ensure_ascii=False))
        sys.exit(1)

    if persisted_config.get("provider") == PROVIDER_OPENAI_COMPATIBLE and not persisted_config.get("base_url"):
        print(json.dumps({
            "status": "error",
            "error": "provider 'openai-compatible' requires a base_url. Use --base-url to point at an OpenAI-compatible endpoint.",
        }, ensure_ascii=False))
        sys.exit(1)

    if persisted_config.get("provider") == PROVIDER_GOOGLE_AI_STUDIO and persisted_config.get("base_url"):
        print(json.dumps({
            "status": "error",
            "error": "provider 'google-ai-studio' cannot keep a custom base_url. Use --clear-base-url or switch --provider gemini-compatible.",
        }, ensure_ascii=False))
        sys.exit(1)

    if persisted_config.get("provider") == PROVIDER_VERTEX_AI and persisted_config.get("base_url"):
        print(json.dumps({
            "status": "error",
            "error": "provider 'vertex-ai' does not use base_url in this runtime. Clear it or switch provider.",
        }, ensure_ascii=False))
        sys.exit(1)

    try:
        _write_persisted_config(persisted_config)
    except OSError as exc:
        print(json.dumps({"status": "error", "error": f"Failed to write config: {exc}"}))
        sys.exit(1)

    print(json.dumps({
        "status": "ok",
        "file": str(SKILL_CONFIG_PATH),
        "config": _load_persisted_config_snapshot(),
    }, ensure_ascii=False, indent=2))


def cmd_telemetry_status(args):
    """Show local telemetry identity and endpoint state."""
    state = _load_telemetry_state(create=not _telemetry_disabled())
    anonymous_id = str(state.get("anonymous_id", "")).strip()

    print(json.dumps({
        "status": "ok",
        "enabled": not _telemetry_disabled(),
        "endpoint": f"{HUB_API_BASE}/usage",
        "state_file": str(TELEMETRY_STATE_PATH),
        "anonymous_id": anonymous_id or None,
    }, ensure_ascii=False, indent=2))


def cmd_telemetry_track(args):
    """Send an explicit template usage telemetry event."""
    try:
        result = _track_template_usage(
            event=args.event,
            template_id=args.template_id,
            template_repo=args.template_repo,
            template_distribution=args.template_distribution,
            template_source=args.template_source,
            command=args.command_name,
        )
    except ValueError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
        sys.exit(1)

    payload = {
        "status": "ok" if result.get("sent") or not result.get("enabled", True) else "skipped",
        "telemetry": result,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


IMAGE_KEYWORDS = {"image", "imagen"}
DEFAULT_MODEL = "gemini-3-pro-image-preview"
MODEL_ALIASES = {
    "nano-banana-pro-preview": "gemini-3-pro-image-preview",
}
NATIVE_IMAGE_SIZES = ("1K", "2K", "4K")

# Ordered fallback chain: try these models in sequence when the requested model fails
MODEL_FALLBACK_CHAIN = [
    "gemini-3-pro-image-preview",
    "gemini-3.1-flash-image-preview",
    "gemini-2.5-flash-image",
    # Keep the old model as the final legacy fallback for older accounts.
    "gemini-2.0-flash-preview-image-generation",
]

# HTTP status codes that trigger fallback (server-side, not user's fault)
FALLBACK_STATUS_CODES = {"500", "502", "503", "504", "UNAVAILABLE", "INTERNAL", "OVERLOADED"}

FALLBACK_MODELS = [
    {"id": "gemini-3-pro-image-preview", "display_name": "Gemini 3 Pro Image Preview", "default": True},
    {"id": "gemini-3.1-flash-image-preview", "display_name": "Gemini 3.1 Flash Image Preview", "default": False},
    {"id": "gemini-2.5-flash-image", "display_name": "Gemini 2.5 Flash Image", "default": False},
    {"id": "gemini-2.0-flash-preview-image-generation", "display_name": "Gemini 2.0 Flash Image Generation", "default": False},
]


def _canonicalize_model(model):
    """Map known aliases to the canonical model id used by the runtime."""
    return MODEL_ALIASES.get((model or "").strip(), (model or "").strip())


def _dedupe_preserve_order(items):
    """Keep the first occurrence of each item while preserving order."""
    seen = set()
    result = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _normalize_image_size(value):
    """Normalize native image-size presets accepted by Gemini image models."""
    if not value:
        return None
    normalized = value.strip().upper()
    if normalized in NATIVE_IMAGE_SIZES:
        return normalized
    return None


def _parse_resize_dims(value):
    """Parse post-processing resize dimensions in WxH form."""
    if not value:
        return None
    match = re.fullmatch(r"(\d+)x(\d+)", value.strip().lower())
    if not match:
        return None
    width, height = map(int, match.groups())
    if width <= 0 or height <= 0:
        return None
    return width, height


def _resolve_image_request_options(args):
    """Resolve native image-size vs legacy/post-processing resize flags."""
    native_image_size = None
    resize_dims = None
    warnings = []

    explicit_image_size = getattr(args, "image_size", None)
    if explicit_image_size:
        native_image_size = _normalize_image_size(explicit_image_size)
        if not native_image_size:
            supported = ", ".join(NATIVE_IMAGE_SIZES)
            raise ValueError(
                f"Invalid --image-size value: {explicit_image_size}. "
                f"Use one of: {supported}."
            )

    explicit_resize = getattr(args, "resize", None)
    if explicit_resize:
        resize_dims = _parse_resize_dims(explicit_resize)
        if not resize_dims:
            raise ValueError(
                f"Invalid --resize value: {explicit_resize}. Use WxH, for example 1024x1024."
            )

    legacy_size = getattr(args, "size", None)
    if legacy_size:
        legacy_native_size = _normalize_image_size(legacy_size)
        legacy_resize_dims = _parse_resize_dims(legacy_size)
        if legacy_native_size:
            if native_image_size and native_image_size != legacy_native_size:
                raise ValueError(
                    f"Conflicting native size values: --image-size {native_image_size} and --size {legacy_size}."
                )
            native_image_size = native_image_size or legacy_native_size
            warnings.append(
                f"`--size {legacy_size}` is treated as a native image-size preset. Prefer `--image-size {legacy_size}`."
            )
        elif legacy_resize_dims:
            if resize_dims and resize_dims != legacy_resize_dims:
                raise ValueError(
                    f"Conflicting resize values: --resize {explicit_resize} and --size {legacy_size}."
                )
            resize_dims = resize_dims or legacy_resize_dims
            warnings.append(
                f"`--size {legacy_size}` is treated as post-processing resize. Prefer `--resize {legacy_size}`."
            )
        else:
            supported = ", ".join(NATIVE_IMAGE_SIZES)
            raise ValueError(
                f"Invalid --size value: {legacy_size}. Use one of {supported} for native image size "
                "or WxH for post-processing resize."
            )

    return native_image_size, resize_dims, warnings


def _add_template_telemetry_flags(parser):
    """Attach optional template telemetry metadata to generate/edit commands."""
    parser.add_argument("--template-id", help="Template id for success telemetry")
    parser.add_argument("--template-repo", help=f"Template repo for telemetry (default: {DEFAULT_TEMPLATE_REPO})")
    parser.add_argument(
        "--template-distribution",
        choices=sorted(VALID_TEMPLATE_DISTRIBUTIONS),
        help="Template distribution for telemetry (bundled or remote)",
    )
    parser.add_argument(
        "--template-source",
        choices=sorted(VALID_CATALOG_SOURCES),
        help="Template source layer for telemetry (curated or discovered)",
    )
    parser.add_argument("--no-telemetry", action="store_true", help="Disable best-effort template telemetry for this run")


def _is_server_error(exception):
    """Check if an exception is a server-side error eligible for fallback."""
    msg = str(exception).upper()
    return any(code in msg for code in FALLBACK_STATUS_CODES)


def _get_fallback_models(current_model):
    """Return fallback models to try after current_model fails.
    If current_model is in the chain, return everything after it.
    If not in the chain, return the full chain (skipping current_model if present).
    """
    current_model = _canonicalize_model(current_model)
    if current_model in MODEL_FALLBACK_CHAIN:
        idx = MODEL_FALLBACK_CHAIN.index(current_model)
        return MODEL_FALLBACK_CHAIN[idx + 1:]
    return [m for m in MODEL_FALLBACK_CHAIN if m != current_model]


def cmd_models(args):
    """List available image generation models from the API, with fallback."""
    config = load_config(getattr(args, "config", None))
    runtime_support = _runtime_support_status(config)
    try:
        if runtime_support["transport"] == TRANSPORT_OPENAI_REST:
            models = _list_openai_models(config)
            filtered = [m for m in models if any(kw in m["id"].lower() for kw in IMAGE_KEYWORDS)]
            if filtered:
                models = filtered
            elif not models:
                models = FALLBACK_MODELS
                print(json.dumps({"status": "ok", "source": "fallback", "models": models}, ensure_ascii=False))
                return

            models = sorted(models, key=lambda x: (not x["default"], x["id"]))
            print(json.dumps({"status": "ok", "source": "api", "models": models}, ensure_ascii=False))
            return

        client = get_client(config)
        api_models = {}
        for m in client.models.list(config={"page_size": 100}):
            name = m.name or ""
            # Strip "models/" prefix if present
            raw_model_id = name.removeprefix("models/")
            model_id = _canonicalize_model(raw_model_id)
            desc = (m.description or "").lower()
            model_id_lower = raw_model_id.lower()
            display = m.display_name or model_id

            # Filter: model id or description mentions image-related keywords
            is_image = any(kw in model_id_lower for kw in IMAGE_KEYWORDS) or any(kw in desc for kw in IMAGE_KEYWORDS)
            if not is_image:
                continue

            existing = api_models.get(model_id)
            if existing:
                if raw_model_id != model_id:
                    existing.setdefault("aliases", [])
                    if raw_model_id not in existing["aliases"]:
                        existing["aliases"].append(raw_model_id)
                continue

            entry = {
                "id": model_id,
                "display_name": display,
                "description": (m.description or "")[:120],
                "input_token_limit": getattr(m, "input_token_limit", None),
                "output_token_limit": getattr(m, "output_token_limit", None),
                "default": model_id == DEFAULT_MODEL,
            }
            if raw_model_id != model_id:
                entry["aliases"] = [raw_model_id]
            api_models[model_id] = entry

        if api_models:
            # Sort: default model first, then alphabetically
            models = sorted(api_models.values(), key=lambda x: (not x["default"], x["id"]))
            print(json.dumps({"status": "ok", "source": "api", "models": models}, ensure_ascii=False))
            return

        # API returned no image models — use fallback
        print(json.dumps({"status": "ok", "source": "fallback", "models": FALLBACK_MODELS}, ensure_ascii=False))

    except Exception as e:
        # API call failed — use fallback
        print(json.dumps({
            "status": "ok",
            "source": "fallback",
            "warning": f"API query failed: {str(e)[:150]}",
            "models": FALLBACK_MODELS,
        }, ensure_ascii=False))


def _try_edit(client, model, prompt, input_images, image_size=None):
    """Attempt image editing with a single model. Returns (image_part, text_parts, None) or (None, [], error_str).

    Args:
        input_images: list of PIL Image objects (main image + optional reference images).
    """
    from google.genai import types

    contents = [prompt] + input_images
    image_config = types.ImageConfig(image_size=image_size) if image_size else None
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=image_config,
        ),
    )

    if not response.candidates or not response.candidates[0].content.parts:
        return None, [], "No response generated. The model may have refused the prompt due to content policy."

    image_part = None
    text_parts = []
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            image_part = part
        elif hasattr(part, "text") and part.text:
            text_parts.append(part.text)

    if not image_part:
        error_msg = "No image in response."
        if text_parts:
            error_msg += f" Model said: {' '.join(text_parts)}"
        return None, text_parts, error_msg

    return image_part, text_parts, None


def _default_output_path(prefix, model):
    """Build the default output path for generated assets."""
    output_dir = Path.cwd()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_short = model.replace("gemini-", "").replace("-preview", "").replace("-image-generation", "")
    return output_dir / f"{prefix}_{model_short}_{timestamp}.png"


def _save_png_bytes(image_bytes, output_path, resize_dims=None):
    """Persist image bytes as PNG, optionally resizing first."""
    from PIL import Image
    import io

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.open(io.BytesIO(image_bytes))
    if resize_dims:
        image = image.resize(resize_dims, Image.LANCZOS)
    image.save(str(output_path), "PNG")
    return image


def cmd_edit(args):
    """Edit an existing image based on a text prompt, with automatic model fallback."""
    import io

    try:
        native_image_size, resize_dims, option_warnings = _resolve_image_request_options(args)
    except ValueError as e:
        print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    config_data = load_config(getattr(args, "config", None))
    runtime_support = _runtime_support_status(config_data)
    if not runtime_support["capabilities"].get("edit", False):
        print(json.dumps({
            "status": "error",
            "error": (
                f"provider '{runtime_support['provider']}' does not support image edit in this runtime yet. "
                "Use google-ai-studio, gemini-compatible, or vertex-ai for edit."
            ),
        }, ensure_ascii=False))
        sys.exit(1)

    # Validate input image before importing heavy dependencies
    input_path = Path(args.input)
    if not input_path.exists():
        print(json.dumps({
            "status": "error",
            "error": f"Input image not found: {input_path}",
        }, ensure_ascii=False))
        sys.exit(1)

    # Validate reference images
    ref_paths = []
    for ref in (args.ref or []):
        rp = Path(ref)
        if not rp.exists():
            print(json.dumps({
                "status": "error",
                "error": f"Reference image not found: {rp}",
            }, ensure_ascii=False))
            sys.exit(1)
        ref_paths.append(rp)

    if len(ref_paths) > 13:
        print(json.dumps({
            "status": "error",
            "error": f"Too many reference images: {len(ref_paths)}. Maximum is 13 reference images.",
        }, ensure_ascii=False))
        sys.exit(1)

    if 1 + len(ref_paths) > 14:
        print(json.dumps({
            "status": "error",
            "error": f"Too many input images: {1 + len(ref_paths)}. Total images (input + refs) must be 14 or fewer.",
        }, ensure_ascii=False))
        sys.exit(1)

    from PIL import Image

    # Load all images: main input + references
    input_images = []
    try:
        input_images.append(Image.open(str(input_path)))
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "error": f"Cannot read input image: {e}",
        }, ensure_ascii=False))
        sys.exit(1)

    for rp in ref_paths:
        try:
            input_images.append(Image.open(str(rp)))
        except Exception as e:
            print(json.dumps({
                "status": "error",
                "error": f"Cannot read reference image {rp}: {e}",
        }, ensure_ascii=False))
        sys.exit(1)

    client = get_client(config_data)

    requested_model_input = _resolve_default_model(config_data, args.model)
    requested_model = _canonicalize_model(requested_model_input)
    prompt = args.prompt
    no_fallback = getattr(args, "no_fallback", False)
    retries = getattr(args, "retries", 1)

    # Determine output path (deferred until model is known)
    user_output = args.output

    # Build model attempt list
    if no_fallback:
        models_to_try = [requested_model]
    else:
        models_to_try = _dedupe_preserve_order([requested_model] + _get_fallback_models(requested_model))

    tried = []
    last_error = None

    for model in models_to_try:
        for attempt in range(1 + retries):
            try:
                image_part, text_parts, gen_error = _try_edit(
                    client,
                    model,
                    prompt,
                    input_images,
                    image_size=native_image_size,
                )

                if gen_error:
                    print(json.dumps({
                        "status": "error",
                        "error": gen_error,
                        "prompt": prompt,
                        "requested_model": requested_model_input,
                        "actual_model": model,
                    }, ensure_ascii=False))
                    sys.exit(1)

                # Success — resolve output path now that we know the actual model
                if user_output:
                    output_path = Path(user_output)
                else:
                    output_dir = Path.cwd()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    model_short = model.replace("gemini-", "").replace("-preview", "").replace("-image-generation", "")
                    output_path = output_dir / f"bananahub_edit_{model_short}_{timestamp}.png"

                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Save image
                image = Image.open(io.BytesIO(image_part.inline_data.data))

                if resize_dims:
                    image = image.resize(resize_dims, Image.LANCZOS)

                image.save(str(output_path), "PNG")

                result = {
                    "status": "ok",
                    "file": str(output_path),
                    "input": str(input_path),
                    "requested_model": requested_model_input,
                    "actual_model": model,
                    "prompt": prompt,
                    "image_size": f"{image.width}x{image.height}",
                    "total_images": len(input_images),
                }
                if requested_model_input != requested_model:
                    result["resolved_requested_model"] = requested_model
                if native_image_size:
                    result["native_image_size"] = native_image_size
                if resize_dims:
                    result["post_resize"] = f"{resize_dims[0]}x{resize_dims[1]}"
                if option_warnings:
                    result["warnings"] = option_warnings
                if ref_paths:
                    result["ref_images"] = [str(rp) for rp in ref_paths]
                if model != requested_model:
                    result["fallback_from"] = requested_model
                result["fallback_chain"] = models_to_try
                result["models_tried"] = tried + [model]
                if text_parts:
                    result["model_text"] = " ".join(text_parts)
                telemetry_result = _track_template_usage_from_args(args, event="edit_success", command="edit")
                if telemetry_result:
                    result["template_telemetry"] = telemetry_result
                print(json.dumps(result, ensure_ascii=False))
                return

            except Exception as e:
                last_error = e
                if not _is_server_error(e):
                    tried.append({"model": model, "error": str(e)[:150]})
                    break
                if attempt < retries:
                    import time
                    delay = 2 ** (attempt + 1)
                    tried.append({"model": model, "error": str(e)[:150], "retry": attempt + 1, "delay_s": delay})
                    time.sleep(delay)
                else:
                    tried.append({"model": model, "error": str(e)[:150]})
        else:
            continue
        break

    # All models failed
    error_msg = str(last_error)
    hint = ""
    if "SAFETY" in error_msg.upper() or "BLOCKED" in error_msg.upper():
        hint = "Content was blocked by safety filters. Try rephrasing the prompt."
    elif "QUOTA" in error_msg.upper() or "429" in error_msg:
        hint = "API quota exceeded. Wait a moment and try again."
    else:
        hint = _provider_error_hint(config_data, error_msg)

    result = {
        "status": "error",
        "error": error_msg,
        "prompt": prompt,
        "requested_model": requested_model_input,
        "resolved_requested_model": requested_model,
        "retries_per_model": retries,
        "fallback_chain": models_to_try,
        "models_tried": tried,
    }
    if native_image_size:
        result["native_image_size"] = native_image_size
    if resize_dims:
        result["post_resize"] = f"{resize_dims[0]}x{resize_dims[1]}"
    if option_warnings:
        result["warnings"] = option_warnings
    if hint:
        result["hint"] = hint
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(1)


def _try_generate(client, model, prompt, aspect_ratio, image_size=None):
    """Attempt image generation with a single model. Returns (image_part, None) or (None, error_str)."""
    from google.genai import types

    image_config_kwargs = {"aspect_ratio": aspect_ratio}
    if image_size:
        image_config_kwargs["image_size"] = image_size

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(**image_config_kwargs),
        ),
    )

    if not response.candidates or not response.candidates[0].content.parts:
        return None, "No image generated. The model may have refused the prompt due to content policy."

    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            return part, None

    text_parts = [p.text for p in response.candidates[0].content.parts if hasattr(p, "text") and p.text]
    error_msg = "No image in response."
    if text_parts:
        error_msg += f" Model said: {' '.join(text_parts)}"
    return None, error_msg


def cmd_generate(args):
    """Generate an image from a text prompt, with automatic model fallback."""
    try:
        native_image_size, resize_dims, option_warnings = _resolve_image_request_options(args)
    except ValueError as e:
        print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    config = load_config(getattr(args, "config", None))
    runtime_support = _runtime_support_status(config)
    client = None
    if runtime_support["transport"] == TRANSPORT_GENAI:
        client = get_client(config)

    requested_model_input = _resolve_default_model(config, args.model)
    requested_model = _canonicalize_model(requested_model_input)
    prompt = args.prompt
    aspect_ratio = args.aspect or "1:1"
    no_fallback = getattr(args, "no_fallback", False)
    retries = getattr(args, "retries", 1)

    # Determine output path (default: current working directory with model name)
    user_output = args.output

    # Build model attempt list
    if no_fallback:
        models_to_try = [requested_model]
    else:
        models_to_try = _dedupe_preserve_order([requested_model] + _get_fallback_models(requested_model))

    tried = []
    last_error = None

    for model in models_to_try:
        # Retry same model up to (1 + retries) times before fallback
        for attempt in range(1 + retries):
            try:
                extra_warnings = []
                if runtime_support["transport"] == TRANSPORT_OPENAI_REST:
                    image_bytes, extra_warnings, gen_error = _openai_try_generate(
                        config,
                        model,
                        prompt,
                        aspect_ratio,
                        image_size=native_image_size,
                    )
                    image_part = None
                else:
                    image_part, gen_error = _try_generate(
                        client,
                        model,
                        prompt,
                        aspect_ratio,
                        image_size=native_image_size,
                    )
                    image_bytes = image_part.inline_data.data if image_part else None

                if gen_error:
                    # Content policy / no image — not a server error, don't fallback
                    print(json.dumps({
                        "status": "error",
                        "error": gen_error,
                        "prompt": prompt,
                        "requested_model": requested_model_input,
                        "actual_model": model,
                    }, ensure_ascii=False))
                    sys.exit(1)

                # Success — resolve output path now that we know the actual model
                if user_output:
                    output_path = Path(user_output)
                else:
                    output_path = _default_output_path("bananahub", model)

                image = _save_png_bytes(image_bytes, output_path, resize_dims=resize_dims)

                result = {
                    "status": "ok",
                    "file": str(output_path),
                    "requested_model": requested_model_input,
                    "actual_model": model,
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "image_size": f"{image.width}x{image.height}",
                }
                if requested_model_input != requested_model:
                    result["resolved_requested_model"] = requested_model
                if native_image_size:
                    result["native_image_size"] = native_image_size
                if resize_dims:
                    result["post_resize"] = f"{resize_dims[0]}x{resize_dims[1]}"
                combined_warnings = option_warnings + extra_warnings
                if combined_warnings:
                    result["warnings"] = combined_warnings
                if model != requested_model:
                    result["fallback_from"] = requested_model
                result["fallback_chain"] = models_to_try
                result["models_tried"] = tried + [model]
                telemetry_result = _track_template_usage_from_args(args, event="generate_success", command="generate")
                if telemetry_result:
                    result["template_telemetry"] = telemetry_result
                print(json.dumps(result, ensure_ascii=False))
                return

            except Exception as e:
                last_error = e
                if not _is_server_error(e):
                    tried.append({"model": model, "error": str(e)[:150]})
                    break
                # Retry same model with exponential backoff
                if attempt < retries:
                    import time
                    delay = 2 ** (attempt + 1)
                    tried.append({"model": model, "error": str(e)[:150], "retry": attempt + 1, "delay_s": delay})
                    time.sleep(delay)
                else:
                    tried.append({"model": model, "error": str(e)[:150]})
        else:
            # Inner loop completed without break — all retries exhausted, try next model
            continue
        # Inner loop was broken (non-server error) — stop trying
        break

    # All models failed
    error_msg = str(last_error)
    hint = ""
    if "SAFETY" in error_msg.upper() or "BLOCKED" in error_msg.upper():
        hint = "Content was blocked by safety filters. Try rephrasing the prompt."
    elif "QUOTA" in error_msg.upper() or "429" in error_msg:
        hint = "API quota exceeded. Wait a moment and try again."
    else:
        hint = _provider_error_hint(config, error_msg)

    result = {
        "status": "error",
        "error": error_msg,
        "prompt": prompt,
        "requested_model": requested_model_input,
        "resolved_requested_model": requested_model,
        "retries_per_model": retries,
        "fallback_chain": models_to_try,
        "models_tried": tried,
    }
    if native_image_size:
        result["native_image_size"] = native_image_size
    if resize_dims:
        result["post_resize"] = f"{resize_dims[0]}x{resize_dims[1]}"
    if option_warnings:
        result["warnings"] = option_warnings
    if hint:
        result["hint"] = hint
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(prog="bananahub.py", description="BananaHub - Gemini image generation")
    parser.add_argument("--config", help="Path to config file (JSON or .env)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # generate command
    gen_parser = subparsers.add_parser("generate", help="Generate an image from a prompt")
    gen_parser.add_argument("prompt", help="Text prompt for image generation")
    gen_parser.add_argument("--model", "-m", help="Model ID (default: gemini-3-pro-image-preview)")
    gen_parser.add_argument("--aspect", "-a", help="Aspect ratio, e.g. 1:1, 16:9, 9:16 (default: 1:1)")
    gen_parser.add_argument("--image-size", help="Native image-size preset: 1K, 2K, or 4K")
    gen_parser.add_argument("--resize", help="Post-process resize to WxH, e.g. 1024x1024")
    gen_parser.add_argument("--size", "-s", help="Legacy compatibility flag: use 1K/2K/4K for native image size, or WxH for post-processing resize")
    gen_parser.add_argument("--output", "-o", help="Output file path (default: current directory)")
    gen_parser.add_argument("--no-fallback", action="store_true", help="Disable automatic model fallback on server errors")
    gen_parser.add_argument("--retries", type=int, default=1, help="Retry count per model on 503 before fallback (default: 1)")
    _add_template_telemetry_flags(gen_parser)

    # edit command
    edit_parser = subparsers.add_parser("edit", help="Edit an existing image with a text prompt")
    edit_parser.add_argument("prompt", help="Text prompt describing the edit")
    edit_parser.add_argument("--input", "-i", required=True, help="Path to the source image")
    edit_parser.add_argument("--ref", "-r", nargs="+", default=[], help="Reference image paths (up to 13 additional images for style/content guidance)")
    edit_parser.add_argument("--model", "-m", help="Model ID (default: gemini-3-pro-image-preview)")
    edit_parser.add_argument("--image-size", help="Native image-size preset: 1K, 2K, or 4K")
    edit_parser.add_argument("--resize", help="Post-process resize to WxH, e.g. 1024x1024")
    edit_parser.add_argument("--size", "-s", help="Legacy compatibility flag: use 1K/2K/4K for native image size, or WxH for post-processing resize")
    edit_parser.add_argument("--output", "-o", help="Output file path (default: current directory)")
    edit_parser.add_argument("--no-fallback", action="store_true", help="Disable automatic model fallback on server errors")
    edit_parser.add_argument("--retries", type=int, default=1, help="Retry count per model on 503 before fallback (default: 1)")
    _add_template_telemetry_flags(edit_parser)

    # models command
    subparsers.add_parser("models", help="List available models")

    # init command
    init_parser = subparsers.add_parser("init", help="Check environment and guide setup")
    init_parser.add_argument("--skip-test", action="store_true", help="Skip API connectivity test")

    # config command
    config_parser = subparsers.add_parser("config", help="Show or persist BananaHub config")
    config_subparsers = config_parser.add_subparsers(dest="config_command", help="Config actions")

    config_show_parser = config_subparsers.add_parser("show", help="Show effective config resolution")
    config_show_parser.set_defaults(config_handler=cmd_config_show)

    config_set_parser = config_subparsers.add_parser("set", help="Write ~/.config/bananahub/config.json")
    config_set_parser.add_argument(
        "--provider",
        choices=sorted(SUPPORTED_PROVIDERS),
        help="Provider to persist",
    )
    config_set_parser.add_argument(
        "--auth-mode",
        choices=sorted(SUPPORTED_AUTH_MODES),
        help="Auth mode to persist: api_key or adc",
    )
    config_set_parser.add_argument("--api-key", help="API key to persist in BananaHub config")
    config_set_parser.add_argument("--base-url", help="Custom Gemini-compatible base URL to persist")
    config_set_parser.add_argument("--project", help="Google Cloud project to persist")
    config_set_parser.add_argument("--location", help="Google Cloud location to persist")
    config_set_parser.add_argument("--model", help="Default model to persist")
    config_set_parser.add_argument("--clear-base-url", action="store_true", help="Remove stored custom base URL")
    config_set_parser.add_argument("--clear-project", action="store_true", help="Remove stored Google Cloud project")
    config_set_parser.add_argument("--clear-location", action="store_true", help="Remove stored Google Cloud location")
    config_set_parser.add_argument("--clear-model", action="store_true", help="Remove stored default model")
    config_set_parser.set_defaults(config_handler=cmd_config_set)

    telemetry_parser = subparsers.add_parser("telemetry", help="BananaHub usage telemetry helpers")
    telemetry_subparsers = telemetry_parser.add_subparsers(dest="telemetry_command", help="Telemetry actions")

    telemetry_status_parser = telemetry_subparsers.add_parser("status", help="Show anonymous telemetry identity")
    telemetry_status_parser.set_defaults(telemetry_handler=cmd_telemetry_status)

    telemetry_track_parser = telemetry_subparsers.add_parser("track", help="Send a template telemetry event")
    telemetry_track_parser.add_argument("--event", required=True, choices=sorted(VALID_TELEMETRY_EVENTS), help="Telemetry event name")
    telemetry_track_parser.add_argument("--template-id", required=True, help="Template id")
    telemetry_track_parser.add_argument("--template-repo", default=DEFAULT_TEMPLATE_REPO, help="Template repo")
    telemetry_track_parser.add_argument(
        "--template-distribution",
        choices=sorted(VALID_TEMPLATE_DISTRIBUTIONS),
        help="Template distribution (bundled or remote)",
    )
    telemetry_track_parser.add_argument(
        "--template-source",
        choices=sorted(VALID_CATALOG_SOURCES),
        help="Template source layer (curated or discovered)",
    )
    telemetry_track_parser.add_argument("--command-name", help="Origin command name, e.g. use/generate/edit")
    telemetry_track_parser.set_defaults(telemetry_handler=cmd_telemetry_track)

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "edit":
        cmd_edit(args)
    elif args.command == "models":
        cmd_models(args)
    elif args.command == "init":
        cmd_init(args)
    elif args.command == "config":
        handler = getattr(args, "config_handler", None)
        if not handler:
            config_parser.print_help()
            sys.exit(1)
        handler(args)
    elif args.command == "telemetry":
        handler = getattr(args, "telemetry_handler", None)
        if not handler:
            telemetry_parser.print_help()
            sys.exit(1)
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
