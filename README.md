# Веб-сервис для оценки эмоционального восприятия новостных сообщений в сети 
Данный сервис предназначен для анализа пользователей таких социальных сетей как Reddit и Twitter.

Пример работы веб-сервиса можно увидеть по [ссылке](http://167.99.141.90.xip.io/) 

# Деплой на удаленный сервер (VPS)
Шаг 1. Активировать виртуальное окружение и установить требуемые зависимости.
```
virtualenv diploma_thesis
source bin/activate
sudo pip3 install -r requirements.txt
```
Шаг 2. Заполнить значения переменных окружения (см. ниже "Настройка переменных окружения"). 

Затем установить параметры окружения, введя в консоли
```
source envs.txt
```
Шаг 3. Выполнить fabric-скрипт для деплоя на удалённую машину.
```
fab deploy_with_train
```
Данный скрипт делает следующие действия на удалённой машине:
* Устанавливает нужные системные пакеты. Python, nginx, PostgreSQL и их требования.
* Конфигурирует БД: создает базу и пользователя со всеми нужными правами.
* Настраивает nginx на пробрасывание запроса к приложению.
* Создает папку с сорцами, клонирует в неё последнюю версию репозитория.
* Создает виртуальное окружение с нужной версией Python, установливает в него все пакеты из requirements.txt.
* Загружает данные для обучения и обучает тональный и тематический анализаторы.
* Рестартует/запускает uwsgi и nginx.

Конфиги для nginx и uwsgi генерируются из шаблонов в папке deploy_configs.

После этого приложение будет доступно по ip-адресу удаленной машины.

В дальнейшем при необходимости повторного деплоя (например, при изменениях в репозитории) это возможно осуществить двумя командами.

В случае деплоя без повторного обучения анализаторов:
```
fab deploy
```
В случае деплоя c повторным обучением анализаторов:
```
fab deploy_with_train
```

# Деплой на localhost
Шаг 1. Активировать виртуальное окружение и установить требуемые зависимости.
```
virtualenv diploma_thesis
source bin/activate
sudo pip3 install -r requirements.txt
```
Шаг 2. Скачать данные для обучения тонального и тематического анализаторов.
```
python3 sentiment/save_sentiment_dataset.py
python3 lda/createuci.py
```
Данные для обучения будут находиться в папках sentiment_dataset и uci_data.

Шаг 3. Обучить тональный и тематический анализаторы.
```
python3 sentiment/train.py
python3 lda/trainmodel.py
```
Шаг 4. Заполнить значения переменных окружения (см. ниже "Настройка переменных окружения"). 

Затем установить параметры окружения, введя в консоли
```
source envs.txt
```

Шаг 4. Запустить сервис на локальном сервере.
```
python3 server.py
```
После этого сервис будет доступен по данной [ссылке](http://localhost:5000/)

# Настройка переменных окружения
Для того, чтобы выполнить деплой на локальный или удаленный сервер, необходимо
указать переменные окружения в файле *ensv.txt*.

Описание переменных окружения:

* ADMIN_EMAIL, ADMIN_PASSWORD - логин и пароль администратора
* DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT - параметры БД
* FACEBOOK_ID, FACEBOOK_SECRET - параметры facebook (получить [здесь](https://developers.facebook.com/))
* GMAIL_USERNAME, GMAIL_PASSWORD - логин и пароль почты gmail
* GOOGLE_ID, GOOGLE_SECRET - параметры Google (получить [здесь](https://developers.google.com/identity/sign-in/web/sign-in))
* HOST, HOST_PORT, HOST_USER, HOST_PASSWORD - параметры удаленного сервера (при деплое на VPS)
* PLOTLY_USERNAME, PLOTLY_API_KEY - параметры, необходимые для построения графиков (получить [здесь](https://plot.ly/))
* PROJECT_NAME, PROJECT_PATH - название проекта и путь к папке с проектом
* REDDIT_USER_AGENT, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_CLIENT_USERNAME, REDDIT_PASSWORD - параметры Reddit (получить [здесь](https://www.reddit.com/prefs/apps))
* REPO - адрес до репозиториев пользователя (например, https://github.com/MakarovYaroslav)
* SECRET_KEY, SECURITY_PASSWORD_SALT - секретный ключ и соль для работы приложения
* SENTRY_DSN - Client Key (DSN) для логирования в Sentry (получить [здесь](https://sentry.io/))
* TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_KEY, TWITTER_ACCESS_SECRET - параметры Twitter (получить [здесь](https://apps.twitter.com/)) 