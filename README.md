# PetFlow 🐾
PetFlow — это backend-приложение для управления ветеринарной платформой:
питомцы, клиники, записи на приём, отзывы и пользовательская система с авторизацией.
Проект построен на Django и Django REST Framework и предоставляет REST API для взаимодействия с клиентской частью
(web/mobile).
---

## 🚀 Функциональность

### 👤 Пользователи
- Регистрация и авторизация (Djoser + SimpleJWT)
- Профиль пользователя
- JWT-аутентификация

### 🐶 Питомцы
- Добавление питомцев пользователем
- Просмотр и управление своими питомцами
- Связь питомца с пользователем

### 🏥 Клиники
- Список ветеринарных клиник
- Детальная информация о клинике

### 📅 Записи на приём
- Создание записи на приём к ветеринару
- Проверка доступности слотов
- Защита от записи на чужих питомцев
- Разделение read/write сериализаторов
- Статусы записей (например: created, confirmed, canceled)

### ⭐ Отзывы
- Добавление отзывов о клиниках
- CRUD для отзывов
- Привязка отзыва к пользователю и клинике
---

## 🛠 Технологии
- Python 3.11+
- Django
- Django REST Framework
- SimpleJWT
- Djoser
- PostgreSQL
---

## 📦 Установка и запуск

### 1. Клонировать репозиторий
```bash
git clone https://github.com/BocharnikovSergey/petflow.git
cd petflow
```

### 2. Создание виртуального окружения
Cоздать и активировать виртуальное окружение:

* Если у вас Linux/macOS
```bash
    python3 -m venv env
    source env/bin/activate
    python3 -m pip install --upgrade pip
```
* Если у вас windows
```bash
    python -m venv env
    source env/scripts/activate
    python -m pip install --upgrade pip
```

### 3. Установить зависимости из файла requirements.txt:
```bash
pip install -r requirements.txt
```

### 4. Выполнить миграции:
* Если у вас Linux/macOS
```bash
    python3 manage.py migrate
```
* Если у вас windows
```bash
    python manage.py migrate
```
Запустить проект:
* Если у вас Linux/macOS
```bash
    python3 manage.py runserver
```
* Если у вас windows
```bash
    python manage.py runserver
```

### 6. Развертывание проекта на Docker:
Подготовить .env файл. Выполнить команды

```bash
cd ./infra/
docker compose up --build.
```
Для заполнения volumes  выполнить команды
```bash
docker run --rm   -v infra_pg_data:/volume   -v "$(pwd -W):/backup"   alpine   sh -c "ls -l /backup && tar xzf /backup/pg_data.tar.gz -C /volume"
docker run --rm   -v infra_media:/volume   -v "$(pwd -W):/backup"   alpine   sh -c "ls -l /backup && tar xzf /backup/media.tar.gz -C /volume"
```

### 7. Документация API
Документация доступна по адресу:
ReDoc: http://localhost:8000/api/v1/docs/
Swagger: http://localhost:8000/api/v1/swagger/


## Примеры запросов:

### Регистрация пользователя
```bash
POST /api/v1/auth/signup/
Content-Type: application/json

{
  "email": "vpupkin@yandex.ru",
  "first_name": "Вася",
  "last_name": "Иванов",
  "password": "Qwerty123"
}
```
### Ответ
```bash
Content-Type: application/json
{
  "email": "vpupkin@yandex.ru",
  "first_name": "Вася",
  "last_name": "Иванов"
}
```

### Текущий пользователь
```bash
GET /api/users/me
```
### Ответ
```bash
Content-Type: application/json
{
  "id": 1,
  "email": "vpupkin@yandex.ru",
  "phone": "89888888888",
  "first_name": "Вася",
  "last_name": "Иванов",
  "avatar": "http://127.0.0.1:8000/media/users/avatars/avatars_admin.jpg",
  "bio": "string",
  "pets": [
    {
      "id": 1,
      "name": "Бобик",
      "species": 1
    },
    {
      "id": 2,
      "name": "Барсик",
      "species": 2
    }
  ]
}
```

### Создание питомца
```bash
POST /api/v1/pets/
Content-Type: application/json

{
  "name": "Бобик",
  "species": 1,
  "breed": 1,
  "birth_date": null,
  "weight": null,
}
```
### Ответ
```bash
Content-Type: application/json
{
  "id": 2,
  "owner": 1,
  "name": "Бобик",
  "species": {
    "id": 1,
    "name": "Собака"},
  "breed": {
    "id": 1,
    "name": "Лабрадор"},
  "birth_date": null,
  "weight": null,
  "avatar": null
}
```

### Получение клиник
```bash
GET api/recipes/{id}/get-link/
```
### Ответ
```bash
Content-Type: application/json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Первая клиника",
      "address": {
        "id": 1,
        "city": "Москва",
        "street": "Ленина",
        "house": "30",
        "full_address": "г.Москва, ул.Ленина, д.30"},
      "phone": null,
      "email": "perva@clinic.ru",
      "description": "string",
      "logo": "http://127.0.0.1:8000/media/clinics/logo/logo_clinic.jpg",
      "rating": 4.6
    }
  ]
}
```

### Оставление отзыва клинике
```bash
POST /api/v1/clinics/{clinic_id}/reviews/
{
  "text": "Лучшая клиника",
  "score": 5
}
```

### Ответ
```bash
Content-Type: application/json
{
  "id": 1,
  "text": "Лучшая клиника",
  "author": 1,
  "score": 5
}
```

### Получение слотов записи в клинику
```bash
GET /api/v1/clinics/{clinic_id}/slots/
```
### Ответ
```bash
Content-Type: application/json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "clinic": 1,
      "start_time": "13:00:00.000000",
      "end_time": "13:30:00.000000"
    }
  ]
}
```

### Запись в клинику
```bash
POST /api/v1/clinics/{clinic_id}/reviews/
{
  "pet": 1,
  "date": "2026-05-15",
  "slot": 1,
  "comment": "string"
}
```
### Ответ
```bash
Content-Type: application/json

{
  "id": 2,
  "pet": {
    "id": 1,
    "name": "Бобик",
    "species": 1},
  "date": "2026-05-15",
  "clinic": {
    "id": 1,
    "name": "Первая клиника",
    "address": 1,
    "phone": null,
    "email": "perva@clinic.ru"},
  "slot": {
    "start_time": "13:00:00.000000",
    "end_time": "13:30:00.000000"},
  "comment": "string",
  "user": {
    "id": 1,
    "full_name": "Вася Иванов",
    "email": "vpupkin@yandex.ru",
    "phone": null},
  "status": "pending"
}
```

- [Сергей Бочарников](https://github.com/BocharnikovSergey)
