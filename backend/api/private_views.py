from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Q
from django.conf import settings
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from itertools import chain
import api.models as APImodels
import api.serializers as APIserializer
import api.serializers_rc as APIrcSerializer
import api.serializers_cs as APIcsSerializer
from api.views import is_model_valid
from functools import reduce
from random import randint
import re
import logging
import json

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@api_view()
def get_gemodels(request):
    """
    List all GEMs that the group have made
    """
    # get models from database

    serializer = APIserializer.GEModelListSerializer(APImodels.GEModel.objects.all(). \
        prefetch_related('gemodelset__reference', 'ref').select_related('gemodelset', 'sample'), many=True)

    return JSONResponse(serializer.data)


@api_view()
def get_gemodel(request, gem_id):
    """
    For a given Genome-scale metabolic model ID or label, pull out everything we know about it.
    """

    try:
        int(gem_id)
        is_int = True
    except ValueError:
        is_int = False

    if is_int:
         model = APImodels.GEModel.objects.filter(id=gem_id). \
         prefetch_related('files', 'ref')
    else:
         model = APImodels.GEModel.objects.filter(tag__iexact=gem_id). \
             prefetch_related('files', 'ref')

    if not model:
        return HttpResponse(status=404)

    serializer = APIserializer.GEModelSerializer(model[0])
    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_reaction(request, model, id):
    # requested from the gem browser page
    try:
        reaction = APImodels.Reaction.objects.using(model).filter(id__iexact=id) \
            .prefetch_related('reactionreactant_set', 'reactionreactant_set__reactant',
                              'reactionproduct_set', 'reactionproduct_set__product', 'genes')
    except APImodels.Reaction.DoesNotExist:
        return HttpResponse(status=404)

    reactionserializer = APIserializer.ReactionPageSerializer(reaction[0])

    pmids = APImodels.ReactionReference.objects.using(model).filter(reaction_id=reaction[0].id)
    pmidserializer = APIserializer.ReactionReferenceSerializer(pmids, many=True)

    return JSONResponse({'reaction': reactionserializer.data,
                         'pmids': pmidserializer.data})


@api_view()
@is_model_valid
def get_related_reactions(request, model, id):
    try:
        rea = APImodels.Reaction.objects.using(model).get(id__iexact=id)
        if rea.related_group == 0:
            return HttpResponse(status=404)
        related_reactions = APImodels.Reaction.objects.using(model).filter(
            Q(related_group=rea.related_group) & ~Q(id=rea.id)) \
            .prefetch_related('reactionreactant_set', 'reactionreactant_set__reactant',
                                 'reactionproduct_set', 'reactionproduct_set__product', 'genes')
    except APImodels.Reaction.DoesNotExist:
        return HttpResponse(status=404)

    return JSONResponse(APIserializer.ReactionRTSerializer(related_reactions, many=True).data)


@api_view()
@is_model_valid
def get_id(request, model, term):
    if not term:
        return JSONResponse([])

    synonym_regex = r"(?:^" + re.escape(term) + r"(?:;|$)" + r")|(?:; " + re.escape(term) + r"(?:;|$))"
    query = Q()
    reaction_query = Q()
    query |= Q(id__iexact=term)
    reaction_query |= Q(id__iexact=term)
    reaction_query |= Q(name__iexact=term)
    reaction_query |= Q(external_databases__external_id__iexact=term)
    query |= Q(name__iexact=term)
    query |= Q(full_name__iexact=term)
    query |= Q(alt_name1__iexact=term)
    query |= Q(alt_name2__iexact=term)
    query |= Q(aliases__iregex=synonym_regex)
    query |= Q(external_databases__external_id__iexact=term)
    query |= Q(formula__iexact=term)

    # get the list of component id
    reaction_component_ids = APImodels.ReactionComponent.objects.using(model).prefetch_related('external_databases').filter(query).values_list('id', flat=True).distinct()

    # get the list of reaction id
    reaction_ids = APImodels.Reaction.objects.using(model).prefetch_related('external_databases').filter(reaction_query).values_list('id', flat=True).distinct()

    if len(reaction_component_ids) + len(reaction_ids) == 0:
        return HttpResponse(status=404)

    results = list(chain(reaction_component_ids, reaction_ids))
    return JSONResponse(results)


def fetch_map_available(results, map_type, dim, model, database, filter_condition, related_model_name, order_by, value_list_tuple):
    res = model.objects.using(database) \
         .filter(filter_condition) \
         .select_related(related_model_name) \
         .order_by(order_by) \
         .values_list(*value_list_tuple)

    if res:
        results[dim][map_type] = res
    return results


