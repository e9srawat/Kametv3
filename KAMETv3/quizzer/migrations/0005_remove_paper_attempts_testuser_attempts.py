# Generated by Django 4.2.9 on 2024-02-03 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quizzer", "0004_rename_subject_question_paper"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="paper",
            name="attempts",
        ),
        migrations.AddField(
            model_name="testuser",
            name="attempts",
            field=models.IntegerField(default=5),
        ),
    ]