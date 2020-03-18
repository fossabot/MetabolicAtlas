#########################################################
# the actual code to read and import the GEM SBML model #
#########################################################
import yaml
import logging
import sys

from django.db import models
from api.models import *
from django.db.models import Q

import api.management.commands.getGithubModels as github_model_parser

import re
import collections

def insert_model_metadata(database, metadata, metadata_only=False, overwrite=False, content_only=False):
    # YAML metadata expected structure:
    # - metadata:
    #     id         : "Human-GEM"
    #     short_name : "human"
    #     full_name  : "Human metabolic model v1"
    #     description: "1-3 lines description"
    #     version    : "1.0.0"
    #     author:
    #       - first_name  : "fn"
    #         last_name   : "ln"
    #         email       : "email"
    #         organization: "org"
    #       - first_name  : "fn2"
    #         last_name   : "ln2"
    #         email       : "email2"
    #         organization: "org2"
    #     date         : "YYYY-MM-DD"
    #     organism     : ""
    #     organ_system : ""
    #     tissue       : ""
    #     cell_type    : ""
    #     cell_line    : ""
    #     condition    : "Generic metabolism"
    #     reference         : (optional)
    #       - title: ""
    #         url: ""
    #         pmid: ""
    #         year: ""
    #     link     : "https://github.com/SysBioChalmers/human-GEM"
    #     gitter: https://gitter.im/SysBioChalmers/Human-GEM

    # currently in the yaml
    # - metaData:
        # short_name  : "humanGEM"
        # full_name   : "Generic genome-scale metabolic model of Homo sapiens"
        # version     : "1.0.2"
        # date        : "2019-04-19"
        # authors     : "Jonathan Robinson, Hao Wang, Pierre-Etienne Cholley, Pınar Kocabaş"
        # email       : "nielsenj@chalmers.se"
        # organization: "Chalmers University of Technology"
        # taxonomy    : "9606"
        # github      : "https://github.com/SysBioChalmers/Human-GEM"
        # description : "Human genome-scale metabolic models are important tools for the study of human health and diseases, by providing a scaffold upon which different types of data can be analyzed. This is the latest version of human-GEM, which is a genome-scale model of the generic human cell. The objective of human-GEM is to serve as a community model for enabling integrative and mechanistic studies of human metabolism."

    if content_only:
        return None

    metadata_dict = metadata[1]
    # fix missing keys
    if "condition" not in metadata_dict:
        metadata_dict["condition"] = "Generic metabolism"
    if "organ_system" not in metadata_dict:
        metadata_dict["organ_system"] = ""
    if "tissue" not in metadata_dict:
        metadata_dict["tissue"] = ""
    if "cell_type" not in metadata_dict:
        metadata_dict["cell_type"] = ""
    if "cell_line" not in metadata_dict:
        metadata_dict["cell_line"] = ""
    if "pmid" not in metadata_dict:
        metadata_dict["pmid"] = []

    #fix metadata dict
    if database == "human1":
        metadata_dict["organism"] = "Homo sapiens"
        metadata_dict["organ_system"] = None
        metadata_dict["tissue"] = None
        metadata_dict["cell_type"] = "Generic cell"
        metadata_dict["cell_line"] = None
        metadata_dict["link"] = "https://github.com/SysBioChalmers/Human-GEM"
        metadata_dict["pmid"] = []
        metadata_dict["chat_link"]: "https://gitter.im/SysBioChalmers/Human-GEM"
        metadata_dict["author"] = [
            {
                "first_name": "Jonathan",
                "last_name": "Robinson",
                "email": "jonrob@chalmers.se",
                "organization": "",
            },{
                "first_name": "Hao",
                "last_name": "Wang",
                "email": "hao.wang@chalmers.se ",
                "organization": "",
            },{
                "first_name": "Pınar",
                "last_name": " Kocabaş",
                "email": "kocabas@@chalmers.se ",
                "organization": "",
            },
        ]

    if "version" not in metadata_dict or not metadata_dict["version"]:
        print("Error: missing version of the model")
        exit(1)

    if "author" not in metadata_dict or not metadata_dict["author"] \
        or "email" not in metadata_dict["author"][0] or not metadata_dict["author"][0]["email"]:
        print("Error: cannot get email of the first author")
        exit(1)

    # check if the model already exists
    try:
        gem = GEM.objects.using('gems').get(Q(short_name=metadata_dict["short_name"]) | Q(database_name=database))

        if not overwrite:
            print("Error: model '%s' already in the database" % metadata_dict["short_name"])
            exit(1)
        # gem.delete()
    except GEM.DoesNotExist:
        if not metadata_only:
            print("Error: model '%s' is not in the database" % metadata_dict["short_name"])
            exit(1)

    # get the sample from the database or create a new one
    try:
        sample = GEModelSample.objects.using('gems').get(organism=metadata_dict["organism"],
                                                      organ_system=metadata_dict["organ_system"],
                                                      tissue=metadata_dict["tissue"],
                                                      cell_line=metadata_dict["cell_line"],
                                                      cell_type=metadata_dict["cell_type"])
    except GEModelSample.DoesNotExist:
        if overwrite:
            print("Error: --overwrite do not support upding model with different sample reference")
            exit(1)
        # create a new sample
        sample = GEModelSample(organism=metadata_dict["organism"],
                      organ_system=metadata_dict["organ_system"],
                      tissue=metadata_dict["tissue"],
                      cell_type=metadata_dict["cell_type"],
                      cell_line=metadata_dict["cell_line"])
        sample.save(using="gems")
        print("New sample created, %s" % sample)

    # get the reference from the db or create new reference
    ref_list = []
    for ref_data in metadata_dict["reference"]:
        try:
            if ref_data['pmid']:
                gr = GEModelReference.objects.get(pmid=ref_data['pmid'])
            else:
                gr = GEModelReference.objects.get(link=ref_data['url'])
        except GEModelReference.DoesNotExist:
            if ref_data['pmid']:
                res = github_model_parser.check_PMID(ref_data['pmid'])
                if res:
                    DOI, PMID = res
                    title, year = github_model_parser.get_info_from_pmid(PMID)
                    gr = GEModelReference(title=title, link='https://www.ncbi.nlm.nih.gov/pubmed/%s' % PMID, pmid=PMID, year=year)
                    gr.save(using="gems")
                    print("New reference created, %s" % PMID)
                else:
                    print("Error: PMID '%s' is invalid" % ref_data['pmid'])
                    exit(1)
            else:
                gr = GEModelReference(title=ref_data['title'], link=ref_data['url'], year=ref_data['year'])
                gr.save(using="gems")
                print("New reference created, %s | %s | %s " % (ref_data['title'], ref_data['url'], ref_data['year']))
        ref_list.append(gr)

    # insert the model
    if overwrite:
        gem.save(update_fields=['short_name', 'full_name', 'description', 'version', 'condition', 'date', 'link', 'chat_link'], using="gems")
    else:
        gem = GEM(short_name=metadata_dict["short_name"],
                    full_name=metadata_dict["full_name"],
                    description=metadata_dict["description"],
                    version=metadata_dict["version"],
                    database_name=database,
                    condition=metadata_dict["condition"],
                    date=metadata_dict["date"],
                    link=metadata_dict["link"],
                    chat_link=metadata_dict["chat_link"],
                    sample=sample)
        gem.save(using="gems")

    for ref in ref_list:
        try:
            gr = GEMreference.objects.get(model=gem, ref=ref)
        except GEMreference.DoesNotExist:
            gr = GEMreference(model=gem, ref=ref)
            gr.save(using="gems")

    #insert authors
    authors_list = []
    for author in metadata_dict["author"]:
        try:
            a = Author.objects.get(given_name=author["first_name"],
                                   family_name=author["last_name"],
                                   email=author["email"],
                                   organization=author["organization"])
        except Author.DoesNotExist:
            a = Author(given_name=author["first_name"],
                       family_name=author["last_name"],
                       email=author["email"],
                       organization=author["organization"])
            a.save(using="gems")

        try:
            ga = GEMAuthor.objects.get(model=gem, author=a)
        except GEMAuthor.DoesNotExist:
            ga = GEMAuthor(model=gem, author=a)
            ga.save(using="gems")

    return gem


