from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from .models import (
    AboutPage,
    Advantage,
    Branch,
    ContactInfo,
    Document,
    DocumentCategory,
    GalleryImage,
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
    ServiceImage,
    ServicePageBlock,
    ServicePageBlockCard,
    SiteSettings,
    SocialLink,
    Specialist,
    SpecialistCategory,
    SpecialistDocument,
    StaticPage,
    Vacancy,
)


TEST_MEDIA_ROOT = "C:/Users/user/PycharmProjects/PythonProject43/clinic_smile/test_media"


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class PublicApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.branch = Branch.objects.create(name="Центр", address="Адрес 1", sort_order=1)
        cls.branch_inactive = Branch.objects.create(name="Скрытый", address="Адрес 2", is_active=False)

        cls.category = ServiceCategory.objects.create(name="Ортопедия", sort_order=1)
        cls.category_inactive = ServiceCategory.objects.create(name="Скрытая категория", is_active=False)

        cls.service = Service.objects.create(
            category=cls.category,
            name="Протезирование",
            short_description="Коротко",
            description="Полное описание",
            hero_badge_1="Без боли",
            hero_badge_2="Под ключ",
            hero_badge_3="С гарантией",
            sort_order=1,
        )
        cls.service.branches.add(cls.branch)
        cls.service_inactive = Service.objects.create(
            category=cls.category,
            name="Скрытая услуга",
            is_active=False,
        )
        cls.service_image = ServiceImage.objects.create(service=cls.service, image=SimpleUploadedFile("a.jpg", b"file"), caption="Фото", sort_order=1)
        ServiceImage.objects.create(service=cls.service, image=SimpleUploadedFile("b.jpg", b"file"), caption="Скрыто", is_active=False)
        cls.service_block = ServicePageBlock.objects.create(
            service=cls.service,
            title="Подробности",
            description="**Markdown** block",
            sort_order=1,
        )
        ServicePageBlock.objects.create(service=cls.service, title="Скрытый блок", is_active=False)
        cls.cards_block = ServicePageBlock.objects.create(
            service=cls.service,
            block_type=ServicePageBlock.BlockType.CARDS,
            title="Виды имплантов",
            sort_order=2,
        )
        ServicePageBlockCard.objects.create(
            block=cls.cards_block,
            title="Neodent",
            subtitle="Бразилия",
            price_text="от 30 000 ₽",
            sort_order=1,
        )
        ServicePageBlockCard.objects.create(block=cls.cards_block, title="Скрытая карточка", is_active=False)

        cls.price_category = PriceCategory.objects.create(name="Основные услуги", sort_order=1)
        PriceItem.objects.create(category=cls.price_category, service=cls.service, branch=cls.branch, title="Коронка", price="12000.00", sort_order=1)
        PriceItem.objects.create(category=cls.price_category, title="Скрытая цена", price="9000.00", is_active=False)

        cls.offer = Offer.objects.create(title="Скидка", short_description="Акция", sort_order=1)
        cls.offer.branches.add(cls.branch)
        Offer.objects.create(title="Скрытая акция", is_active=False)

        cls.doctors_category = SpecialistCategory.objects.create(name="Врачи", sort_order=1)
        SpecialistCategory.objects.create(name="Пустая группа", sort_order=2)
        cls.specialist = Specialist.objects.create(
            category=cls.doctors_category,
            full_name="Иван Иванов",
            position="Стоматолог",
            short_description="Опытный врач",
            description="Подробно о враче",
            experience="10 лет",
            sort_order=1,
        )
        cls.specialist.services.add(cls.service)
        cls.specialist.branches.add(cls.branch)
        SpecialistDocument.objects.create(
            specialist=cls.specialist,
            title="Сертификат",
            file=SimpleUploadedFile("cert.pdf", b"pdf"),
            sort_order=1,
        )
        Specialist.objects.create(full_name="Скрытый врач", is_active=False)

        cls.patients_page = PatientsPage.objects.create(title="Пациентам", text="Инфо")
        cls.patients_page.offers.add(cls.offer)
        PaymentMethod.objects.create(title="Карта", description="Оплата картой", sort_order=1)
        PaymentMethod.objects.create(title="Скрытый способ", is_active=False)

        cls.about_page = AboutPage.objects.create(title="О клинике", text="История")
        GalleryImage.objects.create(about_page=cls.about_page, image=SimpleUploadedFile("gallery.jpg", b"file"), caption="Интерьер", sort_order=1)
        GalleryImage.objects.create(image=SimpleUploadedFile("global.jpg", b"file"), caption="Общая галерея", sort_order=2)

        cls.vacancy = Vacancy.objects.create(title="Администратор", short_description="Описание вакансии", description="Подробно", sort_order=1)
        Vacancy.objects.create(title="Скрытая вакансия", is_active=False)

        cls.contacts = ContactInfo.objects.create(address="Красноярск", phones=["+7 000 000-00-00"], email="info@example.com")
        cls.requisites = Requisites.objects.create(company_name="ООО Улыбнись", inn="1234567890")

        cls.document_category = DocumentCategory.objects.create(title="Лицензии", sort_order=1)
        cls.document = Document.objects.create(
            category=cls.document_category,
            title="Лицензия",
            file=SimpleUploadedFile("license.pdf", b"pdf"),
            sort_order=1,
        )
        Document.objects.create(title="Скрытый документ", file=SimpleUploadedFile("hidden.pdf", b"pdf"), is_active=False)

        Review.objects.create(author_name="Мария", text="Отлично", rating=5, sort_order=1)
        Review.objects.create(author_name="Скрытый", text="Плохо", rating=1, is_active=False)

        cls.home_page = HomePage.objects.create(
            hero_title="Улыбайтесь свободно",
            hero_subtitle="Мы найдем лучший способ",
            hero_button_text="Записаться",
            hero_secondary_button_text="Наши услуги",
            about_title="О клинике",
            about_text="Семейное дело",
        )
        Advantage.objects.create(text="Стерилизация инструментов", sort_order=1)
        Advantage.objects.create(text="Скрытое преимущество", is_active=False)

        cls.settings = SiteSettings.objects.create(
            site_name="Улыбнись",
            copyright_text="© 2026 ООО «Стомалюкс 21 век»",
            disclaimer="Имеются противопоказания",
            cta_title="Запишись на приём",
            cta_subtitle="План лечения за 1000 ₽",
            price_full_url="https://example.com/full-price",
        )
        SocialLink.objects.create(title="Telegram", url="https://t.me/example", sort_order=1)
        SocialLink.objects.create(title="Скрытая соцсеть", url="https://example.com", is_active=False)

        cls.policy_page = StaticPage.objects.create(
            key=StaticPage.PageKey.POLICY,
            title="Политика конфиденциальности",
            text="Текст политики",
        )
        StaticPage.objects.create(key=StaticPage.PageKey.PRICES, title="Цены")

    def test_branches_list_returns_only_active_items(self):
        response = self.client.get(reverse("branch-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.branch.name)

    def test_service_categories_list_returns_only_active_items(self):
        response = self.client.get(reverse("service-category-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.category.name)

    def test_services_list_supports_branch_and_category_filters(self):
        response = self.client.get(reverse("service-list"), {"branch": self.branch.id, "category": self.category.slug})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.service.name)

    def test_service_detail_returns_active_nested_content_and_new_structure(self):
        response = self.client.get(reverse("service-detail", kwargs={"slug": self.service.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.service.name)
        self.assertEqual(response.data["hero_badges"], ["Без боли", "Под ключ", "С гарантией"])
        self.assertEqual(len(response.data["page_blocks"]), 2)
        self.assertEqual(response.data["page_blocks"][0]["title"], self.service_block.title)
        self.assertEqual(response.data["page_blocks"][0]["block_type"], "text")
        self.assertEqual(len(response.data["images"]), 1)

    def test_service_detail_returns_cards_block_with_active_cards(self):
        response = self.client.get(reverse("service-detail", kwargs={"slug": self.service.slug}))
        self.assertEqual(response.status_code, 200)
        cards_block = response.data["page_blocks"][1]
        self.assertEqual(cards_block["block_type"], "cards")
        self.assertEqual(len(cards_block["cards"]), 1)
        self.assertEqual(cards_block["cards"][0]["title"], "Neodent")
        self.assertEqual(cards_block["cards"][0]["price_text"], "от 30 000 ₽")

    def test_prices_list_groups_active_items(self):
        response = self.client.get(reverse("price-list"), {"branch": self.branch.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["items"][0]["title"], "Коронка")

    def test_offers_list_returns_active_items(self):
        response = self.client.get(reverse("offer-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], self.offer.title)

    def test_specialist_categories_group_active_specialists(self):
        response = self.client.get(reverse("specialist-category-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Врачи")
        self.assertEqual(len(response.data[0]["specialists"]), 1)
        self.assertEqual(response.data[0]["specialists"][0]["full_name"], "Иван Иванов")

    def test_specialist_list_includes_category(self):
        response = self.client.get(reverse("specialist-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["category"]["name"], "Врачи")

    def test_specialist_detail_returns_documents(self):
        response = self.client.get(reverse("specialist-detail", kwargs={"slug": self.specialist.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["full_name"], self.specialist.full_name)
        self.assertEqual(len(response.data["documents"]), 1)

    def test_patients_page_returns_payment_methods_and_offers(self):
        response = self.client.get(reverse("patients-page"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.patients_page.title)
        self.assertEqual(len(response.data["payment_methods"]), 1)
        self.assertEqual(len(response.data["offers"]), 1)

    def test_about_page_returns_gallery(self):
        response = self.client.get(reverse("about-page"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.about_page.title)
        self.assertEqual(len(response.data["gallery"]), 1)

    def test_gallery_list_returns_active_items(self):
        response = self.client.get(reverse("gallery-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_vacancy_detail_returns_public_fields(self):
        response = self.client.get(reverse("vacancy-detail", kwargs={"slug": self.vacancy.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.vacancy.title)

    def test_contacts_endpoint_embeds_requisites(self):
        response = self.client.get(reverse("contacts"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["address"], self.contacts.address)
        self.assertEqual(response.data["requisites"]["company_name"], self.requisites.company_name)

    def test_documents_list_returns_full_fields_with_category(self):
        response = self.client.get(reverse("document-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], self.document.title)
        self.assertEqual(response.data[0]["category"]["title"], self.document_category.title)

    def test_document_categories_group_active_documents(self):
        response = self.client.get(reverse("document-category-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], self.document_category.title)
        self.assertEqual(len(response.data[0]["documents"]), 1)

    def test_reviews_list_returns_only_active_items(self):
        response = self.client.get(reverse("review-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["author_name"], "Мария")

    def test_home_page_returns_hero_and_advantages(self):
        response = self.client.get(reverse("home-page"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["hero_title"], self.home_page.hero_title)
        self.assertEqual(response.data["hero_secondary_button_text"], "Наши услуги")
        self.assertEqual(response.data["about_text"], self.home_page.about_text)
        self.assertEqual(len(response.data["advantages"]), 1)

    def test_site_settings_returns_footer_content_and_social_links(self):
        response = self.client.get(reverse("site-settings"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["copyright_text"], self.settings.copyright_text)
        self.assertEqual(response.data["disclaimer"], self.settings.disclaimer)
        self.assertEqual(response.data["price_full_url"], self.settings.price_full_url)
        self.assertEqual(len(response.data["social_links"]), 1)
        self.assertEqual(response.data["social_links"][0]["title"], "Telegram")

    def test_static_page_detail_returns_page_by_key(self):
        response = self.client.get(reverse("static-page-detail", kwargs={"key": "policy"}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.policy_page.title)
        self.assertEqual(response.data["text"], self.policy_page.text)

    def test_static_pages_list_returns_all_pages(self):
        response = self.client.get(reverse("static-page-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
