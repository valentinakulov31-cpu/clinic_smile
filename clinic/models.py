from django.core.exceptions import ValidationError
from django.db import models

from . import model_utils as _model_utils


def make_slug(value):
    return _model_utils.make_slug(value)


def truncate(value, max_length):
    return _model_utils.truncate(value, max_length)


def compact_description(value, max_length=180):
    return _model_utils.compact_description(value, max_length)


def get_title_source(instance):
    return _model_utils.get_title_source(instance)


def get_description_source(instance):
    return _model_utils.get_description_source(instance)


def ensure_unique_slug(instance, source):
    return _model_utils.ensure_unique_slug(instance, source)


def fill_seo_fields(instance):
    return _model_utils.fill_seo_fields(instance)


def validate_upload_size(file):
    return _model_utils.validate_upload_size(file)


def validate_extension(file, allowed):
    return _model_utils.validate_extension(file, allowed)


def validate_image(file):
    return _model_utils.validate_image(file)


def validate_document(file):
    return _model_utils.validate_document(file)


class ActiveOrderedModel(models.Model):
    is_active = models.BooleanField("Активно", default=True)
    sort_order = models.PositiveIntegerField("Сортировка", default=100)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        abstract = True
        ordering = ("sort_order", "id")


class SeoModel(models.Model):
    slug = models.SlugField("Slug", max_length=180, unique=True, blank=True)
    seo_title = models.CharField("SEO title", max_length=255, blank=True)
    seo_description = models.TextField("SEO description", blank=True)
    og_title = models.CharField("Open Graph title", max_length=255, blank=True)
    og_description = models.TextField("Open Graph description", blank=True)
    og_image = models.ImageField(
        "Open Graph image",
        upload_to="seo/",
        blank=True,
        null=True,
        validators=[validate_image],
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        ensure_unique_slug(self, get_title_source(self))
        fill_seo_fields(self)
        super().save(*args, **kwargs)


class Branch(ActiveOrderedModel):
    name = models.CharField("Название", max_length=255)
    address = models.CharField("Адрес", max_length=500)
    phones = models.JSONField("Телефоны", default=list, blank=True)
    email = models.EmailField("Email", blank=True)
    work_hours = models.TextField("Режим работы", blank=True)
    latitude = models.DecimalField("Широта", max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField("Долгота", max_digits=9, decimal_places=6, blank=True, null=True)

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Филиал"
        verbose_name_plural = "Филиалы"

    def __str__(self):
        return self.name


class ServiceCategory(ActiveOrderedModel, SeoModel):
    name = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    icon = models.ImageField("Иконка", upload_to="service-icons/", blank=True, null=True, validators=[validate_image])

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Категория услуги"
        verbose_name_plural = "Категории услуг"

    def __str__(self):
        return self.name


class Service(ActiveOrderedModel, SeoModel):
    category = models.ForeignKey(
        ServiceCategory,
        verbose_name="Категория",
        related_name="services",
        on_delete=models.PROTECT,
    )
    name = models.CharField("Название", max_length=255)
    short_description = models.TextField("Краткое описание", blank=True)
    description = models.TextField("Полное описание", blank=True)
    card_image = models.ImageField("Изображение карточки", upload_to="services/", blank=True, null=True, validators=[validate_image])
    branches = models.ManyToManyField(Branch, verbose_name="Филиалы", related_name="services", blank=True)

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.name


class ServiceImage(ActiveOrderedModel):
    service = models.ForeignKey(Service, verbose_name="Услуга", related_name="images", on_delete=models.CASCADE)
    image = models.ImageField("Изображение", upload_to="services/gallery/", validators=[validate_image])
    caption = models.CharField("Подпись", max_length=255, blank=True)

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Изображение услуги"
        verbose_name_plural = "Изображения услуг"

    def __str__(self):
        return self.caption or self.service.name


class ServicePageBlock(ActiveOrderedModel):
    class BlockType(models.TextChoices):
        FEATURES = "features", "Преимущества"
        CONTENT = "content", "Текстовый блок"
        INDICATIONS = "indications", "Кому подойдет"
        TECHNOLOGIES = "technologies", "Технологии и услуги"
        PRODUCT_CARDS = "product_cards", "Карточки систем/материалов"
        STEPS = "steps", "Этапы работы"
        CTA = "cta", "Блок записи"
        CUSTOM = "custom", "Произвольный блок"

    service = models.ForeignKey(Service, verbose_name="Услуга", related_name="blocks", on_delete=models.CASCADE)
    block_type = models.CharField("Тип блока", max_length=32, choices=BlockType.choices, default=BlockType.CONTENT)
    title = models.CharField("Заголовок", max_length=255, blank=True)
    subtitle = models.CharField("Подзаголовок", max_length=500, blank=True)
    body = models.TextField("Текст", blank=True)
    image = models.ImageField("Изображение", upload_to="services/blocks/", blank=True, null=True, validators=[validate_image])
    button_label = models.CharField("Текст кнопки", max_length=120, blank=True)
    button_url = models.CharField("Ссылка кнопки", max_length=500, blank=True)

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Блок страницы услуги"
        verbose_name_plural = "Блоки страниц услуг"

    def __str__(self):
        return self.title or self.get_block_type_display()


class ServicePageBlockItem(ActiveOrderedModel):
    block = models.ForeignKey(ServicePageBlock, verbose_name="Блок", related_name="items", on_delete=models.CASCADE)
    title = models.CharField("Заголовок", max_length=255, blank=True)
    subtitle = models.CharField("Подзаголовок", max_length=500, blank=True)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="services/block-items/", blank=True, null=True, validators=[validate_image])
    price = models.CharField("Цена", max_length=120, blank=True)
    label = models.CharField("Метка", max_length=120, blank=True)
    url = models.CharField("Ссылка", max_length=500, blank=True)
    metadata = models.JSONField("Дополнительные характеристики", default=dict, blank=True)

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Элемент блока услуги"
        verbose_name_plural = "Элементы блоков услуг"

    def __str__(self):
        return self.title or self.label or self.block.get_block_type_display()


class PriceCategory(ActiveOrderedModel):
    name = models.CharField("Название", max_length=255)
    slug = models.SlugField("Slug", max_length=180, unique=True, blank=True)

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Категория прайса"
        verbose_name_plural = "Категории прайса"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        ensure_unique_slug(self, self.name)
        super().save(*args, **kwargs)


class PriceGroup(ActiveOrderedModel):
    category = models.ForeignKey(PriceCategory, verbose_name="Категория", related_name="groups", on_delete=models.CASCADE)
    title = models.CharField("Название", max_length=255)

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Группа прайса"
        verbose_name_plural = "Группы прайса"

    def __str__(self):
        return self.title


class PriceItem(ActiveOrderedModel):
    category = models.ForeignKey(PriceCategory, verbose_name="Категория", related_name="items", on_delete=models.PROTECT)
    group = models.ForeignKey(PriceGroup, verbose_name="Группа", related_name="items", on_delete=models.SET_NULL, blank=True, null=True)
    service = models.ForeignKey(Service, verbose_name="Связанная услуга", related_name="price_items", on_delete=models.SET_NULL, blank=True, null=True)
    branch = models.ForeignKey(Branch, verbose_name="Филиал", related_name="price_items", on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField("Название", max_length=500)
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2)
    is_from_price = models.BooleanField("Цена от", default=True)
    comment = models.CharField("Комментарий", max_length=255, blank=True)

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Позиция прайса"
        verbose_name_plural = "Позиции прайса"

    def __str__(self):
        return self.title


class Offer(ActiveOrderedModel, SeoModel):
    title = models.CharField("Название", max_length=255)
    short_description = models.TextField("Краткое описание", blank=True)
    description = models.TextField("Полное описание", blank=True)
    image = models.ImageField("Изображение", upload_to="offers/", blank=True, null=True, validators=[validate_image])
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2, blank=True, null=True)
    old_price = models.DecimalField("Старая цена", max_digits=12, decimal_places=2, blank=True, null=True)
    is_from_price = models.BooleanField("Цена от", default=True)
    starts_at = models.DateField("Дата начала", blank=True, null=True)
    ends_at = models.DateField("Дата окончания", blank=True, null=True)
    service = models.ForeignKey(Service, verbose_name="Услуга", related_name="offers", on_delete=models.SET_NULL, blank=True, null=True)
    branches = models.ManyToManyField(Branch, verbose_name="Филиалы", related_name="offers", blank=True)

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Специальное предложение"
        verbose_name_plural = "Специальные предложения"

    def clean(self):
        if self.starts_at and self.ends_at and self.ends_at < self.starts_at:
            raise ValidationError("Дата окончания не может быть раньше даты начала.")

    def __str__(self):
        return self.title


