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
        self.senders_id = {}
        for event in self.long_poll.listen():
            try:
                self._on_event(event)
            except Exception as err:
                print(f'Ошибка при получении события из метода run(): {err}')

    def _on_event(self, event):
        self.sender_path = ''
        self.answer_count = 0
        if event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_REPLY:
            pass
        elif event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
            date = time.ctime(event.object.message['date'])
            sender_id = str(event.object.message['from_id'])
            message_new = event.object.message['text']
            self.sender_path = 'https://vk.com/id' + sender_id
            sender_name, sender_surname = self._parse_data(self.sender_path)

            print('-' * 30)
            print(f'Ссылка на отправителя: {self.sender_path}\nИмя: {sender_name}\nФамилия: {sender_surname}')
            print(f'Время и время: {date}')
            print(f"Сообщение: {message_new}")

            answer_message = self._checking_text(message_new, sender_name, sender_surname, sender_id)
            if self.answer_count == 0:
                self._answer(event.object.message['peer_id'], answer_message)
            else:
                pass
        elif event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_TYPING_STATE:
            self.sender_path = 'https://vk.com/id' + str(event.object.from_id)
            print(f'Пользователь "{self.sender_path}" что-то пишет........')
        else:
            print(f'====> Получено неизвестное событие {event}')
            print(f'>>>> Получено неизвестное событие {event.type}')

    def _answer(self, peer_id, message):
        self.answer_count += 1
        self.api.messages.send(
            message=message,
            random_id=random.randint(0, 2 ** 20),
            peer_id=peer_id,
        )

    def _parse_data(self, sender_path):
        page = requests.get(sender_path)
        page_txt = BeautifulSoup(page.text, features='html.parser')
        title_tag = page_txt.find('title')
        sender_name = str(title_tag).split(' ')[0][7:]
        sender_surname = str(title_tag).split(' ')[1]
        return sender_name, sender_surname

    def _checking_text(self, text, name, surname, sender_id):
        input_text = text.lower()
        words_hello = ('привет', 'hello', 'здравствуйте', 'добрый день')
        words_bot = ("чат", "бот", "робот")
        users_name = ("Дмитрий", "Олег")
        users_surname = ("Щеглов", "Иванов",)

        if str(sender_id) not in self.senders_id.keys():
            self.senders_id[sender_id] = [name, surname]
            return f'Доброго дня, {name}. Пришлите мне сообщение "Help" для вывода помощи.'

        elif input_text == 'help':
            return 'Я пока не знаю всех своих возможностей... Я работаю над этим ;-)'
        elif input_text != 'help':

            for key_ward in words_hello:
                dice = random.randint(1, 3)
                if key_ward in input_text:
                    if dice == 1:
                        return f'Добрый день, {name}! Мы уж знакомы. Как твои дела?'
                    elif dice == 2:
                        return f'Мы уж знакомы. Добрый день, {name}! Как дела?'
                    elif dice == 3:
                        return f'Приветствую тебя снова, {name}! Как дела?'

            for key_ward in words_bot:
                dice = random.randint(1, 3)
                if key_ward in input_text:
                    if dice == 1:
                        return 'Я пока еще глупый чат-бот. Но я еще учусь.'
                    elif dice == 2:
                        return 'Я чат-бот. Но я еще ничего не умею.'
                    elif dice == 3:
                        return 'Чат-боты - это роботы-собеседники.'

            for key_ward in users_name:
                dice = random.randint(1, 3)
                if key_ward == name.capitalize():
                    if dice == 1:
                        return f'Ух ты! {name}, мне очень нравится твое имя!'
                    elif dice == 2:
                        return f'Я раньше не говорил, {name}, но мне нравится твое имя.'
                    elif dice == 3:
                        return f'Кстати, мне нравится твое имя, {name}! ' \
                               f'Оно отлично сочитается с твоей фамилией {name} {surname} ;-)'


if __name__ == '__main__':
    chat_bot_vk = ChatBot(group_id=config.group_id, token=config.token)
    chat_bot_vk.run()
