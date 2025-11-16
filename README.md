# Проект "Погода"

Веб-приложение для просмотра текущей погоды. Пользователь может зарегистрироваться и добавить в коллекцию одну или
несколько локаций (городов, сёл, других пунктов), после чего главная страница приложения начинает отображать список
локаций с их текущей погодой

## Мотивация проекта

- Реализация многопользовательского приложения -
- Работа с внешними API

## Технологии

- Django
- Poetry
- Postgres
- Bootstrap
- Nginx
- Docker

# Деплой

## Базовая настройка Linux (Ubuntu) для деплоя

```shell
    # Разрешаем подключения по SSH
    ufw allow OpenSSH

    # Разрешаем трафик на стандартные веб-порты
    ufw allow 80/tcp   # Для HTTP
    ufw allow 443/tcp  # Для HTTPS (понадобится в будущем)

    # Включаем файрвол
    ufw enable 
```

Иногда системный файрвол блокирует внутреннюю сеть Docker. Чтобы это исправить, нужно явно разрешить трафик из этой сети

```shell
    docker network ls
    # Найдите сеть с именем вроде weatherapp_dbnet или bridge
    docker network inspect bridge | grep Subnet 
    # Скопируйте значение подсети (например, "172.17.0.0/16")
```

Теперь добавьте правило в файрвол, подставив вашу подсеть:

```shell
# Замените 172.17.0.0/16 на вашу подсеть
ufw allow from 172.17.0.0/16
```

## Общие инструкции

**Склонируйте репозиторий:**

```shell
git clone https://github.com/mandalorianec/WeatherApp.git
cd WeatherApp
```

Создайте local_settings в папке weather/weather/settings. Рядом с base.py и tests.py

   ```text
   from weather.weather.settings.base import *
   ```

### Деплой для продакшена

1. Создайте .env рядом с manage.py. Сгенерируйте свой ключ, например, на https://djecrety.ir/

```dotenv
    DEBUG=False
    SECRET_KEY="your_super_secret_production_key"
    API_KEY="your_api_key"

    POSTGRES_DB="weather_db"
    POSTGRES_USER="backender"
    POSTGRES_PASSWORD="12345"
    POSTGRES_HOST=postgres  # <-- Указываем имя сервиса Docker
    POSTGRES_PORT=5432

```

2. В корне проекта(рядом с manage.py) выполните:

   ```shell
   docker compose up -d --build
   ```

3. Приложение доступно по адресу http://127.0.0.1/ (или ip вашего сервера)
4. Чтобы остановить приложение, пропишите:

   ```shell
   docker compose down
   ```

### Локальный деплой, для разработки (БД создаётся докером, а проект находится локально)

1. Создайте .env рядом с manage.py. Сгенерируйте свой ключ, например, на https://djecrety.ir/
    ```dotenv
    DEBUG=True
    SECRET_KEY="local_development_key"
    API_KEY="your_api_key"

    POSTGRES_DB="weather_db"
    POSTGRES_USER="backender"
    POSTGRES_PASSWORD="12345"
    POSTGRES_HOST=127.0.0.1 # <-- Указываем localhost
    POSTGRES_PORT=5432
    ```
2. В проекте есть `docker-compose.yml`, который настроен для запуска всех сервисов. Чтобы запустить только базу данных,
   выполните в терминале:
    ```shell
    docker compose up postgres -d
    ```
3. Установите зависимости
    ```shell
    poetry install
    ```
4. Примените миграции
    ```shell
    poetry run python manage.py migrate
    poetry run python manage.py runserver
    ```
5. Чтобы остановить приложение, пропишите:

   ```shell
     docker compose stop postgres
   ```

Приложение будет доступно по адресу http://127.0.0.1:8000/ с отладкой и всеми инструментами

# Использование разных конфигураций

В проекте представлены 2 конфигурации: base.py и tests.py. base.py копирка settings.py. tests.py импортирует всё
содержимое base.py и дополняет/заменяет его. Можно использовать для изменения срока жизни сессии для тестов(tests.py).
Выбор конфигурации производится в файле local_settings.py, который нужно создать в settings, рядом с base.py и tests.py.
Поместить в него следующее содержимое:

```text
from weather.weather.settings.base import *
```

base/tests - в зависимости от конфигурации, которую вы выбрали

В файле manage.py local_settings.py прописывается вместо settings.py:

```text
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather.weather.settings.local_settings') # без .py
```

