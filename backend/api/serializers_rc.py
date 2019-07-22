from rest_framework import serializers
import api.models as APImodels
from django.db import models
import re

import logging



class MetaboliteSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.Metabolite
        fields = ('mass', 'kegg', 'charge', 'chebi', 'inchi', 'hmdb_description', 'hmdb_link', 'hmdb_function', 'pubchem_link')

class MetaboliteSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.Metabolite
        fields = ('kegg', 'hmdb', 'hmdb_name', 'mass')

class GeneSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.Gene
        fields = ('function', 'catalytic_activity', 'ensembl_link', 'uniprot_acc', 'ncbi')

class GeneSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.Gene
        fields = ('uniprot_acc',)

# ================================================================================

# common serializers, map the name of the db column, should not be serve by swagger queries

class ReactionComponentBasicSerializer(serializers.ModelSerializer):
    compartment = serializers.SerializerMethodField('read_compartment')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'full_name', 'aliases', 'formula', 'compartment')

    def read_compartment(self, model):
        return model.compartment_str


class ReactionComponentLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'full_name')


class ReactionComponentRTSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'full_name', 'compartment_str')


class ReactionComponentSerializer(ReactionComponentBasicSerializer):
    class Meta(ReactionComponentBasicSerializer.Meta):
        model = APImodels.ReactionComponent
        fields = ReactionComponentBasicSerializer.Meta.fields + \
            ('is_currency', 'alt_name1', 'alt_name2', 'external_id1', 'external_id2', 'external_id3', 'external_id4',
                'external_id5', 'external_id6', 'external_id7', 'external_id8')


class GeneReactionComponentSearchSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('read_name')
    subsystem = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
        source='subsystem_gene'
    )
    compartment = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
        source='compartment_gene',
     )

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'subsystem', 'compartment')

    def read_name(self, model):
        return model.name if model.name else None


class MetaboliteReactionComponentSearchSerializer(serializers.ModelSerializer):
    compartment = serializers.SerializerMethodField('read_compartment')
    subsystem = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
        source='subsystem_metabolite'
    )

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'formula', 'subsystem', 'compartment')

    def read_compartment(self, model):
        return model.compartment_str


class GeneReactionComponentSerializer(ReactionComponentSerializer):
    function1 = serializers.SerializerMethodField('read_function1')
    function2 = serializers.SerializerMethodField('read_function2')
    ec =  serializers.SerializerMethodField('read_ec')
    catalytic_activity = serializers.SerializerMethodField('read_catalytic_activity')
    cofactor = serializers.SerializerMethodField('read_cofactor')
    name_link = serializers.SerializerMethodField('read_name_link')

    external_link1 = serializers.SlugRelatedField(
        read_only=True,
        slug_field='model.gene.external_link1',
    )

    # external_link1 = serializers.SerializerMethodField('read_external_link1')
    external_link2 = serializers.SerializerMethodField('read_external_link2')
    external_link3 = serializers.SerializerMethodField('read_external_link3')
    external_link4 = serializers.SerializerMethodField('read_external_link4')
    external_link5 = serializers.SerializerMethodField('read_external_link5')
    external_link6 = serializers.SerializerMethodField('read_external_link6')
    external_link7 = serializers.SerializerMethodField('read_external_link7')
    external_link8 = serializers.SerializerMethodField('read_external_link8')

    class Meta(ReactionComponentSerializer.Meta):
        model = APImodels.ReactionComponent
        fields = ReactionComponentSerializer.Meta.fields + \
            ('function1', 'function2', 'ec', 'catalytic_activity', 'cofactor', 'name_link', 'external_link1', 'external_link2', 'external_link3', 'external_link4',
                'external_link5', 'external_link6', 'external_link7', 'external_link8',)

    def read_function1(self, model):
        return model.gene.function1 if hasattr(model, 'gene') else None

    def read_function2(self, model):
        return model.gene.function2 if hasattr(model, 'gene') else None

    def read_ec(self, model):
        return model.gene.ec if hasattr(model, 'gene') else None

    def read_catalytic_activity(self, model):
        return model.gene.catalytic_activity if hasattr(model, 'gene') else None

    def read_cofactor(self, model):
        return model.gene.cofactor if hasattr(model, 'gene') else None

    def read_name_link(self, model):
        return model.gene.name_link if hasattr(model, 'gene') else None

    def read_external_link1(self, model):
        return model.gene.external_link1 if hasattr(model, 'gene') else None

    def read_external_link2(self, model):
        return model.gene.external_link2 if hasattr(model, 'gene') else None

    def read_external_link3(self, model):
        return model.gene.external_link3 if hasattr(model, 'gene') else None

    def read_external_link4(self, model):
        return model.gene.external_link4 if hasattr(model, 'gene') else None

    def read_external_link5(self, model):
        return model.gene.external_link5 if hasattr(model, 'gene') else None

    def read_external_link6(self, model):
        return model.gene.external_link6 if hasattr(model, 'gene') else None

    def read_external_link7(self, model):
        return model.gene.external_link7 if hasattr(model, 'gene') else None

    def read_external_link8(self, model):
        return model.gene.external_link8 if hasattr(model, 'gene') else None


