from django.core.management.base import BaseCommand
import api.models as APImodels
from django.db.models import Q


def get_mapping_model_annotation_dict(ctype):
    # dict to map header columns of annoations files to database fields
    d = {
        'metabolite': {
            'name_link': [APImodels.Metabolite, 'name_link'],  # 'name_link'is column name in the annotation file
            'alt_name1': [APImodels.ReactionComponent, 'alt_name1'],
            'alt_name2': [APImodels.ReactionComponent, 'alt_name2'],
            'aliases': [APImodels.ReactionComponent, 'aliases'],
            'external_id1': [APImodels.ReactionComponent, 'external_id1'],
            'external_link1': [APImodels.Metabolite, 'external_link1'],
            'external_id2': [APImodels.ReactionComponent, 'external_id2'],
            'external_link2': [APImodels.Metabolite, 'external_link2'],
            'external_id3': [APImodels.ReactionComponent, 'external_id3'],
            'external_link3': [APImodels.Metabolite, 'external_link3'],
            'external_id4': [APImodels.ReactionComponent, 'external_id4'],
            'external_link4': [APImodels.Metabolite, 'external_link4'],
            'external_id5': [APImodels.ReactionComponent, 'external_id5'],
            'external_link5': [APImodels.Metabolite, 'external_link5'],
            'external_id6': [APImodels.ReactionComponent, 'external_id6'],
            'external_link6': [APImodels.Metabolite, 'external_link6'],
            'external_id7': [APImodels.ReactionComponent, 'external_id7'],
            'external_link7': [APImodels.Metabolite, 'external_link7'],
            'external_id8': [APImodels.ReactionComponent, 'external_id8'],
            'external_link8': [APImodels.Metabolite, 'external_link8'],
            'formula': [APImodels.ReactionComponent, 'formula'],
            'description': [APImodels.Metabolite, 'description'],
            'function1': [APImodels.Metabolite, 'function'],
            # 'function2': [APImodels.Metabolite, 'function2'],
            'charge': [APImodels.Metabolite, 'charge'],
            'mass': [APImodels.Metabolite, 'mass'],
            'mass_avg': [APImodels.Metabolite, 'mass_avg'],
            'inchi': [APImodels.Metabolite, 'inchi'],
        },
        'gene': {
            'name': [APImodels.ReactionComponent, 'name'],
            'name_link': [APImodels.Gene, 'name_link'],
            'alt_name1': [APImodels.ReactionComponent, 'alt_name1'],
            'alt_name2': [APImodels.ReactionComponent, 'alt_name2'],
            'aliases': [APImodels.ReactionComponent, 'aliases'],
            'external_id1': [APImodels.ReactionComponent, 'external_id1'],
            'external_link1': [APImodels.Gene, 'external_link1'],
            'external_id2': [APImodels.ReactionComponent, 'external_id2'],
            'external_link2': [APImodels.Gene, 'external_link2'],
            'external_id3': [APImodels.ReactionComponent, 'external_id3'],
            'external_link3': [APImodels.Gene, 'external_link3'],
            'external_id4': [APImodels.ReactionComponent, 'external_id4'],
            'external_link4': [APImodels.Gene, 'external_link4'],
            'external_id5': [APImodels.ReactionComponent, 'external_id5'],
            'external_link5': [APImodels.Gene, 'external_link5'],
            'external_id6': [APImodels.ReactionComponent, 'external_id6'],
            'external_link6': [APImodels.Gene, 'external_link6'],
            'external_id7': [APImodels.ReactionComponent, 'external_id7'],
            'external_link7': [APImodels.Gene, 'external_link7'],
            'external_id8': [APImodels.ReactionComponent, 'external_id8'],
            'external_link8': [APImodels.Gene, 'external_link8'],
            'function1': [APImodels.Gene, 'function'],
            # 'function2': [APImodels.Gene, 'function2'],
            'ec': [APImodels.Gene, 'ec'],
            'catalytic_activity': [APImodels.Gene, 'catalytic_activity'],
            # 'cofactor': [APImodels.Gene, 'cofactor'],
        },
        'reaction': {
            'name': [APImodels.Reaction, 'name'],
            'ec': [APImodels.Reaction, 'ec'],
            'pmid': [APImodels.ReactionReference, 'pmid'],
            'external_id1': [APImodels.Reaction, 'external_id1'],
            'external_link1': [APImodels.Reaction, 'external_link1'],
            'external_id2': [APImodels.Reaction, 'external_id2'],
            'external_link2': [APImodels.Reaction, 'external_link2'],
            'external_id3': [APImodels.Reaction, 'external_id3'],
            'external_link3': [APImodels.Reaction, 'external_link3'],
            'external_id4': [APImodels.Reaction, 'external_id4'],
            'external_link4': [APImodels.Reaction, 'external_link4'],
            'external_id5': [APImodels.Reaction, 'external_id5'],
            'external_link5': [APImodels.Reaction, 'external_link5'],
            'external_id6': [APImodels.Reaction, 'external_id6'],
            'external_link6': [APImodels.Reaction, 'external_link6'],
        },
        'subsystem': {
            'description': [APImodels.Subsystem, 'description'],
            'system': [APImodels.Subsystem, 'system'],
            'external_id1': [APImodels.Subsystem, 'external_id1'],
            'external_link1': [APImodels.Subsystem, 'external_link1'],
            'external_id2': [APImodels.Subsystem, 'external_id2'],
            'external_link2': [APImodels.Subsystem, 'external_link2'],
            'external_id3': [APImodels.Subsystem, 'external_id3'],
            'external_link3': [APImodels.Subsystem, 'external_link3'],
            'external_id4': [APImodels.Subsystem, 'external_id4'],
            'external_link4': [APImodels.Subsystem, 'external_link4'],
        }
    }

    if ctype not in d:
        return

    annfile_model_map_dict = {}
    for model_field, (model_table, file_column) in d[ctype].items():
        annfile_model_map_dict[file_column] = [model_field, model_table]

    return annfile_model_map_dict


