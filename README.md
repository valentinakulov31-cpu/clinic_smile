# Backend сайта стоматологической клиники

Django + Django REST Framework backend для сайта клиники «Улыбнись».

База данных: PostgreSQL.

## Что уже заложено

- Контентные модели для филиалов, услуг, прайса, акций, специалистов, страниц, галереи, вакансий, контактов, документов и отзывов.
- Главная страница (hero, блок «О клинике»), преимущества, соцсети и общие настройки сайта (копирайт, дисклеймер, CTA-блок записи, ссылка на полный прайс).
- Статичные страницы (`/api/pages/`) для заголовков и SEO списковых страниц и политики конфиденциальности.
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

Полное описание разделов админки и всех API: [docs/API_AND_ADMIN.md](docs/API_AND_ADMIN.md).

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
- `GET /api/specialists/`
- `GET /api/specialist-categories/` — специалисты, сгруппированные по разделам (Врачи, Младший персонал, Администрация)
- `GET /api/specialists/{slug}/`
- `GET /api/patients-page/`
- `GET /api/about/`
- `GET /api/gallery/`
- `GET /api/vacancies/`
- `GET /api/vacancies/{slug}/`
- `GET /api/contacts/`
- `GET /api/documents/`
- `GET /api/document-categories/` — документы, сгруппированные по категориям
- `GET /api/reviews/`
- `GET /api/home/` — главная страница (hero, блок «О клинике», преимущества)
- `GET /api/advantages/`
- `GET /api/social-links/`
- `GET /api/settings/` — настройки сайта: логотип, копирайт, дисклеймер, CTA-блок, ссылка на полный прайс, соцсети
- `GET /api/pages/` и `GET /api/pages/{key}/` — статичные страницы (`services`, `prices`, `doctors`, `offers`, `reviews`, `documents`, `vacancies`, `policy`)
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

## Контент страниц услуг

Детальная страница услуги собирается из повторяемых блоков:

- у самой услуги есть верхняя часть страницы: `preview_logo`, `card_image`, `name`, `short_description` и три `hero_badge`;
- ниже идут блоки `ServicePageBlock` с полями `block_type`, `title`, `description`, `image`, `sort_order`;
- `block_type = text` — обычный текстовый блок, `description` предназначено для Markdown-текста;
- `block_type = cards` — карусель карточек (например, виды имплантов): карточки (`title`, `subtitle`, `description`, `price_text`, `image`) добавляются в разделе админки «Блоки страницы услуги» при открытии блока отдельной записью;
- в остальных частях админки используются обычные текстовые поля без HTML-редактора.

## Соглашения по контенту

- Пагинация на контентных списках отключена: фронт получает массивы целиком.
- Телефоны в «Контактах» и «Филиалах» вводятся в админке по одному на строку, в API отдаются массивом строк.
- Источник контактов сайта (шапка, футер, страница контактов) — запись «Контакты» (`/api/contacts/`). «Филиалы» задел на будущее для нескольких адресов; сейчас их можно не заполнять.
- Записи-синглтоны (главная, о клинике, пациентам, контакты, реквизиты, настройки сайта) создаются в одном экземпляре — админка не даст добавить вторую запись.

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
