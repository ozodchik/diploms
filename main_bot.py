import vk_api
from random import randrange
from vk_api.longpoll import VkLongPoll, VkEventType
from pro_diplom.config_keys import user_token as u_t, bots_token as b_t
from pro_diplom.need_functions_modules import info_celtics_wiki as i_s_w, news_celtics as n_c, know_username, \
    search_users
from pro_diplom.work_with_db_alchemy import AllVkUsers, BotUsers, SearchedUsers

STATUSES = dict(hello=0, commands=1, choose_gender=2, choose_age_from=3, choose_age_to=4,
                choose_status=5, news=6, history=7, got_it=8,
                choose_country_wait=9, choose_city_wait=10, wait_database=11,
                )


class ServerBot:
    def __init__(self, users_token=u_t, group_token=b_t):
        self.vk = vk_api.VkApi(token=group_token)
        self.long_poll = VkLongPoll(self.vk)
        self.users_token = users_token
        self.request = ''
        self.user_id = 0
        self.state = STATUSES["hello"]
        self.status = 2
        self.gender = 1
        self.age_from: int = 18
        self.age_to: int = 20
        self.country = "узбекистан"
        self.town = "ташкент"
        self.user_name = ""
        self.user_id_db = 0
        self.gender_text = ""

    def send_msg(self, user_id, message):
        self.vk.method("messages.send", {'user_id': user_id, 'message': message, "random_id": randrange(10 ** 7)})

    def hello(self):
        user = BotUsers(self.user_id, self.user_name)
        self.user_name = know_username(self.user_id)
        self.send_msg(self.user_id, f"Привет {self.user_name}!\n"
                                    f"Я бот VKinder ваш помощник для помощи вводите bot_commands")
        self.state = STATUSES["commands"]
        return self.state

    def commands(self):
        return self.send_msg(self.user_id,
                             f"Выберите команду:\n"
                             f"Search_users: Искать людей для знакомства\n"
                             f"News: Новости про команды Boston Celtics\n"
                             f"History: История команды Boston Celtics и прочие материалы")

    def searching(self):
        search = search_users(self.age_from, self.age_to, self.gender, self.town, self.state, self.country)
        for i in search:
            # insert_into_searched_users(i['User_ID'], i["name"], i["town"], False, self.user_id)
            self.send_msg(self.user_id, f'{i["name"]}, ID: {i["User_ID"]}, '
                                        f'жил(-а) в городе(городах):{i["town"]}')
            # self.send_msg(self.user_id, f"Нравится?) если да то пишите like если нет то пишите hate")
        self.state = STATUSES["commands"]
        self.send_msg(self.user_id, "Этот сеанс окончен и мы возвращаемся в состояние bot_commands")
        self.commands()

    def news(self):
        for news in n_c():
            self.send_msg(self.user_id, news)
        self.send_msg(self.user_id, "Этот сеанс окончен и мы возвращаемся в состояние bot_commands")
        self.state = STATUSES["commands"]
        self.commands()

    def history(self):
        self.send_msg(self.user_id, i_s_w())
        self.send_msg(self.user_id, "Этот сеанс окончен и мы возвращаемся в состояние bot_commands")
        self.state = STATUSES["commands"]
        self.commands()

    def talking(self):
        for event in self.long_poll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    self.request = event.text.lower()
                    self.user_id = event.user_id

                    # print(search_users(self.age_from, self.age_to, self.gender, self.town, self.status, self.country))
                    if self.request == "привет" and self.state == STATUSES["hello"]:
                        self.hello()

                    elif self.request == "bot_commands" and self.state == STATUSES["commands"]:
                        self.commands()

                    elif self.request == "search_users" and self.state == STATUSES["commands"]:
                        self.state = STATUSES["choose_country_wait"]
                        self.send_msg(self.user_id,
                                      f"ВНИМАНИЯ! предупреждаю вас о том когда вы наберёте не правильную"
                                      f" команду или не правильно вводите параметры поиска то это в конце"
                                      f" концов повлияет на ваш же поиск и вы не получите нужный ответ и "
                                      f"мы снова возвращаемся в bot_commands!\n"
                                      f"Поэтому просим вас быть внимательнее и правильно заполнить нужные"
                                      f" поля! спасибо за понимание)\n"
                                      f"Ну а теперь приступим к поиску)\n"
                                      f"Вводите страну поиска Например Россия, Украина, Белорусия и т.д.\n")

                    elif self.state == STATUSES["choose_country_wait"]:
                        self.state = STATUSES["choose_city_wait"]
                        self.country = self.request
                        self.send_msg(self.user_id, f"Вводите город поиска")

                    elif self.state == STATUSES["choose_city_wait"]:
                        self.town = self.request
                        self.state = STATUSES["choose_gender"]
                        self.send_msg(self.user_id, f"вводите пол юзера:\n"
                                                    f"man - мужчина\n"
                                                    f"woman - женщина\n"
                                                    f"any - без разницы")

                    elif self.request == "man" and self.state == STATUSES["choose_gender"]:
                        self.gender = 2
                        self.gender_text = "man"
                        self.state = STATUSES["choose_age_from"]
                        self.send_msg(self.user_id, f"Вводите минимальный возраст пользователя "
                                                    f"от 10 до 100")

                    elif self.request == "woman" and self.state == STATUSES["choose_gender"]:
                        self.gender = 1
                        self.gender_text = "woman"
                        self.state = STATUSES["choose_age_from"]
                        self.send_msg(self.user_id, f"Вводите минимальный возраст пользователя "
                                                    f"от 10 до 100")

                    elif self.request == "any" and self.state == STATUSES["choose_gender"]:
                        self.gender = 0
                        self.gender_text = "any"
                        self.state = STATUSES["choose_age_from"]
                        self.send_msg(self.user_id, f"Вводите минимальный возраст пользователя "
                                                    f"от 10 до 100")

                    elif self.state == STATUSES["choose_age_from"]:
                        self.state = STATUSES["choose_age_to"]
                        self.age_from = self.request
                        self.send_msg(self.user_id, f"Вводите максимальный возраст пользователя"
                                                    f" и оно не должно быть меньше минимального возраста")

                    elif self.state == STATUSES["choose_age_to"]:
                        self.state = STATUSES["choose_status"]
                        self.age_to = self.request
                        self.send_msg(self.user_id, f"Вводите номер статуса пользователя:\n"
                                                    f"1.не женат(не за мужем)\n"
                                                    f"2.встречается\n"
                                                    f"3.помолвлен(-а)\n"
                                                    f"4.женат(за мужем)\n"
                                                    f"5.всё сложно\n"
                                                    f"6.в активном поиске\n"
                                                    f"7.влюблен(-а)\n"
                                                    f"8.в гражданском браке")

                    elif self.state == STATUSES["choose_status"] and self.request == "1":
                        self.state = STATUSES["got_it"]
                        self.status = 1
                        self.send_msg(self.user_id, f"Хотите начать?\n"
                                                    f"пишите да или нет")

                    elif self.state == STATUSES["choose_status"] and self.request == "2":
                        self.state = STATUSES["got_it"]
                        self.status = 2
                        self.send_msg(self.user_id, f"Хотите начать?\n"
                                                    f"пишите да или нет")

                    elif self.state == STATUSES["choose_status"] and self.request == "3":
                        self.state = STATUSES["got_it"]
                        self.status = 3
                        self.send_msg(self.user_id, f"Хотите начать?\n"
                                                    f"пишите да или нет")

                    elif self.state == STATUSES["choose_status"] and self.request == "4":
                        self.state = STATUSES["got_it"]
                        self.status = 4
                        self.send_msg(self.user_id, f"Хотите начать?\n"
                                                    f"пишите да или нет")

                    elif self.state == STATUSES["choose_status"] and self.request == "5":
                        self.state = STATUSES["got_it"]
                        self.status = 5
                        self.send_msg(self.user_id, f"Хотите начать?\n"
                                                    f"пишите да или нет")

                    elif self.state == STATUSES["choose_status"] and self.request == "6":
                        self.state = STATUSES["got_it"]
                        self.status = 6
                        self.send_msg(self.user_id, f"Хотите начать?\n"
                                                    f"пишите да или нет")

                    elif self.state == STATUSES["choose_status"] and self.request == "7":
                        self.state = STATUSES["got_it"]
                        self.status = 7
                        self.send_msg(self.user_id, f"Хотите начать?\n"
                                                    f"пишите да или нет")

                    elif self.state == STATUSES["choose_status"] and self.request == "8":
                        self.state = STATUSES["got_it"]
                        self.status = 8
                        self.send_msg(self.user_id, f"Хотите начать?\n"
                                                    f"пишите да или нет")

                    elif self.state == STATUSES["got_it"] and self.request == "да":
                        self.state = STATUSES["commands"]
                        self.send_msg(self.user_id, f'Параметры поиска вашей половинки:\n'
                                                    f'Минимальный возраст: {self.age_from},\n'
                                                    f'Максимальный возраст: {self.age_to},\n'
                                                    f'Город: {self.town},\n'
                                                    f'Пол: {self.gender_text},\n'
                                                    f'Страна: {self.country},\n'
                                                    f'Семейное положение: {self.status}')
                        self.searching()

                    elif self.state == STATUSES["got_it"] and self.request == "нет":
                        self.send_msg(self.user_id, f"Вы выбрали команду нет поэтому мы возвращаемся в состояние hello")
                        self.state = STATUSES["hello"]
                        self.hello()

                    elif self.request == "news" and self.state == STATUSES["commands"]:
                        self.news()

                    elif self.request == "history" and self.state == STATUSES["commands"]:
                        self.history()

                    else:
                        self.send_msg(self.user_id, "ERROR! Вы набрали не правильную команду или где то "
                                                    "допустили ошибку! поэтому вернёмся в Hello")
                        self.state = STATUSES["hello"]
                        self.hello()


if __name__ == "__main__":
    some_user = ServerBot(u_t, b_t)
    some_user.talking()
