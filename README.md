# Пример биллинг сервиса

Заготовка для сервиса по работе с пользователями, кошельками и осуществлением транзакций.

Реализован на DRF.


## Особенности

Я понимаю, что для получении вебхука от платёжных систем (для пополнения кошелька)
должны быть сделаны отдельные эндпоинты,
но для примера и удобства проверки это обычный эндпоинт с авторизацией пользователя.
Давайте представим, что между платёжной системой и нашим сервисом стоит агрегирующий
сервис, который обрабатывает вебхуки и шлёт нам запрос непосредственно на создание транзакции=)

На самом же деле в кабинете каждой платёжной системы настраивается адрес вебхука 
и отдельно обрабатывается каждый формат.
Там идёт проверка каждой платёжной системы по-разному 
(а не авторизация внутреннего пользователя как в примере).

Поле balance модели Wallet по сути содержит кэш, текущее значение суммы транзакций,
которое обновляется при каждой транзакции, где кошелёк указан в поле sender или payee.

Первичный ключ кошельков и транзакций заменён на uuid для осложнения подбора.


## Что дальше?

Список задач:
* добавить поддержку валюты (по умолчанию одна) с возможностью переключения и пересчёта актуального курса;
* покрыть тестами secure_transaction, хоть он и покрыт отчасти при тестировании создания транзакции;
* ошибку об отсутствии целевого кошелька заменить на более общую;


## Создание базы данных

По умолчанию postgres поднимается с параметрами:
* пользователь postgres
* пароль example (задаётся через переменную окружения POSTGRES_PASSWORD)
* хост db (потому что в докере)
* порт 5432

Необходимо создать базу данных, затем применить миграции.

Как пример, можно создать базу с помощью веб сервиса adminer

```shell
docker-compose -f docker-compose.yml -f docker-compose.manage.yml up --build adminer
```


## Запуск тестов

```shell
docker-compose -f docker-compose.yml -f docker-compose.manage.yml up --build test
```

## Запуск сервиса

Для запуска сервиса можно использовать docker-compose (флаг --build для пересборки)

```shell
docker-compose -f docker-compose.yml up
```


## Миграции

После изменения моделей необходимо пересобрать основной образ сервиса

```shell
docker-compose -f docker-compose.yml build billing_service
```

Затем создать миграции командой

```shell
docker-compose -f docker-compose.yml -f docker-compose.manage.yml up makemigrations
```

И применить их командой

```shell
docker-compose -f docker-compose.yml -f docker-compose.manage.yml up migrate
```


## Swagger для dev окружения

Для нормальной работы сваггера необходимо собрать локально статику с помощью команды

```shell
python billing/manage.py collectstatic
```

Работает только с включенным DEBUG в настройках.

После этого сваггер будет доступен по эндпоинту /swagger
