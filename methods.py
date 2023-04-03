from geopy import geocoders
import requests as req
import json
import urllib3

urllib3.disable_warnings()


CONDITIONS = {'clear': 'ясно', 'partly-cloudy': 'малооблачно', 'cloudy': 'облачно с прояснениями',
              'overcast': 'пасмурно', 'drizzle': 'морось', 'light-rain': 'небольшой дождь',
              'rain': 'дождь', 'moderate-rain': 'умеренно сильный', 'heavy-rain': 'сильный дождь',
              'continuous-heavy-rain': 'длительный сильный дождь', 'showers': 'ливень',
              'wet-snow': 'дождь со снегом', 'light-snow': 'небольшой снег', 'snow': 'снег',
              'snow-showers': 'снегопад', 'hail': 'град', 'thunderstorm': 'гроза',
              'thunderstorm-with-rain': 'дождь с грозой', 'thunderstorm-with-hail': 'гроза с градом'
              }
WIND_DIRECTION = {'nw': 'северо-западное', 'n': 'северное', 'ne': 'северо-восточное', 'e': 'восточное',
                  'se': 'юго-восточное', 's': 'южное', 'sw': 'юго-западное', 'w': 'западное', 'с': 'штиль'
                  }
DAY_PART = {"night": "🌑 Ночью", "morning": "🌤️ Утром",
            "day": "☀️ Днем", "evening": "🌙 Вечером"
            }


class Weather:

    def __init__(self, city: str, api_key: str):
        """
        Определение широты и долготы
        """
        geolcator = geocoders.Nominatim(user_agent='bot')
        self.city = city
        self.lat = str(geolcator.geocode(city).latitude)
        self.lon = str(geolcator.geocode(city).longitude)
        self.api_key = api_key

    def next_six_hours(self):
        """
        Возврат погоды в текущее время суток (ночь, утро, день, вечер)
        """
        weather = self.__parse_weather()
        weather = weather['forecast']['parts'][0]
        answer = f"{DAY_PART[weather['part_name']]} средняя температура {weather['temp_avg']}\n" \
                 f"💨 Скорость ветра {weather['wind_speed']} м/с, направление {WIND_DIRECTION[weather['wind_dir']]}"
        return answer

    def now(self):
        """
        Возврат текущей погоды
        """
        weather = self.__parse_weather()
        weather = weather['fact']
        answer = f"🌍 В г. {self.city} сейчас {CONDITIONS[weather['condition']]}\n" \
                 f"🌡 Температура воздуха {weather['temp']} (ощущ. {weather['feels_like']})\n" \
                 f"💦 Влажность {weather['humidity']}%\n" \
                 f"💨 Скорость ветра {weather['wind_speed']} м/с, направление {WIND_DIRECTION[weather['wind_dir']]}"
        return answer

    def __parse_weather(self):
        """
        Обращение по API к Яндекс Погоде и сериализация JSON
        """
        url_yandex = f'https://api.weather.yandex.ru/v2/informers?lat={self.lat}&lon={self.lon}&[lang=ru_RU]&limit=1&hours=true'
        yandex_req = req.get(url_yandex, headers={'X-Yandex-API-Key': self.api_key}, verify=False)
        yandex_json = json.loads(yandex_req.text)
        return yandex_json

