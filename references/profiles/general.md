# Profile: General (通用兜底)

## Trigger Condition

When user input cannot be clearly matched to any other Profile (photo, illustration, diagram, text-heavy, minimal, sticker, 3d, product, concept-art), fall back to this Profile.

## Behavior

**Perform base optimization + light structural enhancement — but no style/mood/lighting additions.**

Base optimization includes:
1. Format correction (tag-style → natural language)
2. Smart translation (translate descriptions, preserve in-image text)
3. Structuring (subject first)

Light structural enhancement (safe improvements that never distort intent):
4. Ensure the prompt is a complete descriptive sentence, not a bare noun phrase
5. Make spatial relationships explicit: "a cat lying on top of a keyboard" > "a cat on a keyboard"
6. Specify quantity when ambiguous: "a single cat" when only one is intended
7. Infer and suggest an appropriate aspect ratio based on content (scene → 16:9, character → 3:4, square → 1:1)

## Design Principle

- Prefer less optimization over distorting user intent
- User didn't specify a style → don't add a style
- User didn't specify lighting → don't add lighting
- Faithfully convey the user's description; only perform format, language, and structural improvements
- Light structural improvements (complete sentences, explicit spatial relationships, quantity) are always safe

## Example

**User input**: 一只猫趴在键盘上

**Base optimization**: Create an image of a single cat lying on top of a computer keyboard

**Will NOT add**: any style, lighting, composition, or atmosphere descriptions

**May suggest**: aspect ratio 4:3 (fits the scene proportions)

## When to Upgrade to Another Profile

If during analysis you discover clear style signals (e.g., "写实的", "动漫风格的", "画一个流程图"), reclassify to the corresponding Profile instead of staying in general.

General is the fallback choice, not the default choice. Always try to match a specific Profile first.

## Profiles Available for Matching

photo, illustration, diagram, text-heavy, minimal, sticker, 3d, product, concept-art
