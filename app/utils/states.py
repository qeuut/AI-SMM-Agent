from aiogram.fsm.state import StatesGroup, State
from mypyc.ir.ops import SetAttr


class GeneralState(StatesGroup):
    DefaultState = State()

class SchedulePost(StatesGroup):
    WaitScheduleTime = State()


class CreatedPost(StatesGroup):

    WaitMessForPost = State()
    MessForPostReceived = State()

    IsGenerated = State()
    IsEditing = State()
    IsPublishing = State()
    IsPlaning = State()

    AnswerOnQuestionAi = State()


class SetStyleBrand(StatesGroup):
    # стиль
    SelectStyle = State()
    WritesCustomPrompt = State()
    # тон
    SelectCustomStyle = State()
    SelectCustomTone = State()
    # длина поста
    SelectLength = State()
    SelectCustomLength = State()
    # хештеги
    SelectHashtags = State()
    SelectCustomHashtags = State()
    # призыв к действию в постах
    SelectCTA = State()  # СТА - Call to action
    SelectCustomCTA = State()# СТА - Call to action



# class ApplicationForm(StatesGroup):
#     answer = State()
#
# class MenuBackForm(StatesGroup):
#     from_equipment = State()
#     from_application = State()
#
# class GeneralStates(StatesGroup):
#     waiting_faq_question_for_AI = State()