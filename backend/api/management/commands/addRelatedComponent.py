from django.db import models
from api.models import *
from django.core.management.base import BaseCommand
from django.db.models import Q


class Command(BaseCommand):
    def add_arguments(self, parser):
        #  python manage.py populateDB hmr2 database_generation/human1/model.yml
        parser.add_argument('database', type=str)

    def handle(self, *args, **options):
        database = options['database']
        #find analog reactions
        mets = ReactionComponent.objects.using(database).all()
        dict_name = {}
        for m in mets:
            dict_name[m.id] = m.name

        rr = ReactionReactant.objects.using(database).all()
        prev_reaction_id = ''
        reactant_dict = {}
        current_list_reactant = []
        for el in rr.all():
            if prev_reaction_id != el.reaction_id:
                # rest the immutable set
                if prev_reaction_id:
                    immutable_set = frozenset(current_list_reactant)
                    # save the reactant list to the dict
                    if immutable_set not in reactant_dict:
                        reactant_dict[immutable_set] = []

                    reactant_dict[immutable_set].append(prev_reaction_id)

                # reset the reactant list
                current_list_reactant = []

            current_list_reactant.append(dict_name[el.reactant_id])
            prev_reaction_id = el.reaction_id

        # save the last list of reactant
        if prev_reaction_id:
            immutable_set = frozenset(current_list_reactant)
            # save the reactant list to the dict
            if immutable_set not in reactant_dict:
                reactant_dict[immutable_set] = []

            reactant_dict[immutable_set].append(prev_reaction_id)

        # ==============================================================================

        rp = ReactionProduct.objects.using(database).all()
        prev_reaction_id = ''
        product_dict = {}
        current_list_product = []
        for el in rp.all():
            if prev_reaction_id != el.reaction_id:
                # rest the immutable set
                if prev_reaction_id:
                    immutable_set = frozenset(current_list_product)
                    # save the product list to the dict
                    if immutable_set not in product_dict:
                        product_dict[immutable_set] = []

                    product_dict[immutable_set].append(prev_reaction_id)

                # reset the product list
                current_list_product = []

            current_list_product.append(dict_name[el.product_id])
            prev_reaction_id = el.reaction_id

        # save the last list of product
        if prev_reaction_id:
            immutable_set = frozenset(current_list_product)
            # save the product list to the dict
            if immutable_set not in product_dict:
                product_dict[immutable_set] = []

            product_dict[immutable_set].append(prev_reaction_id)

        # combine reactions by identical reactants AND products
        Reaction.objects.using(database).all().update(related_group=0)
        group_id = 1
        for key_r in reactant_dict:
            if len(reactant_dict[key_r]) > 1:
                set_rr = set(reactant_dict[key_r])
                for key_p in product_dict:
                    if len(product_dict[key_p]) > 1:
                        set_rp = set(product_dict[key_p])
                        intersection = set_rr & set_rp
                        if len(intersection) > 1:
                             Reaction.objects.using(database).filter(id__in=intersection).update(related_group=group_id)
                             group_id += 1

        print("Reaction group found: %s" % (group_id - 1))

        # metaboltie groups =======================================================

        metabolite_names = {}
        metabolite_formula = {}
        metabolites = ReactionComponent.objects.using(database).filter(component_type='m')
        for el in metabolites:
            if el.name in metabolite_names:
                metabolite_names[el.name].append(el.id)
            else:
                metabolite_names[el.name] = [el.id]

            if el.formula in metabolite_formula:
                metabolite_formula[el.formula].append(el.id)
            else:
                metabolite_formula[el.formula] = [el.id]

        related_compartment_group = 1
        related_formula_group = 1
        ReactionComponent.objects.using(database).filter(component_type='m') \
            .update(related_compartment_group=0, related_formula_group=0)
        for key in metabolite_names:
            if len(metabolite_names[key]) > 1:
                ReactionComponent.objects.using(database).filter(id__in=metabolite_names[key]) \
                .update(related_compartment_group=related_compartment_group)
                related_compartment_group += 1

        for key in metabolite_formula:
            if len(metabolite_formula[key]) > 1:
                ReactionComponent.objects.using(database).filter(id__in=metabolite_formula[key]) \
                .update(related_formula_group=related_formula_group)
                related_formula_group += 1

        print("Metabolite compartment group found: %s" % (related_compartment_group - 1))
        print("Metabolite formula group found: %s" % (related_formula_group - 1))