class Specialist(ActiveOrderedModel, SeoModel):
    full_name = models.CharField("ФИО", max_length=255)
    photo = models.ImageField("Фото", upload_to="specialists/", blank=True, null=True, validators=[validate_image])
    position = models.CharField("Должность", max_length=255, blank=True)
    specializations = models.CharField("Специализации", max_length=500, blank=True)
    short_description = models.TextField("Краткое описание", blank=True)
    description = models.TextField("Полное описание", blank=True)
    experience = models.CharField("Стаж", max_length=255, blank=True)
    education = models.TextField("Образование", blank=True)
    services = models.ManyToManyField(Service, verbose_name="Услуги", related_name="specialists", blank=True)
    branches = models.ManyToManyField(Branch, verbose_name="Филиалы", related_name="specialists", blank=True)

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Специалист"
        verbose_name_plural = "Специалисты"

    def __str__(self):
        return self.full_name


class SpecialistDocument(ActiveOrderedModel):
    specialist = models.ForeignKey(Specialist, verbose_name="Специалист", related_name="documents", on_delete=models.CASCADE)
    title = models.CharField("Название", max_length=255)
    file = models.FileField("Файл", upload_to="specialist-documents/", validators=[validate_document])

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Документ специалиста"
        verbose_name_plural = "Документы специалистов"

    def __str__(self):
        return self.title


