Taulu
=====

Taulu is a board application for all of your issues between all projects within a GitLab instance.

## Introduction

Currently, there's no "global" board for all of your different projects in GitLab. There _is_ an issue listing
of all issues that you are assigned to but if you'd like to have a Kanban workflow for all of those issues so
that they can be worked on by the priority you give them, GitLab doesn't offer that.

Taulu offers just that. Taulu is actually a Finnish word for "board" and that's what it is. A board for all
of your issues. Taulu uses GitLab REST API to fetch all issues from a GitLab instance and present them to you
in a single, web-based Kanban board view.

## Features

Taulu uses a management command to fetch issues from GitLab and store them in the database. This is not yet automated
or actively scheduled which means fetching issues requires manually running the management command from time to time.
The goal is to have this automated in the future. This probably means that the issues wil be fetched and stored at
every page load. It just needs to be fast enough.

On top of the core drag-and-drop functionality, Taulu also offers:
- WIP limits
- opening and closing issues
- identifying issues states by "Todo" and "Working" labels
- infinite scroll and lazy loading of issues
- etc.

Currently, changes in Taulu are not reflect back to the GitLab instance. This means that if you close an issue in Taulu,
it will not be closed in GitLab. This is a feature that is planned to be implemented soon as it is a crucial feature
for Taulu to be useful.

## Installation

To install Taulu:

1. Clone this repository to your local machine using `git clone`
2. Create a virtual environment and activate it
3. Run `pip install -r requirements.txt` to install dependencies
4. Run `python manage.py migrate` to create database tables
5. Run `python manage.py sync_gitlab_issues` to populate the database with initial data

## Usage

To use the Taulu:

1. Start the development server by running `python manage.py runserver`
2. Open a web browser and navigate to `http://localhost:8000/kanban/board/`
3. Start dragging and dropping issues between columns