class MetaboliteReactionComponentSerializer(ReactionComponentSerializer):
    description = serializers.SerializerMethodField('read_description')
    function1 = serializers.SerializerMethodField('read_function1')
    function2 = serializers.SerializerMethodField('read_function2')
    charge = serializers.SerializerMethodField('read_charge')
    mass =  serializers.SerializerMethodField('read_mass')
    mass_avg =  serializers.SerializerMethodField('read_mass_avg')
    inchi =  serializers.SerializerMethodField('read_inchi')
    name_link =  serializers.SerializerMethodField('read_name_link')
    external_link1 = serializers.SerializerMethodField('read_external_link1')
    external_link2 = serializers.SerializerMethodField('read_external_link2')
    external_link3 = serializers.SerializerMethodField('read_external_link3')
    external_link4 = serializers.SerializerMethodField('read_external_link4')
    external_link5 = serializers.SerializerMethodField('read_external_link5')
    external_link6 = serializers.SerializerMethodField('read_external_link6')
    external_link7 = serializers.SerializerMethodField('read_external_link7')
    external_link8 = serializers.SerializerMethodField('read_external_link8')

    class Meta(ReactionComponentSerializer.Meta):
        model = APImodels.ReactionComponent
        fields = ReactionComponentSerializer.Meta.fields + \
            ('description', 'function1', 'function2',  'charge', 'mass', 'mass_avg', 'inchi', 'name_link', 'external_link1', 'external_link2', 'external_link3', 'external_link4',
                'external_link5', 'external_link6', 'external_link7', 'external_link8',)

    def read_description(self, model):
        return model.metabolite.description if hasattr(model, 'metabolite') else None

    def read_function1(self, model):
        return model.metabolite.function1 if hasattr(model, 'metabolite') else None

    def read_function2(self, model):
        return model.metabolite.function2 if hasattr(model, 'metabolite') else None

    def read_charge(self, model):
        return model.metabolite.charge if hasattr(model, 'metabolite') else None

    def read_mass(self, model):
        return model.metabolite.mass if hasattr(model, 'metabolite') else None

    def read_mass_avg(self, model):
        return model.metabolite.mass_avg if hasattr(model, 'metabolite') else None

    def read_inchi(self, model):
        return model.metabolite.inchi if hasattr(model, 'metabolite') else None

    def read_name_link(self, model):
        return model.metabolite.name_link if hasattr(model, 'metabolite') else None

    def read_external_link1(self, model):
        return model.metabolite.external_link1 if hasattr(model, 'metabolite') else None

    def read_external_link2(self, model):
        return model.metabolite.external_link2 if hasattr(model, 'metabolite') else None

    def read_external_link3(self, model):
        return model.metabolite.external_link3 if hasattr(model, 'metabolite') else None

    def read_external_link4(self, model):
        return model.metabolite.external_link4 if hasattr(model, 'metabolite') else None

    def read_external_link5(self, model):
        return model.metabolite.external_link5 if hasattr(model, 'metabolite') else None

    def read_external_link6(self, model):
        return model.metabolite.external_link6 if hasattr(model, 'metabolite') else None

    def read_external_link7(self, model):
        return model.metabolite.external_link7 if hasattr(model, 'metabolite') else None

    def read_external_link8(self, model):
        return model.metabolite.external_link8 if hasattr(model, 'metabolite') else None

