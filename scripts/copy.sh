#!/bin/bash

cat kanban/admin.py \
    kanban/gitlab.py \
    kanban/management/**/*.py \
    kanban/models.py \
    kanban/templates/**/*.html \
    kanban/views.py \
    kanban/tests.py \
    project/settings.py \
    project/urls.py \
    | wl-copy
