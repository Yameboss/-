from lib import libneuro
import requests
from datetime import datetime

nn = libneuro.NeuroNetLibrary()
nv = libneuro.NeuroVoiceLibrary()
InvalidCallStateError = libneuro.InvalidCallStateError
check_call_state = libneuro.check_call_state


def main():
    """Основная функция запуска звонка"""
    nn.log('ИНИЦИАЛИЗАЦИЯ', 'Запуск бота-советчика по фильмам')
    try:
        return nn.call(msisdn='1234567890', entry_point='entry_point')
    except Exception as e:
        nn.log('ОШИБКА', f'Ошибка при запуске звонка: {str(e)}')
        raise


def entry_point():
    """Точка входа в диалог"""
    nn.log('ДИАЛОГ', 'Начало взаимодействия с пользователем')
    try:
        start_main()
    except InvalidCallStateError as e:
        nn.log('ЗВОНОК', f'Звонок завершен с ошибкой состояния: {str(e)}')
    except Exception as e:
        nn.log('ОШИБКА', f'Критическая ошибка: {str(e)}')
        raise


@check_call_state
def start_main():
    """Начало основного диалога"""
    nn.log('ДИАЛОГ', 'Проигрывание приветственного сообщения')
    nv.say('main')

    with nv.listen() as result:
        nn.log('ДИАЛОГ', 'Ожидание ответа пользователя')
        process_user_response(result)


def process_user_response(result):
    """Обработка ответа пользователя"""
    utterance = result.utterance()
    nn.log('РАСПОЗНАВАНИЕ', f'Распознанный текст: "{utterance}"')

    if not utterance:
        nn.log('ДИАЛОГ', 'Пользователь ничего не сказал')
        nv.say('silence')

        with nv.listen() as result:
            if not result.utterance():
                nn.log('ДИАЛОГ', 'Пользователь не ответил повторно')
                nv.say('hangup_silence')
                return
            process_user_response(result)
        return

    # Логируем все распознанные сущности
    if result.has_entities():
        entities = {k: result.entity(k) for k in ['horror', 'rating', 'year', 'series', 'dont_know', 'any']}
        nn.log('СУЩНОСТИ', f'Распознанные сущности: {entities}')

    # Обработка сущностей
    if result.entity('horror') == 'false':
        nn.log('ПОИСК', 'Запрос фильмов без ужасов')
        search_and_recommend(filter_query={'genres.name': '!ужасы'}, is_series=False)
    elif result.entity('rating') == '7_or_more':
        nn.log('ПОИСК', 'Запрос фильмов с рейтингом >7')
        search_and_recommend(filter_query={'rating.imdb': {'$gte': 7}}, is_series=False)
    elif result.entity('year') == '2025':
        nn.log('ПОИСК', 'Запрос фильмов 2025 года')
        search_and_recommend(filter_query={'year': 2025}, is_series=False)
    elif result.entity('series') == 'true':
        nn.log('ПОИСК', 'Запрос сериалов')
        search_and_recommend(filter_query={}, is_series=True)
    elif result.entity('dont_know') == 'true' or result.entity('any') == 'true':
        nn.log('ПОИСК', 'Случайная рекомендация')
        search_and_recommend(filter_query={}, is_series=False)
    else:
        nn.log('ПОИСК', 'Рекомендация по умолчанию')
        search_and_recommend(filter_query={}, is_series=False)


def search_and_recommend(filter_query, is_series):
    """Поиск и рекомендация контента"""
    try:
        # Добавляем параметр типа контента
        content_type = 'tv-series' if is_series else 'movie'
        filter_query['type'] = content_type

        nn.log('API', f'Отправка запроса к API с параметрами: {filter_query}')

        headers = {'X-API-KEY': nn.storage('X-API-KEY')}
        response = requests.get(
            nn.storage('BASE_URL') + '/search',
            params={'limit': 1, **filter_query},
            headers=headers
        )

        nn.log('API', f'Статус ответа: {response.status_code}')

        if response.status_code == 200:
            data = response.json()
            if data.get('docs'):
                movie_data = data['docs'][0]
                nn.log('API', f'Получены данные: {movie_data.get("name")}')
                recommend_item(movie_data, is_series)
                return

        nn.log('API', 'Не удалось найти подходящий контент')
        nv.say('fail')
        offer_more_help()

    except requests.exceptions.RequestException as e:
        nn.log('ОШИБКА API', f'Ошибка запроса: {str(e)}')
        nv.say('fail')
        offer_more_help()
    except Exception as e:
        nn.log('ОШИБКА', f'Неожиданная ошибка: {str(e)}')
        nv.say('fail')
        offer_more_help()


def recommend_item(movie_data, is_series):
    """Рекомендация конкретного фильма/сериала"""
    try:
        # Подготовка данных
        name = movie_data.get('name', 'Неизвестно')
        year = movie_data.get('year', 'Неизвестен')
        rating = movie_data.get('rating', {}).get('imdb', 'Неизвестен')
        genres = ', '.join([g['name'] for g in movie_data.get('genres', [])]) or 'Неизвестны'

        # Выбор промпта в зависимости от типа и счетчика
        counter_type = 'series' if is_series else 'movie'
        prompt_key = f'{counter_type}_1' if nn.counter(f'{counter_type}_count') == 0 else f'{counter_type}_2'

        nn.log('РЕКОМЕНДАЦИЯ',
               f'Рекомендация: {name} ({year}), рейтинг: {rating}, жанры: {genres}')

        # Озвучивание рекомендации
        nv.say(prompt_key)
        nv.say('info', name=name, year=year, rating=rating, genres=genres)

        # Обновление счетчиков
        nn.counter(f'{counter_type}_count', '+')
        nn.counter('total_recommendations', '+')

        # Предложение продолжить
        offer_more_help()

    except Exception as e:
        nn.log('ОШИБКА', f'Ошибка при рекомендации: {str(e)}')
        nv.say('fail')
        offer_more_help()


def offer_more_help():
    """Предложение дополнительной помощи"""
    try:
        total_recs = nn.counter('total_recommendations')
        prompt_key = 'one_more_1' if total_recs == 1 else 'one_more_2'

        nn.log('ДИАЛОГ', f'Предложение дополнительной помощи (всего рекомендаций: {total_recs})')

        with nv.listen(entities=['confirmation']) as result:
            nv.say(prompt_key)

        if result.entity('confirmation') == 'false':
            nn.log('ДИАЛОГ', 'Пользователь отказался от продолжения')
            nv.say('hangup_goodbye')
        else:
            nn.log('ДИАЛОГ', 'Пользователь хочет продолжить')
            start_main()

    except Exception as e:
        nn.log('ОШИБКА', f'Ошибка в offer_more_help: {str(e)}')
        nv.say('hangup_goodbye')


if __name__ == '__main__':
    # Инициализация счетчиков
    nn.counter('movie_count', 0)
    nn.counter('series_count', 0)
    nn.counter('total_recommendations', 0)

    # Запуск основного кода
    main()