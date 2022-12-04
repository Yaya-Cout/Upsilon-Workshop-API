"""Tests for /ratings/ endpoint."""
from django.test import TestCase

# Import User model to create a superuser
from django.contrib.auth.models import User


class ScriptsTest(TestCase):
    """Test that permissions are enforced on the /ratings/ endpoint."""

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
        self.user_rating = {
            "rating": 5,
            "comment": "This is a comment",
            "script": "/scripts/1/",
        }
        self.admin_rating = {
            "rating": 5,
            "comment": "test",
            "script": "/scripts/1/",
        }
        self.rating_fields = [
            "url", "rating", "comment", "user", "script", "created", "modified"
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
        response = self.client.post(
            "/scripts/",
            {
                "name": "Test Script",
                "language": "python",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')"
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        # Create a rating
        response = self.client.post(
            "/ratings/",
            self.admin_rating,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        # Log out
        self.client.logout()

        # Login as the user
        self.client.login(username=self.user['username'],
                          password=self.user['password'])

        # Create a rating
        response = self.client.post(
            "/ratings/",
            self.user_rating,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        # Logout
        self.client.logout()

    def test_ratings_unauthenticated(self):
        """Test that unauthenticated users can only view ratings."""
        # Get the list of ratings
        response = self.client.get("/ratings/")
        self.assertEqual(response.status_code, 200)
        # Assert that there are two ratings with correct data
        self.assertEqual(len(response.data["results"]), 2)
        for item, rating in zip(response.data["results"], [self.user_rating,
                                                           self.admin_rating]):
            for field in self.rating_fields:
                # Handle url field (not present in self.admin_rating)
                if field == "url":
                    self.assertIn("url", item)
                    continue
                if field == "user":
                    # Admin has id 1, user has id 2
                    user_id = 2 if rating["comment"] == "This is a comment" else 1
                    continue
                if field == "script":
                    self.assertEqual(item[field], f"http://testserver{rating[field]}")
                    continue
                # Ignore created and modified
                if field in ["created", "modified"]:
                    continue

                self.assertEqual(item[field], rating[field])
            self.assertEqual(len(item), len(self.rating_fields))

        # Get a specific rating
        response = self.client.get("/ratings/1/")
        self.assertEqual(response.status_code, 200)

        # Try to create a rating
        response = self.client.post(
            "/ratings/",
            {
                "script": 1,
                "rating": 5,
                "comment": "test"
            }
        )
        self.assertEqual(response.status_code, 403)

        # Try to edit a rating
        response = self.client.put(
            "/ratings/1/",
            {
                "script": 1,
                "rating": 5,
                "comment": "test"
            }
        )
        self.assertEqual(response.status_code, 403)

        # Try to delete a rating
        response = self.client.delete("/ratings/1/")
        self.assertEqual(response.status_code, 403)

    def test_ratings_authenticated(self):
        """Test that authenticated users can view, create, edit, and delete ratings."""
        # Log in as the user
        self.client.login(username=self.user['username'],
                          password=self.user['password'])

        # Get the list of ratings
        response = self.client.get("/ratings/")
        self.assertEqual(response.status_code, 200)
        # Assert that there are two ratings with correct data
        self.assertEqual(len(response.data["results"]), 2)
        for item, rating in zip(response.data["results"], [self.user_rating,
                                                           self.admin_rating]):
            for field in self.rating_fields:
                # Handle url field (not present in self.admin_rating)
                if field == "url":
                    self.assertIn("url", item)
                    continue
                if field == "user":
                    # Admin has id 1, user has id 2
                    user_id = 1 if rating["comment"] == "This is a comment" else 2

                    # Assert that the user field is the correct url
                    self.assertEqual(item[field], f"http://testserver/users/{user_id}/")
                    continue
                if field == "script":
                    self.assertEqual(item[field], f"http://testserver{rating[field]}")
                    continue
                # Ignore created and modified
                if field in ["created", "modified"]:
                    continue

                self.assertEqual(item[field], rating[field])
            self.assertEqual(len(item), len(self.rating_fields))

        # Get a specific rating
        response = self.client.get("/ratings/1/")
        self.assertEqual(response.status_code, 200)

        # Try to create a rating
        response = self.client.post(
            "/ratings/",
            {
                "script": "/scripts/1/",
                "rating": 5,
                "comment": "test"
            }
        )
        self.assertEqual(response.status_code, 201)

        # Try to edit a rating
        response = self.client.put(
            "/ratings/3/",
            {
                "script": "/scripts/1/",
                "rating": 5,
                "comment": "test",
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Try to delete a rating
        response = self.client.delete("/ratings/3/")
        self.assertEqual(response.status_code, 204)

        # Try to delete a rating from another user
        response = self.client.delete("/ratings/1/")
        self.assertEqual(response.status_code, 403)

        # Log out
        self.client.logout()

    def test_ratings_admin(self):
        """Test that admin users can view, create, edit, and delete ratings."""
        # Log in as the admin
        self.client.login(username=self.admin['username'],
                          password=self.admin['password'])

        # Get the list of ratings
        response = self.client.get("/ratings/")
        self.assertEqual(response.status_code, 200)
        # Assert that there are two ratings with correct data
        self.assertEqual(len(response.data["results"]), 2)
        for item, rating in zip(response.data["results"], [self.user_rating,
                                                           self.admin_rating]):
            for field in self.rating_fields:
                # Handle url field (not present in self.admin_rating)
                if field == "url":
                    self.assertIn("url", item)
                    continue
                if field == "user":
                    # Admin has id 1, user has id 2
                    user_id = 1 if rating["comment"] == "This is a comment" else 2

                    # Assert that the user field is the correct url
                    self.assertEqual(item[field], f"http://testserver/users/{user_id}/")
                    continue
                if field == "script":
                    self.assertEqual(item[field], f"http://testserver{rating[field]}")
                    continue
                # Ignore created and modified
                if field in ["created", "modified"]:
                    continue

                self.assertEqual(item[field], rating[field])
            self.assertEqual(len(item), len(self.rating_fields))

        # Get a specific rating
        response = self.client.get("/ratings/1/")
        self.assertEqual(response.status_code, 200)

        # Try to create a rating
        response = self.client.post(
            "/ratings/",
            {
                "script": "/scripts/1/",
                "rating": 5,
                "comment": "test"
            }
        )
        self.assertEqual(response.status_code, 201)

        # Try to edit a rating
        response = self.client.put(
            "/ratings/3/",
            {
                "script": "/scripts/1/",
                "rating": 5,
                "comment": "test",
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Try to delete a rating
        response = self.client.delete("/ratings/3/")
        self.assertEqual(response.status_code, 204)

        # Try to delete a rating from another user
        response = self.client.delete("/ratings/1/")

    def test_ratings_empty_comment(self):
        """Test that ratings can be created without a comment."""
        # Log in as the admin
        self.client.login(username=self.admin['username'],
                          password=self.admin['password'])

        # Create a rating
        response = self.client.post(
            "/ratings/",
            {
                "script": "/scripts/1/",
                "rating": 2,
                "comment": "",
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        # Fetch the rating
        response = self.client.get("/ratings/3/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["comment"], "")
        self.assertEqual(response.data["rating"], 2)
        self.assertEqual(response.data["script"], "http://testserver/scripts/1/")

        # Log out
        self.client.logout()

    def test_ratings_invalid_rating(self):
        """Test that ratings can't be created with an invalid rating."""
        # Log in as the admin
        self.client.login(username=self.admin['username'],
                          password=self.admin['password'])

        ### Test invalid rating

        # Create a rating with a rating of 6 and -1
        for rating in [6, -1, 5.5, -0.5]:
            response = self.client.post(
                "/ratings/",
                {
                    "script": "/scripts/1/",
                    "rating": rating,
                    "comment": "test",
                },
                content_type="application/json"
            )
            self.assertEqual(response.status_code, 400)

        # Try to create a rating with a string
        response = self.client.post(
            "/ratings/",
            {
                "script": "/scripts/1/",
                "rating": "test",
                "comment": "test",
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        ### Test valid rating
        for rating in [0, 1, 2, 3, 4, 5, 4.5, 0.5]:
            response = self.client.post(
                "/ratings/",
                {
                    "script": "/scripts/1/",
                    "rating": rating,
                    "comment": "test",
                },
                content_type="application/json"
            )
            self.assertEqual(response.status_code, 201)

        # Log out
        self.client.logout()
