# Practical Infographic One-Pager

Starter prompt template for turning a short process, comparison, timeline, or framework into one readable infographic card.

## Use

```bash
/bananahub use info-diagram
```

## Verified Models

- `gpt-image-2` — verified with `samples/sample-gpt-image-2-01.png` for a strict-label four-step flow infographic.
- `gemini-3.1-flash-image-preview` — verified with `samples/sample-3.1-flash-01.png` for a simple five-step coffee process card.

## Supported Models

- `gpt-image-2` — recommended when exact labels and strict text limits matter most.
- `gemini-3-pro-image-preview` — good fit for polished visual hierarchy and richer icons.
- `gemini-3.1-flash-image-preview` — good faster option for simple flow cards.
- `gpt-image-1` — compatible fallback through the `gpt-image` prompt variant.

## Sample Outputs

| File | Provider | Model | Prompt Variant | Notes |
|---|---|---|---|---|
| `samples/sample-3.1-flash-01.png` | `google-ai-studio` | `gemini-3.1-flash-image-preview` | `gemini` | Simple five-step coffee process card. |
| `samples/sample-gpt-image-2-01.png` | `chatgpt-compatible` | `gpt-image-2` | `gpt-image` | Four-step flow infographic with locked labels `Plan`, `Build`, `Test`, and `Ship`. |

## License

CC BY 4.0 unless this directory states otherwise.
