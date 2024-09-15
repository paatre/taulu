# kanban/utils.py

import gitlab
from django.conf import settings

class GitLabConfigurationError(Exception):
    pass


class GitLabConnectionError(Exception):
    pass


def get_gitlab_client():
    if not settings.GITLAB_URL:
        raise GitLabConfigurationError(
            'GITLAB_URL is not configured.'
        )
    if not settings.GITLAB_PRIVATE_TOKEN:
        raise GitLabConfigurationError(
            'GITLAB_PRIVATE_TOKEN is not configured.'
        )
    try:
        client = gitlab.Gitlab(
            settings.GITLAB_URL,
            settings.GITLAB_PRIVATE_TOKEN,
        )
        client.auth()
        return client
    except gitlab.GitlabAuthenticationError as e:
        raise GitLabConfigurationError(
            'Invalid GitLab configuration. Please check your settings.'
        ) from e
    except gitlab.GitlabConnectionError as e:
        raise GitLabConnectionError(
            'Could not connect to GitLab. Please check your settings.'
        ) from e
