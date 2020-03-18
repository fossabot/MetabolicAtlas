import os
import collections

# return the header (preffixed with @) as list
def get_metadata(file):
    try:
        header = []
        with open(file, 'r') as fh:
            for line in fh:
                line = line.strip()
                if not line or line[0] == "#":
                    continue
                arr = line.split('\t')
                if line[0] == "@":
                    header = arr
                    header[0] = header[0][1:]
                break
    except Exception as e:
        print(e)
        exit(1)
    return header

# read annotation file and return the content as a dict of dict
def file_to_dicts_values(file):
    try:
        d = collections.OrderedDict()
        IDs = set()
        with open(file, 'r') as fh:
            header = []
            for line in fh:
                line = line.strip('\n')
                if not line or line[0] == "#":
                    continue
                arr = line.split('\t')
                if line[0] == "@":
                    header = arr
                    header[0] = header[0][1:]
                else:
                    new_d = dict(zip(header, arr))
                    if 'id' not in new_d or not new_d['id']:
                        print ("Error: ID key not found or empty when parsing annotation file")
                        exit(1)
                    if new_d['id'] in IDs:
                        print ("Error: duplicate ID '%s'" % new_d['id'])
                        exit(1)
                    d[new_d['id']] = new_d
    except Exception as e:
        print(e)
        exit(1)
    return d

# write the content of the ordered_dict into the existing file 'annotation_file'
def write_dicts_to_annotation_file(ordered_dict, annotation_file):
    if not os.path.isfile(annotation_file):
        print ("Error: file '%s' not found")
        exit(1)

    lines = []
    with open(annotation_file, 'r') as fh:
        lines = []
        header = []
        # save header, comments etc..
        for line in fh:
            line = line.strip('\n')
            if not line or line[0] == "#":
                lines.append(line)
                continue
            arr = line.split('\t')
            if line[0] == "@":
                lines.append(line)
                header = arr
                header[0] = header[0][1:]

        for row_dict in ordered_dict.values():
            lines.append("\t".join([row_dict[c] if c in row_dict else '' for c in header]))

    if lines:
        with open(annotation_file, 'w') as fw:
            fw.write('\n'.join(lines))

# read the annotation file, add the content to the input dict
def merge_values(annotation_file, dict_values_dicts):
    ordered_dict = file_to_dicts_values(annotation_file)
    new_dicts_list = []
    contains_ID = set()

    # read the row data in the file in order
    for ID, dico in ordered_dict.items():
        if ID not in dict_values_dicts:
            continue
        else:
            # merge dicts_values and dict_file
            dict_values_dicts[ID].pop('id', None)  # prevent changing the ID
            dico.update(dict_values_dicts[ID])
        contains_ID.add(ID)

    # add new annotations, for ID not already in the file
    for ID, d in dict_values_dicts.items():
        if ID in contains_ID:
            continue

        d.pop('id', None)  # prevent changing the ID
        d['id'] = ID
        ordered_dict[ID] = d  # might not contains all the headercolumns

    return ordered_dict


