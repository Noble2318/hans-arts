from django.contrib import admin
from django.contrib.admin.models import LogEntry
from .models import Painting, ContactMessage, ArtistProfile, PaintingImage


class PaintingImageInline(admin.TabularInline):
    model = PaintingImage
    extra = 1


@admin.register(Painting)
class PaintingAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'currency', 'is_available', 'is_featured', 'date_added')
    list_filter = ('category', 'is_available', 'is_featured')
    search_fields = ('title', 'description')
    list_editable = ('is_available', 'is_featured')
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'image',
                'video',
                'description',
                'category',
                'medium',
                'size',
            ),
        }),
        ('Price and availability', {
            'fields': ('price', 'currency', 'is_available', 'is_featured'),
        }),
    )
    inlines = [PaintingImageInline]

    def delete_model(self, request, obj):
        object_id = str(obj.pk)
        super().delete_model(request, obj)
        LogEntry.objects.filter(
            content_type__app_label=self.model._meta.app_label,
            content_type__model=self.model._meta.model_name,
            object_id=object_id,
        ).delete()

    def delete_queryset(self, request, queryset):
        object_ids = [str(pk) for pk in queryset.values_list('pk', flat=True)]
        super().delete_queryset(request, queryset)
        LogEntry.objects.filter(
            content_type__app_label=self.model._meta.app_label,
            content_type__model=self.model._meta.model_name,
            object_id__in=object_ids,
        ).delete()


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'inquiry_type',
        'phone',
        'related_painting',
        'created_at',
        'is_read',
    )
    list_filter = ('inquiry_type', 'is_read')
    search_fields = ('name', 'email', 'phone', 'order_details', 'message')
    list_editable = ('is_read',)
    readonly_fields = ('created_at',)


@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'whatsapp_number')

    def has_add_permission(self, request):
        return not ArtistProfile.objects.exists()