def reformat_list(value, separator=";"):
    arr = value.split(separator)
    sep_string = "%s " % separator # add a space after separator
    return sep_string.join([e.strip() for e in arr])



def read_annotation_file(file):
    l = []
    with open(file, 'r') as fh:
        for line in fh:
            line = line.strip('\n')
            if not line.strip() or line[0] == "#":
                continue
            elif line[0] == '@':
                # parse header
                columns = line[1:].split('\t')
            else:
                d = {}
                for i, value in enumerate(line.split('\t')):
                    if value.strip():
                        d[columns[i]] = value.strip()
                if 'ID' not in d:
                    print (d)
                    print ("Error: column 'ID' must be in the annotation file")
                    exit(1)
                if d['ID']:
                    # exclude column with empty id
                    l.append(d)
    return l


def update_metabolite(database, row_ann_dict, mapping_model_annotation_dict):
    reaction_component_dict = {}
    metabolite_dict = {}
    for file_column, value in row_ann_dict.items():
        # check if the column in the mapping dict
        if file_column == 'ID':
            continue
        if file_column not in mapping_model_annotation_dict:
            print ("Error: file column '%s' not found in mapping dictionnary" % file_column)
            exit(1)

        [model_field, model_table] = mapping_model_annotation_dict[file_column]
        if model_table == APImodels.ReactionComponent:
            if model_field in reaction_component_dict:
                print ("Error: multiple columns update the field '%s' in model %s " % (model_field, model_table))
                exit(1)
            reaction_component_dict[model_field] = value
        else:
            if model_field in metabolite_dict:
                print ("Error: multiple columns update the field '%s' in model %s " % (model_field, model_table))
                exit(1)
            metabolite_dict[model_field] = value

    rc = APImodels.ReactionComponent.objects.using(database).filter(id=row_ann_dict['ID'])
    if not rc:
        print ("Warning: reaction component ID '%s' not found, cannot update annotation" % row_ann_dict['ID'])
        return

    # select only the first external ID or external link
    reaction_component_dict, metabolite_dict = reformat_external_ids(reaction_component_dict, metabolite_dict, 8) # 8 external IDs for metabolite

    if 'aliases' in reaction_component_dict:
        reaction_component_dict['aliases'] = reformat_list(reaction_component_dict['aliases'])

    rc.update(**reaction_component_dict)
    meta = APImodels.Metabolite.objects.using(database).filter(rc=rc)
    if not meta:
        m = APImodels.Metabolite(rc=rc[0], **metabolite_dict)
        m.save(using=database)
    else:
        meta.update(**metabolite_dict)


