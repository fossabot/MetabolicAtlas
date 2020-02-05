from rest_framework import serializers
import api.models as APImodels
from django.db import models
from collections import defaultdict
import api.serializers_cs as APIcsSerializer
import logging

# inherited by ReactionComponentLiteSerializer
# used in:
# views get_subsystem
# private_views get_component_with_interaction_partners
class ReactionComponentBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'full_name')


# attr of ReactionSerializer
# used in:
# private_views quick search met
class ReactionComponentLiteSerializer(ReactionComponentBasicSerializer):
    compartment = serializers.CharField(source='compartment_str')
    synonyms = serializers.CharField(source='aliases')

    class Meta(ReactionComponentBasicSerializer.Meta):
        fields = ReactionComponentBasicSerializer.Meta.fields + \
         ('synonyms', 'formula', 'compartment')

# ================================================================================

# used in:
# private_view search (global search table)
class GeneSearchSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    subsystem = APIcsSerializer.SubsystemBasicSerializer(read_only=True, many=True, source="subsystem_gene")
    compartment = APIcsSerializer.CompartmentBasicSerializer(read_only=True, many=True, source="compartment_gene")

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'subsystem', 'compartment')

    def get_name(self, obj):
        # name field has a not NULL, because of metabolite/gene in ReactionComponent
        # null is expected if there is not name
        return obj.name if obj.name else None


# used in:
# views get_genes API
# private_view get_component_with_interaction_partners
class GeneLiteSerializer(serializers.ModelSerializer):
    alternate_name = serializers.SerializerMethodField()
    synonyms = serializers.CharField(source='aliases')
    function = serializers.SerializerMethodField('get_function1')
    # function2 = serializers.SerializerMethodField()
    ec =  serializers.SerializerMethodField()
    catalytic_activity = serializers.SerializerMethodField()
    # cofactor = serializers.SerializerMethodField('read_cofactor')
    subsystems = APIcsSerializer.SubsystemBasicSerializer(read_only=True, many=True, source="subsystem_gene")
    compartments = APIcsSerializer.CompartmentBasicSerializer(read_only=True, many=True, source="compartment_gene")

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'alternate_name', 'synonyms', 'function', 'ec', \
         'catalytic_activity', 'subsystems', 'compartments',)

    def get_alternate_name(self, obj):
        return obj.alt_name1

    def get_function1(self, obj):
        return obj.gene.function1 if hasattr(obj, 'gene') else None

    def get_function2(self, obj):  # unused
        return obj.gene.function2 if hasattr(obj, 'gene') else None

    def get_ec(self, obj):
        return obj.gene.ec if hasattr(obj, 'gene') else None

    def get_catalytic_activity(self, obj):
        return obj.gene.catalytic_activity if hasattr(obj, 'gene') else None

    def read_cofactor(self, obj):  # unused
        return obj.gene.cofactor if hasattr(obj, 'gene') else None


# used in:
# get_gene (gene page)
# private_view get_component_with_interaction_partners
class GeneSerializer(GeneLiteSerializer):
    external_databases = serializers.SerializerMethodField()

    class Meta(GeneLiteSerializer.Meta):
        fields = GeneLiteSerializer.Meta.fields + ('external_databases',)

    def get_external_databases(self, obj):
        return APIcsSerializer.eid_to_dict(obj)


# used in:
# attr of InteractionPartnerSerializer
# attr of ReactionRTSerializer
class GeneInteractionPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name',)

# ================================================================================

# used in:
# private_view search (global search table)
class MetaboliteSearchSerializer(serializers.ModelSerializer):
    subsystem = APIcsSerializer.SubsystemBasicSerializer(read_only=True, many=True, source="subsystem_metabolite")
    compartment = APIcsSerializer.CompartmentBasicSerializer(read_only=True)
    charge = serializers.SerializerMethodField()

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'formula', 'charge', 'subsystem', 'compartment')

    def get_charge(self, obj):
        return obj.metabolite.charge


# used in:
# get_metabolites API
# views get_reaction_reactants
# views get_reaction_products
class MetaboliteLiteSerializer(serializers.ModelSerializer):
    alternate_name = serializers.SerializerMethodField()
    synonyms = serializers.CharField(source='aliases')
    description = serializers.SerializerMethodField()
    # function = serializers.SerializerMethodField('get_function1')
    # function2 = serializers.SerializerMethodField()
    charge = serializers.SerializerMethodField()
    inchi =  serializers.SerializerMethodField()
    subsystems = APIcsSerializer.SubsystemBasicSerializer(read_only=True, many=True, source="subsystem_metabolite")
    compartment = APIcsSerializer.CompartmentBasicSerializer(read_only=True)

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'alternate_name', 'synonyms', 'description', 'formula', \
         'charge', 'inchi', 'subsystems', 'compartment',)

    def get_alternate_name(self, obj):
        return obj.alt_name1

    def get_description(self, obj):
        return obj.metabolite.description if hasattr(obj, 'metabolite') else None

    def get_function1(self, obj):  # unused
        return obj.metabolite.function1 if hasattr(obj, 'metabolite') else None

    def get_function2(self, obj):  # unused
        return obj.metabolite.function2 if hasattr(obj, 'metabolite') else None

    def get_charge(self, obj):
        return obj.metabolite.charge if hasattr(obj, 'metabolite') else None

    def get_inchi(self, obj):
        return obj.metabolite.inchi if hasattr(obj, 'metabolite') else None

# used in:
# views get_metabolite
class MetaboliteSerializer(MetaboliteLiteSerializer):
    external_databases = serializers.SerializerMethodField()

    class Meta(MetaboliteLiteSerializer.Meta):
        fields = MetaboliteLiteSerializer.Meta.fields + ('external_databases',)

    def get_external_databases(self, obj):
        return APIcsSerializer.eid_to_dict(obj)


# used in:
# attr of InteractionPartnerSerializer
class MetaboliteInteractionPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'compartment_str')


# ==========================================================================================

# custom serializers for the GEM browser Tiles
class GemBrowserTileMetaboliteSerializer(serializers.ModelSerializer):
    compartment = serializers.CharField(source='compartment_str')
    reaction_count = serializers.SerializerMethodField()

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'formula', 'compartment', 'reaction_count')

    def get_reaction_count(self, obj):
        return obj.reactions_as_reactant.count() + obj.reactions_as_product.count()


class GemBrowserTileGeneSerializer(serializers.ModelSerializer):
    compartment_count = serializers.SerializerMethodField()
    subsystem_count = serializers.SerializerMethodField()
    reaction_count = serializers.SerializerMethodField()

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'reaction_count', 'compartment_count', 'subsystem_count')

    def get_compartment_count(self, obj):
        return obj.compartment_gene.count()

    def get_subsystem_count(self, obj):
        return obj.subsystem_gene.count()

    def get_reaction_count(self, obj):
        return obj.reactions_as_gene.count()
