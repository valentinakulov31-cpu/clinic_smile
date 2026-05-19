# Backend сайта стоматологической клиники

Django + Django REST Framework backend для сайта клиники «Улыбнись».

База данных: PostgreSQL.

## Что уже заложено

- Контентные модели для филиалов, услуг, прайса, акций, специалистов, страниц, галереи, вакансий, контактов, документов и отзывов.
- Админка Django для управления всем изменяемым контентом.
- Публичные API endpoints для frontend.
- POST endpoints для заявок: консультация, запись, обратный звонок, отклик на вакансию.
- Email-уведомления по заявкам.
- Базовая защита форм: honeypot и rate limit.
- Ограничение форматов и размера загружаемых файлов.

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Перед `migrate` нужно создать PostgreSQL-базу и пользователя, указанные в `.env`.

Пример для локальной разработки:

```sql
CREATE DATABASE clinic_db;
CREATE USER clinic_user WITH PASSWORD 'clinic_password';
GRANT ALL PRIVILEGES ON DATABASE clinic_db TO clinic_user;
```

Если на сервере будут другие доступы, достаточно поменять `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` в `.env`.

## Основные API

Документация API:

- Swagger UI: `http://127.0.0.1:8015/api/docs/`
- ReDoc: `http://127.0.0.1:8015/api/redoc/`
- OpenAPI schema: `http://127.0.0.1:8015/api/schema/`

- `GET /api/branches/`
- `GET /api/service-categories/`
- `GET /api/services/`
- `GET /api/services/{slug}/`
- `GET /api/prices/`
- `GET /api/offers/`
- `GET /api/offers/{slug}/`
- `GET /api/specialists/`
- `GET /api/specialists/{slug}/`
- `GET /api/patients-page/`
- `GET /api/about/`
- `GET /api/gallery/`
- `GET /api/vacancies/`
- `GET /api/vacancies/{slug}/`
- `GET /api/contacts/`
- `GET /api/documents/`
- `GET /api/reviews/`
- `POST /api/requests/consultation/`
- `POST /api/requests/appointment/`
- `POST /api/requests/callback/`
- `POST /api/requests/vacancy/`

## POST заявки

Минимальное тело:

```json
{
  "name": "Иван",
  "phone": "+7 999 000-00-00",
  "email": "ivan@example.com",
  "comment": "Хочу записаться",
  "source": "hero-form",
  "website": ""
}
```

Поле `website` является honeypot-полем. На frontend его нужно отправлять пустым и не показывать пользователю.

## Настройка email

Для production нужно заполнить в `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=user@example.com
EMAIL_HOST_PASSWORD=password
EMAIL_USE_TLS=1
DEFAULT_FROM_EMAIL=user@example.com
REQUEST_NOTIFICATION_EMAIL=clinic@example.com
```
