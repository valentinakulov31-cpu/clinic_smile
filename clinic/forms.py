from django import forms

from .models import Branch, ContactInfo


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
