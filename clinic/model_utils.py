from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import slugify


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".jpeg", ".png", ".webp"}

CYRILLIC_TRANSLIT = str.maketrans(
    {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "c",
        "ч": "ch",
        "ш": "sh",
        "щ": "sch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
    }
)


def validate_upload_size(file):
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file.size > max_size:
        raise ValidationError(f"Файл не должен превышать {settings.MAX_UPLOAD_SIZE_MB} МБ.")


def validate_extension(file, allowed):
    name = file.name.lower()
    if not any(name.endswith(extension) for extension in allowed):
        raise ValidationError("Недопустимый формат файла.")


def validate_image(file):
    validate_upload_size(file)
    validate_extension(file, IMAGE_EXTENSIONS)


def validate_document(file):
    validate_upload_size(file)
    validate_extension(file, DOCUMENT_EXTENSIONS)


def make_slug(value):
    value = (value or "").strip().lower().translate(CYRILLIC_TRANSLIT)
    return slugify(value) or "item"


def truncate(value, max_length):
    return (value or "").strip()[:max_length]


def compact_description(value, max_length=180):
    return truncate(" ".join((value or "").split()), max_length)


def get_title_source(instance):
    for field in ("title", "name", "full_name", "address"):
        value = getattr(instance, field, "")
        if value:
            return str(value)
    return instance.__class__.__name__


def get_description_source(instance):
    for field in ("short_description", "description", "text", "address"):
        value = getattr(instance, field, "")
        if value:
            return str(value)
    return ""


def ensure_unique_slug(instance, source):
    if instance.slug:
        instance.slug = make_slug(instance.slug)
        return

    model = instance.__class__
    base_slug = make_slug(source)
    slug = base_slug
    index = 2
    queryset = model.objects.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    while queryset.filter(slug=slug).exists():
        suffix = f"-{index}"
        slug = f"{base_slug[:180 - len(suffix)]}{suffix}"
        index += 1

    instance.slug = slug


def fill_seo_fields(instance):
    title = get_title_source(instance)
    description = get_description_source(instance)

    if hasattr(instance, "seo_title") and not instance.seo_title:
        instance.seo_title = truncate(title, 255)
    if hasattr(instance, "seo_description") and not instance.seo_description:
        instance.seo_description = compact_description(description)
    if hasattr(instance, "og_title") and not instance.og_title:
        instance.og_title = truncate(instance.seo_title or title, 255)
    if hasattr(instance, "og_description") and not instance.og_description:
        instance.og_description = compact_description(instance.seo_description or description)
