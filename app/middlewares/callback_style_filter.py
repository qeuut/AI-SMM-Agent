STYLE_PREFIXES = ("tone_", "emoji_", "length_", "hashtags_", "cta_", "formality_", "addressing_")

class CallbackFilters:
    @staticmethod
    def is_style(data: str) -> bool:
        if not data:
            return False
        return data.startswith(STYLE_PREFIXES) and not data.endswith(("_custom", "_back"))