# =====================================================================================

# custom serializers for HMR

class HmrGeneReactionComponentLiteSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('read_name')
    description = serializers.SerializerMethodField('read_description')
    gene_synonyms = serializers.SerializerMethodField('read_gene_synonyms')
    ec =  serializers.SerializerMethodField('read_ec')
    hpa_id = serializers.SerializerMethodField('read_hpa')
    uniprot_id = serializers.SerializerMethodField('read_uniprot')
    ncbi_id = serializers.SerializerMethodField('read_ncbi')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'description', 'gene_synonyms', 'ec', 'hpa_id', 'uniprot_id', 'ncbi_id',)

    def read_name(self, model):
        return model.name if model.name else None

    def read_description(self, model):
        return model.alt_name1

    def read_gene_synonyms(self, model):
        return model.aliases

    def read_ec(self, model):
        return model.gene.ec if hasattr(model, 'gene') else None

    def read_hpa(self, model):
        return model.external_id3

    def read_uniprot(self, model):
        return model.external_id2

    def read_ncbi(self, model):
        return model.external_id1


class HmrGeneReactionComponentSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('read_name')
    description = serializers.SerializerMethodField('read_description')
    gene_synonyms = serializers.SerializerMethodField('read_gene_synonyms')
    function =  serializers.SerializerMethodField('read_function')
    ec =  serializers.SerializerMethodField('read_ec')
    catalytic_activity =  serializers.SerializerMethodField('read_catalytic_activity')
    cofactor = serializers.SerializerMethodField('read_cofactor')
    hpa_id = serializers.SerializerMethodField('read_hpa')
    hpa_link =  serializers.SerializerMethodField('read_hpa_link')
    uniprot_id = serializers.SerializerMethodField('read_uniprot')
    uniprot_link =  serializers.SerializerMethodField('read_uniprot_link')
    ncbi_id = serializers.SerializerMethodField('read_ncbi')
    ncbi_link =  serializers.SerializerMethodField('read_ncbi_link')
    ensembl_link =  serializers.SerializerMethodField('read_ensembl_link')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'description', 'gene_synonyms') + \
        ('function', 'ec', 'catalytic_activity', 'cofactor', 'hpa_id', 'hpa_link') + \
        ('uniprot_id', 'uniprot_link', 'ncbi_id', 'ncbi_link', 'ensembl_link',)

    def read_name(self, model):
        return model.name if model.name else None

    def read_description(self, model):
        return model.alt_name1

    def read_gene_synonyms(self, model):
        return model.aliases

    def read_function(self, model):
        return model.gene.function1 if hasattr(model, 'gene') else None

    def read_ec(self, model):
        return model.gene.ec if hasattr(model, 'gene') else None

    def read_catalytic_activity(self, model):
        return model.gene.catalytic_activity if hasattr(model, 'gene') else None

    def read_cofactor(self, model):
        return model.gene.cofactor if hasattr(model, 'gene') else None

    def read_uniprot(self, model):
        return model.external_id2

    def read_uniprot_link(self, model):
        return model.gene.external_link2 if hasattr(model, 'gene') else None

    def read_hpa(self, model):
        return model.external_id3

    def read_hpa_link(self, model):
        return model.gene.external_link3 if hasattr(model, 'gene') else None

    def read_ncbi(self, model):
        return model.external_id1

    def read_ncbi_link(self, model):
        return model.gene.external_link1 if hasattr(model, 'gene') else None

    def read_ensembl_link(self, model):
        return model.gene.name_link if hasattr(model, 'gene') else None


class GeneReactionComponentInteractionPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name',)


# -----------------------------------------------------------------------------------------------------