def update_gene(database, row_ann_dict, mapping_model_annotation_dict):
    reaction_component_dict = {}
    gene_dict = {}
    for file_column, value in row_ann_dict.items():
        # check if the column in the mapping dict
        if file_column == 'ID':
            continue
        if file_column not in mapping_model_annotation_dict:
            print ("Error: file column '%s' not found in mapping dictionnary" % file_column)
            exit(1)

        [model_field, model_table] = mapping_model_annotation_dict[file_column]
        if model_table == APImodels.ReactionComponent:
            if model_field in reaction_component_dict:
                print ("Error: multiple columns update the field '%s' in model %s " % (model_field, model_table))
                exit(1)
            reaction_component_dict[model_field] = value
        else:
            if model_field in gene_dict:
                print ("Error: multiple columns update the field '%s' in model %s " % (model_field, model_table))
                exit(1)
            gene_dict[model_field] = value

    # select only the first external ID or external link
    reaction_component_dict, gene_dict = reformat_external_ids(reaction_component_dict, gene_dict, 8) # 8 external IDs for gene

    if 'aliases' in reaction_component_dict:
        reaction_component_dict['aliases'] = reformat_list(reaction_component_dict['aliases'])
    if 'ec' in gene_dict:
        gene_dict['ec'] = reformat_list(gene_dict['ec'])

    rc = APImodels.ReactionComponent.objects.using(database).filter(id=row_ann_dict['ID'])
    if not rc:
        print ("Warning: reaction component ID '%s' not found, cannot update annotation" % row_ann_dict['ID'])
        return

    rc.update(**reaction_component_dict)
    enzy = APImodels.Gene.objects.using(database).filter(rc=rc)
    if not enzy:
        m = APImodels.Gene(rc=rc[0], **gene_dict)
        m.save(using=database)
    else:
        enzy.update(**gene_dict)


def update_reaction(database, row_ann_dict, mapping_model_annotation_dict):
    reaction_dict = {}
    pmids_list = []
    for file_column, value in row_ann_dict.items():
        # check if the column in the mapping dict
        if file_column == 'ID':
            continue
        if file_column not in mapping_model_annotation_dict:
            print ("Error: file column '%s' not found in mapping dictionnary" % file_column)
            exit(1)

        [model_field, model_table] = mapping_model_annotation_dict[file_column]
        if model_table == APImodels.Reaction:
            if model_field in reaction_dict:
                print ("Error: multiple columns update the field '%s' in model %s " % (model_field, model_table))
                exit(1)
            reaction_dict[model_field] = value

    # select only the first external ID or external link
    reaction_dict, _ = reformat_external_ids(reaction_dict, None, 6)  # 6 external IDs for reaction

    # parse PMID
    if 'pmid' in row_ann_dict:
        pmids_list = row_ann_dict['pmid'].split(';')
    if 'ec' in reaction_dict:
        reaction_dict['ec'] = reformat_list(reaction_dict['ec'])

    r = APImodels.Reaction.objects.using(database).filter(id=row_ann_dict['ID'])
    if not r:
        print ("Warning: reaction ID '%s' not found, cannot update annotation" % row_ann_dict['ID'])
        return

    r.update(**reaction_dict)
    for pmid in pmids_list:
        pmid = pmid.strip()
        rr = APImodels.ReactionReference.objects.using(database).filter(reaction=r, pmid=pmid)
        if not rr:
            rr = APImodels.ReactionReference(reaction=r[0], pmid=pmid)
            rr.save(using=database)


