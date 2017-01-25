from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import relationship

from hma_backend import db


model_authors = db.Table('model_authors',
                      db.Column('model_id', ForeignKey('metabolic_model.id'),
                             primary_key=True),
                      db.Column('author_id', ForeignKey('author.id'),
                             primary_key=True))

model_reactions = db.Table('model_reactions',
                           db.Column('model_id', ForeignKey('metabolic_model.id'),
                                     primary_key=True),
                           db.Column('reaction_id', ForeignKey('reaction.id'),
                                     primary_key=True))

# connect the reaction components to the right type...
reactioncomponent_metabolite = db.Table('reactioncomponent_metabolites',
                      db.Column('component_id', ForeignKey('reaction_component.id'),
                             primary_key=True),
                      db.Column('metabolite_id', ForeignKey('metabolites.id'),
                             primary_key=True))

reactioncomponent_enzyme = db.Table('reactioncomponent_enzymes',
                      db.Column('component_id', ForeignKey('reaction_component.id'),
                             primary_key=True),
                      db.Column('enzyme_id', ForeignKey('enzymes.id'),
                             primary_key=True))

class MetabolicModel(db.Model):
    __tablename__ = "metabolic_model"

    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    authors = relationship("Author", secondary=model_authors,
                           back_populates="models")
    reactions = relationship("Reaction", secondary=model_reactions,
                             back_populates="models")

    def __repr__(self):
        return "<MetabolicModel: {0}>".format(self.short_name)


class Author(db.Model):
    __tablename__ = "author"

    id = db.Column(db.Integer, primary_key=True)
    given_name = db.Column(db.String(255), nullable=False)
    family_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    organization = db.Column(db.String(255), nullable=False)
    models = relationship("MetabolicModel", secondary=model_authors,
                          back_populates="authors")

    def __repr__(self):
        return "<Author: {0} {1}>".format(self.given_name, self.family_name)


reaction_reactants = db.Table("reaction_reactants",
                        db.Column('reaction_id', ForeignKey('reaction.id'),
                                  primary_key=True),
                        db.Column('reactant_id',
                                  ForeignKey('reaction_component.id'),
                                  primary_key=True))

reaction_products = db.Table("reaction_products",
                       db.Column('reaction_id', ForeignKey('reaction.id'),
                                 primary_key=True),
                       db.Column('product_id',
                                 ForeignKey('reaction_component.id'),
                                 primary_key=True))

reaction_modifiers = db.Table("reaction_modifiers",
                        db.Column('reaction_id', ForeignKey('reaction.id'),
                                  primary_key=True),
                        db.Column('modifier_id',
                                  ForeignKey('reaction_component.id'),
                                  primary_key=True))

currency_metabolites = db.Table("currency_metabolites",
                                db.Column('component_id',
                                          ForeignKey('reaction_component.id'),
                                          primary_key=True),
                                db.Column('reaction_id',
                                          ForeignKey('reaction.id'),
                                          primary_key=True))



class Reaction(db.Model):
    __tablename__ = "reaction"

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255))
    sbo_id = db.Column(db.String(255))
    equation = db.Column(db.Text(), nullable=False)
    ec = db.Column(db.String(255))
    lower_bound = db.Column(db.Numeric)
    upper_bound = db.Column(db.Numeric)
    objective_coefficient = db.Column(db.Numeric)
    reactants = relationship("ReactionComponent", secondary=reaction_reactants)
    products = relationship("ReactionComponent", secondary=reaction_products)
    modifiers = relationship("ReactionComponent", secondary=reaction_modifiers)
    currency_metabolites = relationship("ReactionComponent",
                                        secondary=currency_metabolites)
    models = relationship("MetabolicModel", secondary=model_reactions,
                          back_populates="reactions")

    def __repr__(self):
        return "<Reaction: {0}>".format(self.id)