@api_view()
@is_model_valid
def get_available_maps(request, model, component_type, component_id):

    results = {
        "2d" : {
            "compartment" : [],
            "subsystem" : [],
        },
        "3d" : {
            "compartment" : [],
            "subsystem" : [],
        },
      }

    if component_type not in ['reaction', 'gene', 'metabolite', 'compartment', 'subsystem']:
        return HttpResponse(status=404)

    if component_type == 'reaction':
        try:
            reaction = APImodels.Reaction.objects.using(model).get(id__iexact=component_id)
        except APImodels.Reaction.DoesNotExist:
            return HttpResponse(status=404)

        results = fetch_map_available(results, "compartment", "2d", APImodels.ReactionCompartmentSvg, model, Q(reaction_id=reaction.id),
            "compartmentsvg", "compartmentsvg__name", ('compartmentsvg__name_id', 'compartmentsvg__name'))
        results = fetch_map_available(results, "subsystem", "2d", APImodels.ReactionSubsystemSvg, model, Q(reaction_id=reaction.id),
            "subsystemsvg", "subsystemsvg__name", ('subsystemsvg__name_id', 'subsystemsvg__name'))
        results = fetch_map_available(results, "compartment", "3d", APImodels.ReactionCompartment, model, Q(reaction_id=reaction.id),
            "compartment", "compartment__name", ('compartment__name_id', 'compartment__name'))
        results = fetch_map_available(results, "subsystem", "3d", APImodels.SubsystemReaction, model, Q(reaction_id=reaction.id),
            "subsystem", "subsystem__name", ('subsystem__name_id', 'subsystem__name'))

    elif component_type == 'gene':
        try:
            gene = APImodels.ReactionComponent.objects.using(model).get(id__iexact=component_id)
        except APImodels.ReactionComponent.DoesNotExist:
            return HttpResponse(status=404)

        results = fetch_map_available(results, "compartment", "2d", APImodels.CompartmentSvgGene, model, Q(rc_id=gene.id),
            "compartmentsvg", "compartmentsvg__name", ('compartmentsvg__name_id', 'compartmentsvg__name'))
        results = fetch_map_available(results, "subsystem", "2d", APImodels.SubsystemSvgGene, model, Q(rc_id=gene.id),
            "subsystemsvg", "subsystemsvg__name", ('subsystemsvg__name_id', 'subsystemsvg__name'))
        results = fetch_map_available(results, "compartment", "3d", APImodels.CompartmentGene, model, Q(rc_id=gene.id),
            "compartment", "compartment__name", ('compartment__name_id', 'compartment__name'))
        results = fetch_map_available(results, "subsystem", "3d", APImodels.SubsystemGene, model, Q(rc_id=gene.id),
            "subsystem", "subsystem__name", ('subsystem__name_id', 'subsystem__name'))

    elif component_type == 'metabolite':
        try:
            metabolite = APImodels.ReactionComponent.objects.using(model).get(id__iexact=component_id)
        except APImodels.ReactionComponent.DoesNotExist:
            return HttpResponse(status=404)

        results = fetch_map_available(results, "compartment", "2d", APImodels.ReactionComponentCompartmentSvg, model, Q(rc_id=metabolite.id),
            "compartmentsvg", "compartmentsvg__name", ('compartmentsvg__name_id', 'compartmentsvg__name'))
        results = fetch_map_available(results, "subsystem", "2d", APImodels.ReactionComponentSubsystemSvg, model, Q(rc_id=metabolite.id),
            "subsystemsvg", "subsystemsvg__name", ('subsystemsvg__name_id', 'subsystemsvg__name'))
        results = fetch_map_available(results, "compartment", "3d", APImodels.ReactionComponentCompartment, model, Q(rc_id=metabolite.id),
            "compartment", "compartment__name", ('compartment__name_id', 'compartment__name'))
        results = fetch_map_available(results, "subsystem", "3d", APImodels.SubsystemReactionComponent, model, Q(rc_id=metabolite.id),
            "subsystem", "subsystem__name", ('subsystem__name_id', 'subsystem__name'))

    elif component_type == 'compartment':
        try:
            compartment = APImodels.Compartment.objects.using(model).get(name_id__iexact=component_id)
        except APImodels.Compartment.DoesNotExist:
            return HttpResponse(status=404)

        results = fetch_map_available(results, "compartment", "2d", APImodels.CompartmentSvg, model, Q(compartment=compartment.id),
            None, "name", ('name_id', 'name'))
        results = fetch_map_available(results, "compartment", "3d", APImodels.Compartment, model, Q(id=compartment.id),
            None, "name", ('name_id', 'name'))

    elif component_type == 'subsystem':
        try:
            subsystem = APImodels.Subsystem.objects.using(model).get(name_id__iexact=component_id)
        except APImodels.Subsystem.DoesNotExist:
            return HttpResponse(status=404)

        results = fetch_map_available(results, "subsystem", "2d", APImodels.SubsystemSvg, model, Q(subsystem=subsystem.id) & Q(sha__isnull=False),
            None, "name", ('name_id', 'name'))
        results = fetch_map_available(results, "subsystem", "3d", APImodels.Subsystem, model, Q(id=subsystem.id),
            None, "name", ('name_id', 'name'))

    if len(results["2d"]["compartment"]) + len(results["2d"]["subsystem"]) + \
       len(results["3d"]["compartment"]) + len(results["3d"]["subsystem"]) == 0:
        # not possible ?
        return HttpResponse(status=404)

    return JSONResponse(results)


