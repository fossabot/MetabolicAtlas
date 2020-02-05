from django.core.management.base import BaseCommand
import api.models as APImodels
from django.db.models import Q


def get_mapping_model_annotation_dict(ctype):
    # dict to map header columns of annoations files to database fields
    d = {
        'metabolite': {
            'alt_name1': [APImodels.ReactionComponent, 'alt_name1'],
            'alt_name2': [APImodels.ReactionComponent, 'alt_name2'],
            'aliases': [APImodels.ReactionComponent, 'aliases'],
            'formula': [APImodels.ReactionComponent, 'formula'],
            'description': [APImodels.Metabolite, 'description'],
            'function1': [APImodels.Metabolite, 'function'],
            # 'function2': [APImodels.Metabolite, 'function2'],
            'charge': [APImodels.Metabolite, 'charge'],
            'mass': [APImodels.Metabolite, 'mass'],
            'mass_avg': [APImodels.Metabolite, 'mass_avg'],
            'inchi': [APImodels.Metabolite, 'inchi'],
        },
        'metaboliteEID': {
            # 'id': [APImodels.ReactionComponentEID, 'rc'],
            'db_name': [APImodels.ReactionComponentEID, 'db_name'],
            'external_id': [APImodels.ReactionComponentEID, 'ext_id'],
            'external_link': [APImodels.ReactionComponentEID, 'link'],
        },
        'gene': {
            'name': [APImodels.ReactionComponent, 'name'],
            'alt_name1': [APImodels.ReactionComponent, 'alt_name1'],
            'alt_name2': [APImodels.ReactionComponent, 'alt_name2'],
            'aliases': [APImodels.ReactionComponent, 'aliases'],
            'function1': [APImodels.Gene, 'function'],
            # 'function2': [APImodels.Gene, 'function2'],
            'ec': [APImodels.Gene, 'ec'],
            'catalytic_activity': [APImodels.Gene, 'catalytic_activity'],
            # 'cofactor': [APImodels.Gene, 'cofactor'],
        },
        'geneEID': {
            # 'id': [APImodels.ReactionComponentEID, 'rc'],
            'db_name': [APImodels.ReactionComponentEID, 'db_name'],
            'external_id': [APImodels.ReactionComponentEID, 'ext_id'],
            'external_link': [APImodels.ReactionComponentEID, 'link'],
        },
        'reaction': {
            'name': [APImodels.Reaction, 'name'],
            'ec': [APImodels.Reaction, 'ec'],
            'pmid': [APImodels.ReactionReference, 'pmid'],
        },
        'reactionEID': {
            # 'id': [APImodels.ReactionEID, 'reaction'],
            'db_name': [APImodels.ReactionEID, 'db_name'],
            'external_id': [APImodels.ReactionEID, 'ext_id'],
            'external_link': [APImodels.ReactionEID, 'link'],
        },
        'subsystem': {
            'description': [APImodels.Subsystem, 'description'],
            # 'system': [APImodels.Subsystem, 'system'],
        },
        'subsystemEID': {
            # 'id': [APImodels.SubsystemEID, 'subsystem'],
            'db_name': [APImodels.SubsystemEID, 'db_name'],
            'external_id': [APImodels.SubsystemEID, 'ext_id'],
            'external_link': [APImodels.SubsystemEID, 'link'],
        },
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
                if 'id' not in d:
                    print (d)
                    print ("Error: column 'ID' must be in the annotation file")
                    exit(1)
                if d['id']:
                    # exclude column with empty id
                    l.append(d)
    return l


def update_metabolite(database, row_ann_dict, mapping_model_annotation_dict):
    reaction_component_dict = {}
    metabolite_dict = {}
    for file_column, value in row_ann_dict.items():
        # check if the column in the mapping dict
        if file_column == 'id':
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

    rc = APImodels.ReactionComponent.objects.using(database).filter(id=row_ann_dict['id'])
    if not rc:
        print ("Warning: reaction component ID '%s' not in the model, cannot update annotation" % row_ann_dict['id'])
        return

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
        if file_column == 'id':
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

    if 'aliases' in reaction_component_dict:
        reaction_component_dict['aliases'] = reformat_list(reaction_component_dict['aliases'])
    if 'ec' in gene_dict:
        gene_dict['ec'] = reformat_list(gene_dict['ec'])

    rc = APImodels.ReactionComponent.objects.using(database).filter(id=row_ann_dict['id'])
    if not rc:
        print ("Warning: reaction component ID '%s' not in the model, cannot update annotation" % row_ann_dict['id'])
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
        if file_column == 'id':
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

    # parse PMID
    if 'pmid' in row_ann_dict:
        pmids_list = [e.strip() for e in row_ann_dict['pmid'].split(';')]
    if 'ec' in reaction_dict:
        reaction_dict['ec'] = reformat_list(reaction_dict['ec'])

    r = APImodels.Reaction.objects.using(database).filter(id=row_ann_dict['id'])
    if not r:
        print ("Warning: reaction ID '%s' not in the model, cannot update annotation" % row_ann_dict['id'])
        return

    r.update(**reaction_dict)
    for pmid in pmids_list:
        pmid = pmid.strip()
        rr = APImodels.ReactionReference.objects.using(database).filter(reaction=r, pmid=pmid)
        if not rr:
            rr = APImodels.ReactionReference(reaction=r[0], pmid=pmid)
            rr.save(using=database)


def update_subsystem(database, row_ann_dict, mapping_model_annotation_dict):
    subystem_dict = {}
    for file_column, value in row_ann_dict.items():
        # check if the column in the mapping dict
        if file_column == 'id':
            continue
        if file_column not in mapping_model_annotation_dict:
            print ("Error: file column '%s' not found in mapping dictionnary" % file_column)
            exit(1)

        [model_field, model_table] = mapping_model_annotation_dict[file_column]
        if model_field in subystem_dict:
            print ("Error: multiple columns update the field '%s' in model %s " % (model_field, model_table))
            exit(1)
        subystem_dict[model_field] = value

    s = APImodels.Subsystem.objects.using(database).filter(name=row_ann_dict['id'])
    if not s:
        print ("Warning: subsystem name '%s' not in the model, cannot update annotation" % row_ann_dict['id'])
        return

    s.update(**subystem_dict)


def get_clean_database_name(db_name):
    valid_name = {
        'bigg': 'BiGG',
        'chebi': 'ChEBI',
        'ehmn': 'EHMN',
        'ensembl': 'Ensembl',
        'hepatonet1': 'HepatoNET1',
        'hmdb': 'HMDB',
        'hmr 2.0': 'HMR 2.0',
        'kegg': 'KEGG',
        'lipidmaps': 'LipidMaps',
        'metanetx': 'MetaNetX',
        'ncbi gene': 'NCBI Gene',
        'protein atlas': 'Protein Atlas',
        'pubchem': 'PubChem',
        'ratcon': 'Ratcon',
        'reactome': 'Reactome',
        'recon3d': 'Recon3D',
        'uniprot': 'UniProt',
    }
    try:
        return valid_name[db_name.lower()]
    except:
        print("Error: Database name '%s' is not allowed" % db_name)
        exit(1)

def validate_external_link(external_link):
    if external_link and not external_link.startswith(" https://identifiers.org/"):
        print ("Error: invalid link '%s'" % external_link)
        exit(1)

def fill_dict(ann_dict, mapping_model_annotation_dict):
    d = {}
    for file_column, value in ann_dict.items():
        # check if the column in the mapping dict
        if file_column == 'id':
            continue
        if file_column not in mapping_model_annotation_dict:
            print ("Error: file column '%s' not found in mapping dictionnary" % file_column)
            exit(1)
        if file_column == 'db_name':
            value = get_clean_database_name(value)
        elif file_column == 'external_link':
            validate_external_link(value)

        [model_field, model_table] = mapping_model_annotation_dict[file_column]
        if model_field in d:
            print ("Error: multiple columns update the field '%s' in model %s " % (model_field, model_table))
            exit(1)
        d[model_field] = value
    return d


def update_rc_eid(database, row_ann_dict, mapping_model_annotation_dict):
    rce_dict = fill_dict(row_ann_dict, mapping_model_annotation_dict)
    rc = APImodels.ReactionComponent.objects.using(database).filter(id=row_ann_dict['id'])
    if not rc:
        print ("Warning: reaction component ID '%s' not in the model, cannot update annotation" % row_ann_dict['id'])
        return

    rc_eid = APImodels.ReactionComponentEID.objects.using(database).filter(
        rc=rc,
        db_name=rce_dict['db_name'],
        external_id=rce_dict['external_id'])

    if not rc_eid:
        m = APImodels.ReactionComponentEID(rc=rc[0], **rce_dict)
        m.save(using=database)
    else:
        rc_eid.update(**rce_dict)


def update_reaction_eid(database, row_ann_dict, mapping_model_annotation_dict):
    reactioneid_dict = fill_dict(row_ann_dict, mapping_model_annotation_dict)
    r = APImodels.Reaction.objects.using(database).filter(id=row_ann_dict['id'])
    if not r:
        print ("Warning: reaction ID '%s' not in the model, cannot update annotation" % row_ann_dict['id'])
        return

    reaction_eid = APImodels.ReactionEID.objects.using(database).filter(
        reaction=r,
        db_name=reactioneid_dict['db_name'],
        external_id=reactioneid_dict['external_id'])

    if not reaction_eid:
        m = APImodels.ReactionEID(reaction=r[0], **reactioneid_dict)
        m.save(using=database)
    else:
        reaction_eid.update(**reactioneid_dict)


def update_subsystem_eid(database, row_ann_dict, mapping_model_annotation_dict):
    subsystemeid_dict = fill_dict(row_ann_dict, mapping_model_annotation_dict)
    s = APImodels.Subsystem.objects.using(database).filter(id=row_ann_dict['id'])
    if not s:
        print ("Warning: subsystem name '%s' not in the model, cannot update annotation" % row_ann_dict['id'])
        return

    subsystem_eid = APImodels.SubsystemEID.objects.using(database).filter(
        subsystem=s,
        db_name=subsystemeid_dict['db_name'],
        external_id=subsystemeid_dict['external_id'])

    if not subsystem_eid:
        m = APImodels.SubsystemEID(reaction=r[0], **subsystemeid_dict)
        m.save(using=database)
    else:
        subsystem_eid.update(**subsystemeid_dict)


def insert_annotation(database, component_type, file):
    switch = {
        'metabolite': update_metabolite,
        'gene': update_gene,
        'reaction': update_reaction,
        'subsystem': update_subsystem,
        'metaboliteEID': update_rc_eid,
        'geneEID': update_rc_eid,
        'reactionEID': update_reaction_eid,
        'subsystemEID': update_subsystem_eid,
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
                    c += 1
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
        parser.add_argument('type', action='store', help="")
        parser.add_argument('annotation file', action='store', default=None, nargs='?')

    def handle(self, *args, **options):
        database = options['database']
        if not options['annotation file']:
            raise ValueError("Error: the following argument is required: annotation file")
        insert_annotation(database, options['type'], options['annotation file'])


