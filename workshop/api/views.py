from django.contrib.auth.models import Group
from rest_framework import viewsets
from rest_framework import permissions

# Import the models from the models.py file
from workshop.api.models import Script, Rating, OS, Tag, User

# Import the serializers from the serializers.py file
from workshop.api.serializers import UserSerializer, GroupSerializer, ScriptSerializer, RatingSerializer, OSSerializer, TagSerializer, RegisterSerializer

# Import the permissions from the permissions.py file
from workshop.api.permissions import IsAdminOrReadOnly, ReadWriteWithoutPost, IsOwnerOrReadOnly, IsScriptOwnerOrReadOnly, IsRatingOwnerOrReadOnly
# Views are the functions that are called when a user visits a URL


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [ReadWriteWithoutPost, IsOwnerOrReadOnly]

    search_fields = ('username', 'groups__name', 'scripts__name')

    filterset_fields = ('username', 'email', 'first_name', 'last_name')


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('-name')
    serializer_class = GroupSerializer
    permission_classes = [IsAdminOrReadOnly]

    search_fields = ('name', 'user__username')

    filterset_fields = ('name', 'user__username')


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

    search_fields = (
        'name', 'description', 'files', '^licence', 'version', 'language',
        'author__username', 'compatibility__name',
    )

    filterset_fields = (
        'name', 'description', 'licence', 'version', 'language',
        'author__username', 'compatibility__name',
    )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Script.objects.filter(pk=instance.id).update(views=instance.views + 1)
        return super(ScriptViewSet, self).retrieve(request, *args, **kwargs)

    def get_queryset(self):
        # If the user is the admin, get all scripts
        if self.request.user.is_staff:
            return super(ScriptViewSet, self).get_queryset()
        # Get public scripts
        queryset = Script.objects.filter(is_public=True)

        # If the user is authenticated, get their private scripts too
        if self.request.user.is_authenticated:
            queryset = queryset | Script.objects.filter(
                author=self.request.user
            )

            # Add the scripts the user is one of the collaborators of
            queryset = queryset | Script.objects.filter(
                collaborators=self.request.user
            )

        # Remove duplicates
        queryset = queryset.distinct()

        return queryset.order_by('-created')


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

    search_fields = ('script__name', 'script__author__username', 'rating')

    filterset_fields = ('script__name', 'script__author__username', 'rating')


class OSViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows OS to be viewed or edited.
    """
    queryset = OS.objects.all().order_by('-name')
    serializer_class = OSSerializer
    permission_classes = [IsAdminOrReadOnly]

    search_fields = ('name', 'homepage', 'description')

    filterset_fields = ('name', 'homepage', 'description')


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tags to be viewed or edited.
    """
    queryset = Tag.objects.all().order_by('-name')
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]

    search_fields = ('name', 'description')

    filterset_fields = ('name', 'description')


class RegisterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be registered.
    """
    # We don't want to show any data, because it's a POST request
    queryset = User.objects.none()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
