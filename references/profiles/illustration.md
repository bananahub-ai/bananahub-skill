# Profile: Illustration (插画与漫画)

## Trigger Keywords

插画、漫画、动漫、卡通、手绘、二次元、Q版、赛博朋克风、像素画、扁平化、矢量、水彩画、油画、素描、涂鸦、anime、manga、cartoon、pixel art、comic、同人、立绘、浮世绘、国风

## Enhancement Dimensions

After base optimization, check and fill in the following dimensions as needed (only add what the user hasn't mentioned):

### Art Style
- User mentions "动漫/二次元" → anime style / manga style
- User mentions "卡通" → cartoon illustration
- User mentions "手绘" → hand-drawn illustration
- User mentions "水彩" → watercolor painting
- **No explicit style → do not infer a specific style**; instead offer options during enhancement confirmation (e.g., anime / digital illustration / watercolor / cartoon) and let the user choose
- Never override a style the user has already specified
- **Art movement anchoring**: when the user mentions a general category, suggest specific schools for better results — e.g., "Japanese illustration" could mean anime, ukiyo-e, or Studio Ghibli style. "Inspired by [art movement/studio]" is one of the most powerful prompt techniques for Gemini.

### Linework & Rendering Style
- Anime → clean lines, cel-shading
- Watercolor → soft edges, visible brushstrokes, wet-on-wet blending
- Oil painting → visible impasto brushstrokes, rich layered colors, canvas texture
- Sketch → pencil strokes, hatching, grayscale
- Pixel art → visible pixels, limited color palette, retro aesthetic
- Flat design → flat colors, no gradients, no shadows, geometric shapes, clean vector lines, bold color blocking
- Ink / line art → bold ink outlines, variable line weight, minimal color
- Comic book (Western) → bold ink outlines, Ben-Day dots, dramatic shadows, dynamic panel composition
- Isometric illustration → isometric perspective, 30-degree angle, no vanishing point, clean geometric shapes

### Style Mixing
- Gemini handles style blending well — guide users when they want hybrids:
  - Use pattern: "X style with Y elements" or "X meets Y"
  - Examples: "watercolor meets cyberpunk", "pixel art with modern color palette", "anime style but with oil painting textures"

### Color Scheme
- No color scheme specified → infer reasonable default from art style
- Anime → vibrant colors (unless mood is dark)
- Watercolor → soft pastel tones
- Cyberpunk → neon colors against dark background
- Oil painting → rich, warm, saturated tones
- Do not proactively restrict colors; only supplement when the style has a strong color tendency

### Composition & Framing
- Dynamic composition: "dramatic diagonal lines, dynamic pose with foreshortening"
- Centered / iconic: "subject centered, symmetrical composition"
- Vignette: "circular framing with fading edges"
- For character illustrations: consider implied camera angle — "slight low angle for heroic feel", "high angle for vulnerability"

### Background Treatment
- Character design / standing illustration → suggest simple clean background / white background
- Scene illustration → supplement environment details based on description
- Comic panel → use the Comic Panel Template below

### Emotional Storytelling
- Illustrations benefit from explicit mood/narrative descriptions:
  - "sense of wonder and discovery", "lonely melancholic atmosphere"
  - "a moment captured just as..." (narrative descriptions work well with Gemini)
  - "triumphant and powerful", "peaceful and serene"
- Only add when it enhances the scene without contradicting user intent

## Comic Panel Template

For manga/comic panel requests, use this structured template (from Google official guidance):

```
A single comic book panel in a [art style] style. In the foreground, [character description and action].
In the background, [setting details]. The panel has a [dialogue/caption box] with the text "[Text]".
The lighting creates a [mood] mood.
```

- Separate foreground and background descriptions explicitly
- Dialogue box text follows in-image text rules (preserve original language, wrap in quotes)
- Specify panel shape if relevant: "tall vertical panel", "wide horizontal panel", "full-page splash"

## Example

**User input**: 一个拿着魔法杖的小女巫

**Base optimization**: A little witch holding a magic wand

**Enhanced result (when user hasn't specified a style, offer options)**:
> 检测到插画类意图，但未指定画风。建议选择：
> 1. anime style — 日系动漫风
> 2. digital illustration — 数字插画
> 3. watercolor painting — 水彩风格
> 4. cartoon illustration — 欧美卡通

**After user selects anime**: A little witch holding a magic wand in anime style, cheerful expression with sparkling eyes, dynamic pose mid-spell-cast, vibrant colors with clean cel-shading lines, simple gradient background with sparkle effects, whimsical and magical atmosphere

## Known IP Character Handling

When the subject is a well-known character (from anime, games, movies, etc.):

- **Do NOT describe their appearance** — the model already knows what Tachikoma, Pikachu, Totoro, etc. look like
- **Only add**: art style, rendering technique, color palette tendency, background treatment, mood
- **Rationale**: vague descriptions like "round body, optical eyes" can override the model's correct internal knowledge and introduce visual artifacts (e.g., human-like eyes on a robot)

**Example — Known IP character**:

User input: tachikoma（攻壳机动队）头像，像素风格，可爱

- Good: `Create an image of a cute Tachikoma from Ghost in the Shell as a profile avatar, pixel art style with visible pixels and limited color palette, retro pixel aesthetic, clean simple background, cheerful and playful mood`
- Bad: `...the iconic blue spider-like robot with round body and optical eyes rendered in chibi proportions...` (vague appearance description distorts the character)

## Non-Humanoid "Cute" Expression

For robots, vehicles, creatures, and other non-humanoid subjects, "cute/可爱" should be conveyed through:
- Rounded shapes, soft curves, compact proportions
- Bright or pastel color palette
- Soft, warm lighting
- Playful composition or pose

Do NOT add: human facial features (eyes, mouth, smile), chibi/Q版 proportions, or anthropomorphic expressions. These cause the model to render human-like faces on non-human entities.

## Aspect Ratio

- Character illustration → 3:4 or 2:3 (portrait)
- Scene / landscape illustration → 16:9 (wide)
- Square / avatar → 1:1
- Comic panel → varies by panel shape

## Behavioral Notes

- Illustration styles are extremely diverse; when uncertain, prefer not adding a style keyword and let the user choose
- Never apply photographic lens language (85mm lens, bokeh) to illustrations — use illustration-specific composition terms instead
- Text in manga/anime is typically a visual element — preserve original language, do not translate
- **When unsure if a descriptor is unambiguous, omit it** — a missing detail is better than a misleading one
- Write in natural descriptive sentences, not comma-separated tag lists
- Aim for 40-80 words in the final enhanced prompt
