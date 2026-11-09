from django.db.models import Case, CharField, Q, Value, When


CHANNELS = (
    ("search", "Поиск"),
    ("paid", "Реклама"),
    ("qr", "QR-код"),
    ("social", "Соцсети / мессенджеры"),
    ("email", "Почта"),
    ("tagged", "Другие UTM-метки"),
    ("referral", "Другие сайты"),
    ("direct", "Прямой / неизвестный"),
)
CHANNEL_LABELS = dict(CHANNELS)
SEARCH_DOMAINS = (
    "yandex.ru", "yandex.com", "yandex.kz", "yandex.by", "ya.ru",
    "google.com", "google.ru", "google.co.uk", "google.de", "google.kz",
    "bing.com", "duckduckgo.com", "search.yahoo.com", "go.mail.ru",
    "nova.rambler.ru", "search.brave.com", "baidu.com",
)
SOCIAL_DOMAINS = (
    "vk.com", "vk.ru", "m.vk.com", "ok.ru", "t.me", "telegram.me",
    "facebook.com", "instagram.com", "youtube.com", "dzen.ru", "twitter.com", "x.com",
)


def hosts_match(domains):
    query = Q()
    for domain in domains:
        query |= Q(referrer_host__iexact=domain) | Q(referrer_host__iendswith="." + domain)
    return query


def medium_is(*values):
    query = Q()
    for value in values:
        query |= Q(utm_medium__iexact=value)
    return query


def channel_expression():
    # Explicit campaign labels take precedence over the referring site's category.
    return Case(
        When(medium_is("cpc", "ppc", "paid", "paidsearch", "paid_search", "paid_social", "cpm", "display", "retargeting"), then=Value("paid")),
        When(medium_is("qr", "qrcode", "qr_code"), then=Value("qr")),
        When(medium_is("email", "e-mail"), then=Value("email")),
        When(medium_is("social", "social-network", "social_media", "smm"), then=Value("social")),
        When(medium_is("organic", "search"), then=Value("search")),
        When(~Q(utm_source="") | ~Q(utm_medium="") | ~Q(utm_campaign=""), then=Value("tagged")),
        When(hosts_match(SEARCH_DOMAINS), then=Value("search")),
        When(hosts_match(SOCIAL_DOMAINS), then=Value("social")),
        When(~Q(referrer_host=""), then=Value("referral")),
        default=Value("direct"), output_field=CharField(),
    )
