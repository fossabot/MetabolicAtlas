from flask import jsonify, abort
from flask import make_response, request
from flask_swagger import swagger
from sqlalchemy import or_

from hma_backend import app
from hma_backend.models import *


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin','*')
    response.headers.add('Access-Control-Allow-Headers',
                         "Authorization, Content-Type")
    response.headers.add('Access-Control-Expose-Headers', "Authorization")
    response.headers.add('Access-Control-Allow-Methods',
                         "GET, POST, PUT, DELETE, OPTIONS")
    response.headers.add('Access-Control-Allow-Credentials', "true")
    response.headers.add('Access-Control-Max-Age', 60 * 60 * 24 * 20)
    return response


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


@app.route("/api/v1/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "Human Metabolic Atlas"
    swag['info']['description'] = ("This is an API for accessing "
                                   "metabolic models")
    return jsonify(swag)


@app.route("/api/v1/models")
def list_models():
    """
    List models
    ---
    tags:
      - Models
    responses:
      200:
        description: Returns a list of Models
        schema:
          type: array
          items:
            $ref: "#/definitions/Model"
    """
    models = MetabolicModel.query.all()
    json_models = [make_public_model(model) for model in models]
    return jsonify({'models': json_models})


@app.route("/api/v1/models/<int:model_id>")
def list_model(model_id):
    """
    Find model by ID
    ---
    tags:
      - Models
    definitions:
      - schema:
          id: Model
          type: object
          properties:
            model_id:
              type: integer
              description: Model ID
              default: 1
            short_name:
              type: string
              description: Short model name
              default: HMR2.0
            name:
              type: string
              description: Model name
              default: Human Metabolic Reaction (2.0) Database
            authors:
              type: array
              items:
                $ref: "#/definitions/Author"
    parameters:
      - in: path
        name: model_id
        type: integer
        format: int32
        required: true
        description: Model ID
    responses:
      200:
        description: Returns the specified model
        schema:
          $ref: "#/definitions/Model"
      404:
        description: Model not found
    """
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
    """
    List authors
    ---
    tags:
      - Authors
    responses:
      200:
        description: Returns a list of Authors
        schema:
          type: array
          items:
            $ref: "#/definitions/Author"
    """
    authors = Author.query.all()
    json_authors = [make_public_author(author) for author in authors]
    return jsonify({'authors': json_authors})


@app.route("/api/v1/authors/<int:author_id>")
def list_author(author_id):
    """
    Find author by ID
    ---
    tags:
      - Authors
    definitions:
      - schema:
          id: Author
          type: object
          properties:
            author_id:
              type: integer
              description: Author ID
              default: 1
            given_name:
              type: string
              description: Author's given name
              default: Author
            family_name:
              type: string
              description: Author's family name
              default: McAuthor
            email:
              type: string
              description: Author's email
              default: author.mcauthor@example.com
            organization:
              type: string
              description: Author's organization
              default: ACME Modelers
            models:
              type: array
              items:
                type: integer
                default: 1
    parameters:
      - in: path
        name: author_id
        type: integer
        format: int32
        required: true
        description: Author ID
    responses:
      200:
        description: Returns the specified Author
        schema:
          type: object
          $ref: "#/definitions/Author"
      404:
        description: Author not found
    """
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
    """
    List reactions
    ---
    tags:
      - Reactions
    parameters:
      - in: query
        name: limit
        type: integer
        description: Maximum number of results to return
      - in: query
        name: offset
        type: integer
        description: Offset for database query
    responses:
      200:
        description: Returns a list of Reactions
        schema:
          type: object
          properties:
            limit:
              type: integer
              description: Maximum number of results to return
              default: 20
            offset:
              type: integer
              description: Offset for database query
              default: 20
            reactions:
              type: array
              items:
                $ref: "#/definitions/Reaction"
    """
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
    """
    Find reaction by ID
    ---
    tags:
      - Reactions
    definitions:
      - schema:
          id: Reaction
          type: object
          properties:
            reaction_id:
              type: string
              description: Reaction ID
              default: R_HMR_3905
            name:
              type: string
              description: Reaction name
            sbo_id:
              type: string
              description: SBO ID
              default: "SBO:0000176"
            equation:
              type: string
              description: Equation
              default: "reactant_1 + ... + reactant_n => product_1 + ... + product_m"
            lower_bound:
              type: float
              description: Lower bound
              default: 0.0
            upper_bound:
              type: float
              description: Upper bound
              default: 1.0
            objective_coefficient:
              type: float
              description: Objective coefficient
              default: 1.0
            reactants:
              type: array
              items:
                $ref: "#/definitions/ReactionComponent"
              description: Reactants
            products:
              type: array
              items:
                $ref: "#/definitions/ReactionComponent"
              description: Products
            modifiers:
              type: array
              items:
                $ref: "#/definitions/ReactionComponent"
              description: Modifiers
    parameters:
      - in: path
        name: reaction_id
        type: string
        required: true
        description: Reaction ID
    responses:
      200:
        description: Returns the specified Reaction
        schema:
          type: object
          $ref: "#/definitions/Reaction"
      404:
        description: Reaction not found
    """
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
    """
    List reactants for a specific reaction
    ---
    tags:
      - Reactions
    parameters:
      - in: path
        name: reaction_id
        type: string
        description: Reaction ID
    responses:
      200:
        description: Returns a list of reactants for the specified reaction
        schema:
          type: array
          items:
            $ref: "#/definitions/ReactionComponent"
    """
    reaction = Reaction.query.get_or_404(reaction_id)
    reactants = [make_public_component(reactant)
                 for reactant in reaction.reactants]
    return jsonify({'reactants': reactants})


@app.route("/api/v1/reactions/<string:reaction_id>/reactants/<string:reactant_id>")
def list_reaction_reactant(reaction_id, reactant_id):
    """
    Find reactant by ID for a specific reaction
    ---
    tags:
      - Reactions
    parameters:
      - in: path
        name: reaction_id
        type: string
        description: Reaction ID
      - in: path
        name: reactant_id
        type: string
        description: Reactant ID
    responses:
      200:
        description: Returns the specified reactant
        schema:
          type: object
          $ref: "#/definitions/ReactionComponent"
      404:
        description: Reactant not found
    """
    reaction = Reaction.query.get_or_404(reaction_id)
    reactants = [reactant for reactant in reaction.reactants if
                 reactant.id == reactant_id]
    if len(reactants) == 1:
        return jsonify(make_public_component(reactants[0]))
    else:
        abort(404)


@app.route("/api/v1/reactions/<string:reaction_id>/products")
def list_reaction_products(reaction_id):
    """
    List products for a specific reaction
    ---
    tags:
      - Reactions
    parameters:
      - in: path
        name: reaction_id
        type: string
        description: Reaction ID
    responses:
      200:
        description: Returns a list of products for the specified reaction
        schema:
          type: array
          items:
            $ref: "#/definitions/ReactionComponent"
    """
    reaction = Reaction.query.get_or_404(reaction_id)
    products = [make_public_component(product)
                for product in reaction.products]
    return jsonify({'products': products})


@app.route("/api/v1/reactions/<string:reaction_id>/products/<string:product_id>")
def list_reaction_product(reaction_id, product_id):
    """
    Find product by ID for a specific reaction
    ---
    tags:
      - Reactions
    parameters:
      - in: path
        name: reaction_id
        type: string
        description: Reaction ID
      - in: path
        name: product_id
        type: string
        description: Product ID
    responses:
      200:
        description: Returns the specified product
        schema:
          type: object
          $ref: "#/definitions/ReactionComponent"
      404:
        description: Product not found
    """
    reaction = Reaction.query.get_or_404(reaction_id)
    products = [product for product in reaction.products if
                product.id == product_id]
    if len(products) == 1:
        return jsonify(make_public_component(products[0]))
    else:
        abort(404)


@app.route("/api/v1/reactions/<string:reaction_id>/modifiers")
def list_reaction_modifiers(reaction_id):
    """
    List modifiers for a specific reaction
    ---
    tags:
      - Reactions
    parameters:
      - in: path
        name: reaction_id
        type: string
        description: Reaction ID
    responses:
      200:
        description: Returns a list of modifiers for the specified reaction
        schema:
          type: array
          items:
            $ref: "#/definitions/ReactionComponent"
    """
    reaction = Reaction.query.get_or_404(reaction_id)
    modifiers = [make_public_component(modifier)
                 for modifier in reaction.modifiers]
    return jsonify({'modifiers': modifiers})


@app.route("/api/v1/reactions/<string:reaction_id>/modifiers/<string:modifier_id>")
def list_reaction_modifier(reaction_id, modifier_id):
    """
    Find modifier by ID for a specific reaction
    ---
    tags:
      - Reactions
    parameters:
      - in: path
        name: reaction_id
        type: string
        description: Reaction ID
      - in: path
        name: modifier_id
        type: string
        description: Modifier ID
    responses:
      200:
        description: Returns the specified modifier
        schema:
          type: object
          $ref: "#/definitions/ReactionComponent"
      404:
        description: Modifier not found
    """
    reaction = Reaction.query.get_or_404(reaction_id)
    modifiers = [modifier for modifier in reaction.modifiers if
                modifier.id == modifier_id]
    if len(modifiers) == 1:
        return jsonify(make_public_component(modifiers[0]))
    else:
        abort(404)


@app.route("/api/v1/reaction_components")
def list_components():
    """
    List reaction components
    ---
    tags:
      - ReactionComponents
    parameters:
      - in: query
        name: limit
        type: integer
        description: Maximum number of results to return
      - in: query
        name: offset
        type: integer
        description: Offset for database query
      - in: query
        name: name
        type: string
        description: Filter on component_id, short_name, or long_name
    responses:
      200:
        description: Returns a list of ReactionComponentss
        schema:
          type: object
          properties:
            limit:
              type: integer
              description: Maximum number of results to return
              default: 20
            offset:
              type: integer
              description: Offset for database query
              default: 20
            reaction_components:
              type: array
              items:
                $ref: "#/definitions/ReactionComponent"
    """
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    maybe_name = request.args.get('name')
    if maybe_name:
        search = "%{0}%".format(maybe_name)
        components = ReactionComponent.query.filter(
            or_(ReactionComponent.id.like(search),
                or_(ReactionComponent.long_name.like(search),
                    ReactionComponent.short_name.like(search)))).\
                    limit(limit).offset(offset).all()
    else:
        components = ReactionComponent.query.limit(limit).offset(offset).all()
    json = {}
    json['limit'] = limit
    json['offset'] = offset + len(components)
    json['reaction_components'] = [make_public_component(component)
                                   for component in components]
    return jsonify(json)


@app.route("/api/v1/reaction_components/<string:component_id>")
def list_component(component_id):
    """
    Find reaction component by ID
    ---
    tags:
      - ReactionComponents
    definitions:
      - schema:
          id: ReactionComponent
          type: object
          properties:
            component_id:
              type: string
              description: Reaction component ID
              default: M_m02040s
            short_name:
              type: string
              description: Short name
              default: FIXME
            long_name:
              type: string
              description: Long name
              default: H2O
            type_code:
              type: string
              description: Type
              default: FIXME
            organism:
              type: string
              description: Organism
              default: Human
            formula:
              type: string
              description: Formula
              default: H2O
    parameters:
      - in: path
        name: component_id
        type: string
        required: true
        description: Reaction component ID
    responses:
      200:
        description: Returns the specified ReactionComponent
        schema:
          type: object
          $ref: "#/definitions/ReactionComponent"
      404:
        description: ReactionComponent not found
    """
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