# e.g. [('id', 'm00005c'), ('name', '(11R)-HPETE'), ('compartment', 'c'), ('formula', 'C20H32O4'), ('annotation', [('lipidmaps', 'LMFA03060071')])]
# get only id, name and compartment
def make_meta_dict(info):
    d = {}
    for key, value in info:
        if key in ['id', 'name', 'formula', 'charge', 'compartment']:
            d[key] = value
    if 'formula' not in d:
        d['formula'] = None
    if 'charge' not in d:
        d['charge'] = None
    if len(d) != 5:
        print ("Error: missing id, name or compartment for metabolite %s" % info)
        exit(1)
    return d


def make_rxn_dict(info):
    d = {}
    d['reactant'] = []
    d['product'] = []
    try:
        for key, value in info:
            if key in ['id', 'metabolites', 'metabolite', 'gene_reaction_rule', 'lower_bound', 'upper_bound', 'subsystem']:
                if  key == 'subsystem':
                    if not isinstance(value, list):
                        # yeast have multiple subsystem, subsystem in hmr are one, string type
                        d[key] = [value]
                    else:
                        d[key] = value
                elif key == 'metabolites' or key == 'metabolite':
                    for id, stoichiometry in value:
                        if isinstance(stoichiometry, str):
                            stoichiometry = float(stoichiometry)
                        if stoichiometry < 0:
                            d['reactant'].append([id, -stoichiometry])
                        else:
                            d['product'].append([id, stoichiometry])
                else:
                    d[key] = value
        for key in ['id', 'reactant', 'product', 'lower_bound', 'upper_bound']:
            if key not in d:
                print ("Error: missing key '%s' for reaction %s" % (key, info))
                exit(1)
    except Exception as e:
        print(info)
        print(e)
        exit(1)
    return d


