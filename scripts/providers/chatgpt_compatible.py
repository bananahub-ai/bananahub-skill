"""Chat/completions-style image provider adapter."""

import base64
import os
import re
from urllib.parse import urlparse, urlunparse

from .common import http_fetch_bytes, http_json_request, join_endpoint


def normalize_base_url(config, normalize_base_url_fn):
    configured = normalize_base_url_fn(config.get("BANANAHUB_CHATGPT_BASE_URL"))
    parsed = urlparse(configured)
    path = parsed.path.rstrip("/")
    if path.endswith("/chat/completions"):
        path = path[: -len("/chat/completions")]
    elif path.endswith("/completions"):
        path = path[: -len("/completions")]
    if not re.search(r"/(v\d+(?:beta\d*|alpha\d*)?)$", path):
        path = f"{path}/v1" if path else "/v1"
    return urlunparse(parsed._replace(path=path)).rstrip("/")


def headers(config):
    result = {
        "Authorization": f"Bearer {config.get('BANANAHUB_CHATGPT_API_KEY', '')}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": config.get("BANANAHUB_CHATGPT_USER_AGENT") or "BananaHub/0.1 (+https://bananahub.ai)",
    }
    if config.get("BANANAHUB_CHATGPT_REFERER"):
        result["Referer"] = config["BANANAHUB_CHATGPT_REFERER"]
    return result


def extract_image_reference_from_text(text):
    if not text:
        return None
    data_match = re.search(r"data:image/[^;\s]+;base64,[A-Za-z0-9+/=\r\n]+", text)
    if data_match:
        return data_match.group(0)
    markdown_match = re.search(r"!\[[^\]]*\]\((https?://[^)\s]+)\)", text)
    if markdown_match:
        return markdown_match.group(1)
    url_match = re.search(r"https?://[^\s)\]\"']+\.(?:png|jpe?g|webp|gif)(?:\?[^\s)\]\"']*)?", text, re.IGNORECASE)
    if url_match:
        return url_match.group(0)
    return None


def extract_image_reference(payload):
    candidates = []
    if isinstance(payload, dict):
        choices = payload.get("choices")
        if isinstance(choices, list):
            for choice in choices:
                message = choice.get("message") if isinstance(choice, dict) else None
                if isinstance(message, dict):
                    candidates.append(message.get("content"))
                if isinstance(choice, dict):
                    candidates.append(choice.get("text"))
        for key in ("content", "text", "message", "output_text"):
            candidates.append(payload.get(key))
    elif isinstance(payload, str):
        candidates.append(payload)

    for candidate in candidates:
        if isinstance(candidate, str):
            found = extract_image_reference_from_text(candidate)
            if found:
                return found
        elif isinstance(candidate, list):
            for part in candidate:
                if isinstance(part, dict):
                    image_url = part.get("image_url")
                    if isinstance(image_url, dict) and image_url.get("url"):
                        return image_url["url"]
                    if isinstance(part.get("url"), str):
                        return part["url"]
                    if isinstance(part.get("text"), str):
                        found = extract_image_reference_from_text(part["text"])
                        if found:
                            return found
    return None


def describe_image_reference(reference, include_full=None):
    include = include_full if include_full is not None else os.environ.get("BANANAHUB_DEBUG_IMAGE_URL", "").lower() in {"1", "true", "yes", "on"}
    if reference.startswith("data:image/"):
        result = {"type": "data-url"}
        if include:
            result["url"] = reference
        return result
    parsed = urlparse(reference)
    path = parsed.path or ""
    suffix = path[-48:] if len(path) > 48 else path
    result = {"type": "url", "host": parsed.netloc, "path_suffix": suffix}
    if include:
        result["url"] = reference
    return result


def image_bytes_from_reference(reference, request_headers=None, api_base_url=None):
    if reference.startswith("data:image/"):
        _, b64_data = reference.split(",", 1)
        image_bytes = base64.b64decode(re.sub(r"\s+", "", b64_data))
        if not image_bytes.startswith((b"\x89PNG", b"\xff\xd8\xff", b"RIFF", b"GIF8")):
            raise RuntimeError("data:image reference did not contain recognizable PNG/JPEG/WebP/GIF bytes")
        return image_bytes
    if reference.startswith("http://") or reference.startswith("https://"):
        headers_for_download = dict(request_headers or {})
        if api_base_url:
            ref_host = urlparse(reference).netloc
            api_host = urlparse(api_base_url).netloc
            if ref_host and api_host and ref_host != api_host:
                headers_for_download.pop("Authorization", None)
        return http_fetch_bytes(reference, headers=headers_for_download)
    raise RuntimeError("Unsupported image reference returned by chatgpt-compatible endpoint.")


def try_generate(config, model, prompt, normalize_base_url_fn):
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Generate an image for this request and include the resulting image in the response "
                    "as either a markdown image URL or a data:image base64 URL. Request: " + prompt
                ),
            }
        ],
    }
    base_url = normalize_base_url(config, normalize_base_url_fn)
    response = http_json_request(
        "POST",
        join_endpoint(base_url, "chat/completions"),
        headers=headers(config),
        payload=payload,
        timeout=180,
    )
    reference = extract_image_reference(response)
    if not reference:
        return None, [], "No image reference found in chat response. Expected markdown image, image URL, or data:image URL."
    try:
        image_bytes = image_bytes_from_reference(
            reference,
            request_headers=headers(config),
            api_base_url=base_url,
        )
    except Exception as exc:
        return None, [describe_image_reference(reference)], f"Chat response contained an image reference, but downloading it failed: {exc}"
    return image_bytes, [], None
