from django.conf import settings
from django.db import migrations, models
from django.utils.text import slugify


def generate_guide_slugs(apps, schema_editor):
    GuideProfile = apps.get_model('guides', 'GuideProfile')
    seen = set()
    for guide in GuideProfile.objects.select_related('user').all():
        full_name = f'{guide.user.first_name} {guide.user.last_name}'.strip()
        name = full_name or guide.user.username
        base = slugify(name) or f'guide-{guide.pk}'
        slug = base
        i = 1
        while slug in seen or GuideProfile.objects.filter(slug=slug).exclude(pk=guide.pk).exists():
            slug = f'{base}-{i}'
            i += 1
        seen.add(slug)
        guide.slug = slug
        guide.save(update_fields=['slug'])


def generate_tour_slugs(apps, schema_editor):
    Tour = apps.get_model('guides', 'Tour')
    seen = set()
    for tour in Tour.objects.all():
        base = slugify(tour.title)[:180] or 'tour'
        slug = f'{base}-{tour.guide_id}'
        i = 1
        while slug in seen or Tour.objects.filter(slug=slug).exclude(pk=tour.pk).exists():
            slug = f'{base}-{tour.guide_id}-{i}'
            i += 1
        seen.add(slug)
        tour.slug = slug
        tour.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('guides', '0003_rename_price_per_hour_guideprofile_base_price_per_person'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add slug as nullable first, then populate, then enforce unique
        migrations.AddField(
            model_name='guideprofile',
            name='slug',
            field=models.SlugField(blank=True, max_length=150, null=True),
        ),
        migrations.RunPython(generate_guide_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='guideprofile',
            name='slug',
            field=models.SlugField(blank=True, max_length=150, unique=True),
        ),
        migrations.AddField(
            model_name='tour',
            name='category',
            field=models.CharField(blank=True, choices=[('city', 'City Tour'), ('historical', 'Historical'), ('nature', 'Nature & Outdoors'), ('food', 'Food & Culture'), ('photography', 'Photography'), ('adventure', 'Adventure'), ('day_trip', 'Day Trip')], default='city', max_length=30),
        ),
        migrations.AddField(
            model_name='tour',
            name='included',
            field=models.TextField(blank=True, help_text='What is included, one item per line'),
        ),
        migrations.AddField(
            model_name='tour',
            name='location',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='tour',
            name='not_included',
            field=models.TextField(blank=True, help_text='What is not included, one item per line'),
        ),
        migrations.AddField(
            model_name='tour',
            name='slug',
            field=models.SlugField(blank=True, max_length=220, null=True),
        ),
        migrations.RunPython(generate_tour_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='tour',
            name='slug',
            field=models.SlugField(blank=True, max_length=220, unique=True),
        ),
        migrations.AlterField(
            model_name='tour',
            name='itinerary',
            field=models.TextField(blank=True, help_text='Step-by-step tour program, one step per line'),
        ),
        migrations.AddIndex(
            model_name='guideprofile',
            index=models.Index(fields=['slug'], name='guides_guid_slug_866487_idx'),
        ),
        migrations.AddIndex(
            model_name='tour',
            index=models.Index(fields=['guide', 'is_active'], name='guides_tour_guide_i_5395fe_idx'),
        ),
        migrations.AddIndex(
            model_name='tour',
            index=models.Index(fields=['slug'], name='guides_tour_slug_b4b0e9_idx'),
        ),
    ]
