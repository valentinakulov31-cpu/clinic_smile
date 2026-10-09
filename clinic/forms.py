from django import forms

from .models import Branch, ContactInfo, SiteSettings


class PhoneListField(forms.CharField):
    """Телефоны вводятся по одному на строку, в базе хранятся списком (JSON)."""

    widget = forms.Textarea(attrs={"rows": 3})

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        kwargs.setdefault("help_text", "По одному телефону на строку.")
        super().__init__(*args, **kwargs)

    def prepare_value(self, value):
        if isinstance(value, (list, tuple)):
            return "\n".join(str(phone) for phone in value)
        return value

    def to_python(self, value):
        value = super().to_python(value)
        if not value:
            return []
        return [line.strip() for line in value.splitlines() if line.strip()]


class ContactInfoAdminForm(forms.ModelForm):
    phones = PhoneListField(label="Телефоны")

    class Meta:
        model = ContactInfo
        fields = "__all__"


class BranchAdminForm(forms.ModelForm):
    phones = PhoneListField(label="Телефоны")

    class Meta:
        model = Branch
        fields = "__all__"


class EmailListField(forms.CharField):
    widget = forms.Textarea(attrs={"rows": 4})

    def prepare_value(self, value):
        if isinstance(value, list):
            return "\n".join(value)
        return value

    def to_python(self, value):
        value = super().to_python(value)
        addresses = []
        seen = set()
        for line in value.splitlines():
            address = line.strip()
            if address and address.lower() not in seen:
                forms.EmailField().clean(address)
                addresses.append(address)
                seen.add(address.lower())
        return addresses


class SiteSettingsAdminForm(forms.ModelForm):
    request_notification_emails = EmailListField(
        label="Получатели заявок",
        required=False,
        help_text="По одному email на строку. Пустой список отключает уведомления.",
    )

    class Meta:
        model = SiteSettings
        fields = "__all__"
