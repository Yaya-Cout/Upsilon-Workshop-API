from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions

# Import the models from the models.py file
from workshop.quickstart.models import Script

# Import the serializers from the serializers.py file
from workshop.quickstart.serializers import UserSerializer, GroupSerializer, ScriptSerializer

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
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
