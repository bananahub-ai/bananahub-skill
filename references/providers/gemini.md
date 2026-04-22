# Gemini / Nano Banana Provider Guide

Use this guide only after the core optimization pipeline has identified a Gemini-family model or a Gemini-specific capability.

## Model Family

Gemini image models are exposed through Google AI Studio, Vertex AI, Gemini-compatible endpoints, and some OpenAI-style Gemini gateways. BananaHub treats `nano-banana`, `nano-banana-pro`, and `nano-banana-2` as aliases resolved by `references/model-registry.json`.

## Prompt Preferences

- Use natural English descriptions rather than comma-separated tags.
- Put the subject and task near the beginning of the prompt.
- Preserve exact in-image text in quotes and keep it short.
- Use explicit edit deltas: name what changes and what must remain unchanged.
- Avoid SD/Midjourney syntax, quality tag spam, and negative prompt phrasing.
- For known IP or well-known characters, avoid inaccurate appearance descriptions; focus on scene, action, composition, or style requested by the user.

## Runtime Options

- Prefer `aspect_ratio` for composition intent.
- Use native image-size presets `1K`, `2K`, and `4K` only when the selected Gemini model supports them.
- `--resize WxH` is a post-processing transform, not a native generation constraint.
- Multi-reference editing can use up to 14 total input images in Gemini image flows; validate before execution.

## Template Guidance

Templates tested primarily on Gemini should provide `prompt_variant: gemini` when their wording depends on Gemini behavior. If the generic prompt is already conservative and natural-language based, the default prompt variant can be reused.
