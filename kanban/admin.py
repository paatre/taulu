from django.contrib import admin
from .models import Board, Issue, BoardIssue

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'state', 'gitlab_id')
    search_fields = ('title', 'gitlab_id')
    ordering = ('title',)

@admin.register(BoardIssue)
class BoardIssueAdmin(admin.ModelAdmin):
    list_display = ('id', 'board', 'issue', 'position')
    list_filter = ('board',)
    search_fields = ('issue__title', 'board__name')
    ordering = ('board', 'position')

