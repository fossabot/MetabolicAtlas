from coverage import coverage
cov = coverage(branch=True, cover_pylib=False,
               include=['hma_backend/*'], omit=['tests.py'])
cov.start()

import json
import os
import unittest

from hma_backend import app, db
from hma_backend.config import basedir
from hma_backend.models import *


class APITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.client = cls.app.test_client()
        db.create_all()
        cls.populate_db()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()

    def test_method_not_allowed(self):
        response = self.client.post('/api/v1/models')
        data = dict(self.get_json(response))
        assert response.status_code == 405
        assert data['error'] == "Method not allowed"

    def test_index(self):
        expected = ("Welcome to the Human Metabolic Atlas! Please check "
                    "the API documentation for usage.")
        response = self.client.get('/')
        data = dict(self.get_json(response))
        assert data['message'] == expected

    def test_get_models(self):
        response = self.client.get('/api/v1/models')
        data = dict(self.get_json(response))
        assert len(data['models']) == 1

    def test_get_model(self):
        response = self.client.get('/api/v1/models/1')
        data = dict(self.get_json(response))
        assert data['model_id'] == 1
        assert data['short_name'] == "TestModel"
        assert data['name'] == "Metabolic test model"
        assert len(data['authors']) == 2

    def test_get_model_404(self):
        response = self.client.get('/api/v1/models/1234')
        data = dict(self.get_json(response))
        assert response.status_code == 404
        assert data['error'] == "Not found"

    def test_get_authors(self):
        response = self.client.get('/api/v1/authors')
        data = dict(self.get_json(response))
        assert len(data['authors']) == 2

    def test_get_author(self):
        response = self.client.get('/api/v1/authors/1')
        data = dict(self.get_json(response))
        assert data['given_name'] == "First"
        assert data['family_name'] == "Author"
        assert data['email'] == "first.author@example.com"
        assert data['organization'] == "ACME Modeling"
        assert data['models'] == [1]

    def test_get_author_404(self):
        response = self.client.get('/api/v1/authors/1234')
        data = dict(self.get_json(response))
        assert response.status_code == 404
        assert data['error'] == "Not found"

    def test_get_reactions(self):
        response = self.client.get('/api/v1/reactions')
        data = dict(self.get_json(response))
        assert data['limit'] == 20
        assert data['offset'] == 2
        assert len(data['reactions']) == 2

    def test_get_reactions_with_offset(self):
        response = self.client.get('/api/v1/reactions?offset=2')
        data = dict(self.get_json(response))
        assert data['limit'] == 20
        assert data['offset'] == 2
        assert len(data['reactions']) == 0

    def test_get_reaction(self):
        response = self.client.get('/api/v1/reactions/reaction1')
        data = dict(self.get_json(response))
        assert data['reaction_id'] == "reaction1"
        assert data['name'] == "Reaction"
        assert data['sbo_id'] == "SBO:0000176"
        assert data['equation'] == "FO2 => BAr"
        assert data['lower_bound'] == 0.0
        assert data['upper_bound'] == 1.0
        assert data['objective_coefficient'] == 1.0
        assert len(data['reactants']) == 1
        assert len(data['products']) == 1

    def test_get_reaction_404(self):
        response = self.client.get('/api/v1/reactions/no_reaction')
        data = dict(self.get_json(response))
        assert response.status_code == 404
        assert data['error'] == "Not found"

    def test_get_reaction_reactants(self):
        response = self.client.get('/api/v1/reactions/reaction1/reactants')
        data = dict(self.get_json(response))
        assert len(data['reactants']) == 1

    def test_get_reaction_no_reactants(self):
        response = self.client.get('/api/v1/reactions/reaction2/reactants')
        data = dict(self.get_json(response))
        assert len(data['reactants']) == 0

    def test_get_reaction_reactant(self):
        uri = '/api/v1/reactions/reaction1/reactants/reactant1'
        response = self.client.get(uri)
        data = dict(self.get_json(response))
        assert data['component_id'] == "reactant1"
        assert data['short_name'] == "reactant1"
        assert data['long_name'] == "Reactant 1"
        assert data['type_code'] == 1
        assert data['organism'] == "Human"
        assert data['formula'] == "FO2"

    def test_get_reaction_reactant_404(self):
        uri = '/api/v1/reactions/reaction1/reactants/no_reactant'
        response = self.client.get(uri)
        data = dict(self.get_json(response))
        assert response.status_code == 404
        assert data['error'] == "Not found"

    def test_get_reaction_products(self):
        response = self.client.get('/api/v1/reactions/reaction1/products')
        data = dict(self.get_json(response))
        assert len(data['products']) == 1

    def test_get_reaction_no_products(self):
        response = self.client.get('/api/v1/reactions/reaction2/products')
        data = dict(self.get_json(response))
        assert len(data['products']) == 0

    def test_get_reaction_product(self):
        uri = '/api/v1/reactions/reaction1/products/product1'
        response = self.client.get(uri)
        data = dict(self.get_json(response))
        assert data['component_id'] == "product1"
        assert data['short_name'] == "product1"
        assert data['long_name'] == "Product 1"
        assert data['type_code'] == 1
        assert data['organism'] == "Human"
        assert data['formula'] == "BAr"

    def test_get_reaction_product_404(self):
        uri = '/api/v1/reactions/reaction1/products/no_product'
        response = self.client.get(uri)
        data = dict(self.get_json(response))
        assert response.status_code == 404
        assert data['error'] == "Not found"

    def test_get_reaction_modifiers(self):
        response = self.client.get('/api/v1/reactions/reaction1/modifiers')
        data = dict(self.get_json(response))
        assert len(data['modifiers']) == 1

    def test_get_reaction_no_modifiers(self):
        response = self.client.get('/api/v1/reactions/reaction2/modifiers')
        data = dict(self.get_json(response))
        assert len(data['modifiers']) == 0

    def test_get_reaction_modifier(self):
        uri = '/api/v1/reactions/reaction1/modifiers/modifier1'
        response = self.client.get(uri)
        data = dict(self.get_json(response))
        assert data['component_id'] == "modifier1"
        assert data['short_name'] == "modifier1"
        assert data['long_name'] == "Modifier 1"
        assert data['type_code'] == 1
        assert data['organism'] == "Human"
        assert data['formula'] == "BaZ"

    def test_get_reaction_modifier_404(self):
        uri = '/api/v1/reactions/reaction1/modifiers/no_modifier'
        response = self.client.get(uri)
        data = dict(self.get_json(response))
        assert response.status_code == 404
        assert data['error'] == "Not found"

    def test_get_reaction_components(self):
        response = self.client.get('/api/v1/reaction_components')
        data = dict(self.get_json(response))
        assert data['limit'] == 20
        assert data['offset'] == 3
        assert len(data['reaction_components']) == 3

    def test_get_reaction_components_search(self):
        query = '/api/v1/reaction_components?name={0}'
        response = self.client.get(query.format("Reactant"))
        data = dict(self.get_json(response))
        assert len(data['reaction_components']) == 1

        response = self.client.get(query.format("1"))
        data = dict(self.get_json(response))
        assert len(data['reaction_components']) == 3

    def test_get_reaction_component(self):
        response = self.client.get('/api/v1/reaction_components/product1')
        data = dict(self.get_json(response))
        assert data['component_id'] == "product1"
        assert data['short_name'] == "product1"
        assert data['long_name'] == "Product 1"
        assert data['type_code'] == 1
        assert data['organism'] == "Human"
        assert data['formula'] == "BAr"

    def test_get_reaction_component_404(self):
        response = self.client.get('/api/v1/reaction_components/no_component')
        data = dict(self.get_json(response))
        assert response.status_code == 404
        assert data['error'] == "Not found"

    def get_json(self, response):
        return json.loads(response.data.decode('utf-8'))

    @classmethod
    def populate_db(cls):
        model = MetabolicModel()
        model.short_name = "TestModel"
        model.name = "Metabolic test model"
        author1 = Author()
        author1.given_name = "First"
        author1.family_name = "Author"
        author1.email = "first.author@example.com"
        author1.organization = "ACME Modeling"
        author2 = Author()
        author2.given_name = "Second"
        author2.family_name = "Author"
        author2.email = "second.author@example.com"
        author2.organization = "ACME Modeling"
        model.authors.append(author1)
        model.authors.append(author2)

        db.session.add(model)

        reactant1 = ReactionComponent(id="reactant1")
        reactant1.short_name = "reactant1"
        reactant1.long_name = "Reactant 1"
        reactant1.type_code = 1
        reactant1.organism = "Human"
        reactant1.formula = "FO2"

        product1 = ReactionComponent(id="product1")
        product1.short_name = "product1"
        product1.long_name = "Product 1"
        product1.type_code = 1
        product1.organism = "Human"
        product1.formula = "BAr"

        modifier1 = ReactionComponent(id="modifier1")
        modifier1.short_name = "modifier1"
        modifier1.long_name = "Modifier 1"
        modifier1.type_code = 1
        modifier1.organism = "Human"
        modifier1.formula = "BaZ"

        reaction1 = Reaction(id="reaction1")
        reaction1.name = "Reaction"
        reaction1.sbo_id = "SBO:0000176"
        reaction1.equation = "FO2 => BAr"
        reaction1.lower_bound = 0.0
        reaction1.upper_bound = 1.0
        reaction1.objective_coefficient = 1.0
        reaction1.reactants.append(reactant1)
        reaction1.products.append(product1)
        reaction1.modifiers.append(modifier1)

        db.session.add(reaction1)

        reaction2 = Reaction(id="reaction2")
        reaction2.name = "Reaction"
        reaction2.sbo_id = "SBO:0000176"
        reaction2.equation = "FO2 => BAr"
        reaction2.lower_bound = 0.0
        reaction2.upper_bound = 1.0
        reaction2.objective_coefficient = 1.0

        db.session.add(reaction2)

        db.session.commit()


class ModelTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_model_repr(self):
        model = MetabolicModel(short_name="Model")
        assert model.__repr__() == "<MetabolicModel: Model>"

    def test_author_repr(self):
        author = Author(given_name="Given", family_name="Family")
        assert author.__repr__() == "<Author: Given Family>"

    def test_reaction_repr(self):
        reaction = Reaction(id="MyReaction")
        assert reaction.__repr__() == "<Reaction: MyReaction>"

    def test_reaction_component_repr(self):
        rc = ReactionComponent(id="MyComponent")
        assert rc.__repr__() == "<ReactionComponent: MyComponent>"


if __name__ == "__main__":
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print("\n\nCoverage Report:\n")
    cov.report()
    print("\nHTML Version: " +
          os.path.join(basedir, "tmp/coverage/index.html"))
    cov.html_report(directory='tmp/coverage')
    cov.erase()
