from django.db import models

class Podcast(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    audio_file = models.FileField(upload_to='podcasts/')
    cover_image = models.ImageField(upload_to='podcasts_covers/')
    date_created = models.DateTimeField(auto_now_add=True)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title
