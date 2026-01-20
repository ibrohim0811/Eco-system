import uuid
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()


def create_user_from_bot(
    telegram_id: int,
    phone: str,
    district: str,
    full_name: str,
    tg_username: str | None = None
):
    
    if User.objects.filter(telegram_id=telegram_id).exists():
        return None, None, None  

    
    user_uuid = uuid.uuid4()

   
    parts = full_name.strip().split(" ", 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""

    
    if tg_username:
        username = tg_username
        if User.objects.filter(username=username).exists():
            username = f"{tg_username}_{user_uuid.hex[:5]}"
    else:
        username = f"user_{user_uuid.hex[:6]}"

   
    raw_password = str(user_uuid).split("-")[-1]
    hashed_password = make_password(raw_password)

   
    user = User.objects.create(
        username=username,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        district=district,
        telegram_id=telegram_id,
        uuid=user_uuid,
        password=hashed_password
    )

    return user, username, raw_password
