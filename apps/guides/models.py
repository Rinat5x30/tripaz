from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class GuideProfile(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    VERIFICATION_CHOICES = [
        (STATUS_PENDING, 'Pending Review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    LANGUAGE_CHOICES = [
        ('english', 'English'), ('russian', 'Russian'), ('azerbaijani', 'Azerbaijani'),
        ('turkish', 'Turkish'), ('german', 'German'), ('french', 'French'),
        ('arabic', 'Arabic'), ('chinese', 'Chinese'), ('spanish', 'Spanish'),
    ]

    CITY_CHOICES = [
        ('baku', 'Baku'), ('ganja', 'Ganja'), ('sheki', 'Sheki'),
        ('lankaran', 'Lankaran'), ('quba', 'Quba'), ('gabala', 'Gabala'),
        ('nakhchivan', 'Nakhchivan'), ('shamakhi', 'Shamakhi'), ('zagatala', 'Zagatala'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='guide_profile')
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    bio = models.TextField()
    tagline = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=50, choices=CITY_CHOICES, default='baku')
    languages = models.CharField(max_length=300, default='english', help_text='Comma-separated languages')
    experience_years = models.PositiveIntegerField(default=1)
    license_number = models.CharField(max_length=100, blank=True)
    has_certificate = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default=STATUS_PENDING)
    rejection_reason = models.TextField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0,
                                  validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_reviews = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    cover_image = models.ImageField(upload_to='guides/covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-rating', '-created_at']
        indexes = [
            models.Index(fields=['verification_status']),
            models.Index(fields=['city']),
            models.Index(fields=['rating']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f'Guide: {self.user.get_full_name() or self.user.username}'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.user.get_full_name() or self.user.username)
            if not base:
                base = f'guide-{self.user.pk}'
            slug = base
            i = 1
            qs = GuideProfile.objects.exclude(pk=self.pk) if self.pk else GuideProfile.objects.all()
            while qs.filter(slug=slug).exists():
                slug = f'{base}-{i}'
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('guides:profile', kwargs={'pk': self.pk})

    def get_languages_list(self):
        return [lang.strip() for lang in self.languages.split(',') if lang.strip()]

    @property
    def is_approved(self):
        return self.verification_status == self.STATUS_APPROVED


class VerificationDocument(models.Model):
    DOC_PASSPORT = 'passport'
    DOC_LICENSE = 'license'
    DOC_PHOTO = 'photo'

    DOC_CHOICES = [
        (DOC_PASSPORT, 'Passport'),
        (DOC_LICENSE, 'Guide License'),
        (DOC_PHOTO, 'Professional Photo'),
    ]

    guide = models.ForeignKey(GuideProfile, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=20, choices=DOC_CHOICES)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.guide} - {self.doc_type}'


class Tour(models.Model):
    CATEGORY_CHOICES = [
        ('city', 'City Tour'),
        ('historical', 'Historical'),
        ('nature', 'Nature & Outdoors'),
        ('food', 'Food & Culture'),
        ('photography', 'Photography'),
        ('adventure', 'Adventure'),
        ('day_trip', 'Day Trip'),
    ]

    guide = models.ForeignKey(GuideProfile, on_delete=models.CASCADE, related_name='tours')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='city', blank=True)
    duration_hours = models.DecimalField(max_digits=4, decimal_places=1, default=3.0)
    max_people = models.PositiveIntegerField(default=10)
    price_per_person = models.DecimalField(max_digits=8, decimal_places=2)
    location = models.CharField(max_length=200, blank=True)
    itinerary = models.TextField(blank=True, help_text='Step-by-step tour program, one step per line')
    included = models.TextField(blank=True, help_text='What is included, one item per line')
    not_included = models.TextField(blank=True, help_text='What is not included, one item per line')
    meeting_point = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['guide', 'is_active']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f'{self.title} by {self.guide}'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:180]
            if not base:
                base = 'tour'
            guide_id = self.guide_id or 'x'
            slug = f'{base}-{guide_id}'
            i = 1
            qs = Tour.objects.exclude(pk=self.pk) if self.pk else Tour.objects.all()
            while qs.filter(slug=slug).exists():
                slug = f'{base}-{guide_id}-{i}'
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('guides:tour_detail', kwargs={'pk': self.pk})

    def get_included_list(self):
        return [item.strip() for item in self.included.split('\n') if item.strip()]

    def get_not_included_list(self):
        return [item.strip() for item in self.not_included.split('\n') if item.strip()]

    def get_itinerary_lines(self):
        return [line.strip() for line in self.itinerary.split('\n') if line.strip()]


class TourImage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tours/images/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class GuidePhoto(models.Model):
    guide = models.ForeignKey(GuideProfile, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='guides/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'uploaded_at']

    def __str__(self):
        return f'Photo for {self.guide}'


class GuideAvailability(models.Model):
    guide = models.ForeignKey(GuideProfile, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ['guide', 'date']

    def __str__(self):
        return f'{self.guide} - {self.date} - {"Available" if self.is_available else "Blocked"}'


class FavoriteGuide(models.Model):
    tourist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    guide = models.ForeignKey(GuideProfile, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['tourist', 'guide']

    def __str__(self):
        return f'{self.tourist.username} → {self.guide}'
