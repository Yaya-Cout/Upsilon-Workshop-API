"""Tests for /users/ endpoint."""
from django.test import TestCase

# Import the models we're testing
from workshop.api.models import User


class UsersTest(TestCase):
    """Test that permissions are enforced on the /users/ endpoint."""

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

    def test_users_unauthenticated(self):
        """Test that unauthenticated users can only list public users."""
        # Get the response from the API
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, 200)

        # Check that only public fields are returned for each user
        for user in response.data['results']:
            self.ensure_public_fields(user)

        # Edit an user
        response = self.client.patch(
            "/users/user/",
            {
                "username": "user",
                "email": "user@example.com",
                "groups": []
            },
            content_type="application/json"
        )

        # Remove an user
        response = self.client.delete("/users/user/")
        self.assertEqual(response.status_code, 401)

    def test_users_authenticated(self):
        """Test that authenticated users can use their own private data."""
        # Log in as the user
        self.client.login(username="user", password="password")

        # Get the response from the API
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, 200)

        # Check that private fields are returned for the user
        user = response.data['results'][1]  # TODO: This is not robust
        self.ensure_private_fields(user)

        # Edit the user
        response = self.client.patch(
            "/users/user/",
            {
                "username": "user-edited",
                "email": "user@example.com",
                "groups": []
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Edit another user
        response = self.client.patch(
            "/users/admin/",
            {
                "username": "admin-edited",
                "email": "admin@example.com",
                "groups": []
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        # Remove another user
        response = self.client.delete("/users/2/")

    def test_users_admin(self):
        """Test that admins can use private data of other users."""
        # Log in as the admin
        self.client.login(username="admin", password="password")

        # Get the response from the API
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, 200)

        # Check that private fields are returned for the user
        for user in response.data['results']:
            self.ensure_private_fields(user)

        # Edit our user
        response = self.client.patch(
            "/users/admin/",
            {
                "username": "admin-edited",
                "email": "admin@example.com",
                "groups": []
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Edit another user
        response = self.client.patch(
            "/users/user/",
            {
                "username": "user-edited",
                "email": "user@example.com",
                "groups": []
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Remove another user
        response = self.client.delete("/users/1/")

    def test_users_detail_unauthenticated(self):
        """Test that unauthenticated users can only use public data."""
        # Get the response from the API
        response = self.client.get("/users/user/")
        self.assertEqual(response.status_code, 200)

        # Check that only public fields are returned
        self.ensure_public_fields(response.data)

    def test_users_detail_authenticated(self):
        """Test that authenticated users can use their own private data."""
        # Log in as the user
        self.client.login(username="user", password="password")

        # Get the response from the API
        response = self.client.get("/users/user/")
        self.assertEqual(response.status_code, 200)

        # Check that private fields are returned
        self.ensure_private_fields(response.data)

        # Get user 2
        response = self.client.get("/users/admin/")
        self.assertEqual(response.status_code, 200)

        # Check that only public fields are returned
        self.ensure_public_fields(response.data)

    def test_users_detail_admin(self):
        """Test that admins can use private data of other users."""
        # Log in as the admin
        self.client.login(username="admin", password="password")

        # Get the response from the API
        response = self.client.get("/users/user/")
        self.assertEqual(response.status_code, 200)

        # Check that private fields are returned
        self.ensure_private_fields(response.data)

    def test_users_detail_not_found(self):
        """Test that users cannot access data of non-existing users."""
        # Log in as the user
        self.client.login(username="user", password="password")

        # Get the response from the API
        response = self.client.get("/users/nonexisting/")
        self.assertEqual(response.status_code, 404)

    def test_users_edit_unauthenticated(self):
        """Test that unauthenticated users cannot edit users."""
        # Get the response from the API
        response = self.client.patch("/users/user/", self.user,
                                   content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_users_edit_authenticated(self):
        """Test that authenticated users can only edit themselves."""
        # Log in as the user
        self.client.login(username="user", password="password")

        ### Test that users can edit themselves
        # Get the response from the API
        response = self.client.patch("/users/user/", self.user,
                                   content_type="application/json")
        self.assertEqual(response.status_code, 200)

        # Check that private fields are returned
        self.ensure_private_fields(response.data)

        # Check that the user was edited
        self.assertEqual(response.data['username'], self.user['username'])
        self.assertEqual(response.data['email'], self.user['email'])

        ### Test that users cannot edit other users


        # Log in again to get the updated user
        self.client.login(username="user", password="password")

        # Get the response from the API
        response = self.client.patch("/users/admin/", self.admin,
                                   content_type="application/json")
        self.assertEqual(response.status_code, 403)

    def test_users_edit_admin(self):
        """Test that admins can edit users."""
        # Log in as the admin
        self.client.login(username="admin", password="password")

        # Get the response from the API
        response = self.client.patch("/users/user/", self.user, content_type="application/json")
        self.assertEqual(response.status_code, 200)

        # Check that private fields are returned
        self.ensure_private_fields(response.data)

        # Check that the user was edited
        self.assertEqual(response.data['username'], self.user['username'])
        self.assertEqual(response.data['email'], self.user['email'])

    def test_users_edit_not_found(self):
        """Test that users cannot edit non-existing users."""
        # Log in as the user
        self.client.login(username="user", password="password")

        # Get the response from the API
        response = self.client.patch("/users/100/", self.user)
        self.assertEqual(response.status_code, 404)

    def test_users_delete_unauthenticated(self):
        """Test that unauthenticated users cannot delete users."""
        # Get the response from the API
        response = self.client.delete("/users/user/")
        self.assertEqual(response.status_code, 401)

    def test_users_delete_authenticated(self):
        """Test that authenticated users cannot delete users."""
        # Log in as the user
        self.client.login(username="user", password="password")

        # Get the response from the API
        response = self.client.delete("/users/admin/")
        self.assertEqual(response.status_code, 403)

        # List all users
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, 200)

    def test_users_delete_admin(self):
        """Test that admins can delete users."""
        # Log in as the admin
        self.client.login(username="admin", password="password")

        # Get the response from the API
        response = self.client.delete("/users/user/")
        self.assertEqual(response.status_code, 204)

    def test_current_user_unauthenticated(self):
        """Test that unauthenticated users cannot get the current user."""
        # Get the response from the API
        response = self.client.get("/current_user/")
        self.assertEqual(response.status_code, 401)

    def test_current_user_authenticated(self):
        """Test that authenticated users can get the current user."""
        # Log in as the user
        self.client.login(username="user", password="password")

        # Get the response from the API
        response = self.client.get("/current_user/")
        self.assertEqual(response.status_code, 200)

        # Check that private fields are returned
        self.ensure_private_fields(response.data)

        # Check that the user is the correct one
        self.assertEqual(response.data['username'], "user")

    def test_current_user_admin(self):
        """Test that admins can get the current user."""
        # Log in as the admin
        self.client.login(username="admin", password="password")

        # Get the response from the API
        response = self.client.get("/current_user/")
        self.assertEqual(response.status_code, 200)

        # Check that private fields are returned
        self.ensure_private_fields(response.data)

        # Check that the user is the correct one
        self.assertEqual(response.data['username'], "admin")

    def ensure_public_fields(self, user: dict) -> None:
        """Ensure that only public fields are returned."""
        # Check that only public fields are returned
        self.assertEqual(len(user), 6)
        self.assertIn("url", user)
        self.assertIn("username", user)
        self.assertIn("groups", user)
        self.assertIn("scripts", user)
        self.assertIn("collaborations", user)
        self.assertIn("ratings", user)

    def ensure_private_fields(self, user: dict) -> None:
        """Ensure that private fields are returned."""
        # Check that private fields are returned
        self.assertEqual(len(user), 8)
        self.assertIn("url", user)
        self.assertIn("collaborations", user)
        self.assertIn("username", user)
        self.assertIn("email", user)
        self.assertIn("groups", user)
        self.assertIn("scripts", user)
        self.assertIn("ratings", user)
        self.assertIn("warning_private_project", user)
