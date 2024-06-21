# kanban/models.py

from django.db import models


class Board(models.Model):
    name = models.CharField(max_length=255)
    wip_limit = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Issue(models.Model):
    GITLAB_STATES = (
        ("closed", "Closed"),
        ("opened", "Opened"),
    )

    gitlab_id = models.IntegerField(unique=True)
    labels = models.JSONField(default=list)
    state = models.CharField(max_length=6, choices=GITLAB_STATES, default="opened")
    title = models.CharField(max_length=255)
    milestone = models.CharField(max_length=255, blank=True, default="")
    web_url = models.URLField(max_length=200)

    def __str__(self):
        return self.title


class BoardIssue(models.Model):
    board = models.ForeignKey(
        Board, related_name="board_issues", on_delete=models.CASCADE
    )
    issue = models.ForeignKey(
        Issue, related_name="board_issues", on_delete=models.CASCADE
    )
    position = models.IntegerField(default=0)

    class Meta:
        unique_together = ("board", "issue")
        ordering = ["position"]

    def __str__(self):
        return f"{self.issue.title} on {self.board.name}"
