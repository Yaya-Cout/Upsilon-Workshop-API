from django.contrib.auth.models import User, Group
from rest_framework import serializers

# Import the models from the models.py file
from workshop.quickstart.models import Script, Rating, OS

# Serializers define the API representation.


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

    # Allow users to edit their own information only
    def update(self, instance, validated_data):
        if instance == self.context['request'].user:
            return super(UserSerializer, self).update(instance, validated_data)
        else:
            raise serializers.ValidationError("You can only edit your own information.")


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class ScriptSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the Script model."""

    class Meta:
        """Meta class for the ScriptSerializer."""

        model = Script
        fields = ['url', 'name', 'created', 'modified', 'language',
                  'version', 'description', 'ratings', 'downloads',
                  'views', 'authors', 'content', 'licence', 'compatibility']

        # Set the read_only fields
        read_only_fields = ['created', 'modified', 'downloads', 'views',
                            'authors', 'ratings']

    # Handle the author field (can't be changed by the user, for now)
    def create(self, validated_data: dict) -> Script:
        """Create a new Script object."""
        # TODO: Allow multiple authors, if both accept
        # Set the author to the user that created the script
        validated_data['authors'] = [self.context['request'].user]

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
        fields = ['name', 'url', 'description']

        # Set the read_only fields
        read_only_fields = ['version']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    class Meta:
        """Meta class for the RegisterSerializer."""

        model = User
        fields = ['username', 'password', 'email']

        # Set the write_only fields
        write_only_fields = ['password']

    def create(self, validated_data: dict) -> User:
        """Create a new User object."""
        # Create and return the user
        return User.objects.create_user(**validated_data)
