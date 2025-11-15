# Деплой для продакшена

1.  **Склонируйте репозиторий:**
    ```shell
    git clone [ССЫЛКА_НА_ВАШ_GIT_РЕПОЗИТОРИЙ]
    cd Weather-dev
    ```
2. Создайте .env рядом с manage.py

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

3. В корне проекта(рядом с manage.py) выполните:

```shell
docker compose up -d --build
```

4. Приложение доступно по адресу http://127.0.0.1/
5. Чтобы остановить приложение, пропишите:

```shell
docker compose down
```
# Локальный деплой, для разработки (БД создаётся докером, а проект находится локально)
1.  **Склонируйте репозиторий:**
    ```shell
    git clone [ССЫЛКА_НА_ВАШ_GIT_РЕПОЗИТОРИЙ]
    cd Weather-dev
    ```

2. Создайте .env рядом с manage.py
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
3. В проекте есть `docker-compose.yml`, который настроен для запуска всех сервисов. Чтобы запустить **только базу данных**, выполните в терминале:
    ```shell
    docker compose up postgres -d
    ```
4. Установите зависимости  
    ```shell
    poetry install
    ```
5. Примените миграции
    ```shell
    python manage.py migrate
    python manage.py runserver
    ```
6. Чтобы остановить приложение, пропишите:

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
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather.settings.local_settings') # без .py
```
