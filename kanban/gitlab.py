import gitlab
from django.conf import settings
from threading import Lock

class GitLabConfigurationError(Exception):
    pass

class GitLabConnectionError(Exception):
    pass

_gitlab_client = None
_gitlab_client_lock = Lock()

def get_gitlab_client():
    global _gitlab_client
    if _gitlab_client is not None:
        return _gitlab_client

    with _gitlab_client_lock:
        if _gitlab_client is not None:
            return _gitlab_client

        if not settings.GITLAB_URL:
            raise GitLabConfigurationError('GITLAB_URL is not configured.')

        if not settings.GITLAB_PRIVATE_TOKEN:
            raise GitLabConfigurationError('GITLAB_PRIVATE_TOKEN is not configured.')

        try:
            client = gitlab.Gitlab(
                settings.GITLAB_URL,
                private_token=settings.GITLAB_PRIVATE_TOKEN,
            )
            client.auth()
            _gitlab_client = client
            return _gitlab_client
        except gitlab.GitlabAuthenticationError as e:
            raise GitLabConfigurationError(
                'Invalid GitLab configuration. Please check your settings.'
            ) from e
        except gitlab.GitlabConnectionError as e:
            raise GitLabConnectionError(
                'Could not connect to GitLab. Please check your settings.'
            ) from e

