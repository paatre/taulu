from unittest.mock import patch
from django.test import TestCase, override_settings
import gitlab
import kanban.gitlab
from kanban.gitlab import get_gitlab_client, GitLabConfigurationError, GitLabConnectionError

class GitLabClientTests(TestCase):

    def setUp(self):
        kanban.gitlab._gitlab_client = None

    @override_settings(
        GITLAB_URL='https://gitlab.example.com',
        GITLAB_PRIVATE_TOKEN='fake-token'
    )
    @patch('kanban.gitlab.gitlab.Gitlab')
    def test_get_gitlab_client(self, mock_gl):
        gl = get_gitlab_client()

        mock_gl.assert_called_once_with(
            'https://gitlab.example.com',
            'fake-token',
        )

        self.assertEqual(gl, mock_gl.return_value)
        self.assertTrue(gl.user is not None)
        self.assertEqual(gl.user, mock_gl.return_value.user)

    @override_settings(
        GITLAB_URL='https://gitlab.example.com',
        GITLAB_PRIVATE_TOKEN='invalid-token'
    )
    @patch('kanban.gitlab.gitlab.Gitlab')
    def test_get_gitlab_client_invalid_private_token(self, mock_gl):
        gl = mock_gl.return_value
        gl.auth.side_effect = gitlab.GitlabAuthenticationError()

        with self.assertRaises(GitLabConfigurationError) as context:
            get_gitlab_client()

        self.assertIn(
            "Invalid GitLab configuration. Please check your settings.",
            str(context.exception)
        )

    @override_settings(
        GITLAB_URL='https://gitlab.invalid.com',
        GITLAB_PRIVATE_TOKEN='fake-token'
    )
    @patch('kanban.gitlab.gitlab.Gitlab')
    def test_get_gitlab_client_invalid_url(self, mock_gl):
        gl = mock_gl.return_value
        gl.auth.side_effect = gitlab.GitlabConnectionError()

        with self.assertRaises(GitLabConnectionError) as context:
            get_gitlab_client()

        self.assertIn(
            "Could not connect to GitLab. Please check your settings.",
            str(context.exception)
        )

    @override_settings(
        GITLAB_URL=None,
        GITLAB_PRIVATE_TOKEN='fake-token'
    )
    def test_get_gitlab_client_missing_url(self):
        with self.assertRaises(GitLabConfigurationError) as context:
            get_gitlab_client()

        self.assertIn(
            "GITLAB_URL is not configured",
            str(context.exception)
        )

    @override_settings(
        GITLAB_URL='https://gitlab.example.com',
        GITLAB_PRIVATE_TOKEN=None
    )
    def test_get_gitlab_client_missing_private_token(self):
        with self.assertRaises(GitLabConfigurationError) as context:
            get_gitlab_client()

        self.assertIn(
            "GITLAB_PRIVATE_TOKEN is not configured",
            str(context.exception)
        )
