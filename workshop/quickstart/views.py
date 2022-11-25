from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions

# Import the models from the models.py file
from workshop.quickstart.models import Script, Rating, OS

# Import the serializers from the serializers.py file
from workshop.quickstart.serializers import UserSerializer, GroupSerializer, ScriptSerializer, RatingSerializer, OSSerializer, RegisterSerializer

# Import the permissions from the permissions.py file
from workshop.quickstart.permissions import IsAdminOrReadOnly, ReadWriteWithoutPost, IsOwnerOrReadOnly, IsScriptOwnerOrReadOnly, IsRatingOwnerOrReadOnly
# Views are the functions that are called when a user visits a URL


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [ReadWriteWithoutPost, IsOwnerOrReadOnly]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminOrReadOnly]


class ScriptViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows scripts to be viewed or edited.
    """
    queryset = Script.objects.all().order_by('-created')
    serializer_class = ScriptSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsScriptOwnerOrReadOnly
    ]


class RatingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ratings to be viewed or edited.
    """
    queryset = Rating.objects.all().order_by('-created')
    serializer_class = RatingSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsRatingOwnerOrReadOnly
    ]


class OSViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows OS to be viewed or edited.
    """
    queryset = OS.objects.all().order_by('-name')
    serializer_class = OSSerializer
    permission_classes = [IsAdminOrReadOnly]


class RegisterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be registered.
    """
    # We don't want to show any data, because it's a POST request
    queryset = User.objects.none()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
