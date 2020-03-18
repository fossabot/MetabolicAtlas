from rest_framework import serializers
import api.models as APImodels
import api.serializers_rc as APIrcSerializer
import api.serializers_cs as APIcsSerializer
from django.db import models
from collections import defaultdict
import logging
import re

class ReactionReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.ReactionReference
        fields = ('pmid',)

# ===============================================================================
# inherited by ReactionSerializer
# used in:
# views get_reactions
# views get_X_reaction API version
# private views quick search
# private_views global search (ReactionSerializer)
class ReactionBasicSerializer(serializers.ModelSerializer):
    equation = serializers.CharField(source='equation_wname')
    equation_id = serializers.CharField(source='equation')
    equation_compartment = serializers.CharField(source='compartment_str')
    gene_rule_name = serializers.CharField(source='equation_wname')
    subsystems = APIcsSerializer.SubsystemBasicSerializer(many=True, read_only=True, source='subsystem')
    compartments = APIcsSerializer.CompartmentBasicSerializer(many=True, read_only=True, source="compartment")

    class Meta:
        model = APImodels.Reaction
        fields = ('id', 'equation_id', 'equation', 'equation_compartment', 'gene_rule', 'gene_rule_name', 'ec',
                  'lower_bound', 'upper_bound', 'objective_coefficient',
                  'compartments', 'subsystems', 'is_transport', 'is_reversible',)

# attr of ReactionRTSerializer
class ReactionReactantSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    compartment = serializers.SerializerMethodField()

    class Meta:
        model = APImodels.ReactionReactant
        fields = ('id', 'name', 'full_name', 'compartment', 'stoichiometry',)

    def get_id(self, obj):
        return obj.reactant.id;

    def get_name(self, obj):
        return obj.reactant.name;

    def get_full_name(self, obj):
        return obj.reactant.full_name;

    def get_compartment(self, obj):
        return obj.reactant.compartment_str;

# attr of ReactionRTSerializer
class ReactionProductSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    compartment = serializers.SerializerMethodField()

    class Meta:
        model = APImodels.ReactionProduct
        fields = ('id', 'name', 'full_name', 'compartment', 'stoichiometry',)

    def get_id(self, obj):
        return obj.product.id;

    def get_name(self, obj):
        return obj.product.name;

    def get_full_name(self, obj):
        return obj.product.full_name;

    def get_compartment(self, obj):
        return obj.product.compartment_str;


# inherited by ReactionPageSerializer
# used in:
# views get_X_reactions NO API version (reactome tables)
# private_views get_related_reactions
# private_views get_reaction (ReactionPageSerializer)
class ReactionRTSerializer(serializers.ModelSerializer):
    reactionreactant_set = ReactionReactantSerializer(many=True, read_only=True)
    reactionproduct_set = ReactionProductSerializer(many=True, read_only=True)
    genes = APIrcSerializer.GeneInteractionPartnerSerializer(many=True, read_only=True)

    class Meta:
        model = APImodels.Reaction
        fields = ('id', 'compartment_str', 'subsystem_str', 'is_transport',
              'is_reversible', 'reactionreactant_set', 'reactionproduct_set', 'genes')


# used in:
# private_views get_reaction (Gem Browser)
class ReactionPageSerializer(ReactionRTSerializer):
    external_databases = serializers.SerializerMethodField('read_external_databases')
    subsystem = APIcsSerializer.SubsystemBasicSerializer(many=True, read_only=True)
    compartment = APIcsSerializer.CompartmentBasicSerializer(many=True, read_only=True)

    class Meta(ReactionRTSerializer.Meta):
        fields = ('id', 'gene_rule', 'gene_rule_wname', 'compartment_str', 'is_transport',
        'is_reversible', 'reactionreactant_set', 'reactionproduct_set', 'genes',
        'ec', 'lower_bound', 'upper_bound', 'objective_coefficient', 'compartment', 'subsystem', 'external_databases',)

    def read_external_databases(self, obj):
        return APIcsSerializer.eid_to_dict(obj)


# used in:
# private_views global search
class ReactionSearchSerializer(serializers.ModelSerializer):
    subsystem = APIcsSerializer.SubsystemBasicSerializer(many=True, read_only=True)
    compartment = APIcsSerializer.CompartmentBasicSerializer(many=True, read_only=True)

    class Meta:
        model = APImodels.Reaction
        fields = ('id', 'equation_wname', 'subsystem', 'compartment', 'is_transport')


# used in:
# get_reaction API
class ReactionSerializer(ReactionBasicSerializer):
    reactants = APIrcSerializer.ReactionComponentLiteSerializer(many=True, read_only=True)
    products = APIrcSerializer.ReactionComponentLiteSerializer(many=True, read_only=True)
    genes = APIrcSerializer.ReactionComponentLiteSerializer(many=True, read_only=True)
    external_databases = serializers.SerializerMethodField('read_external_databases')

    class Meta(ReactionBasicSerializer.Meta):
        fields = ReactionBasicSerializer.Meta.fields + \
            ('reactants', 'products', 'genes','external_databases',)

    def read_external_databases(self, obj):
        return APIcsSerializer.eid_to_dict(obj)

