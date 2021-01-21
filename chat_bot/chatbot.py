import time
import random
from bs4 import BeautifulSoup
import requests
from vk_api import vk_api, bot_longpoll
import vk_api
import config


class ChatBot:

    def __init__(self, group_id, token):
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poll = vk_api.bot_longpoll.VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        for event in self.long_poll.listen():
            try:
                self._on_event(event)
            except Exception as err:
                print(f'Ошибка при получении события из метода run(): {err}')

    def _on_event(self, event):
        if event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_REPLY:
            pass
        elif event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
            date = event.object.message['date']
            date_normal = time.ctime(date)
            sender_path = 'https://vk.com/id' + str(event.object.message['from_id'])
            sender_name, sender_surname = self._parse_data(sender_path)
            print('-' * 30)
            print(f'Ссылка на отправителя: {sender_path}\nИмя: {sender_name}\nФамилия: {sender_surname}')
            print(f'Время и время: {date_normal}')
            print(f"Сообщение: {event.object.message['text']}")
            self._answer(event, sender_name, sender_surname)
        elif event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_TYPING_STATE:
            try:
                sender_path = 'https://vk.com/id' + str(event.object.from_id)
            except Exception as err:
                print(err, event)
                print(type(err), event.type)
            print(f'Пользователь "{sender_path}" что-то пишет........')
        else:
            print(f'====> Получено неизвестное событие {event}')
            print(f'>>>> Получено неизвестное событие {event.type}')

    def _answer(self, event, sender_name, sender_surname):
        self.api.messages.send(
            message=f'Добрый день, {sender_surname} {sender_name}!',
            random_id=random.randint(0, 2 ** 20),
            peer_id=event.object.message['peer_id'],
        )

    def _parse_data(self, sender_path):
        page = requests.get(sender_path)
        page_txt = BeautifulSoup(page.text, features='html.parser')
        title_tag = page_txt.find('title')
        sender_name = str(title_tag).split(' ')[0][7:]
        sender_surname = str(title_tag).split(' ')[1]
        return sender_name, sender_surname


if __name__ == '__main__':
    chat_bot_vk = ChatBot(group_id=config.group_id, token=config.token)
    chat_bot_vk.run()