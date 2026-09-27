from django.db import models

class Painting(models.Model):
    CATEGORY_CHOICES = [
        ('wanyama', 'Wanyama'),
        ('traditional', 'Traditional'),
        ('other', 'Nyingine'),
    ]

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='paintings/')
    video = models.FileField(upload_to='paintings/videos/', blank=True, null=True, help_text='Video ya hiari (mfano: process ya kuchora)')
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    medium = models.CharField(max_length=100, blank=True, help_text="Mfano: Acrylic on canvas")
    size = models.CharField(max_length=100, blank=True, help_text="Mfano: 60cm x 80cm")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Onyesha kwenye Home page")
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    message = models.TextField()
    related_painting = models.ForeignKey(
        Painting, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d/%m/%Y')}"


class ArtistProfile(models.Model):
    name = models.CharField(max_length=150)
    bio = models.TextField()
    photo = models.ImageField(upload_to='profile/', blank=True, null=True)
    whatsapp_number = models.CharField(
        max_length=20, help_text="Mfano: 255712345678 (bila + au 0 mwanzoni)"
    )
    instagram_url = models.URLField(blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
