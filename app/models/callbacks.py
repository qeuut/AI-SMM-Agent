from enum import Enum




















































class CallbacksContentPlan(str, Enum):
    CONTENT_PLAN = "content_plan"




class CallbacksNavigation(str, Enum):
    MAIN_MENU = "MainMenu"


class CallbacksPost(str, Enum):
    CREATE_POST = "create_post"
    GENERATE_POST = "generate_post"
    QUESTION_FOR_POST = "question_for_post"
    PUBLISHING_POST = "publishing_post"
    EDIT_CURRENT_POST = "edit_current_post"
    SHOW_POST = "show_post"
    GENERATION_IN_ENY_CASE = "generation_in_eny_case"
    APPLY_EDIT = "apply_edit"
    RETRY_REQUEST_TO_N8N = "retry_request_to_n8n"


class CallbacksPublication(str, Enum):
    PUBLICATION = "publication"
    SCHEDULED_POST = "schedule_post"
    QUEUE_PUBLICATION = "queue_publication"
    PUBLISHED_POST = "published_posts"
    YES_ANSWER = "yes_answer"


class CallbacksSettings(str, Enum):
    SETTINGS = "settings"
    PUBLICATION_MODE_SETTINGS = "publication_mode_settings"
    SELECT_CHANNEL_SETTINGS = "select_channel_settings"
    HELP_SETTINGS = "help_settings"


class CallbacksStatistic(str, Enum):
    STATISTICS = "statistics"


class CallbacksStyle(str, Enum):
    # SUFFIXES
    CAT_SUFFIX = "cat_"
    CAT__SUFFIX = "cat__"

    # PREFIXES
    CUSTOM_PREFIX = "_custom"
    BACK_PREFIX = "_back"

    # MAIN
    MAIN_MENU = ""
    CREATE_POST = ""
    PUBLICATION = ""
    STATISTICS = ""
    STYLE_BRAND = "style_brand"
    CONTENT_PLAN = ""
    SETTINGS = ""
    GENERATE_POST = ""

    # POST FLOW
    PUBLISHING_POST = ""
    QUESTION_FOR_POST = ""
    EDIT_CURRENT_POST = ""
    SCHEDULE_POST = ""
    QUEUE_PUBLICATION = ""
    PUBLISHED_POSTS = ""

    # Категории
    CAT__TONE = "cat__tone"
    CAT__EMOJI = "cat__emoji"
    CAT__LENGTH = "cat__length"
    CAT__HASHTAGS = "cat__hashtags"
    CAT__CTA = "cat__cta"
    CAT__FORMALITY = "cat__formality"
    CAT__BRAND_CHARACTER = "cat__brand_character"
    CAT__BANNED = "cat__banned"
    CAT__ADDRESSING = "cat__addressing"
    CAT__CUSTOM = "cat__custom"
    CAT_BACK = "cat_back"

    # Тональность
    TONE_FRIENDLY = "tone_friendly"
    TONE_EXPERT = "tone_expert"
    TONE_NEUTRAL = "tone_neutral"
    TONE_CUSTOM = "tone_custom"
    TONE_BACK = "tone_back"

    # Эмодзи
    EMOJI_LOTS = "emoji_lots"
    EMOJI_MID = "emoji_mid"
    EMOJI_NONE = "emoji_none"
    EMOJI_CUSTOM = "emoji_custom"
    EMOJI_BACK = "emoji_back"

    # Длина
    LENGTH_LONG = "length_long"
    LENGTH_MID = "length_mid"
    LENGTH_SHORT = "length_short"
    LENGTH_CUSTOM = "length_custom"
    LENGTH_BACK = "length_back"

    # Хэштеги
    HASHTAGS_AUTO = "hashtags_auto"
    HASHTAGS_NONE = "hashtags_none"
    HASHTAGS_CUSTOM = "hashtags_custom"
    HASHTAGS_BACK = "hashtags_back"

    # CTA
    CTA_ALWAYS = "cta_always"
    CTA_SOMETIMES = "cta_sometimes"
    CTA_NEVER = "cta_never"
    CTA_CUSTOM = "cta_custom"
    CTA_BACK = "cta_back"

    # Формальность
    FORMALITY_FORMAL = "formality_formal"
    FORMALITY_NEUTRAL = "formality_neutral"
    FORMALITY_CASUAL = "formality_casual"
    FORMALITY_CUSTOM = "formality_custom"
    FORMALITY_BACK = "formality_back"

    # Характер бренда
    BRAND_CHARACTER_CUSTOM = "brand_character_custom"
    BRAND_CHARACTER_BACK = "brand_character_back"

    # Запрещённые темы
    BANNED_CUSTOM = "banned_custom"
    BANNED_BACK = "banned_back"

    # Обращение
    ADDRESSING_YOU = "addressing_you"
    ADDRESSING_VY = "addressing_vy"
    ADDRESSING_NEUTRAL = "addressing_neutral"
    ADDRESSING_CUSTOM = "addressing_custom"
    ADDRESSING_BACK = "addressing_back"


class CallbacksOther(str, Enum):
    BACK = "back"
    CUSTOM = "custom"
