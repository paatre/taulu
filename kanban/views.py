# kanban/views.py

import time
from django.conf import settings
from django.db import transaction, IntegrityError, OperationalError
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseBadRequest,
    JsonResponse,
)
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Board, Issue, BoardIssue

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
                BoardIssue.objects.filter(issue__in=ordered_ids).update(
                    board=board, position=index + 1
                )

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
