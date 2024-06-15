# kanban/views.py

from django.conf import settings
from django.shortcuts import render

import gitlab

gl = gitlab.Gitlab(settings.GITLAB_URL, private_token=settings.GITLAB_PRIVATE_TOKEN)
current_user = gl.users.list(username=settings.GITLAB_USERNAME)[0]


def get_gitlab_issues(user, state=None, label=None, page=1, per_page=10):
    issue_params = {
        "assignee_id": user.id,
        "order_by": "updated_at",
        "page": page,
        "per_page": per_page,
        "scope": "all",
        "sort": "desc",
        "state": state,
        "with_labels_details": True,
    }

    if label:
        issue_params["labels"] = label

    issues = gl.issues.list(**issue_params)

    tasks = []
    for issue in issues:
        labels = [
            {
                "color": label["color"],
                "name": label["name"],
                "text_color": label["text_color"],
            }
            for label in issue.labels
        ]
        tasks.append(
            {
                "author": issue.author["name"],
                "description": issue.description,
                "labels": labels,
                "milestone": issue.milestone["title"] if issue.milestone else None,
                "state": issue.state,
                "title": issue.title,
                "web_url": issue.web_url,
            }
        )

    return tasks


def kanban_board(request):
    open_tasks = get_gitlab_issues(current_user, state="opened")
    working_tasks = get_gitlab_issues(current_user, state="opened", label="Working")
    closed_tasks = get_gitlab_issues(current_user, state="closed")

    return render(
        request,
        "kanban/kanban.html",
        {
            "closed_tasks": closed_tasks,
            "open_tasks": open_tasks,
            "page": 1,
            "working_tasks": working_tasks,
        },
    )


def load_more_issues(request):
    state = request.GET.get("state")
    label = request.GET.get("label")
    page = int(request.GET.get("page", 1))
    tasks = get_gitlab_issues(current_user, state=state, label=label, page=page)

    return render(
        request,
        "kanban/issues_partial.html",
        {"tasks": tasks, "state": state, "label": label, "page": page},
    )
