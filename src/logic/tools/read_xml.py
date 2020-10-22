#encoding:utf-8

import os
import xml.dom.minidom

def GetCommonXMLData(file, path):
    if not os.path.exists(file):
        return None
    
    try:
        domtree = xml.dom.minidom.parse(file)
        path_arr = path.split("/")
        ret_data = domtree
        for item in path_arr:
            curr_nodes = ret_data.getElementsByTagName(item)
            if None != curr_nodes and len(curr_nodes) > 0:
                ret_data = curr_nodes[0]

        return ret_data
    except Exception as err:
        print(err)
        return None
    return None