class PaymentMethod(ActiveOrderedModel):
    title = models.CharField("Название", max_length=255)
    icon = models.ImageField("Иконка", upload_to="payment-icons/", blank=True, null=True, validators=[validate_image])
    description = models.TextField("Описание", blank=True)

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Способ оплаты"
        verbose_name_plural = "Способы оплаты"

    def __str__(self):
        return self.title


class PatientsPage(models.Model):
    title = models.CharField("Заголовок", max_length=255, default="Пациентам")
    text = models.TextField("Текст", blank=True)
    image = models.ImageField("Изображение", upload_to="pages/", blank=True, null=True, validators=[validate_image])
    offers = models.ManyToManyField(Offer, verbose_name="Спецпредложения", blank=True)
    seo_title = models.CharField("SEO title", max_length=255, blank=True)
    seo_description = models.TextField("SEO description", blank=True)

    class Meta:
        verbose_name = "Страница пациентам"
        verbose_name_plural = "Страница пациентам"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        fill_seo_fields(self)
        super().save(*args, **kwargs)


class AboutPage(models.Model):
    title = models.CharField("Заголовок", max_length=255, default="О клинике")
    text = models.TextField("Текст", blank=True)
    image = models.ImageField("Главное изображение", upload_to="pages/", blank=True, null=True, validators=[validate_image])
    seo_title = models.CharField("SEO title", max_length=255, blank=True)
    seo_description = models.TextField("SEO description", blank=True)

    class Meta:
        verbose_name = "Страница о клинике"
        verbose_name_plural = "Страница о клинике"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        fill_seo_fields(self)
        super().save(*args, **kwargs)


class GalleryImage(ActiveOrderedModel):
    image = models.ImageField("Изображение", upload_to="gallery/", validators=[validate_image])
    caption = models.CharField("Подпись", max_length=255, blank=True)
    about_page = models.ForeignKey(AboutPage, verbose_name="Страница", related_name="gallery", on_delete=models.CASCADE, blank=True, null=True)

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Изображение галереи"
        verbose_name_plural = "Галерея"

    def __str__(self):
        return self.caption or str(self.image)


