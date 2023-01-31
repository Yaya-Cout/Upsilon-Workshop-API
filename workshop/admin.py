from django.contrib import admin

from workshop.api.models import Script, Rating, OS, Tag

admin.site.site_header = "Workshop administration"


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    """Admin class for the Script model."""

    list_display = ('name', 'author', 'created', 'modified')
    list_filter = ('created', 'modified', 'author', 'language', 'compatibility')
    search_fields = ('name', 'description', 'files', 'licence', 'version', 'language', 'author__username', 'compatibility__name')
    ordering = ('-created',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Admin class for the Rating model."""

    list_display = ('script', 'user', 'rating', 'created', 'modified')
    list_filter = ('created', 'modified', 'user', 'rating')
    search_fields = ('script__name', 'user__username', 'rating')
    ordering = ('-created',)


@admin.register(OS)
class OSAdmin(admin.ModelAdmin):
    """Admin class for the OS model."""

    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin class for the Tag model."""

    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

# This syntax is easier to write, but it doesn't work with the search and filter
# fields
# admin.site.register(Tag)
