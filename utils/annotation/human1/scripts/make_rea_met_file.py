import tools
import sys

reaction_file_asso = sys.argv[1]
metabolite_file_asso = sys.argv[2]
REA_annotation_file = sys.argv[3]
MET_annotation_file = sys.argv[4]

rea_dict = tools.file_to_dicts_values(reaction_file_asso)
met_dict = tools.file_to_dicts_values(metabolite_file_asso)

updated_rea_dict = tools.merge_values(REA_annotation_file, rea_dict)
tools.write_dicts_to_annotation_file(updated_rea_dict, REA_annotation_file)

updated_met_dict = tools.merge_values(MET_annotation_file, met_dict)
tools.write_dicts_to_annotation_file(updated_met_dict, MET_annotation_file)