class HmrMetaboliteReactionComponentLiteSerializer(serializers.ModelSerializer):
    aliases = serializers.SerializerMethodField('read_aliases')
    inchi =  serializers.SerializerMethodField('read_inchi')
    hmdb_id =  serializers.SerializerMethodField('read_hmdb')
    chebi_id = serializers.SerializerMethodField('read_chebi')
    mnxref_id = serializers.SerializerMethodField('read_mnxref')
    compartment = serializers.SerializerMethodField('read_compartment')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'full_name', 'aliases', 'inchi', 'hmdb_id', 'chebi_id', 'mnxref_id', 'compartment')

    def read_aliases(self, model):
        return model.aliases

    def read_inchi(self, model):
        return model.metabolite.inchi if hasattr(model, 'metabolite') else None

    def read_hmdb(self, model):
        return model.external_id1

    def read_chebi(self, model):
        return model.external_id2

    def read_mnxref(self, model):
        return model.external_id3

    def read_compartment(self, model):
        return model.compartment_str


class HmrMetaboliteReactionComponentSerializer(serializers.ModelSerializer):
    alt_name = serializers.SerializerMethodField('read_alt_name')
    aliases = serializers.SerializerMethodField('read_aliases')
    description = serializers.SerializerMethodField('read_description')
    function = serializers.SerializerMethodField('read_function')
    formula = serializers.SerializerMethodField('read_formula')
    charge = serializers.SerializerMethodField('read_charge')
    mass =  serializers.SerializerMethodField('read_mass')
    mass_avg =  serializers.SerializerMethodField('read_mass_avg')
    inchi =  serializers.SerializerMethodField('read_inchi')
    hmdb_id =  serializers.SerializerMethodField('read_hmdb')
    hmdb_link = serializers.SerializerMethodField('read_hmdb_link')
    chebi_id = serializers.SerializerMethodField('read_chebi')
    chebi_link = serializers.SerializerMethodField('read_chebi_link')
    mnxref_id = serializers.SerializerMethodField('read_mnxref')
    mnxref_link = serializers.SerializerMethodField('read_mnxref_link')
    compartment = serializers.SerializerMethodField('read_compartment')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'alt_name', 'aliases') + \
        ('description', 'function', 'formula', 'charge', 'mass', 'mass_avg', 'inchi') + \
        ('hmdb_id', 'hmdb_link', 'chebi_id', 'chebi_link', 'mnxref_id', 'mnxref_link', 'compartment')

    def read_alt_name(self, model):
        return model.alt_name1

    def read_aliases(self, model):
        return model.aliases

    def read_description(self, model):
        return model.metabolite.description if hasattr(model, 'metabolite') else None

    def read_function(self, model):
        return model.metabolite.function1 if hasattr(model, 'metabolite') else None

    def read_formula(self, model):
        return model.formula

    def read_charge(self, model):
        return model.metabolite.charge if hasattr(model, 'metabolite') else None

    def read_mass(self, model):
        return model.metabolite.mass if hasattr(model, 'metabolite') else None

    def read_mass_avg(self, model):
        return model.metabolite.mass_avg if hasattr(model, 'metabolite') else None

    def read_inchi(self, model):
        return model.metabolite.inchi if hasattr(model, 'metabolite') else None

    def read_hmdb(self, model):
        return model.external_id1

    def read_hmdb_link(self, model):
        return model.metabolite.external_link1 if hasattr(model, 'metabolite') else None

    def read_chebi(self, model):
        return model.external_id2

    def read_chebi_link(self, model):
        return model.metabolite.external_link2 if hasattr(model, 'metabolite') else None

    def read_mnxref(self, model):
        return model.external_id3

    def read_mnxref_link(self, model):
        return model.metabolite.external_link3 if hasattr(model, 'metabolite') else None

    def read_compartment(self, model):
        return model.compartment_str


class MetaboliteReactionComponentInteractionPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'compartment_str')


# ==========================================================================================

# custom serializers for yeast

# ==========================================================================================

# custom serializers for the GEM browser Tiles
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


class GemBrowserTileMetaboliteSerializer(serializers.ModelSerializer):
    compartment = serializers.SerializerMethodField('read_compartment')
    reaction_count = serializers.SerializerMethodField('read_reaction_count')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'formula', 'compartment', 'reaction_count')

    def read_compartment(self, model):
        return model.compartment_str

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
