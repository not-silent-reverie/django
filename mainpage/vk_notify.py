import requests
from django.conf import settings

import requests
from django.conf import settings


def send_vk_message(user_id, message):
    url = "https://api.vk.com/method/messages.send"
    params = {
        'user_id': user_id,
        'message': message,
        'access_token': settings.VK_ACCESS_TOKEN,
        'v': '5.199',
        'random_id': 0
    }

    try:
        response = requests.post(url, data=params)
        print(f"VK send response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return None