def get_genesID_from_GRrule(gr_rule):
    if not gr_rule:
        return []
    # FIXME, this do not work if gene ID contains parenthesis, but is it the case?
    r = re.split('[\s+and\s+|\s+or\s+|(+|)+|\s+]', gr_rule)
    return [e for e in r if e]

def idfy_name(name):
    name = name.lower()
    name = re.sub('[^0-9a-z_]', '_', name)
    name = re.sub('_{2,}', '_', name)
    return name.strip('_')

def insert_subsystem_stats(database):
    subsystems = Subsystem.objects.using(database).all()
    subsystem_stat_dict = {}
    compart_stat_dict = {}

    # update subsystem stats
    for s in subsystems:
        subsystem = Subsystem.objects.using(database).get(name=s.name)

        smsQuerySet = SubsystemMetabolite.objects.using(database). \
            filter(subsystem_id=subsystem).values_list('rc_id', flat=True)

        uniqueMetQuerySet = ReactionComponent.objects.using(database).distinct(). \
            filter(component_type='m', id__in=smsQuerySet).values_list('name', flat=True)

        sesQuerySet = SubsystemGene.objects.using(database). \
            filter(subsystem_id=subsystem).values_list('rc_id', flat=True)
        srsQuerySet = SubsystemReaction.objects.using(database). \
            filter(subsystem_id=subsystem).values_list('reaction_id', flat=True)

        subCompartQuerySet = SubsystemCompartment.objects.using(database). \
            filter(subsystem_id=subsystem).values_list('compartment_id', flat=True)

        compartment_meta = ReactionComponent.objects.using(database). \
            filter(id__in=smsQuerySet).values_list('compartment', flat=True).distinct()
        compartment_meta = Compartment.objects.using(database).filter(id__in=compartment_meta).values_list('name', flat=True)

        compartment_enz = ReactionComponent.objects.using(database). \
            filter(id__in=sesQuerySet).values_list('compartment', flat=True).distinct()
        compartment_enz = Compartment.objects.using(database).filter(id__in=compartment_enz).values_list('name', flat=True)

        compartment_eq = Reaction.objects.using(database). \
             filter(id__in=srsQuerySet).values_list('compartment', flat=True).distinct()
        compartment_react = []
        for el in compartment_eq:
            compartment_react += [c.strip() for c in re.split('[+]|(?:=>)', el) if c]

        # check if compartment list for meta/enz/react are the same
        # ignore compartment_enz, they are all annotated to be in the cytosol
        if set(compartment_meta) != set(compartment_react) or len(set(compartment_meta)) != len(subCompartQuerySet):
            # should not be possible
            print ("error: compartment !=")
            print (s.name)
            print ("comt_sub: ", len(subCompartQuerySet))
            print ("Metabolite: ", set(compartment_meta))
            print ("Gene: ", set(compartment_enz))
            print ("Reaction: ", set(compartment_react))
            exit(1)

        # print ("SS:", s.name)
        # print ("Metabolites: ", smsQuerySet.count())
        # print ("Unique metabolites: ", uniqueMetQuerySet.count())
        # print ("Genes: ", sesQuerySet.count())
        # print ("Reactions: ", srsQuerySet.count())
        # print ("Compartment: ", len(set(compartment_meta)))

        Subsystem.objects.using(database). \
            filter(id=subsystem.id).update(reaction_count=srsQuerySet.count(), compartment_count=len(set(compartment_meta)), \
             metabolite_count=smsQuerySet.count(), unique_metabolite_count=uniqueMetQuerySet.count(), gene_count=sesQuerySet.count())


