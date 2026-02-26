README — Flask проект (регистрация / вход / профиль / проверка email через DNS)

Описание: минимальное Flask-приложение с регистрацией, входом, сессиями, хешированием паролей и проверкой существования домена email через DNS (dnspython).

Что делает проект

Регистрация пользователей (username, email, пароль).

Проверка формата email через re и проверка домена (MX/A) через dnspython.

Хеширование паролей (werkzeug.security) и хранение записей в SQLite (data.db).

Авторизация через session (сохранение user_id/username в cookie, подписанных secret_key).

Структура проекта (рекомендуемая)
Armen/
├── app.py
├── data.db                # создаётся автоматически при первом запуске
├── requirements.txt
└── templates/
    ├── index.html         # регистрация
    ├── Enter.html         # вход
    └── profile.html       # профиль
Требования

Python 3.11 (рекомендовано) или совместимая версия.

pip-пакеты: Flask, dnspython, werkzeug.

Пример requirements.txt:

Flask>=2.0
dnspython>=2.0
werkzeug>=2.0
