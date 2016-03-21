from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from hma_backend import db


model_authors = db.Table('model_authors',
                      db.Column('model_id', ForeignKey('metabolic_model.id'),
                             primary_key=True),
                      db.Column('author_id', ForeignKey('author.id'),
                             primary_key=True))

class MetabolicModel(db.Model):
    __tablename__ = "metabolic_model"

    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    authors = relationship("Author", secondary=model_authors,
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


class Reaction(db.Model):
    __tablename__ = "reaction"

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255))
    sbo_id = db.Column(db.String(255))
    equation = db.Column(db.Text(), nullable=False)
    lower_bound = db.Column(db.Numeric)
    upper_bound = db.Column(db.Numeric)
    objective_coefficient = db.Column(db.Numeric)
    reactants = relationship("ReactionComponent", secondary=reaction_reactants)
    products = relationship("ReactionComponent", secondary=reaction_products)
    modifiers = relationship("ReactionComponent", secondary=reaction_modifiers)

    def __repr__(self):
        return "<Reaction: {0}>".format(self.id)


class ReactionComponent(db.Model):
    __tablename__ = "reaction_component"

    id = db.Column(db.String(50), primary_key=True)
    short_name = db.Column(db.String(255))
    long_name = db.Column(db.String(255))
    type_code = db.Column(db.Integer)
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

    def __repr__(self):
        return "<ReactionComponent: {0}>".format(self.id)
