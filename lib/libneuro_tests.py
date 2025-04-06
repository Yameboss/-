from lib import libneuro


def test_nn_has_records():
    nn = libneuro.NeuroNetLibrary()

    assert nn.has_records(['hangup_hi', 'hangup_goodbye']) == ['hangup_hi']


def test_nn_env():
    nn = libneuro.NeuroNetLibrary()

    nn.env('a', 1)
    nn.env(b=2)

    assert nn.env('a') == 1
    assert nn.env('b') == 2
    assert nn.env('с') is None


def test_nn_counter():
    nn = libneuro.NeuroNetLibrary()

    counter = nn.counter('some_counter')
    assert counter == 0

    counter = nn.counter('some_counter', '+')
    assert counter == 1

    counter = nn.counter('some_counter', 5)
    assert counter == 5

    counter = nn.counter('some_counter', '-')
    assert counter == 4


def test_nn_dump():
    nn = libneuro.NeuroNetLibrary()
    nn.env(result='Проверка')
    assert nn.dump() == {'call_start_time': None,
                         'call_status': None,
                         'call_transcription': [],
                         'call_uuid': None,
                         'msisdn': None,
                         'prompts_history': [],
                         'result': 'Проверка'}


def test_nn_storage():
    nn = libneuro.NeuroNetLibrary()

    assert nn.storage('BASE_URL') == 'https://api.kinopoisk.dev/v1.4/movie'
    assert nn.storage('HOST') is None


def test_nv_say():
    nv = libneuro.NeuroVoiceLibrary()

    assert nv.say('hangup_goodbye') == 'До свидания!'


def test_nv_set_default():
    nv = libneuro.NeuroVoiceLibrary()

    assert nv.set_default('listen', {}) == {'listen': {}}


def test_nv_hangup():
    nv = libneuro.NeuroVoiceLibrary()

    try:
        nv.hangup()
    except Exception as e:
        assert str(e) == 'Бот положил трубку'


if __name__ == '__main__':
    test_nn_has_records()
    test_nn_env()
    test_nn_counter()
    test_nn_storage()
    test_nn_dump()

    test_nv_say()
    test_nv_set_default()
    test_nv_hangup()
