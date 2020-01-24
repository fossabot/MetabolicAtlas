from rest_framework import serializers
import api.models as APImodels
from django.db import models
from collections import defaultdict
import api.serializers_cs as APIcsSerializer
import logging

# ================================================================================

# used in:
# subclass of ReactionComponentSerializer
class ReactionComponentBasicSerializer(serializers.ModelSerializer):
    compartment = serializers.CharField(source='compartment_str')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'full_name', 'aliases', 'formula', 'compartment')


# used in:
# get_subsystem (metabolites / gens keys)
# ReactionBasicRTSerializer (reactomes tables)
class ReactionComponentLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'full_name')


# used in:
# ReactionReactantSerializer and ReactionProductSerializer
# ReactionBasicRTSerializer (reactome tables)
class ReactionComponentRTSerializer(serializers.ModelSerializer):
    compartment = serializers.CharField(source='compartment_str')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'full_name', 'compartment')


# class ReactionComponentExternalDbSerializer(serializers.ModelSerializer):
#     database = serializers.CharField(source='db_name')
#     id = serializers.CharField(source='external_id')
#     url = serializers.CharField(source='external_link')
#     class Meta:
#         model = APImodels.ReactionComponentEID
#         fields = ('database', 'id', 'url',)


# used id:
# subclass of GeneReactionComponentSerializer, MetaboliteReactionComponentSerializer
# subclass of HmrGeneReactionComponentSerializer, HmrMetaboliteReactionComponentSerializer
class ReactionComponentSerializer(ReactionComponentBasicSerializer):
    external_databases = serializers.SerializerMethodField('read_external_databases')

    class Meta(ReactionComponentBasicSerializer.Meta):
        fields = ReactionComponentBasicSerializer.Meta.fields + \
            ('alt_name1', 'alt_name2', 'external_databases',)

    def read_external_databases(self, model):
        return APIcsSerializer.eid_to_dict(model)


# used in:
# private_view search (global search table)
class GeneReactionComponentSearchSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('read_name')
    subsystem = APIcsSerializer.SubsystemBasicSerializer(read_only=True, many=True, source="subsystem_gene")
    compartment = APIcsSerializer.CompartmentBasicSerializer(read_only=True, many=True, source="compartment_gene")

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'subsystem', 'compartment')

    def read_name(self, model):
        return model.name if model.name else None


# used in:
# private_view search (global search table)
class MetaboliteReactionComponentSearchSerializer(serializers.ModelSerializer):
    subsystem = APIcsSerializer.SubsystemBasicSerializer(read_only=True, many=True, source="subsystem_metabolite")
    compartment = APIcsSerializer.CompartmentBasicSerializer(read_only=True)
    charge = serializers.SerializerMethodField('read_charge')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'formula', 'charge', 'subsystem', 'compartment')

    def read_charge(self, model):
        if not hasattr(model, 'metabolite'): # fixme
            return 0
        return model.metabolite.charge


# used in:
# get_gene/s API (gene page)
# private_view get_component_with_interaction_partners
class GeneReactionComponentSerializer(ReactionComponentSerializer):
    function = serializers.SerializerMethodField('read_function1')
    # function2 = serializers.SerializerMethodField('read_function2')
    ec =  serializers.SerializerMethodField('read_ec')
    catalytic_activity = serializers.SerializerMethodField('read_catalytic_activity')
    cofactor = serializers.SerializerMethodField('read_cofactor')

    class Meta(ReactionComponentSerializer.Meta):
        fields = ReactionComponentSerializer.Meta.fields + \
            ('function1', 'function2', 'ec', 'catalytic_activity', 'cofactor',)

    def read_function1(self, model):
        return model.gene.function1 if hasattr(model, 'gene') else None

    # def read_function2(self, model):
    #     return model.gene.function2 if hasattr(model, 'gene') else None

    def read_ec(self, model):
        return model.gene.ec if hasattr(model, 'gene') else None

    def read_catalytic_activity(self, model):
        return model.gene.catalytic_activity if hasattr(model, 'gene') else None

    def read_cofactor(self, model):
        return model.gene.cofactor if hasattr(model, 'gene') else None


# get_gene/s API (metabolite page)
# private_view  get_component_with_interaction_partners
class MetaboliteReactionComponentSerializer(ReactionComponentSerializer):
    description = serializers.SerializerMethodField('read_description')
    function = serializers.SerializerMethodField('read_function1')
    # function2 = serializers.SerializerMethodField('read_function2')
    charge = serializers.SerializerMethodField('read_charge')
    inchi =  serializers.SerializerMethodField('read_inchi')

    class Meta(ReactionComponentSerializer.Meta):
        fields = ReactionComponentSerializer.Meta.fields + \
            ('description', 'function1', 'function2',  'charge', 'inchi',)

    def read_description(self, model):
        return model.metabolite.description if hasattr(model, 'metabolite') else None

    def read_function1(self, model):
        return model.metabolite.function1 if hasattr(model, 'metabolite') else None

    # def read_function2(self, model):
    #     return model.metabolite.function2 if hasattr(model, 'metabolite') else None

    def read_charge(self, model):
        return model.metabolite.charge if hasattr(model, 'metabolite') else None

    def read_inchi(self, model):
        return model.metabolite.inchi if hasattr(model, 'metabolite') else None

