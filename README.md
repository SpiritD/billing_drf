## Запуск сервиса

Для запуска сервиса можно использовать docker-compose (флаг --build для пересборки)

```shell
docker-compose -f docker-compose.yml up
```

## Создание базы данных

По умолчанию postgres поднимается с параметрами:
* пользователь postgres
* пароль example (задаётся через переменную окружения POSTGRES_PASSWORD)
* хост db (потому что в докере)
* порт 5432

Необходимо создать базу данных, затем применить миграции

## Миграции

После изменения моделей необходимо создать миграции командой

```shell
docker-compose -f docker-compose.yml -f docker-compose.manage.yml up --build makemigrations
```

затем применить их командой

```shell
docker-compose -f docker-compose.yml -f docker-compose.manage.yml up --build migrate
```

## Swagger для dev окружения

Для нормальной работы сваггера необходимо собрать локально статику с помощью команды

```shell
python billing/manage.py collectstatic
```

Работает только с включенным DEBUG в настройках.

После этого сваггер будет доступен по эндпоинту /swagger
