# Generated by Django 4.2.9 on 2024-02-02 11:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("quizzer", "0002_remove_testuser_user_testuser_email_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Paper",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subject", models.CharField(max_length=20)),
                ("time_allotted", models.IntegerField(default=60)),
                ("number_questions", models.IntegerField(default=10)),
                ("attempts", models.IntegerField(default=5)),
            ],
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("question_text", models.TextField()),
                (
                    "subject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="quizzer.paper"
                    ),
                ),
            ],
        ),
    ]