@api_view()
@is_model_valid
def get_db_json(request, model, component_name_id=None, ctype=None, dup_meta=False):
    if component_name_id:
        if ctype == 'compartment':
            try:
                compartment = APImodels.Compartment.objects.using(model).get(name_id__iexact=component_name_id)
            except APImodels.Compartment.DoesNotExist:
                return HttpResponse(status=404)

            reactions_id = APImodels.ReactionCompartment.objects.using(model). \
                filter(compartment=compartment).values_list('reaction', flat=True)
            reactions = APImodels.Reaction.objects.using(model).filter(id__in=reactions_id). \
                prefetch_related('reactants', 'products', 'genes')
        else:
            try:
                subsystem = APImodels.Subsystem.objects.using(model).get(name_id__iexact=component_name_id)
            except APImodels.Subsystem.DoesNotExist:
                return HttpResponse(status=404)

            reactions_id = APImodels.SubsystemReaction.objects.using(model). \
                filter(subsystem=subsystem).values_list('reaction', flat=True)
            reactions = APImodels.Reaction.objects.using(model).filter(id__in=reactions_id). \
                prefetch_related('reactants', 'products', 'genes')
    else:
        reactions = APImodels.Reaction.objects.using(model).all().prefetch_related('reactants', 'products', 'genes')

    nodes = {}
    links = {}
    linksList = []

    duplicateGene = True
    duplicatedEnz= {}
    duplicateMetabolite = dup_meta
    duplicatedId = {}

    duplicateMetaName = {'ATP', 'ADP', 'Pi', 'PPi', 'H2O', 'O2', 'PI pool', 'H+', \
     'NADP', 'NADP+', 'NADH', 'NAD+', 'CoA', 'NADPH', 'acetyl-CoA', 'FAD', 'FADH'}

    for r in reactions:
        reaction = {
            'g': 'r',
            'id': r.id,
            'n': r.id,
        }
        nodes[r.id] = reaction;

        for m in r.reactants.all():
            duplicateCurrentMeta = m.name in duplicateMetaName

            doMeta = True;
            metabolite = None;
            mid = m.id
            if duplicateMetabolite:
                if mid not in nodes:
                    duplicatedId[mid] = 0
                elif duplicateCurrentMeta:
                    duplicatedId[m.id] += 1
                    mid = "%s-%s" % (m.id, duplicatedId[m.id])
                else:
                    doMeta = False;

            if doMeta:
                metabolite = {
                    'g': 'm',
                    'id': mid,
                    # 'rid': m.id,
                    'n': m.name or m.alt_name1,
                }

                nodes[mid] = metabolite;

            rel = {
              #'id': mid + "-" + r.id,
              's': mid,
              't': r.id,
              #'g': 'fe',
              # 'rev': r.is_reversible,
            }
            # links[rel['id']] = rel
            linksList.append(rel)

        for m in r.products.all():
            duplicateCurrentMeta = m.name in duplicateMetaName

            doMeta = True;
            metabolite = None
            mid = m.id;
            if duplicateMetabolite:
                if mid not in nodes:
                    duplicatedId[mid] = 0
                elif duplicateCurrentMeta:
                    duplicatedId[m.id] += 1
                    mid = "%s-%s" % (m.id, duplicatedId[m.id])
                else:
                    doMeta = False

            if doMeta:
                metabolite = {
                    'g': 'm',
                    'id': mid,
                    #'rid': m.id,
                    'n': m.name or m.alt_name1 or mid,
                }

                nodes[mid] = metabolite

            rel = {
              #'id': r.id + "-" + mid,
              's': r.id,
              't': mid,
              #'g': 'fe',
              # 'rev': r.is_reversible,
            }
            # links[rel['id']] = rel
            linksList.append(rel)

        for e in r.genes.all():
            eid = "%s-0" % (e.id)
            if eid in nodes:
                duplicatedEnz[eid] += 1;
                eid = "%s-%s" % (eid, duplicatedEnz[eid])
            else:
                duplicatedEnz[eid] = 0;
                # eid = "%s-%s" % (eid, duplicatedEnz[eid])

            gene = {
              'id': eid,
              'g': 'e',
              'n': e.name or e.alt_name1 or e.id,
            }
            nodes[eid] = gene;

            rel = {
              #'id': eid + "-" + r.id,
              's': eid,
              't': r.id,
              #'g': 'ee',
              # 'rev': r.is_reversible,
            }
            # links[rel['id']] = rel
            linksList.append(rel)

    results = {
        'nodes': [v for k, v in nodes.items()],
        # 'links': [v for k, v in links.items()],
        'links': linksList
    }

    return JSONResponse(results)


#####################################################################################

@api_view()
def HPA_all_genes(request):
    model = "human1"
    result = APImodels.SubsystemGene.objects.using(model).values_list('rc__id', 'subsystem__name','subsystem__name_id')
    return JSONResponse(result)

