#!/usr/bin/env python3
import base64
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "bananahub.py"
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("bananahub", MODULE_PATH)
bananahub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bananahub)


def test_markdown_image_extraction():
    payload = {"choices": [{"message": {"content": "Here is it: ![cat](https://example.com/cat.png)"}}]}
    assert bananahub._extract_chatgpt_image_reference(payload) == "https://example.com/cat.png"


def test_data_url_extraction_and_decode():
    raw = b"\x89PNG\r\n\x1a\nminimal"
    data_url = "data:image/png;base64," + base64.b64encode(raw).decode("ascii")
    payload = {"choices": [{"message": {"content": data_url}}]}
    ref = bananahub._extract_chatgpt_image_reference(payload)
    assert ref == data_url
    assert bananahub._image_bytes_from_reference(ref) == raw


def test_structured_content_extraction():
    payload = {
        "choices": [
            {
                "message": {
                    "content": [
                        {"type": "text", "text": "done"},
                        {"type": "image_url", "image_url": {"url": "https://example.com/result.webp"}},
                    ]
                }
            }
        ]
    }
    assert bananahub._extract_chatgpt_image_reference(payload) == "https://example.com/result.webp"


if __name__ == "__main__":
    test_markdown_image_extraction()
    test_data_url_extraction_and_decode()
    test_structured_content_extraction()
    print("ok")
