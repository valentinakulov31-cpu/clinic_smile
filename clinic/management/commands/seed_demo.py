from datetime import date

from django.core.management.base import BaseCommand

from clinic.models import (
    AboutPage,
    Advantage,
    ContactInfo,
    HomePage,
    Offer,
    PatientsPage,
    PaymentMethod,
    PriceCategory,
    PriceItem,
    Requisites,
    Review,
    Service,
    ServiceCategory,
    ServicePageBlock,
    ServicePageBlockCard,
    SiteSettings,
    SocialLink,
    Specialist,
    SpecialistCategory,
    StaticPage,
    Vacancy,
)


class Command(BaseCommand):
    help = "Наполняет базу демо-контентом клиники «Улыбнись» (фактические данные с ulybnis24.ru). Команду можно запускать повторно."

    def handle(self, *args, **options):
        self.seed_site()
        self.seed_home()
        self.seed_services()
        self.seed_prices()
        self.seed_offers()
        self.seed_specialists()
        self.seed_pages()
        self.seed_reviews()
        self.seed_vacancies()
        self.stdout.write(self.style.SUCCESS("Демо-контент загружен."))

    def seed_site(self):
        if not SiteSettings.objects.exists():
            SiteSettings.objects.create(
                site_name="Стоматология «Улыбнись»",
                copyright_text="© 2026 ООО «Стомалюкс 21 век»",
                disclaimer="Имеются противопоказания, необходима консультация специалиста.",
                cta_title="Запишись на приём",
                cta_subtitle="Консультация, осмотр и подробный план лечения за 1000 ₽. Перезвоним в течение часа.",
            )

        if not ContactInfo.objects.exists():
            ContactInfo.objects.create(
                address="г. Красноярск, ул. Менжинского, 10д",
                phones=["+7 (391) 216-83-09", "+7 (391) 216-83-19"],
                email="ulybnis_krsk@mail.ru",
                work_hours="Пн — пт 09:00 — 21:00\nСб 10:00 — 17:00\nВс — выходной",
            )

        if not Requisites.objects.exists():
            Requisites.objects.create(
                company_name="ООО «Стомалюкс 21 век»",
                inn="2460077542",
                kpp="246001001",
                ogrn="1062460045306",
                bank_name="Восточно-Сибирский банк Сбербанка РФ, Красноярское городское отделение № 161",
                checking_account="40702810031280129414",
                bik="040407627",
                legal_address="660001, Красноярский край, г. Красноярск, ул. Менжинского, 10Д, кв. 34",
            )

        socials = [
            ("WhatsApp", "https://wa.me/79050863841"),
            ("Telegram", "https://telegram.im/@Ulybnis_stom"),
            ("ВКонтакте", "https://vk.com/club225923610"),
        ]
        for sort_order, (title, url) in enumerate(socials, start=1):
            SocialLink.objects.get_or_create(title=title, defaults={"url": url, "sort_order": sort_order})

        payments = [
            ("Наличные", "Оплата наличными в кассе клиники."),
            ("По карте", "Принимаем банковские карты любых банков."),
            ("Рассрочка", "Возможна оплата лечения в рассрочку — условия уточняйте у администратора."),
        ]
        for sort_order, (title, description) in enumerate(payments, start=1):
            PaymentMethod.objects.get_or_create(title=title, defaults={"description": description, "sort_order": sort_order})

    def seed_home(self):
        if not HomePage.objects.exists():
            HomePage.objects.create(
                hero_title="Улыбнись",
                hero_subtitle="Мы найдем лучший способ, чтобы вы улыбались свободно",
                hero_button_text="Записаться",
                hero_secondary_button_text="Наши услуги",
                about_title="О клинике",
                about_text=(
                    "Семейная клиника, в которой работают два поколения врачей. "
                    "Современные технологии и материалы сочетаются с многолетним опытом, "
                    "а к лечению применяется бережный комплексный подход."
                ),
            )
        else:
            # Приводим кнопки героя к новому макету, если их не меняли руками.
            home = HomePage.objects.first()
            if not home.hero_secondary_button_text:
                home.hero_button_text = home.hero_button_text or "Записаться"
                home.hero_secondary_button_text = "Наши услуги"
                home.save()

        advantages = [
            "Тщательная стерилизация инструментов и соблюдение санитарных норм",
            "Современные методы лечения и регулярное повышение квалификации врачей",
            "В работе используются только сертифицированные материалы",
        ]
        for sort_order, text in enumerate(advantages, start=1):
            Advantage.objects.get_or_create(text=text, defaults={"sort_order": sort_order})

    def seed_services(self):
        # Три категории с карточек главной страницы нового макета.
        categories = [
            ("esteticheskaya-stomatologiya", "Эстетическая стоматология", "Отбеливание и профессиональная гигиена", 1),
            ("lechenie-zubov", "Лечение зубов", "Без боли и с современными технологиями", 2),
            ("implantaciya-i-protezirovanie", "Имплантация и протезирование", "Вернём комфорт и уверенную улыбку", 3),
        ]
        # Старые названия категорий из первой версии демо-данных.
        legacy_names = {
            "esteticheskaya-stomatologiya": "Эстетика и протезирование",
            "lechenie-zubov": "Лечение и профилактика",
            "implantaciya-i-protezirovanie": "Имплантация и хирургия",
        }
        category_objects = {}
        for slug, name, description, sort_order in categories:
            category = (
                ServiceCategory.objects.filter(name=name).first()
                or ServiceCategory.objects.filter(name=legacy_names[slug]).first()
            )
            if category:
                category.name = name
                category.description = description
                category.sort_order = sort_order
                category.save()
            else:
                category = ServiceCategory.objects.create(name=name, description=description, sort_order=sort_order)
            category_objects[slug] = category

        services = [
            ("Имплантация", "implantation", "implantaciya-i-protezirovanie", "Надежное восстановление утраченных зубов с помощью дентальных имплантатов ведущих систем."),
            ("Протезирование", "protezirovanie", "implantaciya-i-protezirovanie", "Коронки, мосты и съемные протезы: восстановим зубной ряд удобно и эстетично."),
            ("Отбеливание зубов", "otbelivanie-zubov", "esteticheskaya-stomatologiya", "Профессиональное отбеливание для заметно более светлой улыбки без вреда для эмали."),
            ("Лечение", "lechenie", "lechenie-zubov", "Лечение кариеса и его осложнений с современной анестезией и надежными материалами."),
            ("Профилактика", "profilaktika", "esteticheskaya-stomatologiya", "Профессиональная гигиена полости рта: AirFlow, ультразвук, полировка и укрепление эмали."),
            ("Детская стоматология", "detskaya-stomatologiya", "lechenie-zubov", "Бережное лечение зубов у детей: находим подход даже к самым маленьким пациентам."),
            ("Пародонтология", "parodontologiya", "lechenie-zubov", "Лечение дёсен и тканей вокруг зуба: от кровоточивости до комплексной терапии пародонтита."),
            ("Хирургия", "hirurgiya", "implantaciya-i-protezirovanie", "Удаление зубов любой сложности, включая зубы мудрости, и подготовка к имплантации."),
            ("Диагностика", "diagnostika", "lechenie-zubov", "Рентгенография, цифровые оттиски и диагностические модели для точного плана лечения."),
        ]
        service_objects = {}
        for sort_order, (name, slug, category_slug, short_description) in enumerate(services, start=1):
            service, created = Service.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "category": category_objects[category_slug],
                    "short_description": short_description,
                    "sort_order": sort_order,
                },
            )
            if not created and service.category_id != category_objects[category_slug].id:
                service.category = category_objects[category_slug]
                service.save()
            service_objects[slug] = service

        implantation = service_objects["implantation"]
        if not implantation.hero_badge_1:
            implantation.hero_badge_1 = "Восстановление жевательной функции"
            implantation.hero_badge_2 = "Остановка атрофии костной ткани"
            implantation.hero_badge_3 = "Эстетика естественной улыбки"
            implantation.save()

        ServicePageBlock.objects.get_or_create(
            service=implantation,
            title="Этапы установки импланта",
            defaults={
                "block_type": ServicePageBlock.BlockType.TEXT,
                "description": (
                    "1. **Консультация и диагностика** — осмотр, снимки, план лечения.\n"
                    "2. **Подготовка** — санация полости рта, при необходимости костная пластика (до недели).\n"
                    "3. **Установка импланта** — операция занимает 30–60 минут.\n"
                    "4. **Протезирование** — установка коронки после приживления импланта."
                ),
                "sort_order": 1,
            },
        )

        self.seed_block_with_cards(
            implantation,
            title="Кому подойдёт?",
            block_type=ServicePageBlock.BlockType.CARDS,
            sort_order=2,
            cards=[
                ("Один или несколько зубов", "", "Когда предстоит восстановить один или несколько утраченных зубов.", ""),
                ("Полная адентия", "", "Если у пациента нет ни одного зуба.", ""),
                ("Альтернатива съемным протезам", "", "При наличии противопоказаний к установке съемных протезов.", ""),
            ],
        )

        self.seed_block_with_cards(
            implantation,
            title="Этапы работы",
            block_type=ServicePageBlock.BlockType.STEPS,
            sort_order=3,
            cards=[
                ("Шаг 1", "", "Осматриваем и консультируем.", ""),
                ("Шаг 2", "", "Проводим диагностику на современной высокоточной аппаратуре.", ""),
                ("Шаг 3", "", "По результатам осмотра и компьютерной диагностики составляем программу восстановления.", ""),
                ("Шаг 4", "", "По показаниям проводим процедуры для укрепления зубного ряда и дёсен.", ""),
                ("Шаг 5", "", "Назначаем дату следующего посещения, если нужен курс из нескольких процедур.", ""),
                ("Шаг 6", "", "Составляем рекомендации по домашнему уходу с учётом индивидуальных особенностей.", ""),
            ],
        )

        self.seed_block_with_cards(
            implantation,
            title="Виды имплантов",
            block_type=ServicePageBlock.BlockType.CARDS,
            sort_order=4,
            cards=[
                ("Neodent", "Бразилия, Straumann Group", "", "от 30 000 ₽"),
                ("CWM Inno", "Южная Корея", "", "от 24 900 ₽"),
                ("Nobel Biocare", "Швейцария", "", "по запросу"),
                ("Straumann", "Швейцария", "", "по запросу"),
            ],
        )

    def seed_block_with_cards(self, service, title, block_type, sort_order, cards):
        block, created = ServicePageBlock.objects.get_or_create(
            service=service,
            title=title,
            defaults={"block_type": block_type, "sort_order": sort_order},
        )
        if not created:
            return
        for card_sort, (card_title, subtitle, description, price_text) in enumerate(cards, start=1):
            ServicePageBlockCard.objects.create(
                block=block,
                title=card_title,
                subtitle=subtitle,
                description=description,
                price_text=price_text,
                sort_order=card_sort,
            )

    def seed_prices(self):
        prices = {
            "Консультации": [
                ("Прием врача-стоматолога-терапевта первичный", "700"),
                ("Прием врача-стоматолога-терапевта повторный", "660"),
                ("Прием врача-стоматолога-ортопеда первичный", "1000"),
                ("Прием врача-стоматолога-хирурга первичный", "1000"),
            ],
            "Терапия": [
                ("Восстановление зуба пломбой при среднем кариесе", "7700"),
                ("Восстановление зуба пломбой при глубоком кариесе", "8300"),
                ("Пломбирование корневого канала 1-корневого зуба", "2200"),
                ("Пломбирование корневых каналов 2-корневого зуба", "4400"),
            ],
            "Ортопедия": [
                ("Восстановление зуба постоянной коронкой (металлокерамика)", "15000"),
                ("Восстановление зуба постоянной безметалловой коронкой", "27000"),
                ("Протезирование полными съемными пластиночными протезами", "35500"),
                ("Протезирование съемными бюгельными протезами с кламмерной фиксацией", "47000"),
            ],
            "Хирургия": [
                ("Удаление постоянного зуба", "3000"),
                ("Удаление 8-го зуба простое", "6000"),
                ("Имплантация системой «Inno»", "24900"),
                ("Открытый синус-лифтинг", "38500"),
            ],
            "Диагностика": [
                ("Прицельная внутриротовая рентгенография", "470"),
                ("Прицельная внутриротовая рентгенография (на этапе лечения)", "350"),
                ("Снятие цифрового оттиска", "2750"),
                ("Исследование на диагностических моделях", "3300"),
            ],
            "Анестезия": [
                ("Аппликационная анестезия", "360"),
                ("Инфильтрационная анестезия", "850"),
            ],
            "Профилактика": [
                ("Профессиональная гигиена полости рта", "3600"),
                ("Профессиональная гигиена (комплекс: AirFlow, ультразвук)", "6000"),
                ("Обучение гигиене полости рта индивидуальное", "850"),
            ],
        }
        for category_sort, (category_name, items) in enumerate(prices.items(), start=1):
            category, _ = PriceCategory.objects.get_or_create(name=category_name, defaults={"sort_order": category_sort})
            for item_sort, (title, price) in enumerate(items, start=1):
                PriceItem.objects.get_or_create(
                    category=category,
                    title=title,
                    defaults={"price": price, "is_from_price": False, "sort_order": item_sort},
                )

    def seed_offers(self):
        # Заменяем акции первой версии демо-данных на карточки из нового макета.
        Offer.objects.filter(title__in=["Имплантация под ключ", "Профессиональная гигиена", "Скидка до 10% на комплексное лечение"]).delete()
        offers = [
            {
                "title": "Имплантация",
                "short_description": "Восстановление зубов системой Inno CWM Sub.",
                "price": "24900",
                "is_from_price": True,
                "ends_at": date(2026, 12, 31),
            },
            {
                "title": "Профессиональная гигиена полости рта",
                "short_description": "Перед хирургическим вмешательством.",
                "price": "3500",
                "is_from_price": False,
                "ends_at": date(2026, 12, 31),
            },
            {
                "title": "Имплант + коронка из диоксида циркония",
                "short_description": "Комплексное восстановление зуба под ключ.",
                "price": "62500",
                "is_from_price": True,
                "ends_at": date(2026, 12, 31),
            },
            {
                "title": "Бесплатная консультация",
                "short_description": "Осмотр и рекомендации по плану лечения.",
                "price": None,
                "is_from_price": False,
                "ends_at": None,
            },
        ]
        for sort_order, offer in enumerate(offers, start=1):
            Offer.objects.get_or_create(
                title=offer["title"],
                defaults={
                    "short_description": offer["short_description"],
                    "price": offer["price"],
                    "is_from_price": offer["is_from_price"],
                    "ends_at": offer["ends_at"],
                    "sort_order": sort_order,
                },
            )

    def seed_specialists(self):
        # Группы со страницы «Специалисты» нового макета.
        category_names = ["Врачи", "Младший персонал", "Администрация"]
        categories = {}
        for sort_order, name in enumerate(category_names, start=1):
            categories[name], _ = SpecialistCategory.objects.get_or_create(name=name, defaults={"sort_order": sort_order})

        specialists = [
            ("hodykin-a-d", "Ходыкин Артём Дмитриевич", "Руководитель клиники, стоматолог-ортопед, хирург", "Врачи"),
            ("dernovoy-a-a", "Дерновой Александр Андреевич", "Стоматолог-хирург, имплантолог", "Врачи"),
            ("hodykina-s-p", "Ходыкина Светлана Петровна", "Стоматолог-терапевт, пародонтолог", "Врачи"),
            ("simonyan-a-m", "Симонян Арменуи Михаковна", "Стоматолог-терапевт, детский врач", "Врачи"),
            ("ermakov-a-a", "Ермаков Артём Александрович", "Стоматолог-хирург, имплантолог", "Врачи"),
            ("kupriyanova-lada", "Куприянова Лада", "Старшая медицинская сестра", "Младший персонал"),
        ]
        for sort_order, (slug, full_name, position, category_name) in enumerate(specialists, start=1):
            specialist, _ = Specialist.objects.get_or_create(
                slug=slug,
                defaults={
                    "full_name": full_name,
                    "position": position,
                    "sort_order": sort_order,
                    "category": categories[category_name],
                },
            )
            if specialist.category_id is None:
                specialist.category = categories[category_name]
                specialist.save()

    def seed_pages(self):
        if not AboutPage.objects.exists():
            AboutPage.objects.create(
                title="О клинике",
                text=(
                    "История клиники началась более десяти лет назад с небольшого стоматологического кабинета. "
                    "В 2021 году открылась клиника «Улыбнись», чтобы расширить спектр услуг для пациентов.\n\n"
                    "Это семейное дело, в котором трудятся два поколения врачей. Мы совмещаем современные "
                    "технологии и материалы с многолетним опытом и бережным отношением к каждому пациенту."
                ),
            )

        if not PatientsPage.objects.exists():
            page = PatientsPage.objects.create(
                title="Пациентам",
                text=(
                    "Полезная информация и рекомендации от клиники.\n\n"
                    "Оплатить лечение можно наличными, банковской картой или в рассрочку. "
                    "Условия рассрочки уточняйте у администратора."
                ),
            )
            page.offers.set(Offer.objects.all())

        static_pages = [
            ("services", "Услуги", "Все направления стоматологической помощи в клинике «Улыбнись»", ""),
            ("prices", "Цены", "Актуальный прайс-лист на услуги клиники", ""),
            ("doctors", "Специалисты", "Команда клиники «Улыбнись»", ""),
            ("offers", "Акции", "Специальные предложения клиники", ""),
            ("reviews", "Отзывы", "Что говорят о нас пациенты", ""),
            ("documents", "Документы", "Лицензии и правовая информация", ""),
            ("vacancies", "Вакансии", "Присоединяйтесь к нашей команде", ""),
            (
                "policy",
                "Политика конфиденциальности",
                "",
                "Текст политики обработки персональных данных. Заполните этот раздел "
                "актуальной редакцией политики в админке (Статичные страницы → policy).",
            ),
        ]
        for key, title, subtitle, text in static_pages:
            StaticPage.objects.get_or_create(key=key, defaults={"title": title, "subtitle": subtitle, "text": text})

    def seed_reviews(self):
        # Демо-отзывы: имена и тексты вымышленные, для наполнения макета.
        reviews = [
            ("Мария", "Очень внимательные врачи! Лечила кариес — всё прошло безболезненно и быстро. Спасибо клинике!", 5, "2ГИС"),
            ("Ольга", "Делала профессиональную гигиену. Результатом довольна, зубы заметно светлее. Приду ещё.", 5, "Яндекс Карты"),
            ("Дмитрий", "Ставил имплант — всё объяснили, показали план лечения, никаких скрытых доплат. Рекомендую.", 5, "2ГИС"),
            ("Елена", "Вожу сюда ребёнка, врач нашла подход — теперь идём к стоматологу без слёз. Большое спасибо!", 5, "Яндекс Карты"),
            ("Сергей", "Удаляли зуб мудрости. Переживал зря — аккуратно, быстро и с подробными рекомендациями после.", 5, "2ГИС"),
            ("Анна", "Протезирование прошло отлично, коронку не отличить от своих зубов. Приятная и чистая клиника.", 5, "Яндекс Карты"),
        ]
        for sort_order, (author, text, rating, source) in enumerate(reviews, start=1):
            Review.objects.get_or_create(
                author_name=author,
                text=text,
                defaults={"rating": rating, "source": source, "reviewed_at": date(2026, 6, 1), "sort_order": sort_order},
            )

    def seed_vacancies(self):
        Vacancy.objects.get_or_create(
            slug="administrator",
            defaults={
                "title": "Администратор клиники",
                "short_description": "Ищем внимательного администратора в дружную команду.",
                "responsibilities": "Встреча пациентов, запись на приём, работа с кассой и документами.",
                "requirements": "Грамотная речь, доброжелательность, уверенный пользователь ПК.",
                "conditions": "График 2/2, официальное трудоустройство, дружный коллектив.",
                "description": "Демо-вакансия для проверки раздела. Отредактируйте или скройте её в админке.",
                "sort_order": 1,
            },
        )
