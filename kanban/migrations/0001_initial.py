# Generated by Django 5.0.6 on 2024-06-16 20:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Board",
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
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Issue",
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
                ("gitlab_id", models.IntegerField(unique=True)),
                ("labels", models.JSONField(default=list)),
                (
                    "state",
                    models.CharField(
                        choices=[("closed", "Closed"), ("opened", "Opened")],
                        default="opened",
                        max_length=6,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("milestone", models.CharField(blank=True, default="", max_length=255)),
                ("web_url", models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name="BoardIssue",
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
                ("position", models.IntegerField(default=0)),
                (
                    "board",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="board_issues",
                        to="kanban.board",
                    ),
                ),
                (
                    "issue",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="board_issues",
                        to="kanban.issue",
                    ),
                ),
            ],
            options={
                "ordering": ["position"],
                "unique_together": {("board", "issue")},
            },
        ),
    ]
