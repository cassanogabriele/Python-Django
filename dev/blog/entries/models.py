from django.db import models

from django.contrib.auth.models import User

class Entry(models.Model):  
    SUBJECT_CHOICES = [
        ('PHP', 'PHP'),
        ('JavaScript', 'JavaScript'),
        ('Frameworks', 'Frameworks'),
        ('CMS', 'CMS'),
        ('GIT', 'GIT'),
    ]

    entry_title = models.CharField(max_length=50)
    entry_text = models.TextField()
    entry_date = models.DateTimeField(auto_now_add=True)
    entry_author = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, default='autre')  # Champ subject

    class Meta:
      verbose_name_plural = "entries"

    def __str__(self):
     return f"{self.entry_title}"
    
class Wishlist(models.Model):
    name = models.CharField(max_length=255)  # ← Ce champ est nécessaire
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    entry = models.ForeignKey('Entry', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.entry.entry_title} dans {self.wishlist.name}"