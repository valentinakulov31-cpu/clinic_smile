from django.db import migrations, models
import django.db.models.deletion

import clinic.models


class Migration(migrations.Migration):

    dependencies = [
        ("clinic", "0002_alter_documentcategory_slug_alter_offer_slug_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="hero_badge_1",
            field=models.CharField(blank=True, max_length=255, verbose_name="Бейдж героя 1"),
        ),
        migrations.AddField(
            model_name="service",
            name="hero_badge_2",
            field=models.CharField(blank=True, max_length=255, verbose_name="Бейдж героя 2"),
        ),
        migrations.AddField(
            model_name="service",
            name="hero_badge_3",
            field=models.CharField(blank=True, max_length=255, verbose_name="Бейдж героя 3"),
        ),
        migrations.AddField(
            model_name="service",
            name="preview_logo",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="services/logos/",
                validators=[clinic.models.validate_image],
                verbose_name="Логотип для страницы услуги",
            ),
        ),
        migrations.CreateModel(
            name="ServicePageBlock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активно")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="Сортировка")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                ("title", models.CharField(blank=True, max_length=255, verbose_name="Заголовок блока")),
                ("description", models.TextField(blank=True, verbose_name="Описание блока (Markdown)")),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="services/blocks/",
                        validators=[clinic.models.validate_image],
                        verbose_name="Картинка блока",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="page_blocks",
                        to="clinic.service",
                        verbose_name="Услуга",
                    ),
                ),
            ],
            options={
                "verbose_name": "Блок страницы услуги",
                "verbose_name_plural": "Блоки страницы услуги",
                "ordering": ("sort_order", "id"),
                "abstract": False,
            },
        ),
        migrations.AlterField(
            model_name="branch",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Сортировка"),
        ),
        migrations.AlterField(
            model_name="document",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Сортировка"),
        ),
        migrations.AlterField(
            model_name="documentcategory",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Сортировка"),
        ),
        migrations.AlterField(
            model_name="galleryimage",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Сортировка"),
        ),
        migrations.AlterField(
            model_name="offer",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Сортировка"),
        ),
        migrations.AlterField(
            model_name="paymentmethod",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Сортировка"),
        ),
        migrations.AlterField(
            model_name="pricecategory",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Сортировка"),
        ),
        migrations.AlterField(
            model_name="priceitem",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Сортировка"),
        ),
        migrations.AlterField(
            model_name="review",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Сортировка"),
        ),
        migrations.AlterField(
            model_name="service",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Сортировка"),
        ),
        migrations.AlterField(
            model_name="servicecategory",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Сортировка"),
        ),
        migrations.AlterField(
            model_name="serviceimage",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Сортировка"),
        ),
        migrations.AlterField(
            model_name="specialist",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Сортировка"),
        ),
        migrations.AlterField(
            model_name="specialistdocument",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Сортировка"),
        ),
        migrations.AlterField(
            model_name="vacancy",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Сортировка"),
        ),
    ]
