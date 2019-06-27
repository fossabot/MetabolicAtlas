import re
import os
from itertools import chain
from django.db import models
from api.models import *
from django.core.management.base import BaseCommand
from django.db.models import Q

class Command(BaseCommand):
    def add_arguments(self, parser):
        # python manage.py populateDB hmr2 database_generation/human1/model.yml
        parser.add_argument('database', type=str)
        parser.add_argument('--svg-maps-directory', dest='svg-maps-directory', type=str, default="")
        parser.add_argument('--net-maps-directory', dest='net-maps-directory', type=str, default="")

    def handle(self, *args, **options):
        database = options['database']
        svg_map_directory = options['svg-maps-directory']
        net_map_directory = options['net-maps-directory']

        reaction_main_met_dict = {}
        reaction_reactant_dict = {}
        reaction_product_dict = {}
        
        rrs = ReactionReactant.objects.using(database).all().prefetch_related('reactant')
        for rr in rrs:
            if rr.reaction_id not in reaction_reactant_dict:
                reaction_reactant_dict[rr.reaction_id] = [[rr.reactant_id, rr.reactant.name]]
            else:
                reaction_reactant_dict[rr.reaction_id].append([rr.reactant_id, rr.reactant.name])

        rps = ReactionProduct.objects.using(database).all().prefetch_related('product')
        for rp in rps:
            if rp.reaction_id not in reaction_product_dict:
                reaction_product_dict[rp.reaction_id] = [[rp.product_id, rp.product.name]]
            else:
                reaction_product_dict[rp.reaction_id].append([rp.product_id, rp.product.name])

        # identify reactant that cannot be currency metabolite because reaction having a single reactant
        for k, v in reaction_reactant_dict.items():
            if len(v) == 1:
                reaction_main_met_dict[k] = {v[0][0]}  # id

        # identify product that cannot be currency metabolite because reaction having a single product
        for k, v in reaction_product_dict.items():
            if len(v) == 1:
                if k not in reaction_main_met_dict:
                    reaction_main_met_dict[k] = {v[0][0]}
                else:
                    reaction_main_met_dict[k].add(v[0][0]) # id

        # identify reactions with more than 1 reactants / products and all but one is not H+ or water
        # set it as no currency metabolite
        # is all are h+ and water, set them both as not currency

        # print(reaction_product_dict['HMR_7695'])
        # print(reaction_reactant_dict['HMR_7695'])

        # print(reaction_reactant_dict['HMR_8749'])
        # print(reaction_product_dict['HMR_8749'])
        # exit()

        for k, v in reaction_reactant_dict.items():
            no_currency_mets = set()
            if len(v) != 1:
                for reactant in v:
                    if reactant[1].lower() not in ['h', 'h+', 'h2o', 'water', 'h202', 'hco3-', 'atp', 'adp', 'pi', 'ppi', 'co2', 'o2', 'nadp+', 'nadh', 'nad+', 'coa', 'nadph', 'fad', 'fadh']:
                        no_currency_mets.add(reactant[0])
                if len(no_currency_mets) == 1:
                    reaction_main_met_dict[k] = no_currency_mets
                else:
                # elif not no_currency_mets:
                    # if k in reaction_main_met_dict:
                    #     print("error1.1")
                    #     print(k)
                    #     exit()
                    reaction_main_met_dict[k] = {r[0] for r in v}
            else:
                reaction_main_met_dict[k] = {v[0][0]}

        # print(reaction_main_met_dict['HMR_8749'])

        for k, v in reaction_product_dict.items():
            no_currency_mets = set()
            if len(v) != 1:
                for product in v:
                    if product[1].lower() not in ['h', 'h+', 'h2o', 'water', 'h202', 'hco3-', 'atp', 'adp', 'pi', 'ppi', 'co2', 'o2', 'nadp+', 'nadh', 'nad+', 'coa', 'nadph', 'fad', 'fadh']:
                        no_currency_mets.add(product[0])
                if len(no_currency_mets) == 1:
                    if k in reaction_main_met_dict:
                        reaction_main_met_dict[k] |= no_currency_mets
                    else:
                        reaction_main_met_dict[k] = no_currency_mets
                else:
                # elif not no_currency_mets:
                    # if k in reaction_main_met_dict:
                    #     print("error1.2")
                    #     print(k)
                    #     exit()
                    if k in reaction_main_met_dict:
                        reaction_main_met_dict[k] |= {r[0] for r in v}
                    else:
                        reaction_main_met_dict[k] = {r[0] for r in v}
            else:
                if k in reaction_main_met_dict:
                    reaction_main_met_dict[k] |= {v[0][0]}
                else:
                    reaction_main_met_dict[k] = {v[0][0]}

        # print(reaction_main_met_dict['HMR_8749'])
        # exit()

        # ===============================================================================================

        # read the network files if available
        if net_map_directory:
            # print(reaction_main_met_dict['HMR_7695'])
            print ("add subsystem NET maps information")
            reaction_main_met_dict_subsystem = {}
            subsystem_svg = SubsystemSvg.objects.using(database).all()
            for ss in subsystem_svg:
                net_path = os.path.join(net_map_directory, ss.filename.replace('.svg', '.net'))
                if not os.path.isfile(net_path):
                    # print("Warning: file '" + net_path + "' not found")
                    continue
                reaction_main_met_dict_subsystem = get_net_currency_state(net_path, reaction_main_met_dict_subsystem)

            # compare
            c = 0
            for k, v in reaction_main_met_dict_subsystem.items():
                if k not in reaction_main_met_dict:
                    # should not be possible
                    exit()
                elif v.issubset(reaction_main_met_dict[k]):
                    # the no currency mets have been already found
                    # update the list, the subsystem maps are more currated
                    reaction_main_met_dict[k] = reaction_main_met_dict_subsystem[k]
                elif v.issuperset(reaction_main_met_dict[k]):
                    # additional no currency found
                    reaction_main_met_dict[k] = reaction_main_met_dict_subsystem[k]
                else:
                    print("%s different" % k)
                    print("on rule: %s" % reaction_main_met_dict[k])
                    print("on subsystem map: %s" % v)
                    # trust the map
                    reaction_main_met_dict[k] = v
                    c += 1
            print("problem found: %s" % c)

            # print(reaction_main_met_dict['HMR_7695'])
            # read the compartment maps if available and extract the currency states
            # compartment maps are less curated so, add met id with caution
            print ("add compartment NET maps information")
            reaction_main_met_dict_compt = {}
            compartment_svg = CompartmentSvg.objects.using(database).all()
            for cs in compartment_svg:
                svg_path = os.path.join(net_map_directory, cs.filename.replace('.svg', '.net'))
                if not os.path.isfile(svg_path):
                    # print("Warning: file '" + svg_path + "' not found")
                    continue
                reaction_main_met_dict_compt = get_net_currency_state(svg_path, reaction_main_met_dict_compt)

            # compare
            c = 0
            for k, v in reaction_main_met_dict_compt.items():
                if k not in reaction_main_met_dict:
                    # should not be possible
                    exit()
                elif v.issubset(reaction_main_met_dict[k]):
                    # the no currency mets have been already found
                    pass
                elif v.issuperset(reaction_main_met_dict[k]):
                    # additional no currency found
                    reaction_main_met_dict[k] = reaction_main_met_dict_compt[k]
                else:
                    if k not in reaction_main_met_dict_subsystem:
                        # thrust the map
                        reaction_main_met_dict[k] = reaction_main_met_dict[k]
                    else:
                        print("%s different" % k)
                        print("on subsystem/rule map: %s" % reaction_main_met_dict[k])
                        print("on compartment map: %s" % v)
                        c += 1
            print("problem found: %s" % c)

        # ===============================================================================================

        if svg_map_directory and not net_map_directory:
            # read the subsystem maps if available and extract the currency states
            # 
            # The currency state in SVG is not associated to reaction: if a metabolite is no-currency and connected to multiple reactions
            # there is no way to know if this metabolite is main for all of the reaction attached to it because the rule when creating
            # the SVG is to set the state as no-currency if the metabolite is main in at least one reaction. To get this information
            # read the .net file instead
            # 
            subsystem_svg = SubsystemSvg.objects.using(database).all()
            for ss in subsystem_svg:
                svg_path = os.path.join(svg_map_directory, ss.filename)
                if not os.path.isfile(svg_path):
                    print("Warning: file '" + svg_path + "' not found")
                    continue
                # add the main metabolite in addition to the first step
                reaction_main_met_dict = get_svg_currency_state(svg_path, reaction_main_met_dict)

            # ===============================================================================================

            # read the compartment maps if available and extract the currency states
            # compartment maps are less curated so, add met id with caution
            reaction_main_met_dict_compt = {}
            compartment_svg = CompartmentSvg.objects.using(database).all()
            for cs in compartment_svg:
                svg_path = os.path.join(svg_map_directory, cs.filename)
                if not os.path.isfile(svg_path):
                    print("Warning: file '" + svg_path + "' not found")
                    continue
                reaction_main_met_dict_compt = get_svg_currency_state(svg_path, reaction_main_met_dict_compt)

            # compare
            c = 0
            for k, v in reaction_main_met_dict_compt.items():
                if k not in reaction_main_met_dict:
                    # print("%s not in dict, %s" % (k, v))
                    # add it anyway because the compartment maps contain
                    # more reactions than subsystem maps
                    reaction_main_met_dict[k] = reaction_main_met_dict_compt[k]
                elif v.issubset(reaction_main_met_dict[k]):
                    # the no currency mets have been already found
                    continue
                elif v.issuperset(reaction_main_met_dict[k]):
                    # additional no currency found
                    reaction_main_met_dict[k] = reaction_main_met_dict_compt[k]
                else:
                    print("%s different" % k)
                    print(reaction_main_met_dict[k])
                    print(v)
                    reaction_main_met_dict[k] |= v
                    c += 1
            print("problem found: %s" % c)

        # ===============================================================================================

        # get reaction without currency metabolites
        reaction_without_currency = set()
        for k, v in reaction_main_met_dict.items():
            if len(v) == len(reaction_reactant_dict[k]) + len(reaction_product_dict[k]):
                reaction_without_currency.add(k)

        print("Reactions without currency metabolite: %s" % len(reaction_without_currency))
        print("Reaction with currency products or reactants: %s" % len(reaction_main_met_dict.keys()))
        total_reactant_product = 0
        total_main_reactant_product = 0
        no_info = 0
        for k, v in reaction_main_met_dict.items():
            total_main_reactant_product += len(v)

        for k, v in chain(reaction_reactant_dict.items(), reaction_product_dict.items()):
            if k not in reaction_main_met_dict and k not in reaction_without_currency:
                print ("Missing information for %s" % k)
                no_info += 1
            else:
                # count the currency
                total_reactant_product += len(v)
        print ("Total main met: %s" % total_main_reactant_product)
        print ("Total currency met: %s" % (total_reactant_product - total_main_reactant_product))
        print ("Reaction without information: %s" % no_info)

        # insert the main/currency metabolite information
        print ("Saving..")
        for k, v in reaction_main_met_dict.items():
            for met_id in v:
                rmm = ReactionMainMetabolite(reaction_id=k, rc_id=met_id)
                rmm.save(using=database)


