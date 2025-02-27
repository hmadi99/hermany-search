# Generated by Django 5.1.3 on 2025-01-07 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scheduler", "0015_alter_college_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="required_room_type",
            field=models.CharField(
                choices=[
                    ("hall", "قاعة"),
                    ("computer_lab", "معمل حاسوب"),
                    ("chemistry_lab", "معمل كيمياء"),
                    ("rocks_lab", "معمل صخور"),
                    ("biology_lab", "معمل أحياء"),
                ],
                default="hall",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="room",
            name="room_type",
            field=models.CharField(
                choices=[
                    ("hall", "قاعة"),
                    ("computer_lab", "معمل حاسوب"),
                    ("chemistry_lab", "معمل كيمياء"),
                    ("rocks_lab", "معمل صخور"),
                    ("biology_lab", "معمل أحياء"),
                ],
                default="hall",
                max_length=20,
            ),
        ),
    ]
