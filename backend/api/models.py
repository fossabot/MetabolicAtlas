from django.db import models
from django.db.models.fields import Field
from django.db.models import Lookup

@Field.register_lookup
class ILike(Lookup):
    lookup_name = 'ilike'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        # The key word ILIKE make the match case-insensitive according to the active locale.
        # This is not in the SQL standard but is a PostgreSQL extension.
        return '%s ILIKE %s' % (lhs, rhs), params


class GEModelReference(models.Model):
    title = models.TextField()
    link = models.TextField()
    pmid = models.CharField(max_length=20, unique=True, null=True)
    year = models.CharField(max_length=4)

    class Meta:
        db_table = "gemodel_reference"


class GEModelSet(models.Model):
    CATEGORY = (
        ('Species', 'Species'),
        ('Community', 'Community'),
        ('Collection', 'Collection'),
    )
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True)
    reference = models.ManyToManyField(GEModelReference, related_name='gemodelset_references')

    class Meta:
        db_table = "gemodel_set"


class GEModelSample(models.Model):
    organism = models.CharField(max_length=200)
    organ_system = models.CharField(max_length=200, null=True)
    tissue = models.CharField(max_length=200, null=True)
    cell_type = models.CharField(max_length=200, null=True)
    cell_line = models.CharField(max_length=200, null=True)

    unique_together = (('organism', 'organ_system', 'tissue', 'cell_type', 'cell_line'),)

    def __str__(self):
        return "<Sample: {0} {1} {2} {3} {4}>".format(self.organism, self.organ_system, self.tissue, self.cell_type, self.cell_line)

    class Meta:
        db_table = "gemodel_sample"


class GEModelFile(models.Model):
    path = models.CharField(max_length=500, unique=True)
    format = models.CharField(max_length=50)

    class Meta:
        db_table = "gemodel_file"


class GEModel(models.Model):
    gemodelset = models.ForeignKey(GEModelSet, on_delete=models.CASCADE)
    sample = models.ForeignKey(GEModelSample, on_delete=models.CASCADE)
    description = models.TextField(null=True)
    tag = models.CharField(max_length=200, null=True)
    condition = models.CharField(max_length=200, null=True)
    reaction_count = models.IntegerField(default=0, blank=True, null=True)
    metabolite_count = models.IntegerField(default=0, blank=True, null=True)
    gene_count = models.IntegerField(default=0, blank=True, null=True)
    files = models.ManyToManyField(GEModelFile, related_name='gemodel')
    maintained = models.BooleanField(default=False)
    ref = models.ManyToManyField(GEModelReference, related_name='gemodel', blank=True)
    last_update = models.DateField(null=True)
    repo_url = models.CharField(max_length=200, null=True)

    def save(self, *args, **kwargs):
        if not self.gemodelset:
            raise AttributeError("Model set must be specified")
        if not self.sample:
            raise AttributeError("Model sample must be specified")
        if self.reaction_count == 0 and self.metabolite_count == 0 and self.gene_count == 0:
            raise AttributeError("component count cannot be all 0")
        super(GEModel, self).save(*args, **kwargs)

    class Meta:
        db_table = "gemodel"


##########################################################################################################################
##########################################################################################################################
# part of Gems database

class Author(models.Model):
    given_name = models.CharField(max_length=255, blank=False)
    family_name = models.CharField(max_length=255, blank=False)
    email = models.CharField(max_length=255, blank=False)
    organization = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return "<Author: {0} {1}>".format(self.given_name, self.family_name)

    class Meta:
        db_table = "author"

