from django.db import models


class Candidat(models.Model):
    nom = models.CharField(max_length=200)
    parti = models.CharField(max_length=200)

class Thematique(models.Model):
    nom = models.CharField(max_length=200)

class Proposition(models.Model):
    resume = models.TextField()
    description = models.TextField()
    thematique = models.ForeignKey(Thematique)
    candidat = models.ForeignKey(Candidat)