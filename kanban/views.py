# kanban/views.py


from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Prefetch

from .models import Board, Issue, BoardIssue


def kanban_board(request):
    boards = Board.objects.prefetch_related(
        Prefetch(
            "board_issues",
            queryset=BoardIssue.objects.select_related("issue").order_by("position"),
        )
    ).all()

    # Evaluate the prefetch_related queryset
    boards_list = list(boards)

    return render(
        request,
        "kanban/kanban.html",
        {
            "boards": boards_list,
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


@csrf_exempt
def reorder_issues(request):
    if request.method == "POST":
        try:
            board_id = request.POST.get("board_id")
            ordered_ids = request.POST.getlist("items")
            if not ordered_ids:
                raise ValueError("No items received")
            if not board_id:
                raise ValueError("Board ID is required")

            board = Board.objects.get(id=board_id)

            for index, issue_id in enumerate(ordered_ids):
                board_issue = BoardIssue.objects.get(issue__id=issue_id)

                # Check if the issue is moved to a different board
                if board_issue.board_id != int(board_id):
                    old_board_id = board_issue.board_id
                    board_issue.board_id = board_id
                    board_issue.position = index + 1
                    board_issue.save()

                    # Adjust positions in the old board
                    old_board_issues = BoardIssue.objects.filter(
                        board_id=old_board_id
                    ).order_by("position")
                    for i, issue in enumerate(old_board_issues):
                        issue.position = i + 1
                        issue.save()
                else:
                    # If the issue remains in the same board, just update the position
                    board_issue.position = index + 1
                    board_issue.save()

            return JsonResponse({"status": "success", "ordered_ids": ordered_ids})
        except Exception as e:
            return JsonResponse({"status": "failed", "message": str(e)}, status=400)
    return JsonResponse(
        {"status": "failed", "message": "Invalid request method"}, status=400
    )
