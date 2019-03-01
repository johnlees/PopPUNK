#!/usr/bin/env python
# vim: set fileencoding=<utf-8> :
# Copyright 2019 John Lees and Nick Croucher

# core
import sys
import os
import shutil
import json
import hashlib
import operator
from collections import Counter

# poppunk
from .__main__ import assign_query

# main code
def main():

    # Summary doc
    summary = json.load(sys.stdin)

    # Strain docs
    strain_ids = []
    strain_names = {}
    db_loc = None
    for strain in json.load(sys.stdin):
        strain_ids.append(strain['fileId'])
        strain_names[strain['name']] = strain['fileId']

        if db_loc is None:
            db_loc = strain['dbloc']
        elif db_loc is not strain['dbloc']:
            raise RuntimeError('Inconsistent dbloc in strains')

        sys.stderr.write("Read strain doc for " + strain['name'] + "\n")

        if len(strain_ids) == len(summary['strains']):
            if set(strain_ids) != set(summary['strains']):
                raise RuntimeError('Summary and strain doc ID mismatch')
            else:
                break

    # Query docs
    q_file_name = "qlist.txt"
    query_ids = []
    tmp_query_files = []
    for query in json.load(sys.stdin):
        query_ids.append(query['fileID'])

        # Write fasta for sketching (delete later)
        tmp_sequence_file = query['fileID'] + ".fa"
        tmp_query_files.append(tmp_sequence_file)
        with open(tmp_sequence_file, 'w') as qfile:
            qfile.write(tmp_sequence_file + "\n")

        if len(query_ids) == len(summary['inputs']):
            if set(query_ids) != set(summary['inputs']):
                raise RuntimeError('Summary and sample doc ID mismatch')
            else:
                break

    with open(q_file_name, 'w') as qlist:
        for query_file in tmp_query_files:
            qlist.write(query_file + "\n")

    # run assign query mode
    options = {
        'ref_db' : 'strain_db',
        'q_files' : q_file_name,
        'output' : 'pw_db',
        'update_db' : False,
        'distances' : 'strain_db/strain_db.dists',
        'microreact' : True,
        'cytoscape' : False,
        'kmers' : [13, 17, 21, 25, 29],
        'sketch_sizes' : [10000, 10000, 100000, 10000, 10000],
        'ignore_length' : False,
        'threads' : 1,
        'mash' : 'mash',
        'overwrite' : True,
        'plot_fit' : False,
        'no_stream' : True,
        'max_a_dist' : 0.5,
        'model_dir' : 'strain_db',
        'previous_clustering' : None,
        'core_only' : False,
        'accessory_only' : False,
        'phandango' : False,
        'grapetree' : False,
        'info_csv' : None,
        'rapidnj' : 'rapidnj',
        'perplexity' : 20
    }

    clusters = assign_query(options['ref_db'], options['q_files'], options['output'], options['update_db'], options['distances'],
                 options['microreact'], options['cytoscape'], options['kmers'], options['sketch_sizes'], options['ignore_length'],
                 options['threads'], options['mash'], options['overwrite'], options['plot_fit'], options['no_stream'],
                 options['max_a_dist'], options['model_dir'], options['previous_clustering'], options['core_only'],
                 options['accessory_only'], options['phandango'], options['grapetree'], options['info_csv'],
                 options['rapidnj'], options['perplexity'])

    # reformat output as new strain and results JSON

    # find new strains
    new_strains = []
    for updated_strain_name in set(clusters.keys()):
        if str(updated_strain_name) not in strain_names.keys():
            updated_fileId = hashlib.sha1(str(updated_strain_name)).hexdigest()
            strain_names[str(updated_strain_name)] = updated_fileId
            new_strain_doc = {'fileId': updated_fileId, 'name': str(updated_strain_name), 'db_loc': db_loc}
            json.dump(new_strain_doc, sys.stdout)
            new_strains.append(updated_fileId)

    # iterate through cluster dictionary sorting by value
    freq_order = sorted(dict(Counter(clusters.values())).items(), key=operator.itemgetter(1), reverse=True)
    freq_order = [x[0] for x in freq_order]
    new_strain_dict = {}
    for cluster_member, cluster_name in sorted(clusters.items(), key=lambda i:freq_order.index(i[1])):
        new_strain_dict[cluster_member] = strain_names[str(cluster_name)]

    # pick up tree and dot from file
    with open("pw_db/pw_db_core_NJ.nwk", 'r') as nj_file:
        nj_tree = nj_file.read()
    with open("pw_db/pw_db_perplexity" + str(options['perplexity']) + "_accessory_tsne.dot", 'r') as dot_file:
        accessory_dot = dot_file.read()

    # stream results out
    results = {'new_strains': new_strains, 'other': new_strain_dict, 'tree': nj_tree, 'dot': accessory_dot}
    json.dump(results, sys.stdout)

    # delete tmp files
    with open(q_file_name, 'w') as qlist:
        for query_file in tmp_query_files:
            os.remove(query_file)
    os.remove(q_file_name)
    shutil.rmtree('work_db')

if __name__ == "__main__":
    main()

    sys.exit(0)
