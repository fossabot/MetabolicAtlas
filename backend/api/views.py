from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from itertools import chain
from rest_framework import permissions
import api.models as APImodels
import api.serializers as APIserializer
import api.serializers_rc as APIrcSerializer
import api.serializers_cs as APIcsSerializer
import requests
import logging
import functools

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def is_model_valid(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        model = kwargs.get('model')
        if not model:
            model = args.get('model')
        try:
            m = APImodels.GEM.objects.get(Q(database_name=model) | Q(short_name__iexact=model))
            kwargs['model'] = m.database_name
        except APImodels.GEM.DoesNotExist:
            return HttpResponse("Invalid model '%s'" % model, status=404)
        return view_func(request, *args, **kwargs)
    return wrapper


class IsModelValid(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            APImodels.GEM.objects.get(database_name=request.model)
        except APImodels.GEM.DoesNotExist:
            return False
        return True


def componentDBserializerSelector(database, type, serializer_type=None, api_version=None):
    serializer_choice = ['basic', 'lite', 'table', None]
    if serializer_type not in serializer_choice:
        raise ValueError("Error serializer type, choices are %s" % ", ".join([str(e) for e in serializer_choice]))

    if type == 'reaction':
        if serializer_type == 'basic':
            return APIserializer.ReactionBasicSerializer
        if serializer_type == 'table':
            return APIserializer.ReactionRTSerializer
        return APIserializer.ReactionSerializer
    elif type == 'subsystem':
        return APIcsSerializer.SubsystemSerializer
    elif type == 'metabolite':
        if serializer_type in ['lite']:
            return APIrcSerializer.MetaboliteLiteSerializer
        return APIrcSerializer.MetaboliteSerializer
    elif type == 'gene':
        if serializer_type in ['lite']:
            return APIrcSerializer.GeneLiteSerializer
        return APIrcSerializer.GeneSerializer



@api_view()
@is_model_valid
def get_reactions(request, model):
    """
    List all reactions for the given model.
    """
    reactions = APImodels.Reaction.objects.using(model).all().prefetch_related('subsystem', 'compartment')

    ReactionSerializerClass = componentDBserializerSelector(model, 'reaction', serializer_type="basic", api_version=request.version)

    serializer = ReactionSerializerClass(reactions, many=True)
    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_reaction(request, model, id):
    """
    List all the information we have on a reaction (for example HMR_3905).
    """
    try:
        reaction = APImodels.Reaction.objects.using(model).get(id__iexact=id)
    except APImodels.Reaction.DoesNotExist:
        return HttpResponse(status=404)

    ReactionSerializerClass = componentDBserializerSelector(model, 'reaction', serializer_type=None, api_version=request.version)
    reactionserializer = ReactionSerializerClass(reaction)

    pmids = APImodels.ReactionReference.objects.using(model).filter(reaction_id=reaction.id)
    pmidserializer = APIserializer.ReactionReferenceSerializer(pmids, many=True)

    result = reactionserializer.data.copy()
    result.update({'pmids': pmidserializer.data})

    return JSONResponse(result)


@api_view()
@is_model_valid
def get_reaction_reactants(request, model, id):
    """
    For a given reaction, list all the metabolites that are consumed.
    """
    try:
        reaction = APImodels.Reaction.objects.using(model).prefetch_related('reactants__metabolite').get(id__iexact=id)
    except APImodels.Reaction.DoesNotExist:
        return HttpResponse(status=404)

    ReactantsSerializerClass = componentDBserializerSelector(model, 'metabolite', serializer_type='lite', api_version=request.version)
    serializer = ReactantsSerializerClass(reaction.reactants.prefetch_related('subsystem_metabolite', 'compartment'), many=True)
    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_reaction_products(request, model, id):
    """
    For a given reaction, list all the metabolites that are produced.
    """
    try:
        reaction = APImodels.Reaction.objects.using(model).prefetch_related('products__metabolite').get(id__iexact=id)
    except APImodels.Reaction.DoesNotExist:
        return HttpResponse(status=404)

    ProductsSerializerClass = componentDBserializerSelector(model, 'metabolite', serializer_type='lite', api_version=request.version)
    serializer = ProductsSerializerClass(reaction.products.prefetch_related('subsystem_metabolite', 'compartment'), many=True)
    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_reaction_genes(request, model, id):
    """
    For a given reaction, list the genes that are modifying it.
    """
    try:
        reaction = APImodels.Reaction.objects.using(model).prefetch_related('genes__gene').get(id__iexact=id)
    except APImodels.Reaction.DoesNotExist:
        return HttpResponse(status=404)

    GenesSerializerClass = componentDBserializerSelector(model, 'gene', serializer_type='lite', api_version=request.version)
    serializer = GenesSerializerClass(reaction.genes.prefetch_related('subsystem_gene', 'compartment_gene'), many=True)
    return JSONResponse(serializer.data)


@api_view()
def get_metabolite_interaction_partners(request, model, id):
    """
    For a given metabolite, list all the first order interaction partners.
    """
    response = get_interaction_partners(request=request._request, model=model, id=id, type='m')
    return response


@api_view()
def get_gene_interaction_partners(request, model, id):
    """
    For a given gene, list all the first order interaction partners.
    """
    response = get_interaction_partners(request=request._request, model=model, id=id, type='e')
    return response


@api_view()
@is_model_valid
def get_interaction_partners(request, model, id, type=None):
    reactions = []
    metabolites_IP = []
    genes_IP = []
    IP_dict = {}

    try:
        component = APImodels.ReactionComponent.objects.using(model).get(Q(id__iexact=id) | Q(full_name__iexact=id))
    except APImodels.ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)
    type = component.component_type
    if type == 'e':
        reactions = component.reactions_as_gene.prefetch_related('reactants', 'products', 'genes').all()
    elif type == 'm':
        reactions = component.reactions_as_metabolite.prefetch_related('reactants', 'products', 'genes').all()

    for r in reactions:
        for el in chain(r.reactants.all(), r.products.all()):
            if type == 'm' and el.id == component.id:
                continue

            if el.id in IP_dict:
                # this interaction is already known, just add the reaction
                IP_dict[el.id]['reactions'].append({
                    'id': r.id,
                    'equation': r.equation,
                    'reversible': r.is_reversible
                })
                continue

            ip = {
                'id': el.id,
                'name': el.full_name,
                'reactions': [{
                    'id': r.id,
                    'equation': r.equation,
                    'reversible': r.is_reversible
                }]
            }
            IP_dict[el.id] = ip
            metabolites_IP.append(ip)

        for gene in r.genes.all():
            if type == 'e' and gene.id == component.id:
                continue

            if gene.id in IP_dict:
                # this interaction is already known, just add the reaction
                IP_dict[gene.id]['reactions'].append({
                    'id': r.id,
                    'equation': r.equation,
                    'reversible': r.is_reversible
                })
                continue

            ip = {
                'id': gene.id,
                'name': gene.name,
                'reactions': [{
                    'id': r.id,
                    'equation': r.equation,
                    'reversible': r.is_reversible
                }]
            }
            IP_dict[gene.id] = ip
            genes_IP.append(ip)

    return JSONResponse({
        'id': component.id,
        'name': component.name,
        'type': 'metabolite' if type == 'm' else 'gene',
        'interaction_partners': {
            'metabolites': metabolites_IP,
            'genes': genes_IP
        }
    })


@api_view()
@is_model_valid
def get_genes(request, model):
    """
    List all the genes in the given model.
    """

    genes = APImodels.ReactionComponent.objects.using(model).filter(component_type='e') \
        .select_related('gene').prefetch_related('subsystem_gene', 'compartment_gene')

    GeneSerializerClass = componentDBserializerSelector(model, 'gene', serializer_type='lite', api_version=request.version)
    serializer = GeneSerializerClass(genes, many=True)

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_gene(request, model, id):
    """
    List all information for a given gene (for example ENSG00000196502 or SULT1A1).
    """
    try:
        component = APImodels.ReactionComponent.objects.using(model).get(Q(id__iexact=id) |
                                                                         Q(name__iexact=id) &
                                                                         Q(component_type='e'))
    except APImodels.ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    GeneSerializerClass = componentDBserializerSelector(model, 'gene', serializer_type=None, api_version=request.version)
    serializer = GeneSerializerClass(component)

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_metabolites(request, model):
    """
    List all the metabolites in the given model.
    """

    metabolites = APImodels.ReactionComponent.objects.using(model).filter(component_type='m') \
        .select_related('metabolite').prefetch_related('subsystem_metabolite', 'compartment')

    MetaboliteSerializerClass = componentDBserializerSelector(model, 'metabolite', serializer_type='lite', api_version=request.version)
    serializer = MetaboliteSerializerClass(metabolites, many=True)

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_metabolite(request, model, id):
    """
    List all information for a given metabolite (for example m01587m or citrate[m]).
    """
    try:
        component = APImodels.ReactionComponent.objects.using(model).get((Q(id__iexact=id) |
                                                                         Q(full_name__iexact=id)) &
                                                                         Q(component_type='m'))
    except APImodels.ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    MetaboliteSerializerClass = componentDBserializerSelector(model, 'metabolite', serializer_type=None, api_version=request.version)
    serializer = MetaboliteSerializerClass(component)

    return JSONResponse(serializer.data)


@api_view()
def get_metabolite_reactions_all_compartment(request, model, id, api=True):
    """
        List all the reactions involving the metabolite regarding its compartment localisation.
        Supply a metabolite ID or a metabolite name (for example m02439c or malate[c] or malate).
    """
    return get_metabolite_reactions(request=request._request, model=model, id=id, all_compartment=True, api=api)


@api_view()
@is_model_valid
def get_metabolite_reactions(request, model, id, all_compartment=False, api=True):
    """
        List all the reactions involving the metabolite.
        Supply a metabolite ID or its name (for example m02439c or malate[c]).
    """
    if not all_compartment:
        component = APImodels.ReactionComponent.objects.using(model).filter((Q(id__iexact=id) |
                                                                             Q(full_name__iexact=id)) &
                                                                             Q(component_type='m'))
    else:
        component = APImodels.ReactionComponent.objects.using(model).filter((Q(id__iexact=id) |
                                                                      Q(name__iexact=id) |
                                                                      Q(full_name__iexact=id)) &
                                                                      Q(component_type='m'))
    if not component:
        return HttpResponse(status=404)

    if all_compartment:
        component = APImodels.ReactionComponent.objects.using(model).filter(Q(name=component[0].name))

    reactions = APImodels.Reaction.objects.none()
    for c in component:
        if api:
            reactions_as_met = c.reactions_as_metabolite.using(model). \
                prefetch_related('reactants', 'products', 'genes', 'subsystem', 'compartment').distinct()
        else:
            reactions_as_met = c.reactions_as_metabolite.using(model). \
                prefetch_related('reactionreactant_set', 'reactionreactant_set__reactant',
                                 'reactionproduct_set', 'reactionproduct_set__product', 'genes').distinct()
        reactions |= reactions_as_met

    reactions = reactions.distinct()
    if not api:
        reactions = reactions[:200]
        ReactionSerializerClass = componentDBserializerSelector(model, 'reaction', serializer_type='table', api_version=request.version)
    else:
        ReactionSerializerClass = componentDBserializerSelector(model, 'reaction', serializer_type='basic', api_version=request.version)

    serializer = ReactionSerializerClass(reactions, many=True)
    return JSONResponse(serializer.data)

 
@api_view()
@is_model_valid
def get_gene_reactions(request, model, id, api=True):
    """
        list all the reactions involving the gene/gene.
        Supply a gene/gene ID or its name (for example ENSG00000180011).
    """
    component = APImodels.ReactionComponent.objects.using(model).filter((Q(id__iexact=id) |
                                                                         Q(name__iexact=id)) &
                                                                         Q(component_type='e'))

    if not component:
        return HttpResponse(status=404)

    reactions = APImodels.Reaction.objects.none()
    for c in component:
        if api:
            reactions_as_gene = c.reactions_as_gene.using(model). \
                prefetch_related('reactants', 'products', 'genes', 'subsystem', 'compartment').distinct()
        else:
            reactions_as_gene = c.reactions_as_gene.using(model). \
                prefetch_related('reactionreactant_set', 'reactionreactant_set__reactant',
                                 'reactionproduct_set', 'reactionproduct_set__product', 'genes').distinct()
        reactions |= reactions_as_gene

    reactions = reactions.distinct()
    if not api:
        reactions = reactions[:200]
        ReactionSerializerClass = componentDBserializerSelector(model, 'reaction', serializer_type='table', api_version=request.version)
    else:
        ReactionSerializerClass = componentDBserializerSelector(model, 'reaction', serializer_type='basic', api_version=request.version)

    serializer = ReactionSerializerClass(reactions, many=True)

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_subsystem(request, model, id, api=True):
    """
    For a given subsystem name, list all the containing metabolites and genes/genes.
    """
    try:
        subsystem = APImodels.Subsystem.objects.using(model).get(Q(name_id__iexact=id) | Q(name__iexact=id))
        subsystem_id = subsystem.id
    except APImodels.Subsystem.DoesNotExist:
        return HttpResponse(status=404)

    SubsystemSerializerClass = componentDBserializerSelector(model, 'subsystem', serializer_type=None, api_version=request.version)
    if not api:
        limit = 1000
        results = {
            'info': SubsystemSerializerClass(subsystem).data,
            'metabolites': APIrcSerializer.ReactionComponentBasicSerializer(subsystem.metabolites.all()[:limit], many=True).data,
            'genes': APIrcSerializer.ReactionComponentBasicSerializer(subsystem.genes.all()[:limit], many=True).data,
            'limit': limit,
         }
    else:
        results = {}
        results.update(SubsystemSerializerClass(subsystem).data)
        results['metabolites'] = APIrcSerializer.ReactionComponentBasicSerializer(subsystem.metabolites.all(), many=True).data
        results['genes'] = APIrcSerializer.ReactionComponentBasicSerializer(subsystem.genes.all(), many=True).data

    return JSONResponse(results)


@api_view()
@is_model_valid
def get_subsystem_reactions(request, model, id, api=True):
    """
    For a given subsystem/pathway name, list all the containing reactions.
    """
    try:
        subsystem = APImodels.Subsystem.objects.using(model).get(Q(name_id__iexact=id) | Q(name__iexact=id))
        subsystem_id = subsystem.id
    except APImodels.Subsystem.DoesNotExist:
        return HttpResponse(status=404)

    if api:
        r = APImodels.Reaction.objects.using(model).filter(subsystem=subsystem_id). \
            prefetch_related('genes', 'subsystem', 'compartment').distinct()
        ReactionSerializerClass = componentDBserializerSelector(model, 'reaction', serializer_type='basic', api_version=request.version)
    else:
        r = APImodels.Reaction.objects.using(model).filter(subsystem=subsystem_id). \
            prefetch_related('reactionreactant_set', 'reactionreactant_set__reactant',
                 'reactionproduct_set', 'reactionproduct_set__product', 'genes').distinct()[:1000]
        ReactionSerializerClass = componentDBserializerSelector(model, 'reaction', serializer_type='table', api_version=request.version)

    results = {
        'reactions': ReactionSerializerClass(r, many=True).data,
        'limit': 1000,
    }

    if api:
        return JSONResponse(results['reactions'])
    return JSONResponse(results)


@api_view()
@is_model_valid
def get_subsystems(request, model):
    """
    List all the subsystems/pathways/collection of reactions for the given model.
    """
    try:
        subsystems = APImodels.Subsystem.objects.using(model).all().prefetch_related('compartment', 'external_databases')
    except APImodels.Subsystem.DoesNotExist:
        return HttpResponse(status=404)

    serializerClass = componentDBserializerSelector(model, 'subsystem', serializer_type=None, api_version=request.version)
    serializer = serializerClass(subsystems, many=True)

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_compartments(request, model):
    '''
    List all the compartments for the given model.
    '''
    try:
        compartment = APImodels.Compartment.objects.using(model).all()
    except APImodels.Compartment.DoesNotExist:
        return HttpResponse(status=404)

    serializer = APIcsSerializer.CompartmentSerializer(compartment, many=True)

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_compartment(request, model, id, api=True):
    """
    For a given compartment name (e.g., Golgi apparatus or golgi_apparatus), returns all containing metabolites, genes, reactions and subsystems.
    """
    try:
        compartment = APImodels.Compartment.objects.using(model).prefetch_related('subsystem').get(Q(name_id__iexact=id) | Q(name__iexact=id))
        compartment_id = compartment.id
    except APImodels.Compartment.DoesNotExist:
        return HttpResponse(status=404)

    if not api:
        results = {
            'info': APIcsSerializer.CompartmentSerializer(compartment).data,
            'subsystems': APIcsSerializer.SubsystemBasicSerializer(compartment.subsystem, many=True).data,
        }
    else:
        sms = APImodels.ReactionComponentCompartment.objects.using(model).filter(compartment_id=compartment_id).values_list('rc_id', flat=True)
        reactions = APImodels.ReactionCompartment.objects.using(model).filter(compartment_id=compartment_id).values_list('reaction_id', flat=True)

        results = {}
        results.update(APIcsSerializer.CompartmentSerializer(compartment).data)
        results['subsystems'] = APIcsSerializer.SubsystemBasicSerializer(compartment.subsystem, many=True).data
        results['metabolites'] = sms
        results['genes'] = compartment.genes.all().values_list('id', flat=True)
        results['reactions'] = reactions

    return JSONResponse(results)


#=========================================================================================================
# For the integrated Models stored in separate database

@api_view()
def get_models(request):
    """
    List all Genome-scale metabolic models (GEMs) that are available on the GEM browser.
    """
    models = APImodels.GEM.objects.all()
    serializer = APIserializer.GEMSerializer(models, many=True)
    return JSONResponse(serializer.data)



@api_view()
def get_model(request, name):
    """
    List all information for a given model available on the GEM browser, supply its name e.g., 'Human-GEM'.
    """

    try:
        int(name)
        is_int = True
    except ValueError:
        is_int = False

    if is_int:
        model = APImodels.GEM.objects.filter(id=name).select_related('sample').prefetch_related('authors', 'ref')
    else:
        model = APImodels.GEM.objects.filter(short_name__iexact=name).select_related('sample').prefetch_related('authors', 'ref')
    if not model:
        return HttpResponse(status=404)

    serializer = APIserializer.GEMSerializer(model[0])
    return JSONResponse(serializer.data)
