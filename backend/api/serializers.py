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

# class SubsystemReactionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = APImodels.SubsystemReaction
#         fields = ('reaction', 'subsystem')

# ===============================================================================

# used in:
# view get_reactions
# view get_X_reaction API version
# private view quick search
# ReactionSerializer is subclass
class ReactionBasicSerializer(serializers.ModelSerializer):
    id_equation = serializers.SerializerMethodField('read_id_equation')
    equation = serializers.SerializerMethodField('read_equation')
    name_gene_rule = serializers.SerializerMethodField('read_name_gene_rule')
    subsystem = serializers.CharField(source='subsystem_str')

    class Meta:
        model = APImodels.Reaction
        fields = ('id', 'id_equation', 'equation', 'gene_rule', 'name_gene_rule', 'ec', 'lower_bound', 'upper_bound', 'objective_coefficient',
                'compartment', 'subsystem', 'is_transport', 'is_reversible',)

    def read_equation(self, model):
        return model.equation_wname

    def read_id_equation(self, model):
        return model.equation

    def read_name_gene_rule(self, model):
        return model.gene_rule_wname


class ReactionReactantSerializer(serializers.ModelSerializer):
    # reactant = APIrcSerializer.ReactionComponentRTSerializer()
    id = serializers.SerializerMethodField('get_reactant_id')
    # name = serializers.CharField(source='reactant__name', read_only=True)
    name = serializers.SerializerMethodField('get_reactant_name')
    full_name = serializers.SerializerMethodField('get_reactant_full_name')
    compartment = serializers.SerializerMethodField('get_reactant_compartment')

    class Meta:
        model = APImodels.ReactionReactant
        fields = ('id', 'name', 'full_name', 'compartment', 'stoichiometry',)

    def get_reactant_id(self, model):
        return model.reactant.id;

    def get_reactant_name(self, model):
        return model.reactant.name;

    def get_reactant_full_name(self, model):
        return model.reactant.full_name;

    def get_reactant_compartment(self, model):
        return model.reactant.compartment_str;


class ReactionProductSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_product_id')
    name = serializers.SerializerMethodField('get_product_name')
    full_name = serializers.SerializerMethodField('get_product_full_name')
    compartment = serializers.SerializerMethodField('get_product_compartment')

    class Meta:
        model = APImodels.ReactionProduct
        fields = ('id', 'name', 'full_name', 'compartment', 'stoichiometry',)

    def get_product_id(self, model):
        return model.product.id;

    def get_product_name(self, model):
        return model.product.name;

    def get_product_full_name(self, model):
        return model.product.full_name;

    def get_product_compartment(self, model):
        return model.product.compartment_str;


# class ReactionExternalDbSerializer(serializers.ModelSerializer):
#     database = serializers.CharField(source='db_name')
#     id = serializers.CharField(source='external_id')
#     url = serializers.CharField(source='external_link')
#     class Meta:
#         model = APImodels.ReactionEID
#         fields = ('database', 'id', 'url',)



# used in:
# view get_X_reactions NO API version (reactome tables)
# private view get_related_reactions
# ReactionPageSerializer is subclass
class ReactionBasicRTSerializer(serializers.ModelSerializer):
    reactionreactant_set = ReactionReactantSerializer(many=True)
    reactionproduct_set = ReactionProductSerializer(many=True)
    genes = APIrcSerializer.ReactionComponentLiteSerializer(many=True)

    class Meta:
        model = APImodels.Reaction
        fields = ('id', 'gene_rule', 'gene_rule_wname', 'compartment', 'subsystem_str',
             'is_transport', 'is_reversible', 'reactionreactant_set', 'reactionproduct_set', 'genes')


# used in:
# private view get_reaction (reaction GB page)
class ReactionPageSerializer(ReactionBasicRTSerializer):
    external_databases = serializers.SerializerMethodField('read_external_databases')

    class Meta(ReactionBasicRTSerializer.Meta):
        fields = ReactionBasicRTSerializer.Meta.fields + ('ec', 'lower_bound', 'upper_bound', 'objective_coefficient', 'external_databases',)

    def read_external_databases(self, model):
        return APIcsSerializer.eid_to_dict(model)


# used in:
# private_view search (global search table)
class ReactionSearchSerializer(serializers.ModelSerializer):
    subsystem = APIcsSerializer.SubsystemBasicSerializer(many=True, read_only=True)

    class Meta:
        model = APImodels.Reaction
        fields = ('id', 'equation_wname', 'subsystem', 'compartment', 'is_transport')

# # used in:

