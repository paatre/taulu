# kanban/views.py

from django.db import transaction
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseBadRequest,
)
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Board, BoardIssue

MAX_RETRIES = 5


def kanban_board(request):
    boards = Board.objects.all()

    return render(
        request,
        "kanban/kanban.html",
        {
            "boards": boards,
        },
    )


def check_wip_limit(board, ordered_ids):
    if board.name.lower() == "working":
        new_working_count = len(ordered_ids)
        if board.wip_limit > 0 and new_working_count > board.wip_limit:
            return HttpResponseBadRequest(
                "WIP limit exceeded for the Working board"
            )

@csrf_exempt
def reorder_issues(request):
    if request.method == "POST":
        try:
            board_id = request.POST.get("board_id")
            if not board_id:
                raise ValueError("Board ID is required")

            ordered_ids = request.POST.getlist("items")
            if not ordered_ids:
                raise ValueError("No items received")

            board = Board.objects.get(id=board_id)

            check_wip_limit(board, ordered_ids)

            objs = list(BoardIssue.objects.filter(issue__in=ordered_ids))

            with transaction.atomic():
                for index, obj in enumerate(objs):
                    obj.board = board
                    obj.position = index + 1

                BoardIssue.objects.bulk_update(objs, ["board", "position"])

            return HttpResponse()
        except Exception as e:
            return HttpResponseBadRequest(str(e))

    return HttpResponseBadRequest("Invalid request method")


def load_more_issues(request):
    board_id = request.GET.get("board_id")
    page = int(request.GET.get("page", 1))

    if not board_id:
        return HttpResponseBadRequest("Board ID is required")

    try:
        board = Board.objects.get(id=board_id)
        board_issues = (
            BoardIssue.objects.filter(board=board)
            .select_related("issue")
            .order_by("position")[(page - 1) * 10 : page * 10]
        )

        return render(
            request,
            "kanban/issues_partial.html",
            {"board_issues": board_issues, "board_id": board_id, "page": page},
        )
    except Board.DoesNotExist:
        return HttpResponseNotFound("Board not found")