def insert_compartment_stats(database):
    cis = Compartment.objects.using(database).all()
    for compartment in cis:
        srsQuerySet = ReactionCompartment.objects.using(database). \
            filter(compartment_id=compartment).values_list('reaction_id', flat=True)

        sesRC = ReactionComponentCompartment.objects.using(database). \
            filter(compartment_id=compartment).values_list('rc_id', flat=True)

        sesQuerySet = CompartmentGene.objects.using(database). \
            filter(compartment_id=compartment).values_list('rc_id', flat=True)

        smsQuerySet = ReactionComponent.objects.using(database). \
            filter(component_type='m', id__in=sesRC).values_list('id', flat=True)

        uniqueMetQuerySet = ReactionComponent.objects.using(database).distinct(). \
            filter(component_type='m', id__in=sesRC).values_list('name', flat=True)

        subCompartQuerySet = SubsystemCompartment.objects.using(database). \
            filter(compartment_id=compartment.id).values_list('subsystem_id', flat=True)

        # print ("C:", compartment.name)
        # print ("Metabolites: ", smsQuerySet.count())
        # print ("Unique metabolites: ", uniqueMetQuerySet.count())
        # print ("Genes: ", sesQuerySet.count())
        # print ("Reactions: ", srsQuerySet.count())
        # print ("Compartment: ", subCompartQuerySet.count())

        # update the stats
        Compartment.objects.using(database). \
            filter(id=compartment.id).update(reaction_count=srsQuerySet.count(), subsystem_count=subCompartQuerySet.count(), \
             metabolite_count=smsQuerySet.count(), unique_metabolite_count=uniqueMetQuerySet.count(), gene_count=sesQuerySet.count())

