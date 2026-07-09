# сторонние
import logging

# сервисы
from AI_SMM_AGENT.app.services.n8n_client import n8n_request
from AI_SMM_AGENT.app.services.post_service import sort_answer_n8n
from AI_SMM_AGENT.app.services.get_photos_from_draft import get_photos_from_draft

# модели
from AI_SMM_AGENT.app.models.data_models import DraftPost
from AI_SMM_AGENT.app.models.n8n_exceptions import N8NError
from AI_SMM_AGENT.app.models.n8n import N8NStatus, N8NResult

# aiogram
from aiogram.types import InlineKeyboardMarkup

# кнопки
from AI_SMM_AGENT.app.keyboards.general_inline import (
    draft_post, question_for_publication,
    pre_procedural_actions, publishing_post,
    clarifying_question, skip_question_or_back,
    edit_post_back_or_generate, retrying_request_and_back,
    manage_current_post, edit_post_back
)
from AI_SMM_AGENT.app.keyboards import back_to


logger = logging.getLogger(__name__)



async def process_n8n_status(n8n_response, draft_dict) -> tuple[N8NResult, InlineKeyboardMarkup]:
    result = sort_answer_n8n(n8n_response)

    if result.status == N8NStatus.SUCCESS:
        draft = DraftPost.model_validate(draft_dict)
        draft.selected_media_ids = result.selected_file_ids
        photos = get_photos_from_draft(draft, draft.model_dump())
        markup = pre_procedural_actions()

    elif result.status == N8NStatus.REJECTION:
        markup = clarifying_question()
    else:
        markup = back_to() # ДЛЯ --- question, error, unknown, connected

    return result, markup


async def process_response_n8n(payload) -> tuple[bool, str, bool]:
    try:
        response = await n8n_request.send_payload(payload)
    except N8NError as e:
        logger.error(f"N8N недоступен: {e}")
        return False, "Ошибка, к сожалению сервис недоступен...", True # если True то -> retrying_request_and_back()

    if response is None:
        logger.error("Нет ответа от N8N")
        return False, "Ошибка, к сожалению сервис недоступен...", True # если True то -> retrying_request_and_back()

    logger.info(f"N8N response: {response}")

    return True, response, False


async def process_n8n_response(payload: dict, draft_dict: dict) -> tuple[bool, any, bool] | tuple[bool, any, InlineKeyboardMarkup]:
    success, n8n_response, buttons_status = await process_response_n8n(payload)

    if not success:
        return False, n8n_response, buttons_status

    result, markup = await process_n8n_status(n8n_response=n8n_response,draft_dict=draft_dict)

    return True, result, markup



















