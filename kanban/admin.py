from django.contrib import admin
from django.db.models import Q
from .models import Board, Issue, BoardIssue


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "wip_limit")
    search_fields = ("name",)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    def labels_display(self, obj):
        return ", ".join([label["name"] for label in obj.labels])

    def get_search_results(self, request, queryset, search_term):
        """
        Override the default get_search_results to allow searching by labels.
        """
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        search_terms = search_term.split()
        if search_terms:
            label_queries = Q()
            for term in search_terms:
                label_queries |= Q(labels__icontains=term)
            queryset = queryset.filter(label_queries)
        return queryset, use_distinct

    list_display = ("id", "title", "state", "milestone", "web_url", "labels_display")
    search_fields = ("title", "gitlab_id", "milestone", "web_url", "labels")
    ordering = ("title",)
    readonly_fields = ("gitlab_id", "labels_display")
    labels_display.short_description = "Labels"


@admin.register(BoardIssue)
class BoardIssueAdmin(admin.ModelAdmin):
    list_display = ("id", "board", "issue", "position")
    list_filter = ("board",)
    search_fields = ("issue__title", "board__name")
    ordering = ("board", "position")
