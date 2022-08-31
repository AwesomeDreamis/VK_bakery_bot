from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from state_machine import Machine
from set_logger import logger
import sqlite3


token = "vk1.a.V6oFeBEffCx9vC-8qLMV-TwQfnZJZWx0RB5e3VS33Re78gBLpg9bkbmXur2rYmP80liq8FGenJT9lHQw-ECfOCcQrvPIoIL5crUhqG8MHcN37PybNUKT-9QVb_FkFqjw_WFrLBnQmYX1SrdJ5WGSLqLX5TsS4Cw7e1npt8arwi_drAA6JBBt3zuPPiynETkD"
vk = VkApi(token=token)
longpoll = VkLongPoll(vk)

conn = sqlite3.connect('data.db')
cur = conn.cursor()


def send_message(user_id:int, message:str, keyboard=None, attachment:str=None):
    """
    Отправляет сообщение пользователю
    :param user_id: id пользователя
    :param message: сообщение
    :param keyboard: кнопки
    :param attachment: ссылка на картинку, загруженную в сообщество
    :return: None
    """

    post = {
        'user_id': user_id,
        'message': message,
        'random_id': get_random_id(),
    }

    if keyboard != None:
        post['keyboard'] = keyboard.get_keyboard()
    if attachment != None:
        post['attachment'] = attachment

    vk.method('messages.send', post)


sections: dict = {section[1]: section[0] for section in cur.execute("""SELECT * FROM sections;""")}
products: list = [name[0] for name in cur.execute(f"""SELECT name FROM products;""")]


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        text: str = event.text.lower()
        user_id: int = event.user_id
        state_machine = Machine()

        if text:
            if text == 'start' or text == 'назад':
                if text == 'start':
                    logger.info(f'user {user_id} start chat with bot')
                state_machine.set_state('sections')
                message: str = 'выберите раздел'
                keyboard = VkKeyboard()

                for n, section in enumerate(sections):
                    keyboard.add_button(label=f'{section}', color=VkKeyboardColor.PRIMARY)
                    if n < len(sections) - 1:
                        keyboard.add_line()

                send_message(user_id, message, keyboard)

            elif text in sections and state_machine.get_state() == 'sections':
                state_machine.set_state('products')
                message: str = f'выберите продукт'
                keyboard = VkKeyboard()
                prods: list = [name[0] for name in cur.execute(f"""SELECT name FROM products WHERE type_id = {sections[text]};""")]

                for i in range(len(prods)):
                    keyboard.add_button(label=f'{prods[i]}', color=VkKeyboardColor.PRIMARY)
                    if i < len(prods):
                        keyboard.add_line()
                keyboard.add_button(label='назад', color=VkKeyboardColor.NEGATIVE, payload={'type': 'back'})

                send_message(user_id, message, keyboard)

            elif text in products and state_machine.get_state() == 'products':
                prod: list = cur.execute(f"""SELECT * FROM products WHERE name = '{text}';""").fetchone()
                message: str = prod[3]
                attachment: str = prod[4]

                send_message(user_id, message, attachment=attachment)
                logger.info(f'user {user_id} interested in {prod[1]}')
            else:
                message = "Извините, я Вас не понимаю, воспользуйтесь кнопками, расположенными ниже"
                send_message(user_id, message)

