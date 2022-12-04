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
                "url": "https://getupsilon.web.app",
                "description": "Upsilon is a free and open-source operating system for graphing calculators.",
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        # Logout
        self.client.logout()

    def test_os_unauthenticated(self):
        """Test that unauthenticated users can only list OS."""
        # Get the response from the API
        response = self.client.get("/os/")
        self.assertEqual(response.status_code, 200)

        # Check that only public fields are returned for each OS
        for os in response.data['results']:
            self.assertEqual(len(os), 3)
            self.assertIn("url", os)
            self.assertIn("name", os)
            self.assertIn("description", os)

        # Try to create an OS
        response = self.client.post(
            "/os/",
            {
                "name": "Omega",
                "url": "https://getomega.dev",
                "description": "Omega is a free and open-source operating system for graphing calculators.",
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        # Try to update an OS
        response = self.client.put(
            "/os/1/",
            {
                "name": "Omega",
                "url": "https://getomega.dev",
                "description": "Omega is a free and open-source operating system for graphing calculators.",
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        # Try to delete an OS
        response = self.client.delete("/os/1/")
        self.assertEqual(response.status_code, 403)

    def test_os_authenticated(self):
        """Test that authenticated users can only list OS."""
        # Log in as the user
        self.client.login(username="user", password="password")

        # Get the response from the API
        response = self.client.get("/os/")
        self.assertEqual(response.status_code, 200)

        # Check that only public fields are returned for each OS
        for os in response.data['results']:
            self.assertEqual(len(os), 3)
            self.assertIn("url", os)
            self.assertIn("name", os)
            self.assertIn("description", os)

        # Try to create an OS
        response = self.client.post(
            "/os/",
            {
                "name": "Omega",
                "url": "https://getomega.dev",
                "description": "Omega is a free and open-source operating system for graphing calculators.",
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        # Try to update an OS
        response = self.client.put(
            "/os/1/",
            {
                "name": "Omega",
                "url": "https://getomega.dev",
                "description": "Omega is a free and open-source operating system for graphing calculators.",
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        # Try to delete an OS
        response = self.client.delete("/os/1/")
        self.assertEqual(response.status_code, 403)

        # Logout
        self.client.logout()

    def test_os_admin(self):
        """Test that admin users can create, update and delete OS."""
        # Log in as the admin
        self.client.login(username="admin", password="password")

        # Get the response from the API
        response = self.client.get("/os/")
        self.assertEqual(response.status_code, 200)

        # Check that all fields are returned for each OS
        for os in response.data['results']:
            self.assertEqual(len(os), 3)
            self.assertIn("url", os)
            self.assertIn("name", os)
            self.assertIn("description", os)

        # Create an OS
        response = self.client.post(
            "/os/",
            {
                "name": "Omega",
                "url": "https://getomega.dev",
                "description": "Omega is a free and open-source operating system for graphing calculators.",
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        # Update an OS
        response = self.client.put(
            "/os/1/",
            {
                "name": "Omega",
                "url": "https://getomega.dev",
                "description": "Omega is a free and open-source operating system for graphing calculators.",
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Delete an OS
        response = self.client.delete("/os/1/")
        self.assertEqual(response.status_code, 204)

        # Logout
        self.client.logout()
