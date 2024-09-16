import os
from unittest.mock import MagicMock, patch
from django.core.management import call_command
from django.test import TestCase, override_settings
import gitlab
import kanban.gitlab
from kanban.gitlab import get_gitlab_client, GitLabConfigurationError, GitLabConnectionError
from kanban.models import Board, Issue


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


class GitLabIssueTests(TestCase):

    @override_settings(
        GITLAB_PRIVATE_TOKEN='fake-token',
        GITLAB_URL='https://gitlab.example.com',
        GITLAB_USERNAME='user',
    )
    @patch.dict(os.environ, {'TQDM_DISABLE': '1'})
    @patch('kanban.gitlab.gitlab.Gitlab')
    def test_sync_gitlab_issues(self, mock_gl):
        assert Issue.objects.count() == 0

        mock_issue = MagicMock()
        mock_issue.id = 1
        mock_issue.iid = 1
        mock_issue.title = 'Test Issue'
        mock_issue.description = 'This is a test issue.'
        mock_issue.state = 'opened'
        mock_issue.created_at = '2024-09-16T00:00:00Z'
        mock_issue.updated_at = '2024-09-16T00:00:00Z'
        mock_issue.milestone = None
        mock_issue.web_url = 'https://gitlab.example.com/user/project/issues/1'

        mock_gl.return_value.user.username = 'user'
        mock_gl.return_value.issues.list.return_value = [mock_issue]

        with open(os.devnull, 'w') as f:
            call_command('sync_gitlab_issues', stdout=f)

        assert Issue.objects.count() > 0


class KanbanBoardTests(TestCase):

    def test_kanban_board(self):
        # Arrange
        board_names = ['Open', 'Working', 'Closed']
        for name in board_names:
            Board.objects.create(name=name)

        # Act
        response = self.client.get('/')

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kanban/kanban.html')
        self.assertContains(response, 'Kanban Board')

    def test_kanban_board_no_boards(self):
        # Act
        response = self.client.get('/')

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kanban/kanban.html')
        self.assertContains(response, 'No boards yet')
