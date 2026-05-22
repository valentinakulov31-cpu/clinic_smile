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

## Структура кода

- `clinic/models.py` — доменные модели сайта.
- `clinic/model_utils.py` — slug, SEO-автозаполнение и валидация файлов.
- `clinic/admin.py` — регистрация моделей в админке.
- `clinic/admin_utils.py` — общие admin-миксины: вкладки, rich text, сортировка.
- `clinic/*_serializers.py` — публичный JSON-контракт, разнесенный по доменам.
- `clinic/serializers.py` — совместимый фасад для импорта всех serializer-классов.
- `clinic/*_views.py` — публичные API views, разнесенные по доменам.
- `clinic/views.py` — совместимый фасад для импорта всех view-классов.
- `clinic/api_utils.py` — общие API-миксины и фильтрация.
- `appointments/` — формы и заявки.

Новые повторяемые страницы/блоки лучше сначала проверять на возможность переиспользования `ServicePageBlock` / `ServicePageBlockItem`, а не заводить отдельную модель под каждый визуальный блок.

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

## Детальные страницы услуг

По референсу детальная страница услуги состоит не только из основного описания, а из набора повторяемых блоков. Для этого у услуги есть `blocks`.

Типы блоков:

- `features` — преимущества в hero;
- `content` — текстовая секция с HTML;
- `indications` — блок «Кому подойдет»;
- `technologies` — технологии и подуслуги;
- `product_cards` — карточки систем, материалов или имплантов с характеристиками;
- `steps` — этапы работы;
- `cta` — блок записи;
- `custom` — произвольный блок.

У каждого блока могут быть вложенные `items`, чтобы хранить карточки, этапы, характеристики и повторяющиеся элементы.

## Прайс

Прайс поддерживает структуру как в референсе:

- категория прайса как верхний таб;
- группа прайса внутри категории;
- позиции прайса внутри группы.

Позиции без группы тоже поддерживаются и отдаются в `items` категории.

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

## Автозаполнение slug, SEO и Open Graph

Для услуг, категорий услуг, прайса, спецпредложений, специалистов, вакансий и категорий документов технические поля можно не заполнять руками:

- `slug` генерируется автоматически из названия, если пустой;
- `slug` приводится к lowercase и дефисам;
- русские названия транслитерируются, например `Тестовая вакансия` -> `testovaya-vakansiya`;
- если такой `slug` уже занят, добавляется суффикс `-2`, `-3` и так далее;
- `SEO title` заполняется из названия, если пустой;
- `SEO description` заполняется из краткого описания/описания, если пустой;
- `Open Graph title` заполняется из `SEO title` или названия, если пустой;
- `Open Graph description` заполняется из `SEO description` или описания, если пустой.

Если поле заполнено вручную, backend его не перезаписывает.

В админке `slug` остается в основной вкладке записи. SEO и Open Graph поля вынесены в отдельную вкладку `SEO` у сущностей, где они есть.

## HTML-редактор в админке

Для контентных текстовых полей подключен CKEditor 5. Он позволяет вставлять и редактировать:

- заголовки;
- жирный/курсив/подчеркивание;
- ссылки;
- списки;
- цитаты;
- таблицы;
- базовое форматирование текста.

Редактор сохраняет HTML в обычные текстовые поля. Frontend получает этот HTML в API и должен выводить его как HTML-контент.

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
