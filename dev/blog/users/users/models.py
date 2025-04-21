# users/models.py
from django.db import models

class Utilisateur(models.Model):
    nom = models.CharField(max_length=350)
    prenom = models.CharField(max_length=350)
    username = models.CharField(max_length=350)
    email = models.EmailField(max_length=350)

    class Meta:
        db_table = 'utilisateurs'  

    def __str__(self):
        return f"{self.prenom} {self.nom} {self.username} {self.email}"