@api_view()
def HPA_gene_info(request, ensembl_id): # ENSG00000110921
    model = "human1"

    # l = logging.getLogger('django.db.backends')
    # l.setLevel(logging.DEBUG)
    # l.addHandler(logging.StreamHandler())

    try:
        res = APImodels.ReactionComponent.objects.using(model).get(id=ensembl_id)
        rcid = res.id
    except APImodels.ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    subs = APImodels.Subsystem.objects.using(model).filter(
            Q(id__in=APImodels.SubsystemGene.objects.using(model).filter(rc_id=rcid).values('subsystem_id')) &
            ~Q(system='Collection of reactions')
        ).select_related('subsystem_svg').prefetch_related('reactions', 'compartment', 'genes')

    subsystems = []
    for sub in subs.all():
        sub_dict = {}
        # get the reactions
        sub_dict['name'] = sub.name
        sub_dict['compartments'] = sub.compartment.values_list('name', flat=True)
        sub_dict['genes'] = sub.genes.all().values_list('id', flat=True)
        # sub['compartments'] = list(compartments)
        sub_dict['reactions_catalysed'] = APImodels.ReactionGene.objects.using(model).filter(Q(reaction__in=sub.reactions.all()) & Q(gene_id=rcid)).count()
        if sub.subsystem_svg.sha:
            sub_dict['map_url'] = "https://ftp.metabolicatlas.org/.maps/%s/%s.svg" % (model, sub.name_id)
        else:
            sub_dict['map_url'] = ""
        sub_dict['subsystem_url'] = "https://www.metabolicatlas.org/explore/gem-browser/%s/subsystem/%s" % (model, sub.name_id)
        sub_dict['model_metabolite_count'] = sub.unique_metabolite_count
        sub_dict['compartment_metabolite_count'] = sub.metabolite_count
        sub_dict['reaction_count'] = sub.reaction_count
        sub_dict['gene_count'] = sub.gene_count

        subsystems.append(sub_dict)

    result = {
        'gene_url': "https://www.metabolicatlas.org/explore/gem-browser/%s/gene/%s" % (model, ensembl_id),
        'subsystems': subsystems,
        'doc': 'A subsystem can contain the same chemical metabolite that comes from different compartments.',
    }

    return JSONResponse(result)


#########################################################################################

@api_view()
@is_model_valid
def get_data_viewer(request, model):
    try:
        compartments = APImodels.Compartment.objects.using(model).all()
    except APImodels.Compartment.DoesNotExist:
        return HttpResponse(status=404)

    try:
        compartments_svg = APImodels.CompartmentSvg.objects.using(model).select_related('compartment').all()
    except APImodels.CompartmentSvg.DoesNotExist:
        return HttpResponse(status=404)

    try:
        subsystems = APImodels.Subsystem.objects.using(model).all().prefetch_related('compartment')
    except APImodels.Subsystem.DoesNotExist:
        return HttpResponse(status=404)

    try:
        subsystems_svg = APImodels.SubsystemSvg.objects.using(model).select_related('subsystem').all()
    except APImodels.SubsystemSvg.DoesNotExist:
        return HttpResponse(status=404)

    return JSONResponse({
            'subsystem': APIcsSerializer.SubsystemMapViewerSerializer(subsystems, many=True).data,
            'subsystemsvg': APIcsSerializer.SubsystemSvgSerializer(subsystems_svg, many=True).data,
            'compartment':  APIcsSerializer.CompartmentMapViewerSerializer(compartments, many=True).data,
            'compartmentsvg': APIcsSerializer.CompartmentSvgSerializer(compartments_svg, many=True).data
        })

##########################################################################################

@api_view()
@is_model_valid
def get_tiles_data(request, model):
    compartment_count = APImodels.Compartment.objects.using(model).all().count()
    random_index = randint(0, compartment_count - 1)
    compartment = APImodels.Compartment.objects.using(model).all()[random_index]

    subsystem_count = APImodels.Subsystem.objects.using(model).all().count()
    random_index = randint(0, subsystem_count - 1)
    subsystem1 = APImodels.Subsystem.objects.using(model).all()[random_index]

    random_index = randint(0, subsystem_count - 1)
    subsystem2 = APImodels.Subsystem.objects.using(model).all()[random_index]

    reaction_count = APImodels.Reaction.objects.using(model).all().count()
    random_index = randint(0, reaction_count - 1)
    reaction1 = APImodels.Reaction.objects.using(model).all()[random_index]

    random_index = randint(0, reaction_count - 1)
    reaction2 = APImodels.Reaction.objects.using(model).all()[random_index]

    metabolite_count = APImodels.Metabolite.objects.using(model).all().count()
    random_index = randint(0, metabolite_count - 1)
    metabolite1 = APImodels.Metabolite.objects.using(model).all()[random_index].rc

    random_index = randint(0, metabolite_count - 1)
    metabolite2 = APImodels.Metabolite.objects.using(model).all()[random_index].rc

    gene_count = APImodels.Gene.objects.using(model).all().count()
    gene_count = APImodels.ReactionComponent.objects.using(model).filter(component_type='e').count()
    random_index = randint(0, gene_count - 1)
    gene1 = APImodels.ReactionComponent.objects.using(model).filter(component_type='e')[random_index]

    random_index = randint(0, gene_count - 1)
    gene2 = APImodels.ReactionComponent.objects.using(model).filter(component_type='e')[random_index]

    res = APImodels.GemBrowserTile(compartment, [subsystem1, subsystem2], [reaction1, reaction2], [metabolite1, metabolite2], [gene1, gene2])
    return JSONResponse(APIserializer.GemBrowserTileSerializer(res).data)


