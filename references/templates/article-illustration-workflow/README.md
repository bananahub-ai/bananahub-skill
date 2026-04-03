# Article Illustration Workflow

A BananaHub workflow template for turning article text into a compact illustration pack. It helps the agent read the article first, write a small outline, generate one visual at a time, and optionally insert Markdown image refs back into the source file.

## Install

```bash
npx bananahub add bananahub-ai/bananahub-skill/article-illustration-workflow
```

## Verified Models

- `gemini-3-pro-image-preview` — verified with `samples/sample-3-pro-01.png`, `samples/sample-3-pro-02.png`, and `samples/sample-3-pro-03.png`, covering a workflow diagram, a slot-planning comparison card, and a scene-led editorial cover

## Supported Models

- `gemini-3-pro-image-preview` — best fit when label accuracy, layout clarity, and article fidelity matter most
- `gemini-3.1-flash-image-preview` — good faster option for outline-driven drafts and multi-image article packs

## Sample Outputs

| File | Model | Prompt / Variant |
|---|---|---|
| `samples/sample-3-pro-01.png` | `gemini-3-pro-image-preview` | Three-stage article workflow diagram with only the locked labels `Extract claims`, `Plan slots`, and `Generate + review` |
| `samples/sample-3-pro-02.png` | `gemini-3-pro-image-preview` | Three-column slot-planning card with only the locked labels `Flowchart`, `Framework card`, and `Text only` |
| `samples/sample-3-pro-03.png` | `gemini-3-pro-image-preview` | Text-free scene-led editorial cover showing a printed article page, pencil, and three planning frames on a calm desk surface |