class ReactionComponent(db.Model):
    __tablename__ = "reaction_component"

    __table_args__ = (
        Index('reaction_component_search_idx', 'id', 'short_name', 'long_name',
              postgresql_ops={
                  'id': 'gin_trgm_ops',
                  'short_name': 'gin_trgm_ops',
                  'long_name': 'gin_trgm_ops'
              },
              postgresql_using='gin'),
    )

    id = db.Column(db.String(50), primary_key=True)
    short_name = db.Column(db.String(255))
    long_name = db.Column(db.String(255))
    component_type = db.Column(db.String(50), index=True)
    organism = db.Column(db.String(255))
    formula = db.Column(db.String(255))

    reactions_as_reactant = relationship("Reaction",
                                         secondary=reaction_reactants,
                                         back_populates="reactants")
    reactions_as_product = relationship("Reaction",
                                         secondary=reaction_products,
                                         back_populates="products")
    reactions_as_modifier = relationship("Reaction",
                                         secondary=reaction_modifiers,
                                         back_populates="modifiers")

    currency_metabolites = relationship("Reaction",
                                        secondary=currency_metabolites,
                                        back_populates="currency_metabolites")

    compartment = db.Column(db.Integer, ForeignKey("compartment.id"),
                            nullable=True)

    def __repr__(self):
        return "<ReactionComponent: {0}>".format(self.id)


class ReactionComponentAnnotation(db.Model):
    __tablename__ = "reaction_component_annotations"
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.String(50), ForeignKey(ReactionComponent.id))
    annotation_type = db.Column(db.String(50))
    annotation = db.Column(db.String(700)) # some of the functions are quite long, for example for uniprot P05091 (-> E_989)


class Compartment(db.Model):
    __tablename__ = "compartment"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class ExpressionData(db.Model):
    __tablename__ = "expression_data"

    __table_args__ = (
        Index('antibody_profile_search_idx', 'id', 'gene_id', 'gene_name',
              postgresql_ops={
                  'id': 'gin_trgm_ops',
                  'gene_id': 'gin_trgm_ops',
                  'gene_name': 'gin_trgm_ops'
              },
              postgresql_using='gin'),
        Index('tissue_filter_idx', 'tissue', 'expression_type',
              postgresql_ops={
                  'tissue': 'gin_trgm_ops',
                  'expression_type': 'gin_trgm_ops'
              },
              postgresql_using='gin'),
    )

    # FIXME: ForeignKey must be unique, so we can't use long_name here :(
    id = db.Column(db.String(50), ForeignKey(ReactionComponent.id),
                   primary_key=True)
    gene_id = db.Column(db.String(35), primary_key=True)
    gene_name = db.Column(db.String(255))
    transcript_id = db.Column(db.String(35), primary_key=True)
    tissue = db.Column(db.String(100), primary_key=True)
    bto = db.Column(db.String(20), primary_key=True)
    cell_type = db.Column(db.String(255), primary_key=True)
    level = db.Column(db.String(30))
    expression_type = db.Column(db.String(35), index=True)
    reliability = db.Column(db.String(35))
    source = db.Column(db.String(45))


class Metabolite(db.Model):
    __tablename__  = "metabolites"
    id = db.Column(db.Integer, primary_key=True)
    hmdb = db.Column(db.String(10))
    formula = db.Column(db.String(50))
    charge = db.Column(db.Numeric)
    mass = db.Column(db.Numeric)
    #category = db.Column(db.String(15))
    kegg = db.Column(db.String(50))
    chebi = db.Column(db.String(50))
    inchi = db.Column(db.String(255))
    bigg = db.Column(db.String(55))
    # which reaction component(s) are this metabolite 'connected' to?
    components = relationship("ReactionComponent",
        secondary=reactioncomponent_metabolite)

class Enzyme(db.Model):
    __tablename__ = "enzymes"
    id = db.Column(db.Integer, primary_key=True)
    uniprot_acc = db.Column(db.String(35), unique=True)
    protein_name = db.Column(db.String(150))
    short_name = db.Column(db.String(75))
    ec = db.Column(db.String(100))
    kegg = db.Column(db.String(125))
    function = db.Column(db.String(6000))
    catalytic_activity = db.Column(db.String(700))
    # which reaction component(s) are this enzyme 'connected' to?
    components = relationship("ReactionComponent",
        secondary=reactioncomponent_enzyme)
