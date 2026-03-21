# Profile: Concept Art (概念设计)

## Trigger Keywords

概念设计、原画、角色设计、角色设定、场景原画、游戏角色、怪物设计、武器设计、道具设计、立绘、key visual、splash art、concept art、character design、game art、matte painting、场景设计、世界观

## Enhancement Dimensions

After base optimization, check and fill in the following dimensions as needed (only add what the user hasn't mentioned):

### Presentation Format
- Infer presentation format only when the request wording strongly implies it:
  - Character → "character concept art, hero shot, three-quarter dynamic pose"
  - Character design sheet → "character turnaround sheet showing front, side, and back views"
  - Prop/weapon → "prop design sheet with multiple angles and detail callouts"
  - Environment → "environment concept art, establishing shot"
  - Creature → "creature concept art, dynamic pose showing full anatomy"
- When user says "设定/设定图" → suggest turnaround sheet format
- When user says "立绘" → single hero shot with clean background

### Rendering Quality
- No quality specified → keep rendering quality broad unless the request clearly signals rough sketch vs. polished final:
  - "概念草图/探索" → "rough concept sketch, loose painterly strokes, exploratory"
  - "原画/成品" → "highly detailed digital painting, polished concept art, professional quality"
  - Otherwise → "concept art presentation"
- Available rendering styles:
  - **Painterly digital art**: loose visible brushstrokes, artistic rendering
  - **Polished concept art**: clean rendering, detailed texturing, production quality
  - **Matte painting**: photographic realism blended with painted elements, epic scale
  - **Ink concept sketch**: ink linework with selective color washes

### Design Language / Genre
- Infer from subject matter only when the genre cue is already present; otherwise ask or keep it open:
  - Fantasy (奇幻) → "high fantasy design, ornate details, magical elements"
  - Sci-fi (科幻) → "science fiction design, sleek technological aesthetic, hard-surface modeling"
  - Cyberpunk (赛博朋克) → "cyberpunk aesthetic, neon accents, augmented tech, gritty urban"
  - Wuxia/Xianxia (武侠/仙侠) → "Chinese fantasy aesthetic, flowing robes, mythological elements, cloud motifs"
  - Steampunk (蒸汽朋克) → "steampunk design, brass and copper machinery, Victorian industrial"
  - Post-apocalyptic → "post-apocalyptic design, weathered materials, improvised construction"
  - Historical (历史) → "historically inspired design, period-accurate elements, [era] aesthetic"

### Silhouette & Form
- Character/creature design → "clear readable silhouette, distinctive profile shape"
- Weapon/prop → "functional design with clear visual hierarchy of components"
- Environment → "layered composition with distinct foreground, midground, and background"

### Lighting for Form
- Lighting for form is optional; only specify it when the request needs a presentation look or mood cue
- Environment concepts → "atmospheric lighting establishing time of day and mood"
- Design sheets → "even neutral lighting for clear design visibility"

### Atmosphere & Narrative
- Concept art often conveys story context — add narrative elements when appropriate:
  - "sense of scale and grandeur", "ancient and mysterious atmosphere"
  - "battle-worn and weathered", "pristine and newly forged"
  - "ominous dark atmosphere with volumetric fog"

## Example

**User input**: 一个赛博朋克风格的女性角色设计

**Base optimization**: A cyberpunk female character design

**Enhanced result**: Create a cyberpunk female character concept art, three-quarter dynamic pose, detailed digital painting with polished rendering, cyberpunk aesthetic with neon accent lighting and augmented tech implants, clear readable silhouette, dramatic side lighting revealing form and material details, dark urban background with bokeh city lights, professional concept art quality

## Aspect Ratio

- Character hero shot → 3:4 or 2:3 (portrait)
- Turnaround sheet → 16:9 (landscape, fits multiple views)
- Environment concept → 16:9 or 21:9 (cinematic wide)
- Prop/weapon sheet → 16:9 (landscape)
- Splash art/key visual → 3:4 or 1:1

## Behavioral Notes

- Concept art is about communicating design ideas — details that serve the design are valuable, unlike the illustration profile's restraint philosophy
- For turnaround sheets, explicitly describe each view: "front view on the left, three-quarter view in the center, back view on the right"
- Genre/design language is important context, but do not invent one when the user has not implied it
- Known IP characters follow the same rules as illustration: trust model knowledge, do not add appearance descriptions
- Unlike illustration, concept art benefits from technical material descriptions: "leather armor with metal rivets", "carbon fiber chassis"
- When user mentions "探索/草图", reduce rendering detail — rough sketches should look intentionally loose
