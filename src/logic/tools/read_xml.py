#encoding:utf-8

import os
import xml.dom.minidom
import xml.etree.ElementTree
from lxml import etree

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

def GetServerAppBoxList(macros_file, admin_proxy_file):
    if not os.path.exists(macros_file) or not os.path.exists(admin_proxy_file):
        return None
    
    try:
        macros_map = {}
        macro_tree = etree.parse(macros_file)
        macros = macro_tree.getroot().findall("macro")
        for item in macros:
            macros_map[item.get("name")] = item.get("value")
        
        port_list = []
        admin_proxy_tree = etree.parse(admin_proxy_file)
        admin_proxys = admin_proxy_tree.getroot().find("admin_proxy").find("server_addrs").findall("server")
        for item in admin_proxys:
            port_str = item.get("port")
            if port_str[1:] in macros_map:
                port_list.append(macros_map[port_str[1:]])
        return port_list
    except Exception as err:
        print(err)
        return None
    return None
