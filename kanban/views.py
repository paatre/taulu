# kanban/views.py

from django.conf import settings
from django.shortcuts import render

import gitlab


gl = gitlab.Gitlab(settings.GITLAB_URL, private_token=settings.GITLAB_PRIVATE_TOKEN)
current_user = gl.users.list(username=settings.GITLAB_USERNAME)[0]


def get_gitlab_issues(user, state=None, page=1, per_page=20):
    issues = gl.issues.list(
        assignee_id=user.id,
        state=state,
        page=page,
        per_page=per_page,
        order_by="updated_at",
        sort="desc",
        scope="all",
        with_labels_details=True,
    )

    tasks = []
    for issue in issues:
        labels = [
            {
                "name": label["name"],
                "text_color": label["text_color"],
                "color": label["color"],
            }
            for label in issue.labels
        ]
        tasks.append(
            {
                "title": issue.title,
                "description": issue.description,
                "state": issue.state,
                "labels": labels,
                "author": issue.author["name"],
            }
        )

    return tasks


def kanban_board(request):
    open_tasks = get_gitlab_issues(current_user, state="opened")
    closed_tasks = get_gitlab_issues(current_user, state="closed")

    return render(
        request,
        "kanban/kanban.html",
        {"open_tasks": open_tasks, "closed_tasks": closed_tasks, "page": 1},
    )


def load_more_issues(request):
    state = request.GET.get("state")
    page = int(request.GET.get("page", 1))
    tasks = get_gitlab_issues(current_user, state=state, page=page)

    return render(
        request,
        "kanban/issues_partial.html",
        {"tasks": tasks, "state": state, "page": page},
    )
