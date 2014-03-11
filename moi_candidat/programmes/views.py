import re
import random
import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.formtools.wizard.views import CookieWizardView
from django.db.models import Count
from django.db import transaction

from programmes.models import Candidat, Proposition, Thematique, ChoixProposition, ChoixCandidat
from programmes.forms import ThematiqueForm

from moi_candidat import settings

def index(request):
    
    top_choix = ChoixProposition.objects.extra(select={'count': 'count(1)'}, 
                                    order_by=['-count']).values('count', 'proposition')[:10]
    top_choix.query.group_by = ['proposition_id']
   
    top_candidats = ChoixCandidat.objects.extra(select={'count': 'count(1)'}, 
                                    order_by=['-count']).values('count', 'candidat')[:3]
    top_candidats.query.group_by = ['candidat_id']
    context = {'top_choix': top_choix,'top_candidats': top_candidats}
    
    request.session['foo'] = 'bar' # pour initialiser la session
    return render(request, 'index.html', context)


def indexcandidat(request):
    latest_candidat_list = Candidat.objects.all().order_by('parti')[:5]
    context = {'latest_candidat_list': latest_candidat_list}
    return render(request, 'indexCandidat.html', context)


def indexproposition(request):
    latest_proposition_list = Proposition.objects.all()
    context = {'latest_proposition_list': latest_proposition_list}
    return render(request, 'indexProposition.html', context)


@transaction.commit_on_success
def resultat(request):
    chosen_props = request.session['results']

    candidats = Candidat.objects.all()
    thematiques = Thematique.objects.all()
    thematiques_total = thematiques.count()

    #sauve les choix de propositions apres avoir supprime les anciennes le cas echeant
    ancienChoixPropositions = ChoixProposition.objects.filter(session=request.session.session_key)
    for choixProp in ancienChoixPropositions:
        choixProp.delete()
        
    for prop in chosen_props:
        cp = ChoixProposition()
        cp.proposition = Proposition.objects.get(pk=prop)
        cp.origin = "ip:" + get_client_ip(request)
        cp.session = request.session.session_key
        cp.save()

    results = []
    for candidat in candidats:
        candidat_chosen_props = Proposition.objects.filter(candidat=candidat.id, id__in=chosen_props)
        props_per_candidat = candidat_chosen_props.count()
        percent = int(props_per_candidat/(thematiques_total * 1.0) * 100)
        results.append((percent, candidat, candidat_chosen_props))
    results_sorted = sorted(results, key=lambda tup: tup[0], reverse=True)
    
    # sauve le choix de candidat apres avoir supprime l'ancien le cas echeant
    ancienChoixCandidat = ChoixCandidat.objects.filter(session=request.session.session_key)
    for choixCand in ancienChoixCandidat:
        choixCand.delete()
    cc = ChoixCandidat()
    cc.candidat = results_sorted[0][1] # 1er candidat
    cc.percent = results_sorted[0][0]
    cc.origin = "ip:" + get_client_ip(request)
    cc.session = request.session.session_key
    cc.save()
        
    context = {'results': results_sorted}
    return render(request, 'resultat.html', context)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_thematique_forms():
    count = Thematique.objects.all().order_by('id').count()
    thematique_forms = [ThematiqueForm for each in range(count)]
    if not thematique_forms:
        return [ThematiqueForm]
    return thematique_forms

def programmes(request):
    candidats = Candidat.objects.all()
    thematiques = Thematique.objects.all()
    propositions = Proposition.objects.all().order_by('candidat')
    context = {'thematiques': thematiques,'candidats': candidats, 'propositions':propositions}
    return render(request, 'programme.html', context)


class ChoisirWizard(CookieWizardView):
    form_list = get_thematique_forms()
    template_name = 'choisir.html'

    def done(self, form_list, **kwargs):
        results = []
        for form in form_list:
            results.append(form.cleaned_data['proposition'])
        self.request.session['results'] = results
        
        return HttpResponseRedirect('/resultat/')

    def get_context_data(self, **kwargs):
        context = super(ChoisirWizard, self).get_context_data(**kwargs)
        form_name = str(context['form'])
        form_id_regex = re.search('name="(\d+)\-', form_name)
        form_current = int(form_id_regex.groups()[0])
        thematiques = Thematique.objects.all().order_by('id')
        for idx, t in enumerate(thematiques):
            if form_current == idx:
                if t.proposition_set:
                    propositions = list(t.proposition_set.all())
                    random.shuffle(propositions)
                    
                    #limite le nombre de propositions par candidats
                    candidats = Candidat.objects.all();
                    for candidat in candidats:
                        nbPropositions = t.proposition_set.filter(candidat__id=candidat.id).count()
                        toRemove = nbPropositions - settings.MAX_PROPOSITIONS_PER_CANDIDATES
                        if toRemove > 0: 
                            propositionsParCandidat = t.proposition_set.filter(candidat__id=candidat.id)
                            while toRemove > 0:  
                                logging.debug('thematique ' + t.nom + ', proposition supprimee ' + propositionsParCandidat[toRemove-1].resume)
                                propositions.remove(propositionsParCandidat[toRemove-1])
                                toRemove = toRemove -1
    
                context['thematique'] = t
                context['propositions'] = propositions
        return context
