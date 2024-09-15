# kanban/management/commands/sync_gitlab_issues.py

from django.core.management.base import BaseCommand
from django.db.models import F
from tqdm import tqdm
from kanban.gitlab import get_gitlab_client
from kanban.models import Board, Issue, BoardIssue


class Command(BaseCommand):
    help = "Sync issues from GitLab to the local database"

    def handle(self, *args, **kwargs):
        gl = get_gitlab_client()
        user = gl.user

        if not user:
            self.stdout.write(self.style.ERROR("Failed to connect to GitLab"))
            return
        self.stdout.write(self.style.SUCCESS(
            f"Successfully connected to GitLab as {user.username}"
        ))

        boards = {
            "open": Board.objects.get_or_create(name="Open")[0],
            "working": Board.objects.get_or_create(name="Working")[0],
            "closed": Board.objects.get_or_create(name="Closed")[0],
        }

        issue_params = {
            "assignee_id": user.id,
            "order_by": "updated_at",
            "sort": "asc",
            "scope": "all",
            "state": "all",
            "with_labels_details": True,
        }

        self.stdout.write("Syncing issues from GitLab...")
        all_issues = gl.issues.list(**issue_params, iterator=True)

        for issue in tqdm(all_issues, desc="Processing issues"):
            labels = [
                {
                    "color": label["color"],
                    "name": label["name"],
                    "text_color": label["text_color"],
                }
                for label in issue.labels
            ]

            issue_obj, _ = Issue.objects.update_or_create(
                gitlab_id=issue.id,
                defaults={
                    "gitlab_id": issue.id,
                    "labels": labels,
                    "state": issue.state,
                    "title": issue.title,
                    "milestone": issue.milestone["title"] if issue.milestone else "",
                    "web_url": issue.web_url,
                },
            )

            if issue.state == "opened":
                board = (
                    boards["working"]
                    if any(label["name"] == "Working" for label in labels)
                    else boards["open"]
                )
            else:
                board = boards["closed"]

            boardissue_obj, created = BoardIssue.objects.get_or_create(
                issue=issue_obj,
                defaults={
                    "board": board,
                    "position": 0,
                },
            )

            if created:
                BoardIssue.objects.filter(board=board).exclude(issue=issue_obj).update(
                    position=F("position") + 1
                )

            if boardissue_obj.board != board:
                BoardIssue.objects.filter(issue=issue_obj).update(
                    board=board,
                    position=0,
                )
                BoardIssue.objects.filter(board=board).exclude(issue=issue_obj).update(
                    position=F("position") + 1
                )

        self.stdout.write(self.style.SUCCESS("Successfully synced issues from GitLab"))
