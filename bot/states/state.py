from aiogram.fsm.state import State, StatesGroup

class Register(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    region = State()
    
class EcoAlert(StatesGroup):
    district = State()
    video = State()
    
class Questions(StatesGroup):
    feedback = State()
    
class FeedbackState(StatesGroup):
    waiting_for_feedback = State()