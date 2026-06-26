import requests
from django.conf import settings


def send_vk_message(user_id, message):

    url = "https://api.vk.com/method/messages.send"
    params = {
        'user_id': user_id,
        'message': message,
        'access_token': getattr(settings, 'VK_ACCESS_TOKEN', ''),
        'v': '5.199',
        'random_id': 0
    }

    try:
        response = requests.post(url, data=params)
        return response.json()
    except Exception as e:
        print(f"Ошибка отправки сообщения в VK: {e}")
        return None


def send_vk_notification(message):

    url = "https://api.vk.com/method/messages.send"
    params = {
        'peer_id': getattr(settings, 'VK_GROUP_ID', ''),
        'message': message,
        'access_token': getattr(settings, 'VK_ACCESS_TOKEN', ''),
        'v': '5.199',
        'random_id': 0
    }

    try:
        response = requests.post(url, data=params)
        return response.json()
    except Exception as e:
        print(f"Ошибка отправки уведомления в VK: {e}")
        return None