# kanban/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("board/", views.kanban_board, name="kanban_board"),
    path("load-more-issues/", views.load_more_issues, name="load_more_issues"),
    path("reorder-issues/", views.reorder_issues, name="reorder_issues"),
]