"""
    read YAML model files and insert the strict minimum information
    Annotations should be added in a separate script
"""
def load_YAML(database, yaml_file, overwrite=False, metadata_only=False, content_only=False):
    with open(yaml_file, 'r') as fh:
        print ('Reading YAML file...')
        model_list = yaml.load(fh.read()) # using a loader (Loader=yaml.safe_load) returns a dispose() error
        metadata, metabolites, reactions, genes, compartments = model_list

    # counts must be updated so we need the gem object
    gem = insert_model_metadata(database, metadata, overwrite=overwrite, metadata_only=metadata_only, content_only=content_only)

    if not metadata_only:
        if overwrite:
            Gene.objects.using(database).all().delete()
            Metabolite.objects.using(database).all().delete()
            ReactionGene.objects.using(database).all().delete()
            ReactionReactant.objects.using(database).all().delete()
            ReactionProduct.objects.using(database).all().delete()
            ReactionMetabolite.objects.using(database).all().delete()

            SubsystemGene.objects.using(database).all().delete()
            SubsystemMetabolite.objects.using(database).all().delete()
            SubsystemReactionComponent.objects.using(database).all().delete()

            ReactionComponentSubsystemSvg.objects.using(database).all().delete()
            ReactionComponent.objects.using(database).all().delete()

            ReactionCompartment.objects.using(database).all().delete()
            ReactionComponentCompartment.objects.using(database).all().delete()
            CompartmentGene.objects.using(database).all().delete()
            SubsystemCompartment.objects.using(database).all().delete()
            SubsystemCompartmentSvg.objects.using(database).all().delete()
            CompartmentSvgGene.objects.using(database).all().delete()
            ReactionComponentCompartmentSvg.objects.using(database).all().delete()

            CompartmentSvg.objects.using(database).all().delete()
            Compartment.objects.using(database).all().delete()

            SubsystemReaction.objects.using(database).all().delete()
            ReactionCompartmentSvg.objects.using(database).all().delete()
            ReactionSubsystemSvg.objects.using(database).all().delete()
            ReactionReference.objects.using(database).all().delete()
            Reaction.objects.using(database).all().delete()

            SubsystemSvg.objects.using(database).all().delete()
            SubsystemSvgGene.objects.using(database).all().delete()
            Subsystem.objects.using(database).all().delete()

        print("Inserting compartments...")
        compartment_dict = {} 
        for letter_code, name in compartments[1]:
            compartment = Compartment.objects.using(database).filter(name__iexact=name)
            if not compartment:     # only add the compartment if it does not already exists...
                compartment = Compartment(name=name, name_id=idfy_name(name), letter_code=letter_code)
                compartment.save(using=database)
            else:
                print('Error: compartment %s already in DB' % name)
                exit()
            compartment_dict[letter_code] = compartment

    if not metadata_only:
        print("Inserting metabolites (rc)...")
    rc_dict = {} # store reaction component pour connectivity tables (reaction/reactant, rc/subsystem, rc /compartment)
    unique_metabolite = set()
    for el in metabolites[1]:
        dict_metabolite = make_meta_dict(el)
        if not metadata_only:
            rc = ReactionComponent.objects.using(database).filter(id__iexact=dict_metabolite['id'])
            if not rc:
                compartment = compartment_dict[dict_metabolite['compartment']]
                full_name = "%s[%s]" % (dict_metabolite['name'], dict_metabolite['compartment'])
                rc = ReactionComponent(id=dict_metabolite['id'], name=dict_metabolite['name'], full_name=full_name,
                    component_type='m', formula=dict_metabolite['formula'], compartment=compartment, compartment_str=compartment.name)
                rc.save(using=database)

                rcc = ReactionComponentCompartment(rc=rc, compartment=rc.compartment)
                rcc.save(using=database)

                if dict_metabolite['charge'] is not None:
                    ## add Metabolite object, with the charge
                    met = Metabolite(rc=rc, charge=dict_metabolite['charge'])
                    met.save(using=database)
            else:
                print('Error: metabolite %s already in DB' % dict_metabolite['id'])
                exit()

            rc_dict[dict_metabolite['id']] = rc
        unique_metabolite.add(dict_metabolite['name'])

    # update metabolite count
    if not content_only:
        GEM.objects.filter(id=gem.id).update(metabolite_count=len(unique_metabolite))

    if not metadata_only:
        print("Inserting genes (rc)...")
        for el in genes[1]:
            id_string, id_value = el[0]
            rc = ReactionComponent.objects.using(database).filter(id__iexact=id_value)
            if not rc:
                # name should be provide in the annotation file
                # the is no compartment localization for gene
                rc = ReactionComponent(id=id_value, name='', component_type='e')
                rc.save(using=database)
            else:
                print('Error: gene %s already in DB' % id_value)
                exit()

            rc_dict[id_value] = rc

    # update gene count
    if not content_only:
        GEM.objects.filter(id=gem.id).update(gene_count=len(genes[1]))

    if metadata_only and not content_only:
        # update reaction count
        GEM.objects.filter(id=gem.id).update(reaction_count=len(reactions[1]))
        return

    reaction_dict = {}
    print("Inserting reactions...")
    for el in reactions[1]:
        dict_rxn = make_rxn_dict(el)
        # build the reaction equation with id and the reaction equation with name
        equation = Equation(dict_rxn, rc_dict)
        equation_compartment = equation.get_equation_compartment()

        # extract additional info
        is_transport = False
        for id, meta_name in [(a, rc_dict[a].name) for a,b, in dict_rxn['reactant']]:
            if not meta_name:
                print("no name for met" + a + "(" + meta_name + ")")
            if meta_name in [rc_dict[a].name for a,b in dict_rxn['product']]:
                is_transport = True
                break

        is_reversible = dict_rxn['lower_bound'] == -1000
        gr_rule = dict_rxn['gene_reaction_rule'] if 'gene_reaction_rule' in dict_rxn else None

        # fix gr rule useless parenthesis
        if gr_rule and gr_rule.startswith('(') and gr_rule.endswith(')') and gr_rule.count('(') == 1 and gr_rule.count(')') == 1:
            gr_rule = gr_rule[1:-1]

        try:
            r = Reaction.objects.using(database).get(id__iexact=dict_rxn['id'])
            print('Error: reaction %s already in DB' % dict_rxn['id'])
            exit()
        except Reaction.DoesNotExist:
            r  = Reaction(
                    id=dict_rxn['id'],
                    equation=equation.get_equation_id(),
                    equation_wname=equation.get_equation_name(),
                    gene_rule= gr_rule,
                    lower_bound=dict_rxn['lower_bound'],
                    upper_bound=dict_rxn['upper_bound'],
                    subsystem_str = '; '.join(dict_rxn['subsystem']) if 'subsystem' in dict_rxn else None,
                    compartment=equation_compartment,
                    is_reversible=is_reversible,
                    is_transport=is_transport
                )
            r.save(using=database)
            reaction_dict[dict_rxn['id']] = r

        subsystems_list = []
        if 'subsystem' in dict_rxn:
            for subsystem in dict_rxn['subsystem']:
                try:
                    sub = Subsystem.objects.using(database).get(name__iexact=subsystem)
                except Subsystem.DoesNotExist:
                    # save subsystem, just the name
                    sub = Subsystem(name=subsystem, name_id=idfy_name(subsystem))
                    sub.save(using=database)
                subsystems_list.append(sub)

                # save reaction/subsystem relationship
                rs = SubsystemReaction.objects.using(database).filter(reaction=r, subsystem=sub)
                if not rs:
                    rs = SubsystemReaction(reaction=r, subsystem=sub)
                    rs.save(using=database)

        # add reaction/reactant relationship
        for reactant in dict_rxn['reactant']:
            rc = rc_dict[reactant[0]]
            rr = ReactionReactant.objects.using(database).filter(reaction=r, reactant=rc)
            if not rr:
                rr = ReactionReactant(reaction=r, reactant=rc, stoichiometry=reactant[1])
                rr.save(using=database)

            rm = ReactionMetabolite.objects.using(database).filter(reaction=r, rc=rc)
            if not rm:
                rm = ReactionMetabolite(reaction=r, rc=rc)
                rm.save(using=database)

            # save subsystem/metabolite relationship for reactants
            for sub in subsystems_list:
                sm = SubsystemMetabolite.objects.using(database).filter(rc=rc, subsystem=sub)
                if not sm:
                    sm = SubsystemMetabolite(rc=rc, subsystem=sub)
                    sm.save(using=database)

            for sub in subsystems_list:
                src= SubsystemReactionComponent.objects.using(database).filter(rc=rc, subsystem=sub)
                if not src:
                    src = SubsystemReactionComponent(rc=rc, subsystem=sub)
                    src.save(using=database)

            # add reaction/compartment relationship using reactants
            rcompt = ReactionCompartment.objects.using(database).filter(reaction=r, compartment=rc.compartment)
            if not rcompt:
                rcompt = ReactionCompartment(reaction=r, compartment=rc.compartment)
                rcompt.save(using=database)

        # add reaction/product relationship
        for product in dict_rxn['product']:
            rc = rc_dict[product[0]]
            rr = ReactionProduct.objects.using(database).filter(reaction=r, product=rc)
            if not rr:
                rr = ReactionProduct(reaction=r, product=rc, stoichiometry=product[1])
                rr.save(using=database)

            rm = ReactionMetabolite.objects.using(database).filter(reaction=r, rc=rc)
            if not rm:
                rm = ReactionMetabolite(reaction=r, rc=rc)
                rm.save(using=database)

            # save subsystem/metabolite relationship for products
            for sub in subsystems_list:
                sm = SubsystemMetabolite.objects.using(database).filter(rc=rc, subsystem=sub)
                if not sm:
                    sm = SubsystemMetabolite(rc=rc, subsystem=sub)
                    sm.save(using=database)

            for sub in subsystems_list:
                src = SubsystemReactionComponent.objects.using(database).filter(rc=rc, subsystem=sub)
                if not src:
                    src = SubsystemReactionComponent(rc=rc, subsystem=sub)
                    src.save(using=database)

            # add reaction/compartment relationship using products
            rcompt = ReactionCompartment.objects.using(database).filter(reaction=r, compartment=rc.compartment)
            if not rcompt:
                rcompt = ReactionCompartment(reaction=r, compartment=rc.compartment)
                rcompt.save(using=database)

        # add the relationship between genes and compartments as based on the compartment list the above uses...
        # unique list of compartments for this reaction...
        genes = get_genesID_from_GRrule(gr_rule)
        if genes:
            # add reaction/genes relationship
            for m in genes:
                rc = rc_dict[m]
                rm = ReactionGene.objects.using(database).filter(reaction=r, gene=rc)
                if not rm:
                    rm = ReactionGene(reaction=r, gene=rc)
                    rm.save(using=database)

                # save subsystem/genes relationship
                for sub in subsystems_list:
                    se = SubsystemGene.objects.using(database).filter(rc=rc, subsystem=sub)
                    if not se:
                        se = SubsystemGene(rc=rc, subsystem=sub)
                        se.save(using=database)

                for sub in subsystems_list:
                    sm = SubsystemReactionComponent.objects.using(database).filter(rc=rc, subsystem=sub)
                    if not sm:
                        sm = SubsystemReactionComponent(rc=rc, subsystem=sub)
                        sm.save(using=database)

            # add compartment/genes relationship
            r_compts = ReactionCompartment.objects.select_related('compartment').using(database).filter(reaction=r)
            for m in genes:
                rc = rc_dict[m]
                for r_compt in r_compts:
                    rccompt = CompartmentGene.objects.using(database).filter(compartment=r_compt.compartment, rc=rc)
                    if not rccompt:
                        rccompt = CompartmentGene(compartment=r_compt.compartment, rc=rc)
                        rccompt.save(using=database)

        # save the connection subsystem / compartement base on the reaction
        # reaction are part of subsystem and involve metabolites located in one or more compartments
        if 'subsystem' in dict_rxn:
            compartments = ReactionCompartment.objects.using(database). \
                filter(reaction=r).values_list('compartment_id', flat=True)
            for subsystem in dict_rxn['subsystem']:
                ss = Subsystem.objects.using(database).get(name__iexact=subsystem)
                for compartment in compartments:
                    compt = Compartment.objects.using(database).get(id=compartment)
                    try:
                        sc = SubsystemCompartment.objects.using(database).get(subsystem=ss, compartment=compt)
                    except SubsystemCompartment.DoesNotExist:
                        sc = SubsystemCompartment(subsystem=ss, compartment=compt)
                        sc.save(using=database)

    # update reaction count
    if not content_only:
        GEM.objects.filter(id=gem.id).update(reaction_count=len(reactions[1]))

    print("Inserting subsystem stats...")
    insert_subsystem_stats(database)
    print("Inserting compartment stats...")
    insert_compartment_stats(database)
    print("Database %s is now populated" % database)


