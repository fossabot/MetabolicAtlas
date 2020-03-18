from django.conf.urls import url
from api import private_views
from api import views

app_name = 'private_apis'
urlpatterns = [
    url(r'^gems/?$', private_views.get_gemodels),
    url(r'^gems/(?P<gem_id>[^/]+)/?$', private_views.get_gemodel),

    url(r'^hpa/gene/(?P<ensembl_id>[^/]+)/?$', private_views.HPA_gene_info),
    url(r'^hpa/genes/?$', private_views.HPA_all_genes),

    url(r'^(?P<model>[^/]+)/get_id/(?P<term>[^/]+)/?$', private_views.get_id),

    url(r'^(?P<model>[^/]+)/available_maps/(?P<component_type>[^/]+)/(?P<component_id>[^/]+)/?$', private_views.get_available_maps),

    url(r'^(?P<model>[^/]+)/json/?$', private_views.get_db_json),
    url(r'^(?P<model>[^/]+)/json/compartment/(?P<component_name_id>[^/]+)/?$', private_views.get_db_json, {'ctype': 'compartment'}),
    url(r'^(?P<model>[^/]+)/json/subsystem/(?P<component_name_id>[^/]+)/?$', private_views.get_db_json, {'ctype': 'subsystem'}),
    url(r'^(?P<model>[^/]+)/json/compartment/(?P<component_name_id>[^/]+)/duplicate/?$', private_views.get_db_json, {'ctype': 'compartment', 'dup_meta': True}),
    url(r'^(?P<model>[^/]+)/json/subsystem/(?P<component_name_id>[^/]+)/duplicate/?$', private_views.get_db_json, {'ctype': 'subsystem', 'dup_meta': True}),

    url(r'^(?P<model>[^/]+)/get_reaction/(?P<id>[^/]+)/?$', private_views.get_reaction),
    url(r'^(?P<model>[^/]+)/get_reaction/(?P<id>[^/]+)/related/?$', private_views.get_related_reactions),

    url(r'^(?P<model>[^/]+)/reaction_components/(?P<id>[^/]+)/with_interaction_partners/?$', private_views.get_component_with_interaction_partners),
    url(r'^(?P<model>[^/]+)/viewer/?$', private_views.get_data_viewer),
    url(r'^(?P<model>[^/]+)/gem_browser_tiles/?$', private_views.get_tiles_data),

    url(r'^(?P<model>[^/]+)/gene/hpa_rna_levels/(?P<map_type>[^/]+)/(?P<dim>[^/]+)/(?P<name_id>[^/]+)/?$', private_views.get_hpa_rna_levels_map),
    url(r'^(?P<model>[^/]+)/gene/hpa_rna_levels/?$', private_views.get_hpa_rna_levels),
    url(r'^(?P<model>[^/]+)/gene/hpa_tissue/?$', private_views.get_hpa_tissues),

    url(r'^(?P<model>[^/]+)/gene/(?P<id>[^/]+)/get_reactions/?$', views.get_gene_reactions, {'api': False}),

    url(r'^(?P<model>[^/]+)/metabolite/(?P<id>[^/]+)/related/?$', private_views.get_related_metabolites),
    url(r'^(?P<model>[^/]+)/metabolite/(?P<id>[^/]+)/get_reactions/?$', views.get_metabolite_reactions, {'all_compartment': False, 'api': False }),
    url(r'^(?P<model>[^/]+)/metabolite/(?P<id>[^/]+)/get_reactions/all_compartments/?$', views.get_metabolite_reactions_all_compartment, {'api': False}),

    url(r'^(?P<model>[^/]+)/compartment/(?P<id>[^/]+)/summary/?$', views.get_compartment, {'api': False}),
    url(r'^(?P<model>[^/]+)/subsystem/(?P<id>[^/]+)/summary/?$', views.get_subsystem, {'api': False}),
    url(r'^(?P<model>[^/]+)/subsystem/(?P<id>[^/]+)/get_reactions/?$', views.get_subsystem_reactions, {'api': False}),

    url(r'^(?P<model>[^/]+)/search/(?P<term>[^/]+)/?$', private_views.search),
]
