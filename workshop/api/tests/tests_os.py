"""Tests for /os/ endpoint."""
from django.test import TestCase

# Import the models we're testing
from django.contrib.auth.models import User


class OSTest(TestCase):
    """Test that permissions are enforced on the /os/ endpoint."""

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

        # Create an OS
        response = self.client.post(
            "/os/",
            {
                "name": "Upsilon",
                "homepage": "https://getupsilon.web.app",
                "description": "Upsilon is a free and open-source operating system for graphing calculators.",
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        # Logout
        self.client.logout()

    def test_os_unauthenticated(self):
        """Test that unauthenticated users can only list OS."""
        self.check_as_user()

    def test_os_authenticated(self):
        """Test that authenticated users can only list OS."""
        # Log in as the user
        self.client.login(username="user", password="password")

        self.check_as_user()

        # Logout
        self.client.logout()

    def test_os_admin(self):
        """Test that admin users can create, update and delete OS."""
        # Log in as the admin
        self.client.login(username="admin", password="password")

        response = self.add_os(201)
        # Update an OS
        response = self.client.put(
            f"/os/{response.data['name']}/",
            {
                "name": "Omega",
                "homepage": "https://getomega.dev",
                "description": "Omega is a free and open-source operating system for graphing calculators.",
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Delete an OS
        response = self.client.delete(f"/os/{response.data['name']}/")
        self.assertEqual(response.status_code, 204)

        # Logout
        self.client.logout()

    def check_as_user(self) -> None:
        """Run the tests for unauthenticated and authenticated users."""
        # Try to create an OS (should fail)
        response = self.add_os(403)

        # Try to update an OS (should fail)
        response = self.client.put(
            "/os/1/",
            {
                "name": "Omega",
                "homepage": "https://getomega.dev",
                "description": "Omega is a free and open-source operating system for graphing calculators.",
            },
            content_type="application/json",
        )

        # Check the response
        self.assertEqual(response.status_code, 403)

        # Try to delete an OS (should fail)
        response = self.client.delete("/os/1/")

        # Check the response
        self.assertEqual(response.status_code, 403)

    def add_os(self, excepted_status_code: int) -> dict:
        """Add an OS."""

        # Get the list of OS
        result = self.client.get("/os/")

        # Check the response
        self.assertEqual(result.status_code, 200)

        # Verify that the response is correct
        self.check_os_fields(result.data['results'])

        # Create an OS
        result = self.client.post(
            "/os/",
            {
                "name": "Omega",
                "homepage": "https://getomega.dev",
                "description": "Omega is a free and open-source operating system for graphing calculators.",
            },
            content_type="application/json",
        )

        # Check the response
        self.assertEqual(result.status_code, excepted_status_code)

        # Return the result
        return result

    def check_os_fields(self, results: None) -> None:
        """Check that all fields are present in the OS object."""
        for os in results:
            self.assertEqual(len(os), 5)
            self.assertIn("url", os)
            self.assertIn("homepage", os)
            self.assertIn("name", os)
            self.assertIn("description", os)
            self.assertIn("script_set", os)
