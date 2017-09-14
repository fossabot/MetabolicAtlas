from rest_framework import serializers
from api.models import *

class GEMSerializer(serializers.ModelSerializer):
    authors = serializers.StringRelatedField(many=True)

    class Meta:
        model = GEM
        fields = ('id', 'short_name', 'name', 'authors')

class AuthorSerializer(serializers.ModelSerializer):
    models = serializers.StringRelatedField(many=True)

    class Meta:
        model = Author
        fields = ('id', 'given_name', 'family_name', 'email', 'organization', 'models')

class MetaboliteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metabolite
        fields = ('mass', 'kegg', 'charge', 'chebi', 'inchi', 'hmdb_description', 'hmdb_link', 'hmdb_function', 'pubchem_link')

class MetaboliteSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metabolite
        fields = ('kegg', 'hmdb', 'hmdb_name', 'mass')

class EnzymeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enzyme
        fields = ('function', 'catalytic_activity', 'uniprot_link', 'ensembl_link')

class EnzymeSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enzyme
        fields = ('uniprot_acc',)

class ReactionComponentSerializer(serializers.ModelSerializer):
    compartment = serializers.StringRelatedField()
    metabolite = MetaboliteSerializer(read_only=True)
    enzyme = EnzymeSerializer(read_only=True)

    class Meta:
        model = ReactionComponent
        fields = ('id', 'short_name', 'long_name', 'component_type', 'organism', 'formula', 'compartment', 'metabolite', 'enzyme', 'currency_metabolites')

class ReactionComponentSearchSerializer(serializers.ModelSerializer):
    compartment = serializers.StringRelatedField()
    metabolite = MetaboliteSearchSerializer(read_only=True)
    enzyme = EnzymeSearchSerializer(read_only=True)

    class Meta:
        model = ReactionComponent
        fields = ('id', 'short_name', 'long_name', 'component_type', 'organism', 'formula', 'compartment', 'metabolite', 'enzyme')

class SubsystemReactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubsystemReaction
        fields = ('reaction', 'subsystem')

class ReactionSerializer(serializers.ModelSerializer):
    reactants = ReactionComponentSerializer(many=True)
    products = ReactionComponentSerializer(many=True)
    modifiers = ReactionComponentSerializer(many=True)
    subsystem = serializers.SerializerMethodField('get_subsystems')

    class Meta:
        model = Reaction
        fields = ('id', 'name', 'sbo_id', 'equation', 'ec', 'lower_bound', 'upper_bound', 'objective_coefficient',
            'reactants', 'products', 'modifiers', 'compartment', 'subsystem')

    def get_subsystems(self, model):
        ss_ids = SubsystemReaction.objects.filter(reaction=model.id).values_list('subsystem')
        return Subsystem.objects.filter(id__in=ss_ids).values_list('name')

class ReactionSearchSerializer(serializers.ModelSerializer):
    subsystem = serializers.SerializerMethodField('get_subsystems')

    class Meta:
        model = Reaction
        fields = ('id', 'name', 'sbo_id', 'equation', 'ec', 'lower_bound', 'upper_bound', 'objective_coefficient',
            'compartment', 'subsystem')

    def get_subsystems(self, model):
        ss_ids = SubsystemReaction.objects.filter(reaction=model.id).values_list('subsystem')
        return Subsystem.objects.filter(id__in=ss_ids).values_list('name')


# This is a helper class to determine if a component is a currency metabolite
class CurrencyMetaboliteReactionComponent(object):
    def __init__(self, reaction_component, reaction_id):
        self.reaction_component = reaction_component
        self.reaction_id = reaction_id
        self.is_currency_metabolite = self.__is_currency_metabolite__()

    def __is_currency_metabolite__(self):
        for r in self.reaction_component.currency_metabolites.all():
            if r.id == self.reaction_id:
                return True
        return False

