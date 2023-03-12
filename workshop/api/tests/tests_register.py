"""Tests for /register/ endpoint."""
from django.test import TestCase

# Import the models we're testing
from workshop.api.models import User


class RegisterTest(TestCase):
    """Test that a user can register with the API."""

    def setUp(self):
        """Set up the test client."""
        self.user = {
            "username": "user",
            "password": "password",
            "email": "email@example.com",
        }

    def test_register(self):
        """Test that a user can register with the API."""
        # Get the response from the API
        response = self.client.post("/register/", self.user)
        self.assertEqual(response.status_code, 201)

        # Check that the user was created
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "user")

    def test_register_duplicate(self):
        """Test that a user cannot register with the same username twice."""
        # Get the response from the API
        response = self.client.post("/register/", self.user)
        self.assertEqual(response.status_code, 201)

        # Check that the user was created
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "user")

        # Try to create a duplicate user
        response = self.client.post("/register/", self.user)
        self.assertEqual(response.status_code, 400)

        # Check that the user was not created
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "user")

    def test_register_duplicate_email(self):
        """Test that a user cannot register with the same email twice."""
        # Get the response from the API
        response = self.client.post("/register/", self.user)
        self.assertEqual(response.status_code, 201)

        # Check that the user was created
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "user")

        # Try to create a duplicate user
        response = self.client.post("/register/", self.user)
        self.assertEqual(response.status_code, 400)

        # Check that the user was not created
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "user")

    def test_register_no_username(self):
        """Test that a user cannot register without a username."""
        # Get the response from the API
        response = self.client.post("/register/", {
            "password": "password",
            "email": "no_username@example.com",
        })
        self.assertEqual(response.status_code, 400)

        # Check that the user was not created
        self.assertEqual(User.objects.count(), 0)

    def test_register_no_password(self):
        """Test that a user cannot register without a password."""
        # Get the response from the API
        response = self.client.post("/register/", {
            "username": "no_password",
            "email": "no_password@example.com",
        })
        self.assertEqual(response.status_code, 400)

        # Check that the user was not created
        self.assertEqual(User.objects.count(), 0)

    def test_register_no_email(self):
        """Test that a user cannot register without an email."""
        # Get the response from the API
        response = self.client.post("/register/", {
            "username": "no_email",
            "password": "password",
        })

        self.assertEqual(response.status_code, 400)

        # Check that the user was not created
        self.assertEqual(User.objects.count(), 0)

    def test_register_invalid_email(self):
        """Test that a user cannot register with an invalid email."""
        # Get the response from the API
        response = self.client.post("/register/", {
            "username": "invalid_email",
            "password": "password",
            "email": "invalid_email",
        })
        self.assertEqual(response.status_code, 400)

        # Check that the user was not created
        self.assertEqual(User.objects.count(), 0)

    def test_register_invalid_password(self):
        """Test that a user cannot register with an invalid password."""
        # Get the response from the API
        response = self.client.post("/register/", {
            "username": "invalid_password",
            "password": "",
            "email": "email@example.com",
        })
        self.assertEqual(response.status_code, 400)

        # Check that the user was not created
        self.assertEqual(User.objects.count(), 0)
