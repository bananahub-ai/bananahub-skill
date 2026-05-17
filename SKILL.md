---
name: bananahub
description: >
  Agent-native image workflow and optional prompt optimizer for `/bananahub` and generic agent image generation requests.
  Normalizes non-English prompts into English by default, generates or edits images across Gemini/Nano Banana, OpenAI GPT Image,
  chat-compatible routes, and Codex/host-native image tools when available, discovers or uses BananaHub templates,
  and captures successful multi-turn image iterations as reusable workflow templates.
  Explicit `/bananahub` requests execute the BananaHub workflow. Requests like "把刚才的调图流程沉淀成模板",
  "save this image workflow", or "capture workflow" should use the capture-workflow flow. Generic requests like "生成图片", "画一个", "create an image",
  or "edit this image" should load BananaHub as an optimization advisor: ask whether to optimize/template-route the prompt
  before generation, then continue with the user's chosen image channel.
metadata:
  version: 0.1.0
  author: bananahub-ai
  emoji: 🍌
  requires:
    bins:
      - python3
    python:
      - pillow
    env:
      - OPENAI_API_KEY
      - GEMINI_API_KEY
      - GOOGLE_API_KEY
  primaryEnv: OPENAI_API_KEY
user_invocable: true
---

# BananaHub

Generate or edit images from non-English or mixed-language requests inside one `/bananahub` workflow. GPT Image 2 through an OpenAI-compatible image endpoint is the default provider path; user-configured Gemini/Nano Banana, OpenAI official, Vertex, chat-compatible paths, and Codex/host-native image tools are preserved. BananaHub keeps prompt optimization, conservative enhancement, model fallback, image editing, template use, and BananaHub discovery in a single skill instead of splitting them across separate installs.

When BananaHub is loaded implicitly for a generic agent image request, act as a lightweight optimization layer first. Do not silently take over generation: ask whether the user wants BananaHub to optimize the prompt before the image tool runs, then respect the answer.

## Quick Start

- Install via Open Agent Skills: `npx skills add https://github.com/bananahub-ai/bananahub-skill --skill bananahub`
- Install in Claude Code directly: `claude skill install https://github.com/bananahub-ai/bananahub-skill`
- Run setup once: `/bananahub init`
- Test a host-native image tool such as Codex built-in image generation: `/bananahub test-host-imagegen`
- Generate from a natural-language request: `/bananahub 一只橘猫趴在键盘上打盹`
- Edit an image: `/bananahub edit 把背景换成海滩 --input photo.png`
- Discover a reusable template: `/bananahub discover 代码库讲解图`
- Capture the current image iteration as a workflow template: `/bananahub capture-workflow`

## Key Paths