class CurrencyMetaboliteReactionComponentSerializer(serializers.Serializer):
    reaction_component = ReactionComponentSerializer(read_only=True)
    is_currency_metabolite = serializers.BooleanField()

class CurrencyMetaboliteSerializer(serializers.ModelSerializer):
    compartment = serializers.StringRelatedField()

    class Meta:
        model = CurrencyMetabolite
        fields = ('reaction_id', 'compartment')

class ExpressionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpressionData
        fields = ('gene_id', 'gene_name', 'transcript_id', 'tissue', 'expression_type', 'level', 'cell_type', 'reliability', 'source')

class InteractionPartnerSerializer(serializers.ModelSerializer):
    modifiers = ReactionComponentSerializer(many=True, read_only=True)
    products = ReactionComponentSerializer(many=True, read_only=True)
    reactants = ReactionComponentSerializer(many=True, read_only=True)
    currency_metabolites = CurrencyMetaboliteSerializer(many=True, read_only=True)

    class Meta:
        model = ReactionComponent
        fields = ('id', 'modifiers', 'products', 'reactants', 'currency_metabolites')

class MetaboliteReactionSerializer(serializers.Serializer):
    reaction_id = serializers.CharField()
    enzyme_role = serializers.CharField()
    subsystem = serializers.SerializerMethodField('get_subsystems')
    reactants = ReactionComponentSerializer(many=True, read_only=True)
    products = ReactionComponentSerializer(many=True, read_only=True)
    modifiers = ReactionComponentSerializer(many=True, read_only=True)

    def get_subsystems(self, model):
        ss_ids = SubsystemReaction.objects.filter(reaction=model.reaction_id).values_list('subsystem')
        return Subsystem.objects.filter(id__in=ss_ids).values_list('name')


class ConnectedMetabolitesSerializer(serializers.Serializer):
    enzyme = ReactionComponentSerializer(read_only=True)
    compartment = serializers.CharField()
    reactions = MetaboliteReactionSerializer(many=True)


class SubsystemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subsystem
        fields = ('name', 'system', 'external_id', 'description')

class CompartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Compartment
        fields = ('name',)

# =======================================================================================

class GEModelFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GEModelFile
        fields = ('path', 'format')

class GEModelReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GEModelReference
        fields = ('title', 'link', 'pubmed', 'year')

class GEModelSetSerializer(serializers.ModelSerializer):
    reference = GEModelReferenceSerializer(many=True, read_only=True)
    class Meta:
        model = GEModelSet
        fields = ('name', 'description', 'reference')

class GEModelSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GEModelSample
        fields = ('organism', 'organ_system', 'tissue', 'cell_line', 'cell_type')


class GEModelSerializer(serializers.ModelSerializer):
    gemodelset = GEModelSetSerializer()
    sample = GEModelSampleSerializer()
    files = GEModelFileSerializer(many=True, read_only=True)
    reference = GEModelReferenceSerializer()

    class Meta:
        model = GEModel
        fields = ('id', 'gemodelset', 'sample', 'label', 'description', 'reaction_count', 'metabolite_count', 'enzyme_count', 'files', 'reference', 'maintained')


class GEModelListSerializer(serializers.ModelSerializer):
    set_name = serializers.SerializerMethodField('get_model_set_name')
    sample = GEModelSampleSerializer()
    year = serializers.SerializerMethodField('get_model_year')

    def get_model_set_name(self, model):
        gg = GEModelSet.objects.get(id=model.gemodelset.id)
        return gg.name

    def get_model_year(self, model):
        return model.reference.year

    class Meta:
        model = GEModel
        fields = ('id','set_name', 'sample', 'label', 'reaction_count', 'metabolite_count', 'enzyme_count', 'maintained', 'year')


# =======================================================================================


class TileSubsystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TileSubsystem
        fields = ('subsystem_id', 'subsystem_name', 'compartment_name', 'x_top_left', 'y_top_left', 'x_bottom_right', 'y_bottom_right',)
