#!/usr/bin/env python3
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "runtime_config.py"
spec = importlib.util.spec_from_file_location("runtime_config", MODULE_PATH)
runtime_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime_config)


def test_provider_aliases():
    assert runtime_config.normalize_provider("openai-official") == runtime_config.PROVIDER_OPENAI
    assert runtime_config.normalize_provider("chatgpt") == runtime_config.PROVIDER_CHATGPT_COMPATIBLE
    try:
        runtime_config.normalize_provider("nano")
    except ValueError:
        pass
    else:
        raise AssertionError("unexpected nano provider alias")


def test_openai_endpoint_normalization():
    result = runtime_config.resolve_openai_endpoint("https://api.example.com")
    assert result["resolved_base_url"] == "https://api.example.com/v1"


def test_gemini_endpoint_version_split():
    result = runtime_config.resolve_genai_endpoint("https://generativelanguage.googleapis.com/v1beta")
    assert result["resolved_base_url"] == "https://generativelanguage.googleapis.com"
    assert result["api_version"] == "v1beta"


if __name__ == "__main__":
    test_provider_aliases()
    test_openai_endpoint_normalization()
    test_gemini_endpoint_version_split()
    print("ok")