# =========================================================================================

class InteractionPartnerSerializer(serializers.ModelSerializer):
    genes = APIrcSerializer.GeneInteractionPartnerSerializer(many=True, read_only=True)
    products = APIrcSerializer.MetaboliteInteractionPartnerSerializer(many=True, read_only=True)
    reactants = APIrcSerializer.MetaboliteInteractionPartnerSerializer(many=True, read_only=True)
    compartment = serializers.CharField(source='compartment_str')
    subsystem = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
     )

    class Meta:
        model = APImodels.Reaction
        fields = ('id', 'is_reversible', 'genes', 'products', 'reactants', 'subsystem', 'compartment')


# =======================================================================================

class GemBrowserTileCompartmentSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='name_id')
    subsystems = serializers.SerializerMethodField('fetch_subsystems')

    class Meta:
        model = APImodels.Compartment
        fields = ('id', 'name', 'metabolite_count', 'gene_count', 'reaction_count', 'subsystem_count', 'subsystems')

    def fetch_subsystems(self, obj):
        return obj.subsystem.order_by('-reaction_count').values_list('name', flat=True)[:15]


class GemBrowserTileSubsystemSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='name_id')

    class Meta:
        model = APImodels.Subsystem
        fields = ('id', 'name', 'metabolite_count', 'gene_count', 'reaction_count', 'compartment_count')


class GemBrowserTileReactionSerializer(serializers.ModelSerializer):
    compartment_count = serializers.SerializerMethodField()
    subsystem_count = serializers.SerializerMethodField()
    gene_count = serializers.SerializerMethodField()

    class Meta:
        model = APImodels.Reaction
        fields = ('id', 'equation_wname', 'is_reversible', 'subsystem_count', 'compartment_count', 'gene_count')

    def get_compartment_count(self, obj):
        return len(re.compile(" => | + ").split(obj.compartment_str)) # FIXME use field compartment

    def get_subsystem_count(self, obj):
        return obj.subsystem.count()

    def get_gene_count(self, obj):
        return obj.genes.count()


class GemBrowserTileSerializer(serializers.Serializer):
    compartment = GemBrowserTileCompartmentSerializer(read_only=True)
    subsystems = GemBrowserTileSubsystemSerializer(many=True, read_only=True)
    reactions = GemBrowserTileReactionSerializer(many=True, read_only=True)
    metabolites = APIrcSerializer.GemBrowserTileMetaboliteSerializer(many=True, read_only=True)
    genes = APIrcSerializer.GemBrowserTileGeneSerializer(many=True, read_only=True)


# =======================================================================================
# GEM models database

class GEModelFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.GEModelFile
        fields = ('path', 'format')

class GEModelReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.GEModelReference
        fields = ('title', 'link', 'pmid', 'year')

class GEModelSetSerializer(serializers.ModelSerializer):
    reference = GEModelReferenceSerializer(many=True, read_only=True)

    class Meta:
        model = APImodels.GEModelSet
        fields = ('name', 'description', 'reference')

class GEModelSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.GEModelSample
        fields = ('organism', 'organ_system', 'tissue', 'cell_type', 'cell_line')


class GEModelSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='model_id')
    gemodelset = GEModelSetSerializer(read_only=True)
    sample = GEModelSampleSerializer(read_only=True)
    files = GEModelFileSerializer(many=True, read_only=True)
    ref = GEModelReferenceSerializer(many=True, read_only=True)

    class Meta:
        model = APImodels.GEModel
        fields = ('id', 'gemodelset', 'sample', 'tag', 'description', 'condition', 'reaction_count', 'metabolite_count', 'gene_count', 'files', 'ref', 'maintained', 'repo_url', 'last_update')


class GEModelListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='model_id')
    set_name = serializers.SerializerMethodField()
    sample = GEModelSampleSerializer(read_only=True)
    year = serializers.SerializerMethodField()

    def get_set_name(self, obj):
        return obj.gemodelset.name

    def get_year(self, obj):
        refs = obj.ref
        if refs.all():
            return max([r.year for r in refs.all()])
        else:
            refs = obj.gemodelset.reference
            if refs.all():
                return max([r.year for r in refs.all()])

    class Meta:
        model = APImodels.GEModel
        fields = ('id', 'set_name', 'sample', 'tag', 'condition', 'reaction_count', 'metabolite_count', 'gene_count', 'maintained', 'year', 'last_update')


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.Author
        fields = ('given_name', 'family_name', 'email', 'organization')

############################################################################################################


class GEMSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)
    sample = GEModelSampleSerializer(read_only=True)
    ref = GEModelReferenceSerializer(many=True, read_only=True)

    def get_model_details(self, obj):
        return GEModelListSerializer(obj.model).data

    class Meta:
        model = APImodels.GEM
        fields = ('short_name', 'full_name', 'database_name', 'description', 'version', 'link', 'chat_link', 'authors', 'condition', 'date', 'sample', 'ref', 'metabolite_count', 'gene_count', 'reaction_count',)

