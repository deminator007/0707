import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

class Bot:
    def __init__(self):
        self.vk_user = vk_api.VkApi(token="user_token")
        self.vk_user_got_api = self.vk_user.get_api()
        self.vk_group = vk_api.VkApi(token="group_token")
        self.vk_group_got_api = self.vk_group.get_api()
        self.longpoll = VkLongPoll(self.vk_group)

    def send_msg(self, user_id, message):
        self.vk_group_got_api.messages.send(
            user_id=user_id,
            message=message,
        )

    def naming_of_years(self, years, till=True):
        name_years_singular = [1, 21, 31, 41, 51, 61]
        name_years_plural = [2, 3, 4, 22, 23, 24, 32, 33, 34, 42, 43, 44, 52, 53, 54, 62, 63, 64]
    
        if till:
            if years in name_years_singular:
                return f'{years} года'
            else:
                return f'{years} лет'
        else:
            if years in name_years_singular:
                return f'{years} год'
            elif years in name_years_plural:
                return f'{years} года'
            else:
                return f'{years} лет'

    def input_looking_age(self, user_id, age):
        try:
            age_range = [int(a) for a in age.split("-")] 
            if len(age_range) == 1:
                age_from = age_to = age_range[0]
                self.send_msg(user_id, f'Возраст {self.naming_of_years(age_to, False)}')
            else:
                age_from, age_to = age_range
                if age_from == age_to:
                    self.send_msg(user_id, f'Возраст {self.naming_of_years(age_to, False)}')
                else:
                    self.send_msg(user_id, f'Возраст в пределах от {age_from} и до {self.naming_of_years(age_to, True)}')
        except ValueError:
            self.send_msg(user_id, 'Введен неправильный числовой формат')
        except Exception as e:
            self.send_msg(user_id, f' {type(e).__name__} Введены некорректные данные!')

    def get_years_of_person(self, bdate: str) -> object:
        bdate_splited = bdate.split(".")
        month_names = {
            "1": "января",
            "2": "февраля",
            "3": "марта",
            "4": "апреля",
            "5": "мая",
            "6": "июня",
            "7": "июля",
            "8": "августа",
            "9": "сентября",
            "10": "октября",
            "11": "ноября",
            "12": "декабря"
        }


    def get_age_of_user(self, user_id):
        try:
            info = self.vk_user_got_api.users.get(
                user_ids=user_id,
                fields="bdate",
            )[0]['bdate']
            num_age = self.get_years_of_person(info).split()[0]
            age_from = age_to = num_age
            if num_age == "День":
                print(f'Ваш {self.get_years_of_person(info)}')
                self.send_msg(user_id, 'Бот ищет людей вашего возраста, но в ваших настройках профиля установлен пункт "Показывать только месяц и день рождения"!\n'
                          'Поэтому, введите возраст поиска, например от 21 года и до 35 лет, в формате: 21-35 (или 21 для конкретного возраста 21 год).')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return self.input_looking_age(user_id, age)
            print(f'Ищем вашего возраста {self.naming_of_years(age_to)}')
        except KeyError:
            print('День рождения скрыт настройками приватности!')
            self.send_msg(user_id, 'Бот ищет людей вашего возраста, но в ваших настройках профиля установлен пункт "Не показывать дату рождения".\n'
                      'Поэтому, введите возраст поиска, например от 21 года и до 35 лет, в формате: 21-35 (или 21 для конкретного возраста 21 год).')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    return self.input_looking_age(user_id, age)

    def get_target_city(self, user_id):
        self.send_msg(user_id, 'Введите "Да", чтобы выполнить поиск в городе, указанном в вашем профиле, или введите название города, например: Москва.') 
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                answer = event.text.lower()
                if answer == "да" or answer == "y":
                    info = self.vk_user_got_api.users.get(
                        user_id=user_id,
                        fields="city")
                    city_id = info[0]['city'].get("id")
                    city_title = info[0]['city'].get("title")
                    if city_id is not None and city_title is not None:
                        return f'в городе {city_title}.'
                    else:
                        return 'Не удалось получить информацию о вашем городе из профиля.'
                else:
                    cities = self.vk_user_got_api.database.getCities(
                        country_id=1,
                        q=answer.capitalize(),
                        need_all=1,
                        count=1000)['items']
                    for city in cities:
                        if city["title"] == answer.capitalize():
                            city_id = city["id"]
                            city_title = answer.capitalize()
                            return f'в городе {city_title}'
                    return 'Город не найден. Пожалуйста, уточните название города.'

    def looking_for_gender(self, user_id):
        info = self.vk_user_got_api.users.get(
            user_id=user_id,
                fields="sex")
        if info[0]['sex'] == 1:
            print('Ваш пол - женский')
            return 2
        elif info[0]['sex'] == 2:
            print('Ваш пол - мужской')
            return 1
        else:
            print("Ошибка")

    def looking_for_persons(self, user_id):
        global list_found_persons
        list_found_persons = []
        res = self.vk_user_got_api.users.search(
            sort=0,
            sex=self.looking_for_gender(user_id),
            status=1,
            has_photo=1,
            count=1000,
            fields="can_write_private_message,city,domain,home_town")
        list_found_persons = [person["id"] for person in res["items"] if not person["is_closed"]]
        number = len(list_found_persons)
        print(f'Bot found {number} opened profiles for viewing from {res["count"]}')
        return list_found_persons

    def photo_of_found_person(self, user_id):
        """getting a photo of a found person"""
        global attachments
        res = self.vk_user_got_api.photos.get(
            owner_id=user_id,
            album_id="profile",
            extended=1,
            count=30
        )
        dict_photos = dict()
        for i in res['items']:
            photo_id = str(i["id"])
            i_likes = i["likes"]
            if i_likes["count"]:
                likes = i_likes["count"]
                dict_photos[likes] = photo_id
        list_of_ids = sorted(dict_photos.items(), reverse=True)
        attachments = []
        photo_ids = []
        for i in list_of_ids:
            photo_ids.append(i[1])
        try:
            attachments.append('photo{}_{}'.format(user_id, photo_ids[0]))
            attachments.append('photo{}_{}'.format(user_id, photo_ids[1]))
            attachments.append('photo{}_{}'.format(user_id, photo_ids[2]))
            return attachments
        except IndexError:
            try:
                attachments.append('photo{}_{}'.format(user_id, photo_ids[0]))
                return attachments
            except IndexError:
                return print(f'Нет фото')

    def get_found_person_id(self):
        global unique_person_id, found_persons
        seen_person = []
        for i in check():
            seen_person.append(int(i[0]))
        if not seen_person:
            try:
                unique_person_id = list_found_persons[0]
                return unique_person_id
            except NameError:
                found_persons = 0
                return found_persons
        else:
            try:
                for ifp in list_found_persons:
                    if ifp in seen_person:
                        pass
                    else:
                        unique_person_id = ifp
                        return unique_person_id
            except NameError:
                found_persons = 0
                return found_persons


    def found_person_info(self, show_person_id):
        """Retrieve information about the found person"""
        res = self.vk_user_got_api.users.get(
            user_ids=show_person_id,
            fields="about, "
                   "activities, "
                   "city, "
                   "common_count, "
                   "contacts, "
                   "interests, "
                   "occupation"
        )
        first_name = res[0]["first_name"]
        last_name = res[0]["last_name"]
        age = self.get_years_of_person(res[0]["bdate"])
        vk_link = 'vk.com/' + res[0]["domain"]
        city = ''
        try:
            if res[0]["city"]["title"] is not None:
                city = f'City: {res[0]["city"]["title"]}'
            else:
                city = f'City: {res[0]["home_town"]}'
        except KeyError:
            pass
        print(f'{first_name} {last_name}, Age: {age}, {city}. VK Profile: {vk_link}')
        return f'{first_name} {last_name}, Age: {age}, {city}. VK Profile: {vk_link}'


    def send_photo(self, user_id, message, attachments):
        try:
            self.vk_group_got_api.messages.send(
                user_id=user_id,
                message=message,
                attachment=",".join(attachments)
            )
        except TypeError:
            pass

    def show_found_person(self, user_id):
        print(self.get_found_person_id())
        if self.get_found_person_id() == None:
            self.send_msg(user_id,
                          f'Все анекты ранее были просмотрены. Будет выполнен новый поиск. '
                          f'Измените критерии поиска (возраст, город). '
                          f'Введите возраст поиска, на пример от 21 года и до 35 лет, '
                          f'в формате : 21-35 (или 21 конкретный возраст 21 год).  ')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    self.input_looking_age(user_id, age)
                    self.get_target_city(user_id)
                    self.looking_for_persons(user_id)
                    self.show_found_person(user_id)
                    return
        else:
            self.send_msg(user_id, self.found_person_info(self.get_found_person_id()))
            self.send_photo(user_id, 'Фото с максимальными лайками',
                            self.photo_of_found_person(self.get_found_person_id()))
