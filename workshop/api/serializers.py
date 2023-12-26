from django.contrib.auth.models import Group
from rest_framework import serializers, exceptions

# Import the models from the models.py file
from workshop.api.models import Script, Rating, OS, Tag, User

# Serializers define the API representation.


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """A serializer for the User model."""

    class Meta:
        """Meta class for the UserSerializer."""

        model = User
        fields = ['url', 'username', 'email', 'groups', 'scripts',
                  'collaborations', 'ratings', 'password',
                  'warning_private_project']

        read_only_fields = ['scripts', 'collaborations', 'ratings']

    def update(self, instance, validated_data):
        """Update an user."""
        # TODO: See if we can use view permissions to do this
        # Prevent non-staff users from adding themselves to groups
        if not self.context['request'].user.is_superuser and\
                'groups' in validated_data:
            # Get the groups the user is in
            user_groups = list(instance.groups.all())

            # Get the groups the user wants to be in
            new_groups = validated_data["groups"]\
                if 'groups' in validated_data else []

            # Ensure that the groups are the same
            if user_groups != new_groups:
                raise exceptions.PermissionDenied(
                    "You can't add or remove yourself from groups"
                )

        # If the password is being updated, hash it
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            del validated_data['password']

        # If everything is OK, update the user
        return super(UserSerializer, self).update(instance, validated_data)

    # Show only public information about users if not the user themselves
    def to_representation(self, instance):
        """Show user information."""
        # Allow staff users to see all information (except password)
        if instance == self.context['request'].user\
                or self.context['request'].user.is_superuser:
            representation = super(UserSerializer, self)\
                .to_representation(instance)

            # Remove the password from the representation
            representation.pop('password')

            # Return the representation
            return representation

        # Get the representation of the user
        representation = super(UserSerializer, self)\
            .to_representation(instance)

        # Remove private scripts querying the database with a filter
        queryset = Script.objects.filter(author=instance, is_public=True)
        queryset |= Script.objects.filter(
            author=instance,
            collaborators=self.context['request'].user
        )
        queryset = queryset.distinct()
        representation['scripts'] = ScriptSerializer(
            queryset,
            many=True,
            context={'request': self.context['request']}
        ).data
        representation['scripts'] = [script['url']
                                     for script in representation['scripts']]

        # Remove private collaborations querying the database with a filter
        queryset = Script.objects.filter(collaborators=instance,
                                         is_public=True)
        queryset |= Script.objects.filter(
            collaborators=instance,
            author=self.context['request'].user
        )
        queryset |= Script.objects.filter(collaborators=instance)\
            .filter(collaborators=self.context['request'].user)
        queryset = queryset.distinct()
        representation['collaborations'] = ScriptSerializer(
            queryset,
            many=True,
            context={'request': self.context['request']}
        ).data
        representation['collaborations'] = [
            script['url'] for script in representation['collaborations']
        ]

        # Return only the url and username
        return {
            'url': representation['url'],
            'username': representation['username'],
            'groups': representation['groups'],
            'scripts': representation['scripts'],
            'collaborations': representation['collaborations'],
            'ratings': representation['ratings']
        }


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the Group model."""

    class Meta:
        """Meta class for the GroupSerializer."""

        model = Group
        fields = ['url', 'name', 'user_set']

        read_only_fields = ['user_set']


class ScriptSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the Script model."""

    class Meta:
        """Meta class for the ScriptSerializer."""

        model = Script
        fields = ['url', 'name', 'created', 'modified', 'language', 'version',
                  'short_description', 'long_description', 'ratings', 'author',
                  'collaborators', 'files', 'licence', 'compatibility', 'views',
                  'id', 'tags', 'is_public', 'runner']

        # Set the read_only fields
        read_only_fields = ['created', 'modified', 'downloads', 'views',
                            'author', 'ratings']

    # Handle the author field (can't be changed by the user, for now)
    def create(self, validated_data: dict) -> Script:
        """Create a new Script object."""
        # Set the author to the user that created the script
        validated_data['author'] = self.context['request'].user

        # Return the created script
        return super().create(validated_data)


class RatingSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the Rating model."""

    class Meta:
        """Meta class for the RatingSerializer."""

        model = Rating
        fields = ['url', 'rating', 'comment', 'user', 'script', 'created',
                  'modified']

        # Set the read_only fields
        read_only_fields = ['user']

    # Handle the user field (can't be changed by the user, for now)
    def create(self, validated_data: dict) -> Rating:
        """Create a new Rating object."""
        # Set the user to the user that created the rating
        validated_data['user'] = self.context['request'].user

        # Return the created rating
        return super().create(validated_data)


class OSSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the OS model."""

    class Meta:
        """Meta class for the OSSerializer."""

        model = OS
        fields = ['name', 'homepage', 'description', 'url', 'script_set']

        # Set the read_only fields
        read_only_fields = ['version', 'script_set']


class TagSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the Tag model."""

    class Meta:
        """Meta class for the TagSerializer."""

        model = Tag
        fields = ['name', 'description', 'url', 'script_set']

        # Set the read_only fields
        read_only_fields = ['version', 'script_set']


class RegisterSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the User model."""

    class Meta:
        """Meta class for the RegisterSerializer."""

        model = User
        fields = ['username', 'password', 'email', 'url']

        # Set the write_only fields
        write_only_fields = ['password']

        # Mark username, password and email as required
        required_fields = ['username', 'password', 'email']

        # Mark username and email as unique
        unique_fields = ['username', 'email']

        # Don't show the password in POST requests
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data: dict) -> User:
        """Create a new User object."""
        # Create and return the user (we need it to be hashed)
        return User.objects.create_user(**validated_data)