- **Generation script**: `{baseDir}/scripts/bananahub.py`
- **Provider adapters**: `{baseDir}/scripts/providers/` — Gemini, OpenAI Images, and chat/completions-compatible runtime adapters
- **Runtime config module**: `{baseDir}/scripts/runtime_config.py` — provider constants, aliases, transport defaults, config keys, and endpoint normalization
- **Config store module**: `{baseDir}/scripts/config_store.py` — config loading, profile merge, validation, provider override, and serialization helpers
- **Prompt optimization rules**: `references/prompt-guide.md` — read during Phase 1 (base optimization)
- **Enhancement profiles**: `references/profiles/{name}.md` — read during Phase 3 (on-demand)
- **Official references**: `references/official-sources.md` — authoritative source URLs, core example library
- **Capability registry**: `references/capability-registry.md` — provider/model feature routing and fallback policy
- **Model registry**: `references/model-registry.json` — canonical model ids, aliases, defaults, and provider families
- **Provider guides**: `references/providers/{provider}.md` — lazy-loaded model-family prompt and runtime rules
- **Template system**: `references/template-system.md` — read when handling templates/use/create-template commands
- **Hub discovery guide**: `references/hub-discovery.md` — read when handling `discover` or when local template matching is weak
- **Template files**: `{baseDir}/references/templates/<id>/template.md` (built-in) + `~/.config/bananahub/templates/<id>/template.md` (user-installed)
- **Telemetry helper**: `python3 {baseDir}/scripts/bananahub.py telemetry ...` — use for built-in/installed template adoption events
- **Telemetry state**: `~/.config/bananahub/telemetry.json` — stores the local anonymous usage id
- **Init guide**: `references/init-guide.md` — read when handling `init` command
- **Optimization pipeline**: `references/optimization-pipeline.md` — read when optimizing prompts
- **Template format spec**: `references/template-format-spec.md` — detailed field definitions, repo structure, sample requirements
- **Template validator**: `python3 {baseDir}/scripts/validate_templates.py` — validates bundled/user template metadata for schema v1/v2 compatibility
- **Mode detector**: `python3 {baseDir}/scripts/bananahub.py check-mode` — reports provider-backed / host-native / prompt-only execution mode and capability layer boundaries
- **Host-native image tool test**: `/bananahub test-host-imagegen` or `/bananahub test-codex-imagegen` — skill-layer command; call the host/Codex built-in image generation tool with the validation prompt below
- **Prompt archive**: current working directory `bananahub-prompts/` when `--save-prompt`, `--prompt-output`, or `BANANAHUB_SAVE_PROMPTS=1` is used
- **API config** (priority high→low):
  1. `--config <file>` CLI flag
  2. Selected skill profile in `~/.config/bananahub/config.json`
  3. Environment variables fill missing fields by default (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `GOOGLE_API_KEY`, `GEMINI_API_KEY`, `BANANAHUB_PROVIDER`, `BANANAHUB_AUTH_MODE`, `BANANAHUB_MODEL`, `GOOGLE_GEMINI_BASE_URL`, `GEMINI_BASE_URL`, `BANANAHUB_BASE_URL`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`)
     - Use `BANANAHUB_PROFILE=<name>` to select another persisted profile
     - Set `BANANAHUB_ENV_OVERRIDE=1` only when environment variables should temporarily override profile fields
  4. Skill config examples:
     - `{"provider": "google-ai-studio", "api_key": "...", "model": "gemini-3-pro-image-preview"}`
     - `{"provider": "gemini-compatible", "api_key": "...", "base_url": "https://..."}`
     - `{"provider": "openai", "openai_api_key": "...", "model": "gpt-image-2"}`
     - `{"provider": "openai-compatible", "openai_api_key": "...", "openai_base_url": "https://...", "model": "gpt-image-2"}`
     - `{"provider": "chatgpt-compatible", "chatgpt_api_key": "...", "chatgpt_base_url": "https://...", "model": "gpt-5.4"}`
     - multi-profile: `{"default_profile":"gpt","profiles":{"gpt":{"provider":"openai-compatible","openai_api_key":"...","openai_base_url":"https://...","model":"gpt-image-2"},"nano":{"provider":"google-ai-studio","api_key":"..."}}}`
     - `{"provider": "vertex-ai", "auth_mode": "adc", "project": "...", "location": "global"}`
  5. Persistent config helpers:
     - `python3 {baseDir}/scripts/bananahub.py config show`
     - `python3 {baseDir}/scripts/bananahub.py config doctor --json`
     - `python3 {baseDir}/scripts/bananahub.py config quickset --provider openai-compatible --profile gpt --default-profile --base-url https://your-openai-compatible-endpoint --api-key <key> --model gpt-image-2`
     - `python3 {baseDir}/scripts/bananahub.py config quickset --provider openai-compatible --profile gpt --default-profile --base-url https://your-openai-compatible-endpoint --api-key-stdin --model gpt-image-2`
     - `python3 {baseDir}/scripts/bananahub.py config quickset --provider openai --profile gpt --default-profile --api-key <key> --model gpt-image-2`
     - `python3 {baseDir}/scripts/bananahub.py config quickset --provider google-ai-studio --profile nano --default-profile --api-key <key> --model gemini-3-pro-image-preview`
     - `python3 {baseDir}/scripts/bananahub.py config quickset --provider vertex-ai --profile vertex --default-profile --auth-mode adc --project <gcp-project> --location global`
     - `python3 {baseDir}/scripts/bananahub.py init --wizard` (human-terminal fallback only)
     - `python3 {baseDir}/scripts/bananahub.py config set --clear-base-url`
- **Output directory**: current working directory (where the skill is invoked)

## First-Run Detection

Before executing any command other than `help`, check if the environment is ready:
1. Run `python3 {baseDir}/scripts/bananahub.py config doctor --json` when setup status is unclear.
2. If `status` is `needs_setup`, read `references/init-guide.md`, ask only for missing provider-required fields, then persist them with the matching `config quickset` command.
3. Direct API-key entry is allowed when the user chooses it or already pasted a key. Write it with `config quickset --api-key-stdin` and do not echo it back.
4. If the user does not want secrets in chat, give them the `config quickset` command with `<key>` placeholders for their local terminal.
5. If config exists but generation fails with auth/dependency errors → suggest `config doctor --json`.
6. Persist new config into `~/.config/bananahub/config.json`, preferably as a named profile (`gpt`, `nano`, `vertex`, or `chat`).
7. Treat `init --wizard` as a human-terminal fallback only; do not assume agents can run interactive prompts.
8. Treat `openai-compatible` + `gpt-image-2` as the default setup path. If the user already configured a provider/profile/model, preserve it and route within that provider.
9. Before asking for a provider API key, check whether the current client exposes a host-native image generation tool. In Codex, OAuth sessions and some API logins expose a built-in image tool; if available, offer it as a no-local-AK image channel and optionally run `/bananahub test-host-imagegen`.
10. Supported runtime providers:
   - `google-ai-studio`: generate / edit / models / init
   - `gemini-compatible`: generate / edit / models / init
   - `vertex-ai`: generate / edit / models / init
   - `openai`: OpenAI-native GPT Image generate / edit / models / init
   - `openai-compatible`: OpenAI-style Images API generate / edit / models / init, capability-dependent
   - `chatgpt-compatible`: chat/completions endpoint that returns images inside assistant replies
11. `openai-compatible` is not the same as OpenAI-native GPT Image. The runtime attempts standard Images API generation/editing, but exact support still depends on the gateway.
12. Endpoint normalization rules:
   - `gemini-compatible`: if the user pastes a URL ending in `/v1beta`, keep it conceptually but normalize the trailing version during runtime so it is not duplicated
   - `openai-compatible`: if the user pastes a bare host, the runtime may append `/v1`; for Google's official endpoint, resolve it to `/v1beta/openai`

## Runtime Mode Layers

Run `python3 {baseDir}/scripts/bananahub.py check-mode --pretty` when the execution path is unclear. BananaHub has three execution modes:

| Mode | Trigger | Behavior |
|---|---|---|
| `provider-backed` | Config validates for a supported provider | Optimize/render prompt, call `generate` or `edit`, and save image outputs |
| `host-native` | Provider config is missing or incomplete, but `BANANAHUB_HOST_IMAGEGEN=1`, `check-mode --host-imagegen`, or the agent has a Codex/host built-in image tool | Optimize/render prompt, optionally archive it, then hand it to the host image tool instead of calling the provider script |
| `prompt-only` | No valid provider and no host image tool | Act as a prompt/template advisor: return the final prompt and archive it when requested; do not claim image generation succeeded |

Capability ownership is layered:

- **Cross-model skill layer**: prompt optimization, translation policy, conservative enhancement, `--direct`, `--raw`, prompt archiving, template discovery/activation, host-native delegation, and prompt-only advisory output.
- **Template layer**: matching and activation are common, but provider/model compatibility, prompt variants, tested quality, and samples belong to template metadata.
- **Provider/model layer**: image edit, mask edit, multi-reference, exact size, native quality, transparent background, output format/compression, and fallback are not universal; route them through `references/capability-registry.md`, `references/model-registry.json`, and provider adapters.

### Host-Native Codex Image Tool

Treat Codex built-in image generation as a host-native channel, not as a persisted provider. It is useful when the user is authenticated through Codex OAuth or another host/API login that exposes an image tool and does not want to enter a separate BananaHub API key.

- Offer this channel during `init` when the current agent visibly has an image generation tool.
- To verify it, run `/bananahub test-host-imagegen` or `/bananahub test-codex-imagegen`: optimize no extra provider config, call the host image generation tool directly, and report whether an image file was produced.
- Validation prompt:
  ```text
  Create a compact BananaHub channel validation image: a clean workflow card connected to a built-in image generation tool node, with a green check indicator. Include only the exact label "Codex Image Tool OK". Crisp modern product illustration, high readability, no logos, no watermark, no extra text.
  ```
- After a successful test, treat the current session as host-native. For CLI-only diagnostics, run `python3 {baseDir}/scripts/bananahub.py check-mode --host-imagegen --pretty` or set `BANANAHUB_HOST_IMAGEGEN=1`.
- Do not promise provider-native controls on this path. Exact pixel size, mask editing, native quality, output format, compression, transparent background, and multi-reference limits depend on the host tool surface.
- If a generated image is meant for the current project, move or copy the final asset from the host tool's default output location into the workspace before referencing it.

If a feature changes request payload shape, file validation, cost, policy behavior, or output parsing, do not treat it as cross-model even if several providers happen to support similar wording.

Agent operating principle: do not ask the human to make choices the agent can resolve from diagnosis, config, templates, or file paths. Ask only for secrets, provider/channel selection when unknown, paid generation consent, or genuinely creative direction.

## Implicit Image Request Flow

This flow applies when BananaHub is loaded by a generic agent image request rather than an explicit `/bananahub` command.

1. Detect the user's intent:
   - image generation: "生成图片", "画一个", "create an image", "make a poster", "generate a logo", etc.
   - image editing: "改这张图", "replace the background", "edit this image", etc.
2. If the user explicitly asks to skip optimization, says "直接生成/直接画/raw/no optimization", or the request is already a highly structured final prompt, do not interrupt. Use the current image channel directly.
3. Otherwise ask one short confirmation before generation:
   ```text
   要不要我先用 BananaHub 优化一下 prompt，再用当前可用的生图通道生成？我会保留你的原意，只增强结构、约束和模型适配。
   ```
   In English sessions:
   ```text
   Do you want BananaHub to optimize the prompt before I generate it? I will preserve your intent and only tighten structure, constraints, and model fit.
   ```
4. If the user agrees, run the normal BananaHub optimization pipeline, suggest a matching local template only when there is a clear fit, then generate through the active provider or host-native image tool.
5. If the user declines, do not use BananaHub optimization for that request. Hand the original request to the current image generation tool.
6. If the request includes exact text, brand constraints, a reference image, editing boundaries, a workflow/template need, or a deliverable that benefits from prompt archiving, briefly recommend optimization but still wait for confirmation unless the user invoked `/bananahub` explicitly.

## Command Routing

Route user input to the appropriate action based on arguments:

| Argument | Action |
|---|---|
| `init` | Read `references/init-guide.md`, then diagnose and fix environment issues |
| `help` | Show usage instructions (brief list of supported commands and examples) |
| `<description>` | Read `references/optimization-pipeline.md`, then: base optimization → intent recognition → optional enhancement → generate |
| `edit <description> --input <image-path> [--ref <reference-image>...]` | Edit an existing image: optimize prompt → call edit subcommand |
| `optimize <description>` | Optimize prompt only; display result without generating |
| `generate <English prompt>` | Generate image directly with given English prompt (skip optimization) |
| `models` | Run `python3 {baseDir}/scripts/bananahub.py models` to query image-capable models from API |
| `check-mode` | Run `python3 {baseDir}/scripts/bananahub.py check-mode --pretty` to inspect provider-backed / host-native / prompt-only mode and capability layers |
| `test-host-imagegen` / `test-codex-imagegen` | Skill-layer command: call the host/Codex built-in image generation tool with the validation prompt, then mark the session as host-native if it succeeds |
| `templates` | Read `references/template-system.md`, then list all templates grouped by profile and type |
| `templates <name>` | Read `references/template-system.md`, parse frontmatter `type`, then show prompt-template or workflow-template details accordingly |
| `use <template-id> [custom description]` | Read `references/template-system.md`, parse frontmatter `type`, then either generate from a prompt template or activate a workflow template |
| `discover <request>` | Read `references/hub-discovery.md`, then search BananaHub for matching templates without scraping the visual site |
| `discover curated <request>` | Read `references/hub-discovery.md`, then search only the curated BananaHub catalog |
| `discover trending` | Read `references/hub-discovery.md`, then show current trending BananaHub templates |
| `create-template [description]` | Read `references/template-system.md`, determine whether the user needs a prompt or workflow template, then guide creation |
| `capture-workflow` / `save-workflow` / `summarize-workflow` | Read `references/template-system.md`, inspect the current multi-turn image iteration, and draft a reusable `type: workflow` template |

Note:
- `optimize`, `--direct`, and `--raw` are **skill-layer controls** interpreted by you before invoking the script
- Do **not** pass `--direct` or `--raw` through to `{baseDir}/scripts/bananahub.py`
- `optimize`, `templates`, `use`, `discover`, `create-template`, `capture-workflow`, `save-workflow`, `summarize-workflow`, `test-host-imagegen`, and `test-codex-imagegen` are **skill-layer commands**. If they are accidentally passed to `{baseDir}/scripts/bananahub.py`, the script returns a machine-readable `status: "skill_layer_command"` explanation for agents.
- `discover` uses BananaHub machine-readable files and `npx bananahub add ...`, not provider generation directly.
- `telemetry` is an **internal helper**, not a user-facing chat command. Use it when a template is selected or successfully produces output.

Optional flags (append to any generation command):
- `--model <model_id>` — specify model
- `--aspect <ratio>` — aspect ratio (e.g., 16:9, 1:1, 9:16)
- `--image-size <preset>` — native image-size preset (`1K`, `2K`, `4K`)
- `--openai-size <value>` — OpenAI-native size for OpenAI-style image generation
- `--quality <value>` — provider-native quality preset when supported
- `--background <value>` — provider-native background option when supported
- `--output-format <value>` — provider-native output format when supported
- `--output-compression <N>` — provider-native output compression when supported
- `--resize <WxH>` — post-process resize after generation/edit (e.g., `1024x1024`)
- `--size <value>` — legacy compatibility flag; `1K/2K/4K` means native image size, `WxH` means post-process resize
- `--output <path>` — specify output path
- `--save-prompt` — archive the final prompt under `bananahub-prompts/`
- `--prompt-output <path>` — archive the final prompt to a specific file or directory
- `--input <path>` — source image for edit commands
- `--ref <path> [path...]` — reference images for edit commands (Gemini up to 13 refs; OpenAI provider enforces its own lower runtime limit)
- `--mask <path>` — OpenAI-native mask image for masked edits
- `--direct` — direct mode: skip all confirmations, generate immediately
- `--raw` — raw mode: translate only, no optimization
- `--retries <N>` — retry count per model on 503 before fallback (default: 1, i.e. try each model twice)
- `--no-fallback` — disable automatic model fallback

## Three Optimization Modes

### Mode 1: Default (no flag)
```
User input → Base optimization (silent) → Intent recognition → Profile match?
  ├─ Yes → Show enhancement suggestion → User confirms/edits/rejects → Generate
  └─ No (general) → Generate directly
```

### Mode 2: Direct (`--direct` or user says "直接画/直出")
```
User input → Base optimization → Intent recognition → Load Profile enhancement → Generate directly
```
No confirmations. Suitable for experienced users or batch generation.

### Mode 3: Raw (`--raw`)
```
User input → Translate to English only → Generate directly
```
No optimization. In-image text is still preserved in original language.

## Prompt Optimization Summary

Read `references/optimization-pipeline.md` for the full pipeline. Overview:

1. **Phase 0**: Extract hard constraints (exact_text, must_keep, must_avoid, style_lock, approved_baseline, allowed_delta when relevant)
2. **Phase 1**: Base optimization — format correction, smart translation, structuring, conservative guardrail
3. **Phase 1.5**: Capability/provider routing — inspect `references/capability-registry.md`, resolve model aliases from `references/model-registry.json`, then lazy-load `references/providers/*.md` only for the selected model family
4. **Phase 2**: Intent recognition — match to one of 10 profiles via keyword table
4. **Phase 2.1**: Local template auto-matching — suggest installed templates (progressive disclosure)
5. **Phase 2.2**: BananaHub discovery — search remote catalog only when explicitly useful
6. **Phase 2.5**: Style overlay detection (hand-drawn sketch-note)
7. **Phase 3**: Enhancement — read matching profile from `references/profiles/`, classify subject, fill missing dimensions
8. **Phase 3.5**: Model recommendation — prefer `gpt-image-2` for generation-led high-fidelity outputs; prefer Gemini/Nano Banana for edit/reference/consistency-heavy flows unless the user or template overrides it

## Image Generation Flow

1. If execution mode is `host-native`, use the final optimized prompt with the host/Codex built-in image tool instead of calling `{baseDir}/scripts/bananahub.py generate`. Save or report the host-generated output path, and archive the prompt when requested.
2. Otherwise build command:
   ```bash
   python3 {baseDir}/scripts/bananahub.py generate "<prompt>" [--aspect RATIO] [--model MODEL] [--output PATH]
   ```
   When this generation comes from an active template, also pass:
   `--template-id <id> --template-repo <repo> --template-distribution bundled|remote --template-source curated|discovered`
3. Execute script and parse JSON output
4. **Automatic model fallback**: on server error (500/502/503/504), tries the selected provider family fallback chain from `references/model-registry.json`. Do not cross provider families unless the user explicitly enables cross-provider fallback. Use `--no-fallback` to disable.
5. On success:
   ```
   ✅ 图片已生成
   📁 路径: [file_path]
   🔧 模型: [model] | 宽高比: [ratio] | 尺寸: [WxH]
   📝 使用的 Prompt: [final prompt used]
   ```
   If the script returns `template_telemetry`, treat it as best-effort success reporting only; do not surface failures unless the user asked.
6. On failure: suggest fix based on error type (content policy → rephrase, auth → check key, network → check proxy)

## Image Editing Flow

1. **Validate input**: confirm `--input` image path exists; validate `--ref` images
   Reject more than 13 reference images or more than 14 total images.
2. **Extract invariants**: what must remain unchanged in the source image
3. **Lock the baseline when applicable**: if the source image is an accepted result, treat it as the only source of truth for later rounds
4. **Name the allowed delta**: isolate the one change this round is allowed to make
5. **Optimize edit prompt**: run Phase 1 only (skip Phase 2/3); keep conservative, isolate the delta
6. **Build command**:
   ```bash
   python3 {baseDir}/scripts/bananahub.py edit "<prompt>" --input <image_path> [--ref <ref1> ...] [--model MODEL] [--output PATH]
   ```
   `--ref` accepts up to 13 reference images. Total images (input + refs) ≤ 14.
   When this edit runs inside an active template/workflow, also pass:
   `--template-id <id> --template-repo <repo> --template-distribution bundled|remote --template-source curated|discovered`
7. On success:
   ```
   ✅ 图片已编辑
   📁 路径: [file_path]
   📥 原图: [input_path]
   📎 参考图: [ref_images, if any]
   🔧 模型: [model] | 尺寸: [WxH]
   📝 使用的 Prompt: [final prompt used]
   ```

Multi-image use cases: style transfer, character consistency, multi-image blending, object replacement.

## Iteration Guide

- Change one variable at a time
- Retain the last effective prompt as a base
- Treat follow-ups as deltas, not full rewrites
- Preserve locked constraints unless user explicitly changes them
- After the user accepts an output, treat that file as the approved baseline until the user replaces it
- For follow-up edits, state the exact keep-unchanged constraints before the allowed delta
- For deterministic derivative tasks such as invert, crop, export, add safe padding, or build exact lockups, prefer local deterministic transforms instead of asking the model to redraw the asset

## Template System Summary

Read `references/template-system.md` for the full template system. Overview:

- **Search paths**: built-in (`references/templates/`) + user-installed (`~/.config/bananahub/templates/`)
- **Local vs remote**: `templates` / `use` operate on installed templates; `discover` operates on BananaHub catalog, including the official `bananahub-ai/templates` library, and installs only on demand
- **Format**: `template.md` with YAML frontmatter and `type: prompt | workflow`
- **Prompt templates**: produce a reusable prompt with variables, then generate or edit
- **Workflow templates**: act as progressive-disclosure context; load the workflow, ask only for missing blockers, and execute step-by-step with `generate` / `edit` primitives when needed
- **Model transparency**: when a template or heuristic selects `gpt-image-2` or Gemini/Nano Banana automatically, state that recommendation explicitly instead of hiding the model choice
- **Built-in starter examples**: `info-diagram` for one-page infographics, `article-one-page-summary` for article explainers, `background-replace-edit` for edit workflows
- **Commands**: `templates` (list installed), `templates <name>` (details), `use <id> [desc]` (activate), `discover <need>` (search hub), `create-template` (create), `capture-workflow` (turn current iteration into a workflow draft)
- **Auto-matching**: Phase 2.1 suggests installed templates first; Phase 2.2 can search BananaHub when local coverage is weak
- **Adoption telemetry**: when a template is selected, call `python3 {baseDir}/scripts/bananahub.py telemetry track --event selected ...`; when template-driven `generate`/`edit` succeeds, pass template telemetry flags so the script can report `generate_success` / `edit_success`
- **Install more**: prefer `discover` inside the skill; official rich templates install from `bananahub-ai/templates`, and known targets can still be installed with `npx bananahub add <user/repo[/template]>`
- **Publishing rule**: when creating templates, save samples as `sample-{model-short}-{nn}.png` and make README list verified models, supported models, and sample-to-prompt mappings

## Safety Rules

- Never generate images that violate content policies (violence, sexual content, hate, etc.)
- Never expose the API key in output
- If a user request might trigger safety filters, proactively suggest alternative phrasing