@api_view()
@is_model_valid
def get_component_with_interaction_partners(request, model, id):
    """
    Get the annotation + interaction partners for a given reaction component,
    supply an id (for example M_m01954g or E_3640)
    """
    try:
        component = APImodels.ReactionComponent.objects.using(model).get(Q(id__iexact=id) | Q(full_name__iexact=id))
    except APImodels.ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    component_serializer = APIrcSerializer.ReactionComponentBasicSerializer(component)
    c = {}
    c.update(component_serializer.data)
    c['type'] = 'metabolite' if component.component_type == 'm' else 'gene';

    reactions = None
    if component.component_type == 'm':
        reactions = component.reactions_as_metabolite. \
        prefetch_related('subsystem', 'reactants', 'products', 'genes').all()

    else:
        reactions = component.reactions_as_gene. \
        prefetch_related('subsystem', 'reactants', 'products', 'genes').all()

    if len(reactions) > 200:
        result = {
             'component': c,
             'reactions': None
         }

        return JSONResponse(result)

    reactions_serializer = APIserializer.InteractionPartnerSerializer(reactions, many=True)
    result = {
        'component': c,
        'reactions': reactions_serializer.data
    }

    return JSONResponse(result)

##########################################################################################

@api_view()
@is_model_valid
def get_hpa_tissues(request, model):
    tissues = APImodels.HpaTissue.objects.using(model).all().values_list('tissue', flat=True)
    return JSONResponse(tissues)


@api_view()
@is_model_valid
def get_hpa_rna_levels_map(request, model, map_type, dim, name_id):
    if map_type == "compartment":
        if dim == "2d":
            try:
                compartment = APImodels.CompartmentSvg.objects.using(model).get(name_id__iexact=name_id)
            except APImodels.CompartmentSvg.DoesNotExist:
                return HttpResponse(status=404)
            levels = APImodels.HpaProteinLevel.objects.using(model). \
                filter(rc__in=APImodels.CompartmentSvgGene.objects.filter(compartmentsvg=compartment).values('rc')).values_list('rc_id', 'levels')
        elif dim == "3d":
            try:
                compartment = APImodels.Compartment.objects.using(model).get(name_id__iexact=name_id)
            except APImodels.Compartment.DoesNotExist:
                return HttpResponse(status=404)
            levels = APImodels.HpaProteinLevel.objects.using(model). \
                filter(rc__in=APImodels.CompartmentGene.objects.filter(compartment=compartment).values('rc')).values_list('rc_id', 'levels')
        else:
            return HttpResponse(status=404)
    elif map_type == "subsystem":
        if dim == "2d":
            try:
                subsystem = APImodels.SubsystemSvg.objects.using(model).get(name_id__iexact=name_id)
            except APImodels.SubsystemSvg.DoesNotExist:
                return HttpResponse(status=404)
            levels = APImodels.HpaProteinLevel.objects.using(model). \
                filter(rc__in=APImodels.SubsystemSvgGene.objects.filter(subsystemsvg=subsystem).values('rc')).values_list('rc_id', 'levels')
        elif dim == "3d":
            try:
                subsystem = APImodels.Subsystem.objects.using(model).get(name_id__iexact=name_id)
            except APImodels.Subsystem.DoesNotExist:
                return HttpResponse(status=404)
            levels = APImodels.HpaProteinLevel.objects.using(model). \
                filter(rc__in=APImodels.SubsystemGene.objects.filter(subsystem=subsystem).values('rc')).values_list('rc_id', 'levels')
        else:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=404)

    tissues = APImodels.HpaTissue.objects.using(model).all().values_list('tissue', flat=True)
    return JSONResponse(
        {
          'tissues': tissues,
          'levels': levels
        })


@api_view(['POST'])
@is_model_valid
def get_hpa_rna_levels(request, model):
    ensemblIDs = [el.strip() for el in request.data['data'] if len(el) != 0]
    if not ensemblIDs:
        return HttpResponse(status=404)

    levels = APImodels.HpaProteinLevel.objects.using(model).filter(rc__in=ensemblIDs).values_list('rc_id', 'levels')
    tissues = APImodels.HpaTissue.objects.using(model).all().values_list('tissue', flat=True)

    return JSONResponse(
        {
          'tissues': tissues,
          'levels': levels
        })


@api_view()
@is_model_valid
def get_related_metabolites(request, model, id):
    try:
        met = APImodels.ReactionComponent.objects.using(model).get(id__iexact=id)
        if met.related_compartment_group == 0:
            return HttpResponse(status=404)
        related_mets = APImodels.ReactionComponent.objects.using(model).filter(
            Q(related_compartment_group=met.related_compartment_group) & ~Q(id=met.id)).values('id', 'full_name', 'compartment_str')
    except APImodels.ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    return JSONResponse(related_mets)


