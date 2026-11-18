import os
import json
import datetime

from . import utils

################
# File merging #
################

# Combine multiple IBIS XAIF dicts into one.
def merge_ibis_xaif_list(xaif_list, file_name='', save_to_dir=''):
    merged_xaif_dict = utils.new_ibis_aif()

    for i, current_xaif in enumerate(xaif_list):
        # with open(input_path) as f:
            # current_aif = json.loads(f.read())

        # Core
        for n in current_xaif['AIF']['nodes']:
            old_id = n['nodeID']
            n['nodeID'] = f"{old_id}_{i}"

        # Seems silly to go through the edges separately, but it might actually
        # be more sensible than searching for all relevant edges every time you update a node.
        for e in current_xaif['AIF']['edges']:
            old_from_id = e['fromID']
            old_to_id = e['toID']
            e['fromID'] = f"{old_from_id}_{i}"
            e['toID'] = f"{old_to_id}_{i}"

        merged_xaif_dict['AIF']['nodes'] += current_xaif['AIF']['nodes']
        merged_xaif_dict['AIF']['edges'] += current_xaif['AIF']['edges']

        # Doing this 
        for t in ['issues', 'positions', 'arguments']:
            current_xaif['IBIS'][t] = [f"{old_id}_{i}" for old_id in current_xaif['IBIS'][t]]

        merged_xaif_dict['IBIS']['issues'] += current_xaif['IBIS']['issues']
        merged_xaif_dict['IBIS']['positions'] += current_xaif['IBIS']['positions']
        merged_xaif_dict['IBIS']['arguments'] += current_xaif['IBIS']['arguments']

    for j, e in enumerate(merged_xaif_dict['AIF']['edges']):
        e['edgeID'] = j


    if save_to_dir:
        if file_name:
            with open(os.path.join(save_to_dir, file_name), 'w') as f:
                json.dump(merged_xaif_dict, f, indent=4)
        else:
            with open(os.path.join(save_to_dir, f"xaifmerge_{datetime.datetime.now().strftime("%y%m%d%m%H%M%S")}.json"), 'w') as f:
                json.dump(merged_xaif_dict, f, indent=4)
    
    return merged_xaif_dict


def merge_ibis_list_with_parent(xaif_list, topic, file_name='', save_to_dir=''):
    # 1. Create the simply merged file
    merged_xaif = merge_ibis_xaif_list(xaif_list, file_name=file_name, save_to_dir=save_to_dir)

    # 2. Attach the top level issues of the merge to the supplied parent issue
    # Get the current orphan issues
    orphans = utils.get_orphans(merged_xaif)

    # Add new nodes for topic and connect them with edges
    topic_i = utils.add_node('origI', 'I', topic, merged_xaif)
    topic_l = utils.add_node('origL', 'L', f"User: {topic}", merged_xaif)
    merged_xaif['IBIS']['issues'].append('origI')
    utils.add_s_node_with_edges('origYA','YA', f"Default Illocuting", [topic_l['nodeID']], topic_i['nodeID'], merged_xaif)

    # Attach orphans to the topic issue
    for o_id in orphans:
        utils.add_s_node_with_edges(f"rel{o_id}_{topic_i['nodeID']}", 'MA', 'Related Issue', [o_id], topic_i['nodeID'], merged_xaif)
    
    if save_to_dir:
        if file_name:
            with open(os.path.join(save_to_dir, file_name), 'w') as f:
                json.dump(merged_xaif, f, indent=4)
        else:
            with open(os.path.join(save_to_dir, f"xaifmergetopic_{datetime.datetime.now().strftime("%y%m%d%H%M%S")}.json"), 'w') as f:
                json.dump(merged_xaif, f, indent=4)

    return merged_xaif

