"""Tests for /scripts/ endpoint."""
from django.test import TestCase

# Import User model to create a superuser
from django.contrib.auth.models import User


class ScriptsTest(TestCase):
    """Test that permissions are enforced on the /scripts/ endpoint."""

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

        self.scriptPublicFields = [
            "url",
            "name",
            "created",
            "modified",
            "language",
            "version",
            "description",
            "ratings",
            "downloads",
            "views",
            "author",
            "content",
            "licence",
            "compatibility",
        ]

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

        # Create a script
        self.client.post(
            "/scripts/",
            {
                "name": "admin_script",
                "language": "python",
                "description": "test",
                "content": "print('test')"
            }
        )

        # Logout
        self.client.logout()

        # Login as the user
        self.client.login(username=self.user['username'],
                          password=self.user['password'])

        # Create a script
        self.client.post(
            "/scripts/",
            {
                "name": "user_script",
                "language": "python",
                "description": "test",
                "content": "print('test')"
            }
        )

        # Logout
        self.client.logout()

    def test_scripts_unauthenticated(self):
        """Test that unauthenticated users can only list public scripts."""
        # Get the response from the API
        response = self.client.get("/scripts/")
        self.assertEqual(response.status_code, 200)

        # Check that all fields are returned for each script
        for script in response.data['results']:
            self.assertEqual(len(script), len(self.scriptPublicFields))
            for field in self.scriptPublicFields:
                self.assertIn(field, script)

        # Check that we can't create a new script
        response = self.client.post(
            "/scripts/",
            {
                "name": "test",
                "language": "python",
                "content": "print('Hello, world!')"
            }
        )
        self.assertEqual(response.status_code, 403)

        # Check that we can't remove scripts
        response = self.client.delete("/scripts/1/")
        self.assertEqual(response.status_code, 403)

        # Check we can't edit scripts
        response = self.client.put(
            "/scripts/1/",
            {
                "name": "test",
                "language": "python",
                "content": "print('Hello, world!')"
            }
        )
        self.assertEqual(response.status_code, 403)

    def test_scripts_authenticated(self):
        """Test that authenticated users can use their own private data."""
        # Log in as the user
        self.client.login(username=self.user['username'],
                          password=self.user['password'])

        # Get the response from the API
        response = self.client.get("/scripts/")
        self.assertEqual(response.status_code, 200)

        # Check that all fields are returned for each script
        for script in response.data['results']:
            self.assertEqual(len(script), len(self.scriptPublicFields))
            for field in self.scriptPublicFields:
                self.assertIn(field, script)

        # Check that we can create a new script
        response = self.client.post(
            "/scripts/",
            {
                "name": "test2",
                "language": "python",
                "content": "print('Hello, world!')"
            }
        )
        self.assertEqual(response.status_code, 201)

        # Check that we can remove this script
        response = self.client.delete("/scripts/3/")
        self.assertEqual(response.status_code, 204)

        # Check that we can't remove other people's scripts
        response = self.client.delete("/scripts/1/")
        self.assertEqual(response.status_code, 403)

        # Check that we can edit our own scripts
        response = self.client.put(
            "/scripts/2/",
            {
                "name": "user_script2",
                "language": "python",
                "content": "print('Hello, world!')"
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Check that we can't edit other people's scripts
        response = self.client.put(
            "/scripts/1/",
            {
                "name": "admin_script2",
                "language": "python",
                "content": "print('Hello, world!')"
            }
        )
        self.assertEqual(response.status_code, 403)

    def test_scripts_admin(self):
        """Test that admins can use all data."""
        # Log in as the admin
        self.client.login(username=self.admin['username'],
                          password=self.admin['password'])

        # Get the response from the API
        response = self.client.get("/scripts/")
        self.assertEqual(response.status_code, 200)

        # Check that all fields are returned for each script
        for script in response.data['results']:
            self.assertEqual(len(script), len(self.scriptPublicFields))
            for field in self.scriptPublicFields:
                self.assertIn(field, script)

        # Check that we can create a new script
        response = self.client.post(
            "/scripts/",
            {
                "name": "test3",
                "language": "python",
                "content": "print('Hello, world!')"
            }
        )
        self.assertEqual(response.status_code, 201)

        # Check that we can edit our own scripts
        response = self.client.put(
            "/scripts/1/",
            {
                "name": "user_script2",
                "language": "python",
                "content": "print('Hello, world!')"
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Check that we can edit other people's scripts
        response = self.client.put(
            "/scripts/2/",
            {
                "name": "admin_script2",
                "language": "python",
                "content": "print('Hello, world!')"
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Check that we can remove this script
        response = self.client.delete("/scripts/3/")
        self.assertEqual(response.status_code, 204)

        # Check that we can remove other people's scripts
        response = self.client.delete("/scripts/1/")
        self.assertEqual(response.status_code, 204)

    def test_scripts_invalid(self):
        """Test that invalid requests are rejected."""
        # Log in as the user
        self.client.login(username=self.user['username'],
                          password=self.user['password'])

        # Check that we can't create a script with no name
        response = self.client.post(
            "/scripts/",
            {
                "language": "python",
                "content": "print('Hello, world!')"
            }
        )
        self.assertEqual(response.status_code, 400)

        # Check that we can't create a script with no language
        response = self.client.post(
            "/scripts/",
            {
                "name": "test",
                "content": "print('Hello, world!')"
            }
        )
        self.assertEqual(response.status_code, 400)

        # Check that we can't create a script with no content
        response = self.client.post(
            "/scripts/",
            {
                "name": "test",
                "language": "python"
            }
        )
        self.assertEqual(response.status_code, 400)

        # Check that we can't create a script with invalid language
        response = self.client.post(
            "/scripts/",
            {
                "name": "test",
                "language": "invalid",
                "content": "print('Hello, world!')"
            }
        )
        self.assertEqual(response.status_code, 400)

        # Check that we can't edit a script with invalid language
        response = self.client.put(
            "/scripts/2/",
            {
                "name": "user_script2",
                "language": "invalid",
                "content": "print('Hello, world!')"
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    # TODO: Test script download and views when they are implemented