def update_subsystem(database, row_ann_dict, mapping_model_annotation_dict):
    # to tmp fix annotation of hmr2 sub for human1 db: run 
    # update subsystem set system = '', external_id = 'external_id', external_link = 'external_link', description = 'subsystem description';
    subystem_dict = {}
    for file_column, value in row_ann_dict.items():
        # check if the column in the mapping dict
        if file_column == 'ID':
            continue
        if file_column not in mapping_model_annotation_dict:
            print ("Error: file column '%s' not found in mapping dictionnary" % file_column)
            exit(1)

        [model_field, model_table] = mapping_model_annotation_dict[file_column]
        if model_field in subystem_dict:
            print ("Error: multiple columns update the field '%s' in model %s " % (model_field, model_table))
            exit(1)
        subystem_dict[model_field] = value

    s = APImodels.Subsystem.objects.using(database).filter(name=row_ann_dict['ID'])
    if not s:
        print ("Warning: subsystem name '%s' not found, cannot update annotation" % row_ann_dict['ID'])
        return

    s.update(**subystem_dict)


def reformat_external_ids(data_id_dict, data_link_dict, external_ids_count):
    # data_link_dict is Nomne for reaction, both external ids and external links are in the same dictionnary
    if not data_link_dict:
        data_link_dict = data_id_dict

    for i in range(1, external_ids_count + 1):
        id_key = 'external_id%s' % i
        link_key = 'external_link%s' % i
        if id_key not in data_id_dict or not data_id_dict[id_key]:
            continue
        data_id_dict[id_key] = data_id_dict[id_key].split(';')
        data_link_dict[link_key] = data_link_dict[link_key].split(';')

        if len(data_id_dict[id_key]) != len(data_link_dict[link_key]):
            print("Error: number of external IDs do not match the number of external links (%s)" % row_ann_dict['ID'])
            exit()
        data_id_dict[id_key] = data_id_dict[id_key][0].strip()  # select only the first ID
        data_link_dict[link_key] = data_link_dict[link_key][0].strip() # select only the first link
    return data_id_dict, data_link_dict


def insert_annotation(database, component_type, file):
    switch = {
        'metabolite': update_metabolite,
        'gene': update_gene,
        'reaction': update_reaction,
        'subsystem': update_subsystem
    }

    if component_type not in switch:
        print ("Error: invalid compoenent type '%s'" % component_type)
        exit(1)

    mapping_model_annotation_dict = get_mapping_model_annotation_dict(component_type)
    if not mapping_model_annotation_dict:
        print ("Error: couldn't get annotation mapping with component type '%s'" % component_type)
        exit(1)

    annotation_dicts = read_annotation_file(file)
    for row_ann_dict in annotation_dicts:
        switch[component_type](database, row_ann_dict, mapping_model_annotation_dict)

    # special annotations
    if component_type == "gene":
        # if name have been provided for gene, then the gene_rule of reaction can be stored with the gene's name
        reaction_w_gene = APImodels.ReactionGene.objects.using(database).values('reaction_id')
        for r in APImodels.Reaction.objects.using(database).filter(id__in=reaction_w_gene):
            if not r.gene_rule:
                continue
            gene_rule_string = r.gene_rule
            gene_wo_name = []
            c = 0
            for gene in r.genes.all():
                if gene.name:
                    gene_rule_string = gene_rule_string.replace(gene.id, gene.name)
                    c +=1
                else:
                    gene_wo_name.append(gene.id)
            if c == r.genes.count():
                r.gene_rule_wname = gene_rule_string
                r.save(using=database)
            else:
                print ("Warning: cannot complete gr_rule for reaction '%s': %s have no name" % (r.id, "; ".join(gene_wo_name)))

    print("Annotation inserted for type %s" % component_type)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('database', type=str, help="database's name as defined in the settings file")
        parser.add_argument('type', action='store', help="specify 'all' to insert metabolite, gene, reaction and subsystem annotations")
        parser.add_argument('annotation file', action='store', default=None, nargs='?')

    def handle(self, *args, **options):
        database = options['database']
        if options['type'] == 'all':
            insert_annotation(database, 'metabolite', '/project/annotation/%s/METABOLITES.txt' % database)
            insert_annotation(database, 'gene', '/project/annotation/%s/GENES.txt' % database)
            insert_annotation(database, 'reaction', '/project/annotation/%s/REACTIONS.txt' % database)
            insert_annotation(database, 'subsystem', '/project/annotation/%s/SUBSYSTEMS.txt' % database)
        else:
            if not options['annotation file']:
                raise ValueError("Error: the following argument is required: annotation file")
            insert_annotation(database, options['type'], options['annotation file'])


