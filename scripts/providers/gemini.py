"""Gemini image provider adapter."""


def try_generate(client, types_module, model, prompt, aspect_ratio, image_size=None):
    """Attempt Gemini image generation with a single model."""
    image_config_kwargs = {"aspect_ratio": aspect_ratio}
    if image_size:
        image_config_kwargs["image_size"] = image_size

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types_module.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types_module.ImageConfig(**image_config_kwargs),
        ),
    )

    if not response.candidates or not response.candidates[0].content.parts:
        return None, "No image generated. The model may have refused the prompt due to content policy."

    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            return part, None

    text_parts = [p.text for p in response.candidates[0].content.parts if hasattr(p, "text") and p.text]
    error_msg = "No image in response."
    if text_parts:
        error_msg += f" Model said: {' '.join(text_parts)}"
    return None, error_msg


def try_edit(client, types_module, model, prompt, input_images, image_size=None):
    """Attempt Gemini image editing with a single model."""
    contents = [prompt] + input_images
    image_config = types_module.ImageConfig(image_size=image_size) if image_size else None
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types_module.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=image_config,
        ),
    )

    if not response.candidates or not response.candidates[0].content.parts:
        return None, [], "No response generated. The model may have refused the prompt due to content policy."

    image_part = None
    text_parts = []
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            image_part = part
        elif hasattr(part, "text") and part.text:
            text_parts.append(part.text)

    if not image_part:
        error_msg = "No image in response."
        if text_parts:
            error_msg += f" Model said: {' '.join(text_parts)}"
        return None, text_parts, error_msg

    return image_part, text_parts, None
