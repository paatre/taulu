#!/bin/bash

cat kanban/views.py kanban/models.py kanban/admin.py kanban/management/**/*.py kanban/templates/kanban/*.html | wl-copy