# # subclass of ReactionSerializer
# class ReactionLiteSerializer(ReactionBasicSerializer):
#     reactants = APIrcSerializer.ReactionComponentLiteSerializer(many=True)
#     products = APIrcSerializer.ReactionComponentLiteSerializer(many=True)
#     genes = APIrcSerializer.ReactionComponentLiteSerializer(many=True)

#     class Meta(ReactionBasicSerializer.Meta):
#         model = APImodels.Reaction
#         fields = ReactionBasicSerializer.Meta.fields + ('reactants', 'products', 'genes')

# used in:
# get_reaction API
class ReactionSerializer(ReactionBasicSerializer):
    reactants = APIrcSerializer.ReactionComponentLiteSerializer(many=True)
    products = APIrcSerializer.ReactionComponentLiteSerializer(many=True)
    genes = APIrcSerializer.ReactionComponentLiteSerializer(many=True)
    subsystem = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
     )
    external_databases = serializers.SerializerMethodField('read_external_databases')

    class Meta(ReactionBasicSerializer.Meta):
        fields = ReactionBasicSerializer.Meta.fields + \
            ('reactants', 'products', 'genes','external_databases',)

    def read_external_databases(self, model):
        return APIcsSerializer.eid_to_dict(model)

# =========================================================================================

class InteractionPartnerSerializer(serializers.ModelSerializer):
    genes = APIrcSerializer.GeneReactionComponentInteractionPartnerSerializer(many=True, read_only=True)
    products = APIrcSerializer.MetaboliteReactionComponentInteractionPartnerSerializer(many=True, read_only=True)
    reactants = APIrcSerializer.MetaboliteReactionComponentInteractionPartnerSerializer(many=True, read_only=True)
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

    def fetch_subsystems(self, model):
        return model.subsystem.order_by('-reaction_count').values_list('name', flat=True)[:15]


class GemBrowserTileSubsystemSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='name_id')
    class Meta:
        model = APImodels.Subsystem
        fields = ('id', 'name', 'metabolite_count', 'gene_count', 'reaction_count', 'compartment_count')


class GemBrowserTileReactionSerializer(serializers.ModelSerializer):
    compartment_count = serializers.SerializerMethodField('read_compartment_count')
    subsystem_count = serializers.SerializerMethodField('read_subsystem_count')
    gene_count = serializers.SerializerMethodField('read_gene_count')

    class Meta:
        model = APImodels.Reaction
        fields = ('id', 'equation_wname', 'is_reversible', 'subsystem_count', 'compartment_count', 'gene_count')

    def read_compartment_count(self, model):
        return len(re.compile(" => | + ").split(model.compartment))

    def read_subsystem_count(self, model):
        return model.subsystem.count()

    def read_gene_count(self, model):
        return model.genes.count()


class GemBrowserTileSerializer(serializers.Serializer):
    compartment = GemBrowserTileCompartmentSerializer()
    subsystems = GemBrowserTileSubsystemSerializer(many=True)
    reactions = GemBrowserTileReactionSerializer(many=True)
    metabolites = APIrcSerializer.GemBrowserTileMetaboliteSerializer(many=True)
    genes = APIrcSerializer.GemBrowserTileGeneSerializer(many=True)


# =======================================================================================
# models database


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
    gemodelset = GEModelSetSerializer(read_only=True)
    sample = GEModelSampleSerializer(read_only=True)
    files = GEModelFileSerializer(many=True, read_only=True)
    ref = GEModelReferenceSerializer(many=True, read_only=True)

    class Meta:
        model = APImodels.GEModel
        fields = ('id', 'gemodelset', 'sample', 'tag', 'description', 'condition', 'reaction_count', 'metabolite_count', 'gene_count', 'files', 'ref', 'maintained', 'repo_url', 'last_update')


class GEModelListSerializer(serializers.ModelSerializer):
    set_name = serializers.SerializerMethodField('get_model_set_name')
    sample = GEModelSampleSerializer(read_only=True)
    year = serializers.SerializerMethodField('get_model_year')

    def get_model_set_name(self, model):
        return model.gemodelset.name

    def get_model_year(self, model):
        refs = model.ref
        if refs.all():
            return max([r.year for r in refs.all()])
        else:
            refs = model.gemodelset.reference
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

    def get_model_details(self, model):
        return GEModelListSerializer(model.model).data

    class Meta:
        model = APImodels.GEM
        fields = ('short_name', 'full_name', 'database_name', 'description', 'version', 'link', 'authors', 'condition', 'date', 'sample', 'ref', 'metabolite_count', 'gene_count', 'reaction_count',)