# integrate models!
class GEM(models.Model):
    short_name = models.CharField(max_length=255, blank=False, unique=True)
    full_name = models.CharField(max_length=255, null=True, unique=True)
    description = models.TextField()
    version = models.CharField(max_length=20)
    database_name = models.CharField(max_length=255, blank=False, unique=True)
    condition = models.CharField(max_length=200, null=True)
    reaction_count = models.IntegerField(default=0)
    metabolite_count = models.IntegerField(default=0)
    gene_count = models.IntegerField(default=0)
    date = models.DateField()
    link = models.CharField(max_length=255, null=True)
    chat_link = models.CharField(max_length=255, null=True)
    ref = models.ManyToManyField(GEModelReference, related_name='gem', through='GEMreference', blank=True)
    authors = models.ManyToManyField(Author, related_name='gem', through='GEMAuthor', blank=True)
    sample = models.ForeignKey(GEModelSample, on_delete=models.CASCADE)

    def __str__(self):
        return "<GEM: {0} {1} {2}>".format(self.full_name, self.short_name, self.database_name)

    class Meta:
        db_table = "gem"


class GEMAuthor(models.Model):
    model = models.ForeignKey(GEM, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        db_table = "gem_author"

class GEMreference(models.Model):
    model = models.ForeignKey(GEM, on_delete=models.CASCADE)
    ref = models.ForeignKey(GEModelReference, on_delete=models.CASCADE)

    class Meta:
        db_table = "gem_reference"

##########################################################################################################################
##########################################################################################################################

#
# Full Models
#

class Reaction(models.Model):
    id = models.CharField(max_length=50, primary_key=True) # ID in the SBML/YAML model
    name = models.CharField(max_length=255, null=True)
    equation = models.TextField(blank=False) # string or/and with metabolite ID (should be meta model ID, e.g M_m0125c)
    equation_wname = models.TextField(blank=False)
    ec = models.CharField(max_length=255, null=True)
    lower_bound = models.FloatField()
    upper_bound = models.FloatField()
    objective_coefficient = models.FloatField(null=True)
    gene_rule = models.TextField(null=True) # string or/and with gene ID (can be any unique gene ID)
    gene_rule_wname = models.TextField(null=True) # string or/and with gene name
    subsystem_str = models.CharField(max_length=1000, null=True)
    subsystem = models.ManyToManyField('Subsystem', related_name='reactions', through='SubsystemReaction')
    compartment_str = models.CharField(max_length=255)
    compartment = models.ManyToManyField('Compartment', related_name='reactions', through='ReactionCompartment')
    is_transport = models.BooleanField(default=False)
    is_reversible = models.BooleanField(default=False)
    related_group = models.IntegerField(default=0)

    metabolites = models.ManyToManyField('ReactionComponent', related_name='reactions_as_metabolite', through='ReactionMetabolite')

    def __str__(self):
        return "<Reaction: {0} {1}>".format(self.id, self.name)

    class Meta:
        db_table = "reaction"
        indexes = [
            models.Index(fields=['related_group']),
        ]

class ReactionReference(models.Model):
    reaction = models.ForeignKey('Reaction', db_column='reaction_id', on_delete=models.CASCADE)
    pmid = models.CharField(max_length=25, blank=False)

    def __str__(self):
        return "<ReactionReference: {0}={1}>".format(self.reaction.id, self.pmid)

    class Meta:
        db_table = "reaction_reference"
        unique_together = (('reaction', 'pmid'),)

class ReactionEID(models.Model):
    reaction = models.ForeignKey('Reaction', related_name='external_databases', on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255)
    external_id = models.CharField(max_length=255)
    external_link = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = "reaction_eid"
        unique_together = (('reaction', 'db_name', 'external_id'),)

# corresponds to either metabolite or gene, should be Serialized with the proper serializer
class ReactionComponent(models.Model):
    id = models.CharField(max_length=50, primary_key=True)  # ID in the SBML/YAML model
    name = models.CharField(max_length=255)  # gene name for gene, or metabolite name
    full_name = models.CharField(max_length=255, null=True, unique=True)  # metabolite name with compartment letter
    alt_name1 = models.CharField(max_length=255, null=True)  # can be ORF ID in case of yeast, proteine name, metabolite short_name etc
    alt_name2 = models.CharField(max_length=255, null=True)  # can be ORF ID in case of yeast, proteine name, metabolite short_name etc
    aliases = models.CharField(max_length=2000, null=True)  # alias of gene name (including gene short name) or alias of metabolite name, semi-colon separated values
    component_type = models.CharField(max_length=1, db_index=True)  # 'm' or 'e' for metabolite or gene
    formula = models.CharField(max_length=255, null=True)  # only metabolites have this! should be in metabolite table but will simplify the queries if here
    compartment_str = models.CharField(max_length=255, null=True)
    compartment = models.ForeignKey('Compartment', db_column='compartment', null=True, on_delete=models.CASCADE)
    is_currency = models.BooleanField(default=False) # only for metabolite, should be in metabolite table but will simplify the queries if here

    reactions_as_reactant = models.ManyToManyField(Reaction, related_name='reactants', through='ReactionReactant')
    reactions_as_product = models.ManyToManyField(Reaction, related_name='products', through='ReactionProduct')
    reactions_as_gene = models.ManyToManyField(Reaction, related_name='genes', through='ReactionGene')

    subsystem_metabolite = models.ManyToManyField('Subsystem', related_name='metabolites', through='SubsystemMetabolite')
    subsystem_gene = models.ManyToManyField('Subsystem', related_name='genes', through='SubsystemGene')

    related_compartment_group = models.IntegerField(default=0)  # only for metabolites
    related_formula_group = models.IntegerField(default=0)  # only for metabolites

    compartment_gene = models.ManyToManyField('Compartment', related_name='genes', through='CompartmentGene')

    def __str__(self):
        return "<ReactionComponent: {0}>".format(self.id)

    class Meta:
        db_table = "reaction_component"
        indexes = [
            models.Index(fields=['related_compartment_group']),
            models.Index(fields=['related_formula_group']),
        ]

class ReactionComponentEID(models.Model):
    rc = models.ForeignKey('ReactionComponent', related_name='external_databases', on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255)
    external_id = models.CharField(max_length=255)
    external_link = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = "rc_eid"
        unique_together = (('rc', 'db_name', 'external_id'),)

class Metabolite(models.Model):
    rc = models.OneToOneField(
            'ReactionComponent',
            related_name='metabolite',
            db_column='rc',
            on_delete=models.CASCADE)
    description = models.TextField(null=True)
    function1 = models.CharField(max_length=3000, null=True)
    function2 = models.CharField(max_length=3000, null=True)
    charge = models.FloatField(null=True)
    mass = models.FloatField(null=True)
    mass_avg = models.FloatField(null=True)
    inchi = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = "metabolite"

class Gene(models.Model):
    rc = models.OneToOneField('ReactionComponent',
        related_name='gene', db_column='rc', on_delete=models.CASCADE)
    function1 = models.CharField(max_length=3000, null=True)
    function2 = models.CharField(max_length=3000, null=True)
    ec = models.CharField(max_length=255, null=True)
    catalytic_activity = models.CharField(max_length=2000, null=True)
    cofactor = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = "gene"

'''
class CoFactor(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "cofactor"
'''

class Subsystem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    name_id = models.CharField(max_length=100, unique=True) # renamed to id when serialized
    system = models.CharField(max_length=100)
    subsystem_svg = models.ForeignKey('SubsystemSvg', on_delete=models.SET_NULL, null=True, related_name='+')
    description = models.CharField(max_length=3000, null=True)
    compartment = models.ManyToManyField('Compartment', related_name='s_compartments', through='SubsystemCompartment')
    reaction_count = models.IntegerField(default=0)
    metabolite_count = models.IntegerField(default=0)
    unique_metabolite_count = models.IntegerField(default=0)
    gene_count = models.IntegerField(default=0)
    compartment_count = models.IntegerField(default=0)

    compounds = models.ManyToManyField('ReactionComponent', related_name='subsystems', through='SubsystemReactionComponent')

    class Meta:
        db_table = "subsystem"

class SubsystemEID(models.Model):
    subsystem = models.ForeignKey('Subsystem', related_name='external_databases', on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255)
    external_id = models.CharField(max_length=255)
    external_link = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = "subsystem_eid"
        unique_together = (('subsystem', 'db_name', 'external_id'),)

class SubsystemSvg(models.Model):
    name = models.CharField(max_length=100, unique=True)
    name_id = models.CharField(max_length=100, unique=True)
    subsystem = models.ForeignKey('Subsystem',on_delete=models.CASCADE, related_name='+')
    filename = models.CharField(max_length=100, unique=True)
    reaction_count = models.IntegerField(default=0)
    metabolite_count = models.IntegerField(default=0)
    unique_metabolite_count = models.IntegerField(default=0)
    gene_count = models.IntegerField(default=0)
    compartment_count = models.IntegerField(default=0)
    sha = models.CharField(max_length=256, unique=True, null=True)

    class Meta:
        db_table = "subsystemsvg"

class Compartment(models.Model):
    name = models.CharField(max_length=50, unique=True)
    name_id = models.CharField(max_length=50, unique=True) # renamed to id when serialized
    letter_code = models.CharField(max_length=3, unique=True)
    subsystem = models.ManyToManyField('Subsystem', related_name='c_subsystems', through='SubsystemCompartment')
    compartment_svg = models.ForeignKey('CompartmentSvg', on_delete=models.SET_NULL, null=True, related_name='+')
    reaction_count = models.IntegerField(default=0)
    subsystem_count = models.IntegerField(default=0)
    metabolite_count = models.IntegerField(default=0)
    unique_metabolite_count = models.IntegerField(default=0)  # = metabolite_count
    gene_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "compartment"

class CompartmentSvg(models.Model):
    name = models.CharField(max_length=50, unique=True)
    name_id = models.CharField(max_length=50, unique=True)
    compartment = models.ForeignKey('Compartment', on_delete=models.CASCADE, related_name='+')
    subsystem = models.ManyToManyField('Subsystem', related_name='csvg_subsystems', through='SubsystemCompartmentSvg')
    filename = models.CharField(max_length=50, unique=True)
    letter_code = models.CharField(max_length=3, unique=True)
    reaction_count = models.IntegerField(default=0)
    subsystem_count = models.IntegerField(default=0)
    metabolite_count = models.IntegerField(default=0)
    unique_metabolite_count = models.IntegerField(default=0)
    gene_count = models.IntegerField(default=0)
    sha = models.CharField(max_length=256, unique=True, null=True)

    class Meta:
        db_table = "compartmentsvg"

class GemBrowserTile(object):
    def __init__(self, compartment, subsystems, reactions, metabolites, genes):
        self.compartment = compartment
        self.subsystems = subsystems
        self.reactions = reactions
        self.metabolites = metabolites
        self.genes = genes

#
# Relationships
#

'''
class GeneCoFactor(models.Model):
    gene = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    cofactor = models.ForeignKey(CoFactor, on_delete=models.CASCADE)

    class Meta:
        db_table = "gene_cofactor"
'''

class ReactionReactant(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    reactant = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    stoichiometry = models.FloatField()

    class Meta:
        db_table = "reaction_reactant"
        unique_together = (('reaction', 'reactant'),)

class ReactionProduct(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    product = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    stoichiometry = models.FloatField()

    class Meta:
        db_table = "reaction_product"
        unique_together = (('reaction', 'product'),)


class ReactionGene(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    gene = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_gene"
        unique_together = (('reaction', 'gene'),)

class ReactionMetabolite(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_metabolite"
        unique_together = (('reaction', 'rc'),)

class CurrencyMetaboliteCompartment(models.Model):
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    compartment = models.ForeignKey(Compartment, on_delete=models.CASCADE)

    class Meta:
        db_table = "currency_metabolite_compartment"
        unique_together = (('rc', 'compartment'),)


class CompartmentGene(models.Model):
    compartment = models.ForeignKey(Compartment, on_delete=models.CASCADE)
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)

    class Meta:
        db_table = "compartment_gene"
        unique_together = (('compartment', 'rc'),)


class SubsystemReaction(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    subsystem = models.ForeignKey(Subsystem, on_delete=models.CASCADE)

    class Meta:
        db_table = "subsystem_reaction"
        unique_together = (('reaction', 'subsystem'),)

class SubsystemMetabolite(models.Model):
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    subsystem = models.ForeignKey(Subsystem, on_delete=models.CASCADE)

    class Meta:
        db_table = "subsystem_metabolite"
        unique_together = (('rc', 'subsystem'),)

class SubsystemGene(models.Model):
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    subsystem = models.ForeignKey(Subsystem, on_delete=models.CASCADE)

    class Meta:
        db_table = "subsystem_gene"
        unique_together = (('rc', 'subsystem'),)

class SubsystemReactionComponent(models.Model):
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    subsystem = models.ForeignKey(Subsystem, on_delete=models.CASCADE)

    class Meta:
        db_table = "subsystem_rc"
        unique_together = (('rc', 'subsystem'),)

class SubsystemCompartment(models.Model):
    subsystem = models.ForeignKey(Subsystem, on_delete=models.CASCADE)
    compartment = models.ForeignKey(Compartment, on_delete=models.CASCADE)

    class Meta:
        db_table = "subsystem_compartment"

class ReactionCompartment(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    compartment = models.ForeignKey(Compartment, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_compartment"
        unique_together = (('reaction', 'compartment'),)

class ReactionComponentCompartment(models.Model):
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    compartment = models.ForeignKey(Compartment, on_delete=models.CASCADE)

    class Meta:
        db_table = "rc_compartment"
        unique_together = (('rc', 'compartment'),)

class CompartmentSvgGene(models.Model):
    compartmentsvg = models.ForeignKey(CompartmentSvg, on_delete=models.CASCADE)
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)

    class Meta:
        db_table = "compartmentsvg_gene"
        unique_together = (('compartmentsvg', 'rc'),)

class ReactionCompartmentSvg(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    compartmentsvg = models.ForeignKey(CompartmentSvg, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_compartmentsvg"
        unique_together = (('reaction', 'compartmentsvg'),)

class ReactionComponentCompartmentSvg(models.Model):
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    compartmentsvg = models.ForeignKey(CompartmentSvg, on_delete=models.CASCADE)

    class Meta:
        db_table = "rc_compartmentsvg"
        unique_together = (('rc', 'compartmentsvg'),)

class ReactionSubsystemSvg(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    subsystemsvg = models.ForeignKey(SubsystemSvg, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_subsystemsvg"
        unique_together = (('reaction', 'subsystemsvg'),)

class ReactionComponentSubsystemSvg(models.Model):
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    subsystemsvg = models.ForeignKey(SubsystemSvg, on_delete=models.CASCADE)

    class Meta:
        db_table = "rc_subsystemsvg"
        unique_together = (('rc', 'subsystemsvg'),)

class SubsystemSvgGene(models.Model):
    subsystemsvg = models.ForeignKey(SubsystemSvg, on_delete=models.CASCADE)
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)

    class Meta:
        db_table = "subsystemsvg_gene"
        unique_together = (('subsystemsvg', 'rc'),)

# relation subsystem / compartment in SVGs was previously found in TilesSubsystems
class SubsystemCompartmentSvg(models.Model):
    subsystem = models.ForeignKey(Subsystem, on_delete=models.CASCADE)
    compartmentsvg = models.ForeignKey(CompartmentSvg, on_delete=models.CASCADE)

    class Meta:
        db_table = "subsystem_compartmentsvg"
        unique_together = (('subsystem', 'compartmentsvg'),)

##########################################################################################################################
##########################################################################################################################


class HpaTissue(models.Model):
    index = models.IntegerField(primary_key=True)
    tissue = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "hpa_tissue"

class HpaProteinLevel(models.Model):
    rc = models.OneToOneField(ReactionComponent, on_delete=models.CASCADE, primary_key=True)
    levels = models.CharField(max_length=1000)

    class Meta:
        db_table = "hpa_protein_level"