def get_svg_currency_state(map_path, reaction_main_met_dict):
    with open(map_path, 'r') as fh:
        parse_next_line = False
        current_met_id = None
        reaction_id = None
        for line in fh:
            line = line.strip()
            if line.startswith('<g class="met'):
                m = re.match('<g class="met ([^"]+)', line)
                rid = m.group(1)
                ids = rid.split(' ')
                if len(ids) == 2:
                    current_met_id = ids[0]
                    reaction_id = ids[1]
                    parse_next_line = True
            elif parse_next_line:
                if line.startswith('<ellipse'):
                    if reaction_id in reaction_main_met_dict:
                        reaction_main_met_dict[reaction_id].add(current_met_id)
                    else:
                        reaction_main_met_dict[reaction_id] = {current_met_id}
                parse_next_line = False

    return reaction_main_met_dict

def get_net_currency_state(map_path, reaction_main_met_dict):
    with open(map_path, 'r') as fh:
        current_met_id = None
        for line in fh:
            line = line.strip()
            if line.startswith('MI'):
                linearr = line.split('\t')
                if linearr[1]:
                    current_met_id = linearr[1]

            elif line.startswith('L'):
                linearr = line.split('\t')
                reaction_id = linearr[2]
                is_currency = linearr[3] == 'true'
                if not is_currency:
                    if reaction_id in reaction_main_met_dict:
                        reaction_main_met_dict[reaction_id].add(current_met_id)
                    else:
                        reaction_main_met_dict[reaction_id] = {current_met_id}

    return reaction_main_met_dict

