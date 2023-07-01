"""Tests for /groups/ endpoint."""
from django.test import TestCase

# Import the models we're testing
from workshop.api.models import User


class GroupsTest(TestCase):
    """Test that permissions are enforced on the /groups/ endpoint."""

    def setUp(self):
        """Set up the test client."""
        self.user = {
            "username": "user",
            "password": "password",
            "email": "user@example.com",
        }
        self.admin = {
            "username": "admin",
            "password": "password",
            "email": "admin@example.com"
        }

        # Register a user
        self.client.post("/register/", self.user)

        # Manually create an admin user (not through the API)
        User.objects.create_superuser(
            self.admin['username'],
            self.admin['email'],
            self.admin['password']
        )

        # Login as the admin
        self.assertTrue(
            self.client.login(username="admin", password="password")
        )

        # Create a group
        response = self.client.post(
            "/groups/",
            {
                "name": "Group 1",
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        # Log out
        self.client.logout()

    def test_groups_unauthenticated(self):
        """Test that unauthenticated users can only list groups."""
        # Get the response from the API
        response = self.client.get("/groups/")
        self.assertEqual(response.status_code, 200)

        # Check that only public fields are returned for each group
        for group in response.data['results']:
            self.assertEqual(len(group), 3)
            self.assertIn("url", group)
            self.assertIn("name", group)
            self.assertIn("user_set", group)

        # Ensure that we can't add groups
        response = self.client.post(
            "/groups/",
            {
                "name": "test"
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

        # Ensure that we can't update groups
        response = self.client.patch(
            "/groups/1/",
            {
                "name": "Group 1 - Updated"
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

        # Ensure that we can't delete groups
        response = self.client.delete("/groups/1/")
        self.assertEqual(response.status_code, 401)

    def test_groups_authenticated(self):
        """Test that authenticated users can only list groups."""
        # Log in as the user
        self.client.login(username="user", password="password")

        # Get the response from the API
        response = self.client.get("/groups/")
        self.assertEqual(response.status_code, 200)

        # Check that only public fields are returned for each group
        for group in response.data['results']:
            self.assertEqual(len(group), 3)
            self.assertIn("url", group)
            self.assertIn("name", group)
            self.assertIn("user_set", group)

        # Ensure that we can't add groups
        response = self.client.post(
            "/groups/",
            {
                "name": "test"
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        # Ensure that we can't update groups
        response = self.client.patch(
            "/groups/1/",
            {
                "name": "Group 1 - Updated"
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        # Ensure that we can't delete groups
        response = self.client.delete("/groups/1/")
        self.assertEqual(response.status_code, 403)

        # Log out
        self.client.logout()

    def test_groups_admin(self):
        """Test that admin users can list, add, delete, and update groups."""
        # Log in as the admin
        self.client.login(username="admin", password="password")

        # Get the response from the API
        response = self.client.get("/groups/")
        self.assertEqual(response.status_code, 200)

        # Check that only public fields are returned for each group
        for group in response.data['results']:
            self.assertEqual(len(group), 3)
            self.assertIn("url", group)
            self.assertIn("name", group)
            self.assertIn("user_set", group)

        # Ensure that we can add groups
        response = self.client.post(
            "/groups/",
            {
                "name": "test"
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        # Ensure that we can update groups
        response = self.client.patch(
            "/groups/1/",
            {
                "name": "Group 1 - Updated"
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Ensure that we can delete groups
        response = self.client.delete("/groups/1/")
        self.assertEqual(response.status_code, 204)

        # Log out
        self.client.logout()


class GroupsUsersTest(TestCase):
    """Test that permissions are enforced user's groups."""
    def setUp(self):
        """Set up the test client."""
        self.user = {
            "username": "user",
            "password": "password",
            "email": "user@example.com",
        }
        self.admin = {
            "username": "admin",
            "password": "password",
            "email": "admin@example.com"
        }

        # Register a user
        self.client.post("/register/", self.user)

        # Manually create an admin user (not through the API)
        User.objects.create_superuser(
            self.admin['username'],
            self.admin['email'],
            self.admin['password']
        )

        # Login as the admin
        self.client.login(username="admin", password="password")

        # Create a group
        response = self.client.post(
            "/groups/",
            {
                "name": "Group 1",
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        # Create a second group
        response = self.client.post(
            "/groups/",
            {
                "name": "Group 2",
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        # Add the user to the group
        # TODO: Try to do this with patch
        response = self.client.patch(
            "/users/user/",
            {
                "username": "user",
                "email": "user@example.com",
                "groups": ["/groups/1/"]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Log out
        self.client.logout()

    def test_groups_unauthenticated(self):
        """Test that unauthenticated users can only list groups."""
        # Ensure that we can't add users to groups
        response = self.client.patch(
            "/users/user/",
            {
                "username": "user",
                "email": "user@example.com",
                "groups": ["/groups/1/", "/groups/2/"]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

        # Ensure we can't remove users from groups
        response = self.client.patch(
            "/users/user/",
            {
                "username": "user",
                "email": "user@example.com",
                "groups": []
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_groups_authenticated(self):
        """Test that authenticated users can only list groups."""
        # Log in as the user
        self.client.login(username="user", password="password")

        # Ensure that we can't add ourselves to groups
        response = self.client.patch(
            "/users/user/",
            {
                "username": "user",
                "email": "user@example.com",
                "groups": ["/groups/1/", "/groups/2/"]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        # Ensure that we can't add other users to groups
        response = self.client.patch(
            "/users/admin/",
            {
                "username": "admin",
                "email": "admin@example.com",
                "groups": ["/groups/1/", "/groups/2/"]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        # Ensure we can't remove ourselves from groups
        response = self.client.patch(
            "/users/user/",
            {
                "username": "user",
                "email": "user@example.com",
                "groups": []
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        # Ensure we can't remove other users from groups
        response = self.client.patch(
            "/users/admin/",
            {
                "username": "admin",
                "email": "admin@example.com",
                "groups": []
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        # Log out
        self.client.logout()

    def test_groups_admin(self):
        """Test that admin users can add and remove users from groups."""
        # Log in as the admin
        self.client.login(username="admin", password="password")

        # Ensure that we can add users to groups
        response = self.client.patch(
            "/users/user/",
            {
                "username": "user",
                "email": "user@example.com",
                "groups": ["/groups/1/", "/groups/2/"]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Ensure that we can remove users from groups
        response = self.client.patch(
            "/users/user/",
            {
                "username": "user",
                "email": "user@example.com",
                "groups": []
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Ensure that we can add ourselves to groups
        response = self.client.patch(
            "/users/admin/",
            {
                "username": "admin",
                "email": "admin@example.com",
                "groups": ["/groups/1/", "/groups/2/"]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Ensure that we can remove ourselves from groups
        response = self.client.patch(
            "/users/admin/",
            {
                "username": "admin",
                "email": "admin@example.com",
                "groups": []
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Log out
        self.client.logout()
