## Тестовое задание "Разработчик логики"

### Наполнение репозитория
Папка lib содержит готовый набор файлов для реализации логики:
- content.py - наполнение бота - менять его нежелательно, но не запрещено;
  - PROMPTS - тексты, которыми общается бот;
  - ENTITIES - сущности (набор синонимичных фраз), которые бот может вычленить из фразы абонента;
  - OUTPUT_PARAMS - выходные параметры бота, которые можно проанализировать после звонка;
  - STORAGE - глобальные переменные бота, в которых можно хранить уникальную для этого бота информацию;
- libneuro.py - библиотека методов, необходимых для реализации логики и общения с ботом в консоли;
- libneuro_tests.py - набор тестов для дополнительного понимания, как должны работать данные методы;
- Script - сценарий, по которому должен работать бот;
- Библиотеки_для_написания_логики - описание библиотек с примерами использования.

Файл LogicDevTestTask.py переименовать в LogicDevTestTask_<Ваша фамилия>.py. В этом файле содержится основа кода логики, которую необходимо дописать. 

Файл logs.txt - создаётся после запуска логики и общения с ботом в терминале. Хранит логи, которые записываются с помощью метода nn.log. Затирается при новом запуске логики.

### Описание задания

Необходимо дописать код логики в файле Logic, опираясь на сценарий Script и описание библиотек.
Код должен состоять из нескольких частей - до общения с абонентом, во время общения с абонентом и, опционально, после общения с абонентом.
Код должен соответствовать следующим требованиям:
- Код опубликован на Github/Gitlab в приватном репозитории; 
- Код соответствует PEP8;
- Python 3.8+;
- **Код запускается**. Если код не запускается, такое решение рассматриваться не будет.

Во время диалога с абонентом бот-советчик также должен обращаться к API Кинопоиска ([документация](https://api.kinopoisk.dev/documentation#/%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B%2C%20%D1%81%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D1%8B%2C%20%D0%B8%20%D1%82.%D0%B4./MovieController_findManyByQueryV1_4))
и использовать различные фильтры.

Обратите внимание, что токен для использования API уже лежит в хранилище агента, осталось только его правильно "добыть".


#### Дополнительным плюсом будет, если

- Поняты и использованы все неприватные методы библиотек 
- Написаны тесты
- Учтены возможные corner-cases при работе с API Кинопоиска

### Контакты

Обращаться по вопросам можно сюда: 

#### **_Ермолаев Максим_**

*Telegram* https://t.me/ErmolaevMaksum

*Email*: mermolaev@neuro.net
"# -"  
