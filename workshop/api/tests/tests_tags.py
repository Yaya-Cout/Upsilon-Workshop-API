"""Tests for /tag/ endpoint."""
from django.test import TestCase

# Import the models we're testing
from django.contrib.auth.models import User


class TagTest(TestCase):
    """Test that permissions are enforced on the /tag/ endpoint."""

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

        # Log in as the admin
        self.client.login(username=self.admin['username'],
                          password=self.admin['password'])

        # Create a tag
        response = self.client.post(
            "/tags/",
            {
                "name": "Game",
                "description": "Any game that runs on the calculator."
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        # Logout
        self.client.logout()

    def test_tags_unauthenticated(self):
        """Test that unauthenticated users can only list tags."""
        self.check_as_user()

    def test_tags_authenticated(self):
        """Test that authenticated users can only list tags."""
        # Log in as the user
        self.client.login(username="user", password="password")

        self.check_as_user()

        # Logout
        self.client.logout()

    def test_tags_admin(self):
        """Test that admin users can create, update and delete tags."""
        # Log in as the admin
        self.client.login(username="admin", password="password")

        response = self.add_tag(201)

        # Update a Tag
        response = self.client.put(
            f"/tags/{response.data['name']}/",
            {
                "name": "Game-3",
                "description": "Any game that runs on the calculator."
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Delete a tag
        response = self.client.delete(f"/tags/{response.data['name']}/")
        self.assertEqual(response.status_code, 204)

        # Logout
        self.client.logout()

    def check_as_user(self) -> None:
        """Run the tests for unauthenticated and authenticated users."""
        # Try to create a tag (should fail)
        response = self.add_tag(403)

        # Try to update a tag (should fail)
        response = self.client.put(
            "/tags/1/",
            {
                "name": "Game",
                "description": "Any game that runs on the calculator."
            },
            content_type="application/json",
        )

        # Check the response
        self.assertEqual(response.status_code, 403)

        # Try to delete a tag (should fail)
        response = self.client.delete("/tags/1/")

        # Check the response
        self.assertEqual(response.status_code, 403)

    def add_tag(self, excepted_status_code: int) -> dict:
        """Add a tag."""

        # Get the list of tags
        result = self.client.get("/tags/")

        # Check the response
        self.assertEqual(result.status_code, 200)

        # Verify that the response is correct
        self.check_tag_fields(result.data['results'])

        # Create a tag
        result = self.client.post(
            "/tags/",
            {
                "name": "Game-2",
                "description": "Any game that runs on the calculator."
            },
            content_type="application/json",
        )

        # Check the response
        self.assertEqual(result.status_code, excepted_status_code)

        # Return the result
        return result

    def check_tag_fields(self, results: None) -> None:
        """Check that all fields are present in the tag object."""
        for tag in results:
            self.assertEqual(len(tag), 4)
            self.assertIn("url", tag)
            self.assertIn("name", tag)
            self.assertIn("description", tag)
            self.assertIn("script_set", tag)
