from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0006_painting_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='artistprofile',
            name='tiktok_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='artistprofile',
            name='x_url',
            field=models.URLField(blank=True),
        ),
    ]
