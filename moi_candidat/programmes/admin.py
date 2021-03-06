from django.contrib import admin
from programmes.models import Parti, Candidat, Thematique, Proposition


class CandidatAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'parti_list')
    fields = (('nom', 'prenom'), 'bio', 'partis', 'photo')


class PropositionAdmin(admin.ModelAdmin):
    list_display = ('resume', 'source', 'candidat', 'thematique', 'published')

admin.site.register(Parti)
admin.site.register(Candidat,CandidatAdmin)
admin.site.register(Thematique)
admin.site.register(Proposition, PropositionAdmin)
