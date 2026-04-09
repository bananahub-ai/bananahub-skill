# Initialization Flow

When the user runs `init`, actively diagnose and fix issues — don't just report status.

## Step 1: Run diagnostics

Run `python3 {baseDir}/scripts/bananahub.py init --skip-test` first (skip API test until basics are ready). Parse the JSON output.

## Step 2: Fix missing dependencies automatically

If `dependencies.ok` is false:
- **Directly run** `python3 -m pip install --user google-genai pillow` to install them
- Do not just tell the user to install — install for them
- If install fails because the environment is externally managed, show the error and suggest using a virtual environment

## Step 3: Fix missing config file

If `config_source.ok` is false (no config found anywhere):
1. Ask the user **which access path they want**:
   - **Recommended**: Google AI Studio / Gemini Developer API
   - **Alternative**: Gemini-compatible relay / proxy (`base_url + key`)
   - **OpenAI-style endpoint**: OpenAI-compatible (`base_url + key`)
   - **Enterprise**: Vertex AI (`project + location + ADC` or Vertex API key)
2. If they choose **Google AI Studio**:
   - Ask for their Google AI Studio key
   - Key management URL: https://aistudio.google.com/apikey
   - Pricing note: usage may be free or paid depending on Google's current pricing/quota policy, the selected model, and the user's account/region
   - Persist it with:
     ```bash
     python3 {baseDir}/scripts/bananahub.py config set --provider google-ai-studio --api-key "<user's key>"
     ```
3. If they choose a **Gemini-compatible relay / proxy**:
   - Ask for both their proxy key and `base_url`
   - If the vendor docs show a full endpoint ending in `/v1beta`, the user can paste it directly; BananaHub normalizes the trailing API version automatically
   - Persist them with:
     ```bash
     python3 {baseDir}/scripts/bananahub.py config set --provider gemini-compatible --base-url "<relay base url>" --api-key "<user's key>"
     ```
4. If they choose an **OpenAI-compatible** endpoint:
   - Ask for both their endpoint `base_url` and API key
   - If they only have a bare host, BananaHub will try to append `/v1`; for Google's official OpenAI-compatible endpoint, it resolves to `/v1beta/openai`
   - Persist them with:
     ```bash
     python3 {baseDir}/scripts/bananahub.py config set --provider openai-compatible --base-url "<openai-compatible base url>" --api-key "<user's key>"
     ```
   - Note: current runtime supports `generate`, `models`, and `init` healthcheck on this path, but not `edit`
5. If they choose **Vertex AI**:
   - Ask whether they want `adc` or `api_key`
   - For `adc`, ask for `project` and `location`, then persist with:
     ```bash
     python3 {baseDir}/scripts/bananahub.py config set --provider vertex-ai --auth-mode adc --project "<gcp-project>" --location "<location>"
     ```
   - For `api_key`, persist with:
     ```bash
     python3 {baseDir}/scripts/bananahub.py config set --provider vertex-ai --auth-mode api_key --api-key "<vertex api key>"
     ```
6. Ask whether they want a default model pinned. If yes, run:
   ```bash
   python3 {baseDir}/scripts/bananahub.py config set --model "<model_id>"
   ```
7. If they later want to revert from relay/proxy mode back to Google's default endpoint, run:
   ```bash
   python3 {baseDir}/scripts/bananahub.py config set --clear-base-url
   python3 {baseDir}/scripts/bananahub.py config set --provider google-ai-studio
   ```

## Step 4: Fix missing API key

If config source exists but `api_key.ok` is false:
- A config file exists but `GEMINI_API_KEY` / `GOOGLE_API_KEY` / `api_key` is empty or missing
- Ask the user which path they are using: `google-ai-studio`, `gemini-compatible`, `openai-compatible`, or `vertex-ai`
- Then write/update the key via:
  ```bash
  python3 {baseDir}/scripts/bananahub.py config set --provider "<provider>" --api-key "<user's key>"
  ```
- If they are using `gemini-compatible` or `openai-compatible` and `base_url` is also missing, ask for it and persist it in the same command.
- If they are using `vertex-ai` in `adc` mode, an API key is not required; instead check `project`, `location`, and ADC readiness.

## Step 5: Run full diagnostics with API test

After dependencies and config are in place:
- Run `python3 {baseDir}/scripts/bananahub.py init` (without --skip-test)
- If API test passes → report success, environment is ready
- If API test fails:
  - **Auth error (401/403)**: API key is invalid — ask user to double-check and provide a new one
  - **Network error**: base URL may be wrong, or proxy is down — show the current `provider` and `base_url` and ask user to verify
  - **Other error**: show the error message and suggest the user check their configuration

## Step 6: Report final status

Show a clear summary:
```
✅ 依赖: google-genai ✓, pillow ✓
✅ 配置: [实际命中的配置源] ✓
✅ Provider: google-ai-studio ✓
✅ API Key: AIzaSy...xxxx ✓
✅ 端点: https://... ✓
✅ 连通性: API 响应正常 ✓

🎉 环境已就绪，可以开始生图！试试: /bananahub 一只猫趴在键盘上
```

Or if issues remain:
```
✅ 依赖: google-genai ✓, pillow ✓
✅ 配置: [实际命中的配置源] ✓
✅ Provider: openai-compatible ✓
❌ 连通性: [error message]

请检查 provider、API Key 和端点地址是否正确。
```
