from flask import jsonify, abort
from flask import make_response, request

from hma_backend import app
from hma_backend.models import *


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(405)
def method_not_allowed(error):
    return make_response(jsonify({'error': 'Method not allowed'}), 405)


@app.errorhandler(500)
def internal_server_error(error):
    return make_response(jsonify({'error': 'Internal server error'}), 500)


@app.route("/")
def index():
    msg = ("Welcome to the Human Metabolic Atlas! Please check the API "
           "documentation for usage.")
    return jsonify({'message': msg})


@app.route("/api/v1/models")
def list_models():
    models = MetabolicModel.query.all()
    json_models = [make_public_model(model) for model in models]
    return jsonify({'models': json_models})


@app.route("/api/v1/models/<int:model_id>")
def list_model(model_id):
    model = MetabolicModel.query.get_or_404(model_id)
    return jsonify(make_public_model(model))


def make_public_model(model):
    json = {}
    json['model_id'] = model.id
    json['short_name'] = model.short_name
    json['name'] = model.name
    json['authors'] = [make_public_author(author) for author in model.authors]
    return json


@app.route("/api/v1/authors")
def list_authors():
    authors = Author.query.all()
    json_authors = [make_public_author(author) for author in authors]
    return jsonify({'authors': json_authors})


@app.route("/api/v1/authors/<int:author_id>")
def list_author(author_id):
    author = Author.query.get_or_404(author_id)
    return jsonify(make_public_author(author))


def make_public_author(author):
    json = {}
    json['author_id'] = author.id
    json['given_name'] = author.given_name
    json['family_name'] = author.family_name
    json['email'] = author.email
    json['organization'] = author.organization
    json['models'] = [model.id for model in author.models]
    return json


@app.route("/api/v1/reactions")
def list_reactions():
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    reactions = Reaction.query.limit(limit).offset(offset).all()
    json = {}
    json['offset'] = offset + len(reactions)
    json['limit'] = limit
    json['reactions'] = [make_public_reaction(reaction)
                         for reaction in reactions]
    return jsonify(json)


@app.route("/api/v1/reactions/<string:reaction_id>")
def list_reaction(reaction_id):
    reaction = Reaction.query.get_or_404(reaction_id)
    return jsonify(make_public_reaction(reaction))


def make_public_reaction(reaction):
    json = {}
    json['reaction_id'] = reaction.id
    json['name'] = reaction.name
    json['sbo_id'] = reaction.sbo_id
    json['equation'] = reaction.equation
    json['lower_bound'] = float(reaction.lower_bound)
    json['upper_bound'] = float(reaction.upper_bound)
    json['objective_coefficient'] = float(reaction.objective_coefficient)
    json['reactants'] = [make_public_component(component)
                         for component in reaction.reactants]
    json['products'] = [make_public_component(component)
                        for component in reaction.products]
    json['modifiers'] = [make_public_component(component)
                         for component in reaction.modifiers]
    return json


@app.route("/api/v1/reactions/<string:reaction_id>/reactants")
def list_reaction_reactants(reaction_id):
    reaction = Reaction.query.get_or_404(reaction_id)
    reactants = [make_public_component(reactant)
                 for reactant in reaction.reactants]
    return jsonify({'reactants': reactants})


@app.route("/api/v1/reactions/<string:reaction_id>/reactants/<string:reactant_id>")
def list_reaction_reactant(reaction_id, reactant_id):
    reaction = Reaction.query.get_or_404(reaction_id)
    reactants = [reactant for reactant in reaction.reactants if
                 reactant.id == reactant_id]
    if len(reactants) == 1:
        return jsonify(make_public_component(reactants[0]))
    else:
        abort(404)


@app.route("/api/v1/reactions/<string:reaction_id>/products")
def list_reaction_products(reaction_id):
    reaction = Reaction.query.get_or_404(reaction_id)
    products = [make_public_component(product)
                for product in reaction.products]
    return jsonify({'products': products})


@app.route("/api/v1/reactions/<string:reaction_id>/products/<string:product_id>")
def list_reaction_product(reaction_id, product_id):
    reaction = Reaction.query.get_or_404(reaction_id)
    products = [product for product in reaction.products if
                product.id == product_id]
    if len(products) == 1:
        return jsonify(make_public_component(products[0]))
    else:
        abort(404)


@app.route("/api/v1/reaction_components")
def list_components():
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    components = ReactionComponent.query.limit(limit).offset(offset).all()
    json = {}
    json['limit'] = limit
    json['offset'] = offset + len(components)
    json['reaction_components'] = [make_public_component(component)
                                   for component in components]
    return jsonify(json)


@app.route("/api/v1/reaction_components/<string:component_id>")
def list_component(component_id):
    component = ReactionComponent.query.get_or_404(component_id)
    return jsonify(make_public_component(component))


def make_public_component(component):
    json = {}
    json['component_id'] = component.id
    json['short_name'] = component.short_name
    json['long_name'] = component.long_name
    json['type_code'] = component.type_code
    json['organism'] = component.organism
    json['formula'] = component.formula
    return json