@api_view()
def search(request, model, term):
    """
        Searches for the term in metabolites, genes, reactions, subsystems and compartments.
        Current search rules:

        =: exact match, case insensitive
        ~: contain in, case insensitive

        compartment:
            ~name
        subsystem:
            ~name
            =external_ids
        reaction:
            =id
            ~name
            ~equation
            ~name_equation
            ~ec
            =external_ids
        metabolite:
            =id
            ~full_name
            ~alt_name1
            ~alt_name2
            ~aliases
            =external_ids
            ~formula
        gene:
            same as metabolite, but name instead of full_name
            (genes do not have formula)
    """

    # l = logging.getLogger('django.db.backends')
    # l.setLevel(logging.DEBUG)
    # l.addHandler(logging.StreamHandler())

    term = term.replace(";", "#") # to avoid match list of aliases
    term = term.strip()

    if len(term) < 2:
        return HttpResponse("Invalid query, term must be at least 2 characters long", status=400)

    results = {}
    quickSearch = model != 'all'
    if not quickSearch:
        models = [k for k in settings.DATABASES if k not in ['default', 'gems']]
        limit = 10000
    else:
        models = [model]
        limit = 50

    # iterate on GEMs (databases might be empty)
    filtered_models = []
    for model_db_name in models:
        try:
            m = APImodels.GEM.objects.get(database_name=model_db_name)
            filtered_models.append(m)
        except APImodels.GEM.DoesNotExist:
            return HttpResponse("Invalid model name '%s'" % model, status=404)
    models = filtered_models

    match_found = False
    for modelData in models:
        model = modelData.database_name
        model_short_name = modelData.short_name
        if model not in results:
            results[model] = {}

        term = term.replace("→", "=>")
        term = term.replace("⇒", "=>")
        term = term.replace("⇔", "=>")
        term = term.replace("->", "=>")

        reactions = APImodels.Reaction.objects.using(model).none()
        metabolites = APImodels.ReactionComponent.objects.using(model).none()
        genes = APImodels.ReactionComponent.objects.using(model).none()
        compartments = APImodels.Compartment.objects.using(model).none()
        subsystems = APImodels.Subsystem.objects.using(model).none()

        if '=>' in term and term.count('=>') == 1:
            if not term.strip() == '=>':
                dr = {}
                reactants, products = term.split('=>')
                reactants_mets_terms = [rm.strip() for rm in reactants.split(" + ") if rm.strip()]
                if reactants_mets_terms:
                    reactants = APImodels.ReactionComponent.objects.using(model).filter(
                        Q(component_type__exact='m') &
                        (reduce(lambda x, y: x | y, [Q(id__iexact=w) for w in reactants_mets_terms]) |
                        reduce(lambda x, y: x | y, [Q(name__iexact=w) for w in reactants_mets_terms]) |
                        reduce(lambda x, y: x | y, [Q(full_name__iexact=w) for w in reactants_mets_terms]))
                    )
                    # convert into dicts of list
                    for m in reactants:
                        if m.name not in dr:
                            dr[m.name] = []
                        dr[m.name].append(m.id)

                dp = {}
                products_mets_terms = [pm.strip() for pm in products.split(" + ") if pm.strip()]
                if products_mets_terms:
                    products = APImodels.ReactionComponent.objects.using(model).filter(
                        Q(component_type__exact='m') &
                        (reduce(lambda x, y: x | y, [Q(id__iexact=w) for w in products_mets_terms]) |
                        reduce(lambda x, y: x | y, [Q(name__iexact=w) for w in products_mets_terms]) |
                        reduce(lambda x, y: x | y, [Q(full_name__iexact=w) for w in products_mets_terms]))
                    )
                    # convert into dicts of list
                    for m in products:
                        if m.name not in dp:
                            dp[m.name] = []
                        dp[m.name].append(m.id)

                if dr and len(dr) == len(reactants_mets_terms) and dp and len(dp) == len(products_mets_terms):
                    reactions = APImodels.Reaction.objects.using(model) \
                    .prefetch_related('subsystem', 'compartment').filter(
                        reduce(lambda x, y: x & y, [Q(id__in=APImodels.ReactionReactant.objects.filter(reactant_id__in=l) \
                            .values_list('reaction_id', flat=True)) for l in dr.values()]), \
                        reduce(lambda x, y: x & y, [Q(id__in=APImodels.ReactionProduct.objects.filter(product_id__in=l) \
                            .values_list('reaction_id', flat=True)) for l in dp.values()]), \
                        )[:limit]
                    if set((r.id for r in reactants)) != set((p.id for p in products)) and len(reactions) < limit:
                        reactions_rev = APImodels.Reaction.objects.using(model) \
                        .prefetch_related('subsystem', 'compartment').filter(Q(is_reversible=True) &
                            reduce(lambda x, y: x & y, [Q(id__in=APImodels.ReactionReactant.objects.filter(reactant_id__in=l) \
                                .values_list('reaction_id', flat=True)) for l in dp.values()]), \
                            reduce(lambda x, y: x & y, [Q(id__in=APImodels.ReactionProduct.objects.filter(product_id__in=l) \
                                .values_list('reaction_id', flat=True)) for l in dr.values()]), \
                            )[:(limit - len(reactions))]
                        reactions = list(chain(reactions, reactions_rev))
                elif dr and len(dr) == len(reactants_mets_terms) and not products_mets_terms:
                    reactions = APImodels.Reaction.objects.using(model) \
                    .prefetch_related('subsystem', 'compartment').filter(
                        reduce(lambda x, y: x & y, [Q(id__in=APImodels.ReactionReactant.objects.filter(reactant_id__in=l) \
                            .values_list('reaction_id', flat=True)) for l in dr.values()]) \
                        )[:limit]
                    if len(reactions) < limit:
                        reactions_rev = APImodels.Reaction.objects.using(model) \
                        .prefetch_related('subsystem', 'compartment').filter(Q(is_reversible=True) &
                            reduce(lambda x, y: x & y, [Q(id__in=APImodels.ReactionProduct.objects.filter(product_id__in=l) \
                                .values_list('reaction_id', flat=True)) for l in dr.values()]) \
                            )[:(limit - len(reactions))]
                        reactions = list(chain(reactions, reactions_rev))
                elif dp and len(dp) == len(products_mets_terms) and not reactants_mets_terms:
                    reactions = APImodels.Reaction.objects.using(model) \
                    .prefetch_related('subsystem', 'compartment').filter(
                        reduce(lambda x, y: x & y, [Q(id__in=APImodels.ReactionProduct.objects.filter(product_id__in=l) \
                            .values_list('reaction_id', flat=True)) for l in dp.values()]) \
                        )[:limit]
                    if len(reactions) < limit:
                        reactions_rev = APImodels.Reaction.objects.using(model) \
                        .prefetch_related('subsystem', 'compartment').filter(Q(is_reversible=True) &
                            reduce(lambda x, y: x & y, [Q(id__in=APImodels.ReactionReactant.objects.filter(reactant_id__in=l) \
                                .values_list('reaction_id', flat=True)) for l in dp.values()]) \
                            )[:(limit - len(reactions))]
                        reactions = list(chain(reactions, reactions_rev))

        elif " + " in term:
            mets_terms = [m.strip() for m in term.split(" + ") if m.strip()]
            if mets_terms:
                mets = APImodels.ReactionComponent.objects.using(model).filter(
                    Q(component_type__exact='m') &
                    (reduce(lambda x, y: x | y, [Q(id__iexact=w) for w in mets_terms]) |
                    reduce(lambda x, y: x | y, [Q(name__iexact=w) for w in mets_terms]) |
                    reduce(lambda x, y: x | y, [Q(full_name__iexact=w) for w in mets_terms]))
                ).distinct()
                d = {}
                for m in mets:
                    if m.name not in d:
                        d[m.name] = []
                    d[m.name].append(m.id)

                if len(d) == len(mets_terms):
                    reactions = APImodels.Reaction.objects.using(model).filter(
                        reduce(lambda x, y: x & y, [Q(id__in=APImodels.ReactionMetabolite.objects.filter(rc_id__in=l).values_list('reaction_id', flat=True)) \
                         for l in d.values()])).prefetch_related('subsystem', 'compartment')[:limit]

        else:
            synonym_regex = r"(?:^" + re.escape(term) + r"(?:;|$)" + r")|(?:; " + re.escape(term) + r"(?:;|$))"
            compartments = APImodels.Compartment.objects.using(model).filter(
                Q(name_id__iexact=term) |
                Q(name__icontains=term)
            )[:limit]

            subsystems = APImodels.Subsystem.objects.using(model).prefetch_related('compartment').filter(
                Q(name_id__iexact=term) |
                Q(name__icontains=term) |
                Q(id__in=APImodels.SubsystemEID.objects.using(model).filter(external_id__iexact=term).values('subsystem'))
            )[:limit]

            metabolites = APImodels.ReactionComponent.objects.using(model).select_related('metabolite'). \
            prefetch_related('subsystem_metabolite', 'compartment').filter(
                Q(component_type__exact='m') &
                (Q(id__iexact=term) |
                Q(full_name__icontains=term) |
                Q(alt_name1__icontains=term) |
                Q(alt_name2__icontains=term) |
                Q(aliases__iregex=synonym_regex) |
                Q(formula__icontains=term) |
                Q(id__in=APImodels.ReactionComponentEID.objects.using(model).filter(external_id__iexact=term).values('rc')))
            )[:limit]

            exact_metabolites = APImodels.ReactionComponent.objects.using(model).filter(
                Q(component_type__exact='m') &
                (Q(id__iexact=term) |
                Q(name__iexact=term) |
                Q(full_name__iexact=term))
            )

            reactions = APImodels.Reaction.objects.using(model).prefetch_related('subsystem', 'compartment').filter(
                Q(id__iexact=term) |
                Q(name__icontains=term) |
                Q(ec__icontains=term) |
                Q(id__in=APImodels.ReactionEID.objects.using(model).filter(external_id__iexact=term).values('reaction'))
            )[:limit]

            if len(exact_metabolites) and len(reactions) < limit:
                reactions_mets = APImodels.Reaction.objects.using(model).prefetch_related('subsystem', 'compartment').distinct().filter(
                    Q(metabolites__in=exact_metabolites) & ~Q(id__in=reactions))[:(limit - len(reactions))]
                reactions = list(chain(reactions, reactions_mets))

            genes = APImodels.ReactionComponent.objects.using(model).select_related('gene'). \
            prefetch_related('subsystem_gene', 'compartment_gene').filter(
                Q(component_type__exact='e') &
                (Q(id__iexact=term) |
                Q(name__icontains=term) |
                Q(alt_name1__icontains=term) |
                Q(alt_name2__icontains=term) |
                Q(aliases__iregex=synonym_regex) |
                Q(id__in=APImodels.ReactionComponentEID.objects.using(model).filter(external_id__iexact=term).values('rc')))
            )[:limit]

        if (len(metabolites) or len(genes) or len(compartments) or len(subsystems) + len(reactions)) != 0:
            match_found = True

        MetaboliteSerializerClass = APIrcSerializer.ReactionComponentLiteSerializer if quickSearch else APIrcSerializer.MetaboliteSearchSerializer
        GeneSerializerClass = APIrcSerializer.ReactionComponentBasicSerializer if quickSearch else APIrcSerializer.GeneSearchSerializer
        ReactionSerializerClass = APIserializer.ReactionBasicSerializer if quickSearch else APIserializer.ReactionSearchSerializer
        SubsystemSerializerClass = APIcsSerializer.SubsystemBasicSerializer if quickSearch else APIcsSerializer.SubsystemSearchSerializer
        CompartmentSerializerClass = APIcsSerializer.CompartmentBasicSerializer if quickSearch else APIcsSerializer.CompartmentSerializer

        metaboliteSerializer = MetaboliteSerializerClass(metabolites, many=True)
        geneSerializer = GeneSerializerClass(genes, many=True)
        compartmentSerializer = CompartmentSerializerClass(compartments, many=True)
        subsystemSerializer = SubsystemSerializerClass(subsystems, many=True)
        reactionSerializer = ReactionSerializerClass(reactions, many=True)

        results[model]['metabolite'] = metaboliteSerializer.data
        results[model]['gene'] = geneSerializer.data
        results[model]['compartment'] = compartmentSerializer.data
        results[model]['subsystem'] = subsystemSerializer.data
        results[model]['reaction'] = reactionSerializer.data
        results[model]['name'] = model_short_name

        response = JSONResponse(results)

    if not match_found:
        term = term.lower()
        if len(term) > 4:
            mismatch_for_name = 3
        else:
            mismatch_for_name = 1 if len(term) < 3 else 2

        suggestions = []
        # search for similar results using levenshtein string distance function
        # allow a distance of 3 or less depending on the field
        # limit to 10 suggestions in total
        for modelData in models:
            model = modelData.database_name
            compartment_name = APImodels.Compartment.objects.using(model).raw('SELECT id, name from compartment where levenshtein_less_equal(\'%s\', LOWER(name), %d) <= %d limit 10' % (term, mismatch_for_name, mismatch_for_name))

            subsystem_name = APImodels.Subsystem.objects.using(model).raw('SELECT id, name from subsystem where levenshtein_less_equal(\'%s\', LOWER(name), %d) <= %d limit 10' % (term, mismatch_for_name, mismatch_for_name))
            subsystem_eid = APImodels.SubsystemEID.objects.using(model).raw('SELECT id, external_id from subsystem_eid where levenshtein_less_equal(\'%s\', LOWER(external_id), 2) <= 2 limit 10' % term)

            reaction_component_id = APImodels.ReactionComponent.objects.using(model).raw(
                'SELECT id, id from reaction_component where levenshtein_less_equal(\'%s\', LOWER(id), 1) <= 1' % term)
            reaction_component_name = APImodels.ReactionComponent.objects.using(model).raw(
                'SELECT id, name from reaction_component where levenshtein_less_equal(\'%s\', LOWER(name), %d) <= %d' % (term, mismatch_for_name, mismatch_for_name))
            reaction_component_formula = APImodels.ReactionComponent.objects.using(model).raw(
                'SELECT id, formula from reaction_component where levenshtein_less_equal(\'%s\', LOWER(formula), %d) <= %d' % (term, mismatch_for_name, mismatch_for_name))
            reaction_component_eid = APImodels.ReactionComponentEID.objects.using(model).raw(
                'SELECT id, external_id from rc_eid where levenshtein_less_equal(\'%s\', LOWER(external_id), 2) <= 2 limit 10' % term)

            reaction_id = APImodels.Reaction.objects.using(model).raw('SELECT id, id from reaction where levenshtein_less_equal(\'%s\', LOWER(id), 1) <= 1 limit 10' % term)
            reaction_name = APImodels.Reaction.objects.using(model).raw('SELECT id, name from reaction where levenshtein_less_equal(\'%s\', LOWER(name), %d) <= %d limit 10' % (term, mismatch_for_name, mismatch_for_name))
            reaction_eid = APImodels.ReactionEID.objects.using(model).raw('SELECT id, external_id from reaction_eid where levenshtein_less_equal(\'%s\', LOWER(external_id), 2) <= 2 limit 10' % term)

            suggestions += [c.name for c in compartment_name] \
                + [s.name for s in subsystem_name] \
                + [rc.id for rc in reaction_component_id] \
                + [rc.name for rc in reaction_component_name] \
                + [rc.formula for rc in reaction_component_formula] \
                + [rc.external_id for rc in reaction_component_eid] \
                + [r.id for r in reaction_id] \
                + [r.name for r in reaction_name] \
                + [r.external_id for r in reaction_eid] \
                + [s.external_id for s in subsystem_eid]

        response = HttpResponse(status=404)
        response['suggestions'] = json.dumps(list(set([s for s in suggestions if s]))[:10])
        return response

    return response
