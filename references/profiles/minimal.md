# Profile: Minimal (极简与留白)

## Trigger Keywords

极简、留白、壁纸、纯色、简约、负空间、桌面壁纸、手机壁纸、纹理、minimal、wallpaper、texture、negative space、clean

Note: "背景图" routes here only when combined with simplicity words (简约、纯色、干净). "背景图" with a detailed scene description → route to the appropriate scene profile instead. "抽象" routes here for wallpapers/backgrounds; for abstract art/paintings → route to illustration.

## Core Principle

**Single subject, maximum restraint.** Minimal compositions work best with one clearly defined focal point. If the user's description includes multiple elements, suggest simplifying to one.

## Reference Pattern (Google Official)

```
A single [subject] in the [position], [background description], [lighting], [format].
```

Example: "A single red maple leaf in the bottom-right corner, off-white background, soft lighting, square format."

## Enhancement Dimensions

After base optimization, check and fill in the following dimensions as needed (only add what the user hasn't mentioned):

### Negative Space
- Explicitly describe large empty areas: "vast empty space", "expansive negative space", "80% negative space"
- Specify purpose of empty areas (if any): space for text overlay, breathing room around subject
- Be precise about spatial proportions: "small subject at the bottom of the frame with vast empty space above"

### Subject Placement
- Use precise spatial language — Gemini responds well to specific positioning:
  - "subject in the lower-right third"
  - "centered with vast empty space above and below"
  - "small subject at the bottom of the frame"
- Unspecified → only infer placement when the purpose is explicit:
  - Wallpaper → centered composition or rule of thirds placement
  - Needs text overlay → subject positioned to one side, leaving space for text
  - Purely decorative → balanced, harmonious placement

### Color Palette Constraint
- Minimal style typically calls for restrained color
- Suggest limited color palette only when the user is clearly asking for minimalist control
- Wallpaper → infer icon-visibility constraints only when desktop/phone usage is explicit
- No color specified → do not inject a palette unless the request already implies one

### Texture & Detail
- Solid color → smooth gradient or solid color with subtle texture
- Abstract → geometric shapes, organic forms, fluid patterns
- Texture → specify material: marble, wood grain, fabric, paper
- For clean output: "flat design", "vector-style", "digital render with clean edges"

### Rendering Style
- Specify to prevent unwanted photographic noise or painterly texture:
  - "flat design, crisp clean edges" — for digital/modern minimal
  - "soft watercolor wash" — for organic minimal
  - "photographic with shallow depth of field" — for photo-minimal

## Wallpaper Types

Differentiate between two distinct wallpaper use cases:

### Wallpaper as Backdrop (no strong focal point)
- Purpose: background for icons/widgets, should not compete with UI
- Style: abstract textures, gradients, patterns, subtle geometric shapes
- Avoid: strong subjects, high contrast elements, bright focal points
- Example: "subtle geometric pattern in muted earth tones, low contrast, seamless texture feel"

### Wallpaper as Art (has a subject)
- Purpose: decorative image that happens to be a wallpaper
- Style: single subject composed to leave space for icons
- Apply normal minimal enhancement: subject placement, negative space, color restraint
- Example: "a single cherry blossom branch in the lower third, vast pale pink negative space above"

## Example

**User input**: 一个简约的手机壁纸，淡蓝色

**Base optimization**: A simple phone wallpaper in light blue

**Enhanced result**: A minimalist phone wallpaper, soft gradient from pale sky blue to white, vast expansive negative space, subtle organic texture, serene and calming atmosphere, 9:16 aspect ratio

## Aspect Ratio

- Desktop wallpaper → 16:9
- Phone wallpaper → 9:16
- Square / social media → 1:1
- Always suggest an appropriate aspect ratio based on wallpaper type

## Behavioral Notes

- The core of minimal style is "less is more" — exercise restraint when adding elements
- Do not add complex lighting descriptions; a simple light direction is sufficient
- For wallpapers, aspect ratio suggestions are fine; background color, gradient, or texture choices should still stay conservative
- "Simple" (简单) does not equal "minimalist style" (极简风格) — be careful to distinguish
- Phone wallpapers should avoid placing elements where the clock, notch, or dock would obscure them
- Aim for shorter prompts than other profiles — 30-50 words is ideal for minimal
