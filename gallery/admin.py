from django.contrib import admin
from .models import Painting, ContactMessage, ArtistProfile

@admin.register(Painting)
class PaintingAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'is_available', 'is_featured', 'date_added')
    list_filter = ('category', 'is_available', 'is_featured')
    search_fields = ('title', 'description')
    list_editable = ('is_available', 'is_featured')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'related_painting', 'created_at', 'is_read')
    list_filter = ('is_read',)
    list_editable = ('is_read',)
    readonly_fields = ('created_at',)


@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'whatsapp_number')

    def has_add_permission(self, request):
        return not ArtistProfile.objects.exists()