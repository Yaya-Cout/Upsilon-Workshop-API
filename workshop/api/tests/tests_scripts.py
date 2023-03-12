"""Tests for /scripts/ endpoint."""
import json

from django.test import TestCase

# Import User model to create a superuser
from workshop.api.models import User


class ScriptsTest(TestCase):
    """Test that permissions are enforced on the /scripts/ endpoint."""

    def setUp(self):
        """Set up the test client."""
        self.user = {
            "username": "user",
            "password": "password",
            "email": "user@example.com",
        }

        self.user2 = {
            "username": "user2",
            "password": "password",
            "email": "user2@example.com",
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
            "author",
            "collaborators",
            "files",
            "licence",
            "compatibility",
            "views",
            "id",
            "tags",
            "is_public"
        ]

        # Register a user
        response = self.client.post("/register/", self.user)
        self.assertEqual(response.status_code, 201)
        self.user["url"] = response.data["url"]

        # Register a second user
        response = self.client.post("/register/", self.user2)
        self.assertEqual(response.status_code, 201)
        self.user2["url"] = response.data["url"]

        # Manually create an admin user (not through the API)
        User.objects.create_superuser(
            self.admin['username'],
            self.admin['email'],
            self.admin['password']
        )

        # Log in as the admin
        logged = self.client.login(username=self.admin['username'],
                                   password=self.admin['password'])
        self.assertTrue(logged)

        # Create a script
        response = self.client.post(
            "/scripts/",
            {
                "name": "admin_script",
                "language": "python",
                "description": "test",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello world!')",
                    }
                ],
                "collaborators": [
                    self.user2['url']
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        self.admin_script = response.data

        # Logout
        self.client.logout()

        # Login as the user
        logged = self.client.login(username=self.user['username'],
                                   password=self.user['password'])
        self.assertTrue(logged)

        # Create a script
        response = self.client.post(
            "/scripts/",
            {
                "name": "user_script",
                "language": "python",
                "description": "test",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello world!')",
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        self.user_script = response.data

        # Logout
        self.client.logout()

    def ensure_script_fields(self, script):
        """Ensure that all fields are present in the script."""
        for field in self.scriptPublicFields:
            self.assertIn(field, script)
        self.assertEqual(len(script), len(self.scriptPublicFields))

    def ensure_files_valid(self, files):
        """Ensure that files are valid."""
        for file in files:
            self.assertIn('name', file)
            self.assertIn('content', file)
            self.assertEqual(len(file), 2)

    def test_scripts_unauthenticated(self):
        """Test that unauthenticated users can only list public scripts."""
        # Check that we can list scripts
        response = self.ensure_list_valid()

        # Check that we can't create a new script
        response = self.client.post(
            "/scripts/",
            {
                "name": "test",
                "language": "python",
                "content": "print('Hello, world!')"
            }
        )
        self.assertEqual(response.status_code, 401)

        # Check that we can't remove scripts
        response = self.client.delete("/scripts/1/")
        self.assertEqual(response.status_code, 401)

        # Check we can't edit scripts
        response = self.client.put(
            "/scripts/1/",
            {
                "name": "test",
                "language": "python",
                "content": "print('Hello, world!')"
            }
        )
        self.assertEqual(response.status_code, 401)

    def test_scripts_authenticated(self):
        """Test that authenticated users can use their own private data."""
        # Log in as the user
        logged = self.client.login(username=self.user['username'],
                                   password=self.user['password'])
        self.assertTrue(logged)

        response = self.ensure_list_valid()
        # Check that we can create a new script
        response = self.client.post(
            "/scripts/",
            {
                "name": "test2",
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

        # Check that we can remove this script
        response = self.client.delete(response.data['url'])
        self.assertEqual(response.status_code, 204)

        # Check that we can't remove other people's scripts
        response = self.client.delete(self.admin_script['url'])
        self.assertEqual(response.status_code, 403)

        # Check that we can edit our own scripts
        response = self.client.put(
            self.user_script['url'],
            {
                "name": "user_script2",
                "language": "python",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')"
                    },
                    {
                        "name": "test2.py",
                        "content": "from test import *"
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Check that we can't edit other people's scripts
        response = self.client.put(
            self.admin_script['url'],
            {
                "name": "admin_script2",
                "language": "python",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')"
                    },
                    {
                        "name": "test2.py",
                        "content": "from test import *"
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    def test_script_collaborators(self):
        """Test that collaborators can use each other's private data."""
        # Log in as the user
        logged = self.client.login(username=self.user2['username'],
                                   password=self.user2['password'])
        self.assertTrue(logged)

        # Check that we can't edit other people's scripts
        response = self.client.put(
            self.user_script['url'],
            {
                "name": "user_script2",
                "language": "python",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')"
                    },
                    {
                        "name": "test2.py",
                        "content": "from test import *"
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        # Try to add the user as a collaborator, but don't have permission
        response = self.client.patch(
            self.admin_script['url'],
            {
                "collaborators": [
                    self.user['url'],
                    self.user2['url']
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        # Check that we can edit other people's scripts
        response = self.client.patch(
            self.admin_script['url'],
            {
                "name": "admin_script2",
                "language": "python",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')"
                    },
                    {
                        "name": "test2.py",
                        "content": "from test import *"
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Ensure we can't change the author
        response = self.client.patch(
            self.admin_script['url'],
            {
                "author": self.user['url']
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Ensure we can't delete the script
        response = self.client.delete(self.admin_script['url'])
        self.assertEqual(response.status_code, 403)

        # Log in as the admin
        logged = self.client.login(username=self.admin['username'],
                                   password=self.admin['password'])
        self.assertTrue(logged)

        # Add the user as a collaborator
        response = self.client.patch(
            self.admin_script['url'],
            {
                "collaborators": [
                    self.user['url'],
                    self.user2['url']
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Log in as the user
        logged = self.client.login(username=self.user['username'],
                                   password=self.user['password'])
        self.assertTrue(logged)

        # Check that we can read the shared script
        response = self.client.get(self.admin_script['url'])
        self.assertEqual(response.status_code, 200)

        # Check that we can edit the shared script
        response = self.client.put(
            self.admin_script['url'],
            {
                "name": "admin_script2",
                "language": "python",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')"
                    },
                    {
                        "name": "test2.py",
                        "content": "from test import *"
                    }
                ]
            },
            content_type="application/json"
        )

    def test_scripts_admin(self):
        """Test that admins can use all data."""
        # Log in as the admin
        self.client.login(username=self.admin['username'],
                          password=self.admin['password'])

        response = self.ensure_list_valid()
        # Check that we can create a new script
        response = self.client.post(
            "/scripts/",
            {
                "name": "test3",
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

        # Check that we can edit our own scripts
        response = self.client.put(
            self.admin_script['url'],
            {
                "name": "user_script2",
                "language": "python",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')"
                    },
                    {
                        "name": "test2.py",
                        "content": "from test import *"
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Check that we can edit other people's scripts
        response = self.client.put(
            self.user_script['url'],
            {
                "name": "admin_script2",
                "language": "python",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')"
                    },
                    {
                        "name": "test2.py",
                        "content": "from test import *"
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Check that we can remove this script
        response = self.client.delete(response.data['url'])
        self.assertEqual(response.status_code, 204)

        # Check that we can remove other people's scripts
        response = self.client.delete(self.admin_script['url'])
        self.assertEqual(response.status_code, 204)

    def test_scripts_invalid(self):
        """Test that invalid requests are rejected."""
        # Log in as the admin
        self.client.login(username=self.admin['username'],
                          password=self.admin['password'])

        # Check that we can't create a script with no name
        response = self.client.post(
            "/scripts/",
            {
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
        self.assertEqual(response.status_code, 400)

        # Check that we can't create a script with no language
        response = self.client.post(
            "/scripts/",
            {
                "name": "test",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')"
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        # Check that we can't create a script with no content
        response = self.client.post(
            "/scripts/",
            {
                "name": "test",
                "language": "python"
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        # Check that we can't create a script with invalid language
        response = self.client.post(
            "/scripts/",
            {
                "name": "test",
                "language": "invalid",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')"
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        # Check that we can't edit a script with invalid language
        response = self.client.put(
            self.user_script['url'],
            {
                "name": "user_script2",
                "language": "invalid",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')"
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        # Check that we can't create a script with invalid files
        response = self.client.post(
            "/scripts/",
            {
                "name": "test",
                "language": "python",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')"
                    },
                    {
                        "name": "test2.py",
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            "/scripts/",
            {
                "name": "test",
                "language": "python",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')"
                    },
                    {
                        "content": "from test import *"
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            "/scripts/",
            {
                "name": "test",
                "language": "python",
                "files": []
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            "/scripts/",
            {
                "name": "test",
                "language": "python",
                "files": [{}]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        # Check that we can't create a file with extra fields
        response = self.client.post(
            "/scripts/",
            {
                "name": "test",
                "language": "python",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')",
                        "extra": "extra"
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        # Check that we can't create a file with no extension
        self.create_script_with_file_name("test", 400)

        # Check that we can't create a file with a slash
        self.create_script_with_file_name("test.py/", 400)
        self.create_script_with_file_name("/test.py", 400)
        self.create_script_with_file_name("test/test.py", 400)

        # Check that files with the same name are rejected
        response = self.client.post(
            "/scripts/",
            {
                "name": "test",
                "language": "python",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')"
                    },
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')"
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        # Check that we can't create a script that is bigger than the limit
        # (100 * 1024 bytes)
        # Generate the base files
        files = [
            {
                "name": "test.py",
                "content": ""
            }
        ]

        # Generate the content that is too big based on the payload size
        content = "a" * (100 * 1024 - len(json.dumps(files)) + 1)
        files[0]['content'] = content

        # Assert that the payload is the correct size
        self.assertEqual(len(json.dumps(files)), 100 * 1024 + 1)

        response = self.client.post(
            "/scripts/",
            {
                "name": "test",
                "language": "python",
                "files": files
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def create_script_with_file_name(self, file_name, expected_status_code):
        """Helper function to create a script with a file name."""
        response = self.client.post(
            "/scripts/",
            {
                "name": "test",
                "language": "python",
                "files": [
                    {
                        "name": file_name,
                        "content": "print('Hello, world!')"
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, expected_status_code)

    def test_private_scripts(self):
        """Test that private scripts are not visible to other users."""
        # Log in as the user
        self.client.login(username=self.user['username'],
                          password=self.user['password'])

        # Create a private script
        response = self.client.post(
            "/scripts/",
            {
                "name": "private_script",
                "language": "python",
                "files": [
                    {
                        "name": "test.py",
                        "content": "print('Hello, world!')"
                    }
                ],
                "is_public": False
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        # Save the URL
        private_script = response.data['url']

        # Get the script
        response = self.client.get(private_script)
        self.assertEqual(response.status_code, 200)

        # Get the list of scripts and check that the private script is in it
        response = self.client.get("/scripts/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(private_script, [script['url'] for script in
                                       response.data['results']])

        # Log in as the admin
        self.client.logout()
        self.client.login(username=self.admin['username'],
                          password=self.admin['password'])

        # Get the script and check that it it is visible (admins can see
        # everything)
        response = self.client.get(private_script)
        self.assertEqual(response.status_code, 200)

        # Get the list of scripts and check that the private script is in it
        response = self.client.get("/scripts/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(private_script, [script['url'] for script in
                                        response.data['results']])
        self.client.logout()

        # Log in as the other user
        self.client.login(username=self.user2['username'],
                          password=self.user2['password'])

        # Get the script and check that it is not visible
        response = self.client.get(private_script)
        self.assertEqual(response.status_code, 404)

        # Get the list of scripts and check that the private script is not in
        # it
        response = self.client.get("/scripts/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(private_script, [script['url'] for script in
                                          response.data['results']])
        self.client.logout()

        # Log in as the user and add the other user as a collaborator
        self.client.login(username=self.user['username'],
                            password=self.user['password'])
        response = self.client.patch(
            private_script,
            {
                "collaborators": [self.user2['url']]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Get the script and check that it is visible
        response = self.client.get(private_script)
        self.assertEqual(response.status_code, 200)

        # Get the list of scripts and check that the private script is in it
        response = self.client.get("/scripts/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(private_script, [script['url'] for script in
                                       response.data['results']])

        # Log in as the other user
        self.client.logout()
        self.client.login(username=self.user2['username'],
                            password=self.user2['password'])

        # Get the script and check that it is visible
        response = self.client.get(private_script)
        self.assertEqual(response.status_code, 200)

        # Get the list of scripts and check that the private script is in it
        response = self.client.get("/scripts/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(private_script, [script['url'] for script in
                                       response.data['results']])


    def ensure_list_valid(self) -> dict:
        """Ensure that the list of scripts is valid and return it."""
        # Get the list of scripts
        result = self.client.get("/scripts/")

        # Check the return code
        self.assertEqual(result.status_code, 200)

        # Check that the script fields are present
        for script in result.data['results']:
            self.ensure_script_fields(script)

        # Check that the files are valid
        for script in result.data['results']:
            self.ensure_files_valid(script['files'])

        # Return the result
        return result

    # TODO: Test script download and views when they are implemented