# =====================================================================================

# custom serializers for HMR TO BE DELETED

# used in:
# get_gene/s API (gene page)
# private_view get_component_with_interaction_partners
class HmrGeneReactionComponentLiteSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('read_name')
    description = serializers.SerializerMethodField('read_description')
    synonyms = serializers.CharField(source='aliases')
    ec =  serializers.SerializerMethodField('read_ec')
    external_databases = serializers.SerializerMethodField('read_external_databases')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'description', 'synonyms', 'ec', 'external_databases',)

    def read_name(self, model):
        return model.name if model.name else None

    def read_description(self, model):
        return model.alt_name1

    def read_ec(self, model):
        return model.gene.ec if hasattr(model, 'gene') else None

    def read_external_databases(self, model):
        return APIcsSerializer.eid_to_dict(model)


# used in:
# get_gene/s API (metabolite page)
# private_view  get_component_with_interaction_partners
class HmrGeneReactionComponentSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('read_name')
    description = serializers.SerializerMethodField('read_description')
    synonyms = serializers.CharField(source='aliases')
    function =  serializers.SerializerMethodField('read_function')
    ec =  serializers.SerializerMethodField('read_ec')
    catalytic_activity =  serializers.SerializerMethodField('read_catalytic_activity')
    cofactor = serializers.SerializerMethodField('read_cofactor')
    external_databases = serializers.SerializerMethodField('read_external_databases')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'description', 'synonyms', 'function', 'ec', 'catalytic_activity',
        'cofactor', 'external_databases',)

    def read_name(self, model):
        return model.name if model.name else None

    def read_description(self, model):
        return model.alt_name1

    def read_function(self, model):
        return model.gene.function1 if hasattr(model, 'gene') else None

    def read_ec(self, model):
        return model.gene.ec if hasattr(model, 'gene') else None

    def read_catalytic_activity(self, model):
        return model.gene.catalytic_activity if hasattr(model, 'gene') else None

    def read_cofactor(self, model):
        return model.gene.cofactor if hasattr(model, 'gene') else None

    def read_external_databases(self, model):
        return APIcsSerializer.eid_to_dict(model)


class GeneReactionComponentInteractionPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name',)


# -----------------------------------------------------------------------------------------------------


class HmrMetaboliteReactionComponentLiteSerializer(serializers.ModelSerializer):
    synonyms = serializers.CharField(source='aliases')
    inchi =  serializers.SerializerMethodField('read_inchi')
    compartment = serializers.CharField(source='compartment_str')
    external_databases = serializers.SerializerMethodField('read_external_databases')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'full_name', 'synonyms', 'inchi', 'compartment', 'external_databases',)

    def read_inchi(self, model):
        return model.metabolite.inchi if hasattr(model, 'metabolite') else None

    def read_external_databases(self, model):
        return APIcsSerializer.eid_to_dict(model)


class HmrMetaboliteReactionComponentSerializer(serializers.ModelSerializer):
    alt_name = serializers.CharField(source='alt_name1')
    synonyms = serializers.CharField(source='aliases')
    description = serializers.SerializerMethodField('read_description')
    function = serializers.SerializerMethodField('read_function')
    charge = serializers.SerializerMethodField('read_charge')
    inchi = serializers.SerializerMethodField('read_inchi')
    compartment = serializers.CharField(source='compartment_str')
    external_databases = serializers.SerializerMethodField('read_external_databases')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'alt_name', 'synonyms', 'description', 'function', 'formula', 'charge', 'inchi',
        'compartment', 'external_databases')

    def read_description(self, model):
        return model.metabolite.description if hasattr(model, 'metabolite') else None

    def read_function(self, model):
        return model.metabolite.function1 if hasattr(model, 'metabolite') else None

    def read_charge(self, model): #fixme, diff def than MetaboliteReactionComponentSearchSerializer
        return model.metabolite.charge if hasattr(model, 'metabolite') else None

    def read_inchi(self, model):
        return model.metabolite.inchi if hasattr(model, 'metabolite') else None

    def read_external_databases(self, model):
        return APIcsSerializer.eid_to_dict(model)


class MetaboliteReactionComponentInteractionPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'compartment_str')


# ==========================================================================================

# custom serializers for the GEM browser Tiles

class GemBrowserTileMetaboliteSerializer(serializers.ModelSerializer):
    compartment = serializers.CharField(source='compartment_str')
    reaction_count = serializers.SerializerMethodField('read_reaction_count')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'formula', 'compartment', 'reaction_count')

    def read_reaction_count(self, model):
        return model.reactions_as_reactant.count() + model.reactions_as_product.count()


class GemBrowserTileGeneSerializer(serializers.ModelSerializer):
    compartment_count = serializers.SerializerMethodField('read_compartment')
    subsystem_count = serializers.SerializerMethodField('read_subsystem')
    reaction_count = serializers.SerializerMethodField('read_reaction_count')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'reaction_count', 'compartment_count', 'subsystem_count')

    def read_compartment(self, model):
        return model.compartment_gene.count()

    def read_subsystem(self, model):
        return model.subsystem_gene.count()

    def read_reaction_count(self, model):
        return model.reactions_as_gene.count()