class Equation(object):
    def __init__(self, reaction, meta_dict):
        self.id = reaction['id']
        self.reactants = reaction['reactant']
        self.products = reaction['product']
        self.meta_dict = meta_dict
        self.fetch_meta_info()

    def get_equation_id(self):
        reactants_string = self.format_reaction_part([id for id,b,c,d,e in self.reactants])
        products_string = self.format_reaction_part([id for id,b,c,d,e in self.products])
        return "{0} => {1}".format(reactants_string, products_string)

    def get_equation_name(self):
        reactants_string = self.format_reaction_element(self.reactants, using_name=True)
        products_string = self.format_reaction_element(self.products, using_name=True)
        return "{0} => {1}".format(reactants_string, products_string)

    def get_equation_compartment(self):
        reactants_set = {compt for a,b,compt,d,e in self.reactants}
        products_set = {compt for a,b,compt,d,e in self.products}
        reactants_list = [compt for a,b,compt,d,e in self.reactants]
        products_list = [compt for a,b,compt,d,e in self.products]
        reactants_set_string = self.format_reaction_part(reactants_set)
        products_set_string = self.format_reaction_part(products_set)
        reactants_list_string = self.format_reaction_part(reactants_list)
        products_list_string = self.format_reaction_part(products_list)

        if (len(reactants_set) == 1 and reactants_set_string != products_set_string) or (len(products_set) == 1 and reactants_set_string != products_set_string):
            return "{0} => {1}".format(reactants_set_string, products_set_string)
        elif reactants_list == products_list or (reactants_set == products_set and len(reactants_set) == 1 and len(products_set) == 1):
            return reactants_set_string
        elif len(reactants_set) == len(reactants_list) and len(products_set) == len(products_list):
            return "{0} => {1}".format(reactants_list_string, products_list_string)
        else:
            # beautiful code to remove consecutive compartment name
            reactants_list = [e for i, e in enumerate(reactants_list) if i == 0 or (i != len(reactants_list) and reactants_list[i] != reactants_list[i-1])]
            products_list = [e for i, e in enumerate(products_list) if i == 0 or (i != len(products_list) and products_list[i] != products_list[i-1])]
            if len(reactants_set) == len(reactants_list) and len(products_set) == len(products_list):
                return "{0} => {1}".format(self.format_reaction_part(reactants_list), self.format_reaction_part(products_list))
            elif reactants_set == products_set and len(reactants_list) == len(products_list):
                #check if same pairs
                pairs = set()
                for e1, e2 in zip(reactants_list, products_list):
                    pairs.add("".join(sorted(list({e1, e2}))))
                if len(pairs) == 1:
                    return "{0} => {1}".format(self.format_reaction_part(reactants_set), self.format_reaction_part(list(reversed(list(reactants_set)))))
                elif len(pairs) == 2:
                     print("Warning: check compartment equation for reaction %s" % self.id)
                     print (reactants_list, products_list, "=>", "{0} => {1}".format(self.format_reaction_part(reactants_set), self.format_reaction_part(list(reversed(list(reactants_set))))))
                     return "{0} => {1}".format(self.format_reaction_part(reactants_set), self.format_reaction_part(list(reversed(list(reactants_set)))))

                else:
                    print("Error: cannot get compartment equation for reaction %s" % self.id)
                    print (reactants_list, products_list)
                    print(pairs)
                    exit()
            else:
                print("Warning: check compartment equation for reaction %s" % self.id)
                print (reactants_list, products_list, "=>", " + ".join(set(reactants_list + products_list)))
                return " + ".join(set(reactants_list + products_list))
                # exit()

        return ""


    def format_reaction_element(self, elements, using_name=False):
        formatted = []
        for id, name, compartment, compartment_code, stoichiometry in elements:
            if using_name:
                if stoichiometry == 1:
                    formatted.append("{0}[{1}]".format(name, compartment_code))
                else:
                    formatted.append("{0} {1}[{2}]".format(stoichiometry,
                                                           name,
                                                           compartment_code))
            else:
                formatted.append(id)
        return self.format_reaction_part(formatted)

    def format_reaction_part(self, elements):
        return " + ".join(elements)

    def fetch_meta_info(self):
        self.reactants = [
                            (id,
                            self.meta_dict[id].name,
                            self.meta_dict[id].compartment.name,
                            self.meta_dict[id].compartment.letter_code,
                            stoichiometry)
                            for id, stoichiometry in self.reactants
                        ]
        self.products = [
                            (id,
                            self.meta_dict[id].name,
                            self.meta_dict[id].compartment.name,
                            self.meta_dict[id].compartment.letter_code,
                            stoichiometry)
                            for id, stoichiometry in self.products
                        ]
