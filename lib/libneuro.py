import datetime
import inspect
import pprint
from time import sleep
from uuid import uuid4

from lib.content import ENTITIES, PROMPTS, STORAGE, OUTPUT_PARAMS

class InvalidCallStateError(Exception):
    pass


class NeuroNetLibrary:
    def __init__(self, env: dict = None):
        self._counters = {}
        self._env = env or {}
        self._call_start_time = datetime.datetime.now()
        with open('logs.txt', 'w'):
            pass

    def call(self, msisdn: str, entry_point: str, after_call: str = None):
        try:
            if not msisdn:
                raise Exception('Не указан номер телефона')

            OUTPUT_PARAMS.update(msisdn=msisdn,
                                 call_uuid=str(uuid4()),
                                 call_start_time=datetime.datetime.now().isoformat())
            print(f"Начало звонка на номер {msisdn}: {OUTPUT_PARAMS.get('call_start_time')}\n")
            globals().get(entry_point)()
        except Exception as e:
            OUTPUT_PARAMS['call_status'] = 'FAIL'
        else:
            OUTPUT_PARAMS['call_status'] = 'SUCCESS'
        finally:
            (after_call or self.dump)()

    @staticmethod
    def has_records(lst: list):
        return [name for name in lst if not isinstance(PROMPTS.get(name), str)]

    def env(self, *args, **kwargs):
        if args and kwargs:
            raise AttributeError

        if kwargs:
            self._env.update(kwargs)
            return

        if len(args) == 2:
            self._env.update({args[0]: args[1]})
            return

        return self._env.get(args[0])

    def counter(self, name, op=None):
        c = self._counters.setdefault(name, 0)
        if not op:
            return c
        elif op == '+':
            c += 1
        elif op == '-':
            c -= 1
        elif isinstance(op, int):
            c = op
        self._counters.update({name: c})
        return c

    @staticmethod
    def log(name, data=None):
        with open('logs.txt', 'a') as logs:
            logs.writelines(['\n', ' - '.join(str(_) for _ in [str(datetime.datetime.now()), inspect.stack()[1][3], name, data] if _)])

    def dump(self):
        OUTPUT_PARAMS.update(self._env)
        pprint.pprint(OUTPUT_PARAMS)
        return OUTPUT_PARAMS

    @staticmethod
    def storage(name):
        return STORAGE.get(name)


class NeuroVoiceLibrary:
    DEFAULT_PARAMS = {}

    @staticmethod
    def __print_partial_text(who: str, text: str):
        for i in range(len(text)):
            print(f'\r{who.upper()}: {text[:i + 1]}', end='')
            sleep(0.02)
        print(end='\n')

    def say(self, prompt, **kwargs):
        text = PROMPTS.get(prompt, '').format(**kwargs)
        self.__print_partial_text('bot', text)
        OUTPUT_PARAMS['call_transcription'].append({'bot': text})
        OUTPUT_PARAMS['prompts_history'].append(prompt)
        return text

    def listen(self, **kwargs):
        listen_params = self.DEFAULT_PARAMS.get('listen') or {}
        return NeuroNluRecognitionResult(**{k: kwargs.get(k) or listen_params.get(k) for k in ['entities']})

    def set_default(self, name, params):
        self.DEFAULT_PARAMS[name] = params
        return self.DEFAULT_PARAMS

    @staticmethod
    def hangup():
        raise InvalidCallStateError('Бот положил трубку')


class NeuroNluRecognitionResult:
    def __init__(self, **kwargs):
        self._utterance = ""
        self.entities = kwargs.get('entities') or list(ENTITIES)
        self.recognized_entities = {}

    def __enter__(self):
        return self

    def utterance(self):
        return self._utterance

    @staticmethod
    def __get_clear_utterance(utterance):
        return utterance.replace('?', ' ').replace('!', ' ').replace(',', ' ').replace('.', ' ').strip().lower()

    def __exit__(self, type, value, traceback):
        utterance = input('HUMAN: ')
        self._utterance = self.__get_clear_utterance(utterance)
        if self._utterance in ('h', 'hangup'):
            return NeuroVoiceLibrary.hangup()

        OUTPUT_PARAMS['call_transcription'].append({'human': utterance})

        for entity in self.entities:
            for flag, patterns in ENTITIES.get(entity, {}).items():
                if any(p.lower() in utterance.lower() for p in patterns):
                    self.recognized_entities[entity] = flag
                    break
        return self

    def entity(self, value):
        return self.recognized_entities.get(value)


def check_call_state(nv: NeuroVoiceLibrary):
    def wrapper(f):
        def inner(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except InvalidCallStateError as i:
                raise InvalidCallStateError('Абонент положил трубку')
            except Exception as e:
                raise Exception(e)
        return inner
    return wrapper
