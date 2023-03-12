#!/usr/bin/env bash
# Reset the database and repopulate it with the dev environment
# Usage: reset.sh
rm -rf db.sqlite3
python manage.py migrate

# Create a superuser (username: admin, password: password, email: admin@example.org)
echo "from workshop.api.models import User; User.objects.create_superuser(username='admin', password='password', email='admin@example.org')" | python manage.py shell

# Create a user (username: user, password: password, email: user@example.org)
echo "from workshop.api.models import User; User.objects.create_user(username='user', password='password', email='user@example.org')" | python manage.py shell

# Create a user (username: user2, password: password, email: user2@example.org)
echo "from workshop.api.models import User; User.objects.create_user(username='user2', password='password', email='user2@example.org')" | python manage.py shell
