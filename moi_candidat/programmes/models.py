# -*- coding: utf-8 -*-
from django.db import models


class Parti(models.Model):
    nom = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.nom


class Candidat(models.Model):
    nom = models.CharField(max_length=200)
    prenom = models.CharField(u'prénom', max_length=200)
    bio = models.TextField(blank=True)
    photo = models.FileField(upload_to='candidats', blank=True)
    partis = models.ManyToManyField(Parti)

    def __unicode__(self):
        return self.nom + ' ' + self.prenom

    def parti_list(self):
        partis = [p.nom for p in self.partis.all()]
        return ", ".join(partis)
    parti_list.short_description = 'Partis'


class Thematique(models.Model):
    nom = models.CharField(max_length=200)
    #image = models.FileField(upload_to='thematiques', blank=True)
    
    class Meta:
        verbose_name = u'thématique'

    def __unicode__(self):
        return self.nom


class Proposition(models.Model):
    resume = models.TextField(u'résumé',max_length=5000)
    description = models.TextField(max_length=20000,blank=True)
    source = models.TextField(max_length=255,blank=True)
    thematique = models.ForeignKey(Thematique, verbose_name=u'thématique')
    candidat = models.ForeignKey(Candidat)
    published = models.BooleanField(default=True, verbose_name=u'publié')

    def __unicode__(self):
        return self.resume
    
class ChoixProposition(models.Model):
    creation = models.DateField(auto_now_add=True)
    session = models.CharField(max_length=255,blank=True)
    origin = models.CharField(max_length=255,blank=True)
    proposition = models.ForeignKey(Proposition)

    def __unicode__(self):
        return self.proposition.resume + ' at ' + self.creation

class ChoixCandidat(models.Model):
    creation = models.DateField(auto_now_add=True)
    session = models.CharField(max_length=255,blank=True)
    origin = models.CharField(max_length=255,blank=True)
    candidat = models.ForeignKey(Candidat)
    percent = models.DecimalField(max_digits=4, decimal_places=2,blank=True)

    def __unicode__(self):
        return self.candidat + ' at ' + self.creation
