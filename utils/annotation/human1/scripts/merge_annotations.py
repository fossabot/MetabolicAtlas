import tools
import sys
import argparse

# reaction_file_asso = sys.argv[1]  # TSV from https://github.com/SysBioChalmers/HMA_Sandbox/tree/master/Hao
# metabolite_file_asso = sys.argv[2]  # TSV from https://github.com/SysBioChalmers/HMA_Sandbox/tree/master/Hao
# REA_annotation_file = sys.argv[3]  # formated as annotation/human1/example/REACTIONS.tsv
# MET_annotation_file = sys.argv[4] # formated as annotation/human1/example/METABOLITES.tsv

# rea_dict = tools.file_to_dicts_values(reaction_file_asso)
# met_dict = tools.file_to_dicts_values(metabolite_file_asso)

# updated_rea_dict = tools.merge_values(REA_annotation_file, rea_dict)
# tools.write_dicts_to_annotation_file(updated_rea_dict, REA_annotation_file)

# updated_met_dict = tools.merge_values(MET_annotation_file, met_dict)
# tools.write_dicts_to_annotation_file(updated_met_dict, MET_annotation_file)

def main(annotation_file, annotation_plus_file):

    addon_dict = tools.file_to_dicts_values(annotation_plus_file)
    updated_dict = tools.merge_values(annotation_file, addon_dict)
    tools.write_dicts_to_annotation_file(updated_dict, annotation_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('annotation-file', help='TSV file, content to be inserted in the model database. see annotation/human1/example/REACTIONS.tsv')
    parser.add_argument('annotation-plus', help='partial annotation file to be merge inside the annotation-file')
    args = parser.parse_args()
    argv_dict = vars(args)

    annotation_file = argv_dict['annotation-file']
    annotation_plus_file = argv_dict['annotation-plus']
    main(annotation_file, annotation_plus_file)
