from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions

# Import the models from the models.py file
from workshop.quickstart.models import Script, Rating

# Import the serializers from the serializers.py file
from workshop.quickstart.serializers import UserSerializer, GroupSerializer, ScriptSerializer, RatingSerializer

# Views are the functions that are called when a user visits a URL


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class ScriptViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows scripts to be viewed or edited.
    """
    queryset = Script.objects.all().order_by('-created')
    serializer_class = ScriptSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class RatingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ratings to be viewed or edited.
    """
    queryset = Rating.objects.all().order_by('-created')
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
