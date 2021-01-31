import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode
from pro_diplom.config_keys import user_token


# ЭТО КОД ДЛЯ ПОЛУЧЕНИЕ ТОКЕНА
def get_token():
    APP_ID = 7637207
    OAUTH_URL = "https://oauth.vk.com/authorize"
    REDIRECT_URI = "https://oauth.vk.com/blank.html"
    SCOPE = "status"
    OAUTH_PARAMS = {
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "response_type": "token",
        "client_id": APP_ID
    }
    print('?'.join([OAUTH_URL, urlencode(OAUTH_PARAMS)]))


def info_celtics_wiki():
    content = f"https://ru.wikipedia.org/wiki/" \
              f"%D0%91%D0%BE%D1%81%D1%82%D0%BE%D0%BD_%D0%A1%D0%B5%D0%BB%D1%82%D0%B8%D0%BA%D1%81"
    response = f"Ссылка на статью про Boston_Celtics с Википедии:\n{content}"

    return response


def news_celtics():
    response = requests.get("https://www.sports.ru/boston-celtics/")
    parser = BeautifulSoup(response.text, "html.parser")
    res = parser.find_all("div", class_="nl-item")
    some_list = []
    for i in res:
        article = i.find_all("a", class_="short-text")
        for news in article:
            link = news["href"]
            for name in news:
                description = name
                some_list.append(f"Название: {description} -> Ссылка: {link}")
    return some_list


def know_username(users_id):
    response = requests.get("https://vk.com/id" + str(users_id))
    parsing = BeautifulSoup(response.text, "html.parser")
    title = parsing.find("title")
    splitname = ""
    for i in title:
        splitname = i.split()
    name = splitname[0] + " " + splitname[1]

    return name


def get_photos(owner_user_id):
    API_BASE_URL = "https://api.vk.com/method/"
    API_BASE_VERSION = "5.77"
    link = urljoin(API_BASE_URL, "photos.get")
    res = requests.get(
        link,
        params={
            "access_token": user_token,
            "v": API_BASE_VERSION,
            "album_id": "profile",
            "extended": 1,
            "owner_id": owner_user_id,
            "photo_sizes": 1,
        },
    )
    res_json = res.json()["response"]["items"]
    likes_nums = sorted(list({like_photo["likes"]["count"] for like_photo in res_json}))
    likes_list = likes_nums[-3:]
    top_photos = {photo["likes"]["count"]: photo["sizes"][0]["url"] for photo in res_json if
                  photo["likes"]["count"] in likes_list}
    # self.send_msg(user_id, f"Топ 3 фотографии юзера:\n")
    # for like, like_link in get_photos(user_id).items():
    #     self.send_msg(user_id, f'{like} - {like_link}')

    return top_photos


def search_country(country):
    V = "5.126"
    API_BASE_URL = "https://api.vk.com/method/"
    link = urljoin(API_BASE_URL, "database.getCountries")
    response = requests.get(link,
                            params={
                                "access_token": user_token,
                                "v": V,
                                "need_all": 1,
                                "count": 1000
                            })
    # print(response.json())
    response_json = response.json()["response"]["items"]
    # print(response_json)
    country_dict = {}
    for i in response_json:
        ids = i["id"]
        country_name = i["title"]
        if country.lower() in country_name.lower():
            country_dict["country_name"] = country_name.lower()
            country_dict["country_id"] = ids
    return country_dict


def search_users(age_from, age_to, gender, town, status, country):
    country_id = search_country(country)
    V = "5.89"
    API_BASE_URL = "https://api.vk.com/method/"
    link = urljoin(API_BASE_URL, "users.search")
    response = requests.get(link,
                            params={
                                "sort": 0,
                                "access_token": user_token,
                                "age_from": age_from,
                                "age_to": age_to,
                                "sex": gender,
                                "status": status,
                                "v": V,
                                "is_closed": False,
                                "can_access_closed": False,
                                "country".lower(): country_id["country_id"],
                                "hometown": town,
                                "fields": ["home_town"],
                                "count": 1000,
                                "has_photo": 1
                            })
    response_json = response.json()["response"]["items"]

    users = ({"name": f'{i["first_name"]} {i["last_name"]}', "User_ID": i["id"],
              "town": i["home_town"]} for i in response_json if
             "home_town" in i and town.lower() in i["home_town"].lower())

    return users


# search_users(18, 30, 1, "ташкент", 6, "Узбекистан")
# get_token()
# search_country("Узбекистан")


# def search_town(country_name, town_name): inner = search_country(country_name) name = inner["country_name"] ids =
# inner["country_id"] V = "5.126" API_BASE_URL = "https://api.vk.com/method/" link = urljoin(API_BASE_URL,
# "database.getCities") response = requests.get(link, params={ "access_token": user_token, "country_id": ids, "v": V,
# "need_all": 1, "count": 1000 }) response_json = response.json()["response"]["items"] # print(response_json)
# some_generator = ({"ID": i["id"], "town": i["title"], "region": i["region"]} for i in response_json if "region" in
# i and town_name.lower() in i["region"].lower()) for i in some_generator: print(i)
#
#
# search_town("узбекистан", "Ташкент")