from django.conf.urls import url
from api import views

app_name = 'public_apis'
urlpatterns = [
    url(r'^models/?$', views.get_models),
    url(r'^models/(?P<name>[^/]+)/?$', views.get_model),

    url(r'^(?P<model>[^/]+)/reactions/?$', views.get_reactions),
    url(r'^(?P<model>[^/]+)/reaction/(?P<id>[^/]+)/?$', views.get_reaction),
    url(r'^(?P<model>[^/]+)/reaction/(?P<id>[^/]+)/reactants/?$', views.get_reaction_reactants),
    url(r'^(?P<model>[^/]+)/reaction/(?P<id>[^/]+)/products/?$', views.get_reaction_products),
    url(r'^(?P<model>[^/]+)/reaction/(?P<id>[^/]+)/genes/?$', views.get_reaction_genes),

    url(r'^(?P<model>[^/]+)/genes/?$', views.get_genes),
    url(r'^(?P<model>[^/]+)/gene/(?P<id>[^/]+)/?$', views.get_gene),
    url(r'^(?P<model>[^/]+)/gene/(?P<id>[^/]+)/interaction_partners/?$', views.get_gene_interaction_partners),
    url(r'^(?P<model>[^/]+)/gene/(?P<id>[^/]+)/reactions/?$', views.get_gene_reactions),

    url(r'^(?P<model>[^/]+)/metabolites/?$', views.get_metabolites),
    url(r'^(?P<model>[^/]+)/metabolite/(?P<id>[^/]+)/?$', views.get_metabolite),
    url(r'^(?P<model>[^/]+)/metabolite/(?P<id>[^/]+)/interaction_partners/?$', views.get_metabolite_interaction_partners),
    url(r'^(?P<model>[^/]+)/metabolite/(?P<id>[^/]+)/reactions/?$', views.get_metabolite_reactions, {'all_compartment': False }),
    url(r'^(?P<model>[^/]+)/metabolite/(?P<id>[^/]+)/reactions/all_compartments/?$', views.get_metabolite_reactions_all_compartment),

    url(r'^(?P<model>[^/]+)/subsystems/?$', views.get_subsystems),
    url(r'^(?P<model>[^/]+)/subsystem/(?P<id>[^/]+)/?$', views.get_subsystem),
    url(r'^(?P<model>[^/]+)/subsystem/(?P<id>[^/]+)/reactions/?$', views.get_subsystem_reactions),

    url(r'^(?P<model>[^/]+)/compartments/?$', views.get_compartments),
    url(r'^(?P<model>[^/]+)/compartment/(?P<id>[^/]+)/?$', views.get_compartment),
]
