# Profile: Sticker / Emoji (贴纸与表情包)

## Trigger Keywords

表情包、贴纸、meme、梗图、emoji、sticker、LINE、微信表情、聊天表情、头像贴纸、reaction

## Enhancement Dimensions

After base optimization, check and fill in the following dimensions as needed (only add what the user hasn't mentioned):

### Outline & Edge Treatment (highest priority)
- Do not force a specific outline treatment unless the user asks for sticker-platform / die-cut / LINE-style output
- Kawaii/LINE style → rounded bold outline, white border margin
- Meme/reaction → optional outline; focus on expression clarity
- Use a clean simple background only when needed for sticker readability or export intent; do not always force white background

### Expression & Emotion
- The emotion IS the content — make it the central focus of the prompt
- Exaggerated facial expressions: "wide sparkling eyes, huge open-mouth smile", "comically angry with steam puffs"
- Body language amplification: "arms thrown up in celebration", "slumped over in defeat"
- For non-humanoid subjects (animals, objects): express emotion through body posture, shape distortion, motion lines — NOT by adding human facial features (see Illustration profile's Non-Humanoid rules)

### Size & Readability
- Stickers display at small sizes (128x128 to 512x512) — composition must read clearly at thumbnail scale
- Simplify details: "simple rounded shapes, minimal fine detail, bold visual elements"
- Limit text: if text is included, keep it to 1-4 characters/words maximum, bold outlined text
- High contrast between subject and background

### Art Style
- No style specified → keep the sticker style generic, or offer kawaii / LINE / meme as options instead of auto-picking one
- Available styles:
  - Kawaii (可爱风) → round shapes, pastel accents, sparkling effects
  - LINE style → clean vector lines, flat colors, consistent character proportions
  - Meme/reaction → photographic base with text overlay, or exaggerated cartoon
  - Chibi → 2-3 head proportions, oversized head, tiny body (appropriate here, unlike general illustration)
  - Emoji style → flat design, geometric shapes, universal expressions

### Series Consistency (for multi-sticker requests)
- When user requests a set of stickers: "consistent character design across all images, same art style, same color palette, same outline weight"
- Specify the character's key visual traits once: "a round orange cat with a red collar"
- Each sticker varies only in expression/pose/action

## Aspect Ratio

- Default: 1:1 (square, standard for most sticker platforms)
- Do not suggest other ratios unless user requests

## Example

**User input**: 画一个开心的柴犬贴纸

**Base optimization**: A happy Shiba Inu sticker

**Enhanced result**: Create an image of a happy Shiba Inu sticker, kawaii style, bold black outline with die-cut edge, exaggerated cheerful expression with sparkling eyes and wide open smile, tail wagging energetically, simple rounded shapes, vibrant warm colors, clean white background, 1:1 aspect ratio

## Behavioral Notes

- Stickers are a legitimate use case for chibi proportions and exaggerated expressions — unlike the general illustration profile, anthropomorphic cuteness IS appropriate here
- For character stickers, prioritize expression clarity over detail richness
- Do not force white background unless the user wants platform-ready sticker output or a clean cut-out look
- Meme-style stickers may include text — use Impact font or bold outlined text, placed at top/bottom
- When user requests a "set" or "series" (一组/一套), generate one at a time but maintain consistency instructions in every prompt
