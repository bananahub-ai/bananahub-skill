# Profile: Photo (写实摄影)

## Trigger Keywords

照片、写实、人像、肖像、风景、街拍、美食摄影、纪实、抓拍、摄影、真实感、photo、portrait、landscape、风光

## Reference Template (Google Official)

Follow this structural pattern when building enhanced prompts:

```
A photorealistic [shot type] of [subject], [action or expression], set in [environment].
The scene is illuminated by [lighting description], creating a [mood] atmosphere.
Captured with [camera/lens].
```

Not every element needs to be present — only fill in what's relevant and what the user hasn't specified.

## Enhancement Dimensions

After base optimization, check and fill in the following dimensions as needed (only add what the user hasn't mentioned):

### 1. Style Anchor
- Always prepend "photorealistic" or "a photograph of" for photo-intent prompts — without this, Gemini may drift toward illustrative rendering
- This is the single most important word for photo-quality output

### 2. Lens Language & Composition
- No composition specified → keep framing generic unless the shot type is strongly implied by the request
- Shot types: close-up, medium shot, full body shot, wide angle, telephoto, macro, bird's eye view, low angle, Dutch angle, over-the-shoulder
- Focal length reference (optional, for precise control):
  - 24-35mm — street photography, environmental portraits, architecture (wide angle)
  - 50mm — general purpose, natural perspective (standard lens)
  - 85mm — portrait sweet spot (portrait lens, shallow DoF)
  - 135-200mm — telephoto compression, sports, wildlife
- Composition guidance (apply when it enhances the shot):
  - Rule of thirds: "subject positioned at the right third of the frame"
  - Leading lines: "converging lines drawing the eye toward the subject"
  - Framing: "subject framed by archway / doorway / foliage"
  - Foreground interest: "foreground elements adding depth"

### 3. Action / Pose
- What is the subject doing? Specify a natural action or expression
- Portraits: "looking directly at camera", "gazing into the distance", "laughing naturally"
- People in scenes: "reading a book", "walking through rain", "leaning against a wall"
- Animals: "mid-leap", "curled up sleeping", "tilting head curiously"
- If the user hasn't mentioned an action, do not invent one unless it is already obvious from the scene description

### 4. Environment / Setting
- Describe the environment where the scene takes place
- Indoor: "cozy café with worn wooden tables", "bright modern office with floor-to-ceiling windows"
- Outdoor: "rain-soaked urban street", "misty mountain trail at dawn", "sun-drenched Mediterranean terrace"
- Weather/atmosphere: fog, rain, snow, dust particles, haze — these add depth and dimensionality

### 5. Lighting Description
- No lighting specified → omit it unless the scene already implies a clear lighting condition
- Outdoor: golden hour, blue hour, soft natural lighting, overcast diffused light, harsh midday sun
- Indoor: soft window light, studio lighting, warm ambient light
- Night: neon lights, streetlamp glow, moonlight
- Time-of-day markers are more precise than generic terms: "blue hour light" > "natural light"

### 6. Depth of Field
- Portrait / close-up → shallow depth of field is an optional refinement, not a default requirement
- Landscape / architecture → deep focus may be helpful when the user wants overall clarity
- Product → slightly blurred background is only appropriate when the user wants a photographic product scene rather than catalog clarity

### 7. Film / Sensor Simulation (optional, advanced)
- Dramatically shifts color rendering — use when the user wants a specific photographic look:
  - Kodak Portra 400 → warm skin tones, soft pastel highlights
  - Fujifilm Velvia → vivid saturated colors, rich greens and blues
  - Kodak Tri-X 400 → classic black and white, rich grain
  - Cinestill 800T → tungsten cinema look, halation around highlights
- Camera body hints: "shot on Canon 5D Mark IV", "Leica M10 aesthetic"
- Only add when user implies a specific aesthetic or when it strongly complements the scene

### 8. Material & Texture (primarily for close-up / still life scenes)
- Explicitly describe key materials to enhance realism: weathered wood, smooth ceramic, translucent silk, brushed metal, matte finish
- Only add material descriptions when the subject has prominent texture features

### 9. Mood & Color Tone
- Mood and color tone can follow scene emotion when it is already evident from the request
- Do not add proactively — only supplement when the user or scene has a clear emotional direction

## Prompt Element Order

When building the enhanced prompt, follow this order for best results:
1. Style anchor ("photorealistic")
2. Shot type / composition
3. Subject + action
4. Environment / setting
5. Lighting
6. Technical details (DoF, film simulation, material)
7. Mood / color tone

## Example

**User input**: 一个女孩在咖啡厅看书

**Base optimization**: A girl reading a book in a café

**Enhanced result**: A photorealistic medium shot of a girl reading a book in a café, natural indoor lighting, realistic colors, clear focus on the subject

## Aspect Ratio

- Portrait / character → 3:4 or 9:16
- Landscape / panorama → 16:9 or 3:2
- Square / social media → 1:1
- Cinematic → 16:9

## Behavioral Notes

- Do not add overly dramatic lighting unless the user's description implies it
- Maintain realism; avoid adding artistic filter vocabulary
- Do not add specific appearance details (hair color, skin tone, etc.) to people unless the user mentioned them
- The word "photorealistic" is critical — always include it for photo-intent prompts
- Do not add lens, bokeh, action, or time-of-day details unless they are requested or clearly implied
- Aim for 40-80 words in the final enhanced prompt — enough detail for Gemini without overloading
- Write in natural sentence form, not comma-separated tag lists — Gemini processes natural language better