class Vacancy(ActiveOrderedModel, SeoModel):
    title = models.CharField("Название", max_length=255)
    short_description = models.TextField("Краткое описание", blank=True)
    image = models.ImageField("Изображение", upload_to="vacancies/", blank=True, null=True, validators=[validate_image])
    responsibilities = models.TextField("Обязанности", blank=True)
    requirements = models.TextField("Требования", blank=True)
    conditions = models.TextField("Условия", blank=True)
    description = models.TextField("Полный текст", blank=True)

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

    def __str__(self):
        return self.title


class ContactInfo(models.Model):
    address = models.CharField("Адрес", max_length=500)
    phones = models.JSONField("Телефоны", default=list, blank=True)
    email = models.EmailField("Email", blank=True)
    work_hours = models.TextField("Режим работы", blank=True)
    latitude = models.DecimalField("Широта", max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField("Долгота", max_digits=9, decimal_places=6, blank=True, null=True)
    map_url = models.URLField("Ссылка на карту", blank=True)
    seo_title = models.CharField("SEO title", max_length=255, blank=True)
    seo_description = models.TextField("SEO description", blank=True)

    class Meta:
        verbose_name = "Контакты"
        verbose_name_plural = "Контакты"

    def __str__(self):
        return self.address

    def save(self, *args, **kwargs):
        fill_seo_fields(self)
        super().save(*args, **kwargs)


class Requisites(models.Model):
    company_name = models.CharField("Полное наименование", max_length=500)
    inn = models.CharField("ИНН", max_length=32, blank=True)
    kpp = models.CharField("КПП", max_length=32, blank=True)
    ogrn = models.CharField("ОГРН/ОГРНИП", max_length=32, blank=True)
    bank_name = models.CharField("Банк", max_length=255, blank=True)
    checking_account = models.CharField("Расчетный счет", max_length=64, blank=True)
    correspondent_account = models.CharField("Корреспондентский счет", max_length=64, blank=True)
    bik = models.CharField("БИК", max_length=32, blank=True)
    legal_address = models.CharField("Юридический адрес", max_length=500, blank=True)

    class Meta:
        verbose_name = "Реквизиты"
        verbose_name_plural = "Реквизиты"

    def __str__(self):
        return self.company_name


class DocumentCategory(ActiveOrderedModel):
    title = models.CharField("Название", max_length=255)
    slug = models.SlugField("Slug", max_length=180, unique=True, blank=True)

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Категория документа"
        verbose_name_plural = "Категории документов"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        ensure_unique_slug(self, self.title)
        super().save(*args, **kwargs)


class Document(ActiveOrderedModel):
    category = models.ForeignKey(DocumentCategory, verbose_name="Категория", related_name="documents", on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    file = models.FileField("Файл", upload_to="documents/", validators=[validate_document])
    published_at = models.DateField("Дата публикации", blank=True, null=True)

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def __str__(self):
        return self.title


class Review(ActiveOrderedModel):
    author_name = models.CharField("Автор", max_length=255)
    text = models.TextField("Текст")
    rating = models.PositiveSmallIntegerField("Рейтинг", default=5)
    source = models.CharField("Источник", max_length=255, blank=True)
    source_url = models.URLField("Ссылка на источник", blank=True)
    reviewed_at = models.DateField("Дата отзыва", blank=True, null=True)
    specialist = models.ForeignKey(Specialist, verbose_name="Специалист", related_name="reviews", on_delete=models.SET_NULL, blank=True, null=True)
    service = models.ForeignKey(Service, verbose_name="Услуга", related_name="reviews", on_delete=models.SET_NULL, blank=True, null=True)

    class Meta(ActiveOrderedModel.Meta):
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValidationError("Рейтинг должен быть от 1 до 5.")

    def __str__(self):
        return self.author_name
