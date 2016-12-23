from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET
import re

tree = ET.parse("files.xml")
root = tree.getroot()

for file in root.findall('file'):
    try:
        filename = file.find('name').text
        list_type_line = []
        list_val_value = []
        vuln_type = ""
        vuln_dict = {}
        for var in file.findall('var'):
            echo_flag = False
            filter_flag = False
            filter_of_value_flag = False
            name = ""
            value = ""
            if var.get('echo_line') != '':
                echo_flag = True
            if var.get('filter') != '':
                #must add filter check
                filter_flag = True
            if var.get('filter_of_value') != '':
                # must add filter check
                filter_of_value_flag = True
            if var.get('value') != '':
                value = var.get('value')
            name = var.get('name')

            #logic

            if '[' in value and not filter_flag and not filter_of_value_flag:
                if echo_flag:
                    vuln_type = "xss"
                    list_val_value.append(name)
                    list_val_value.append(value)
                    list_type_line.append(vuln_type)
                    list_type_line.append(var.get('echo_line'))
                    vuln_dict[str(list_type_line)] = list_val_value
                    list_val_value = []
                    list_type_line = []
                if not echo_flag:
                    for proof_var in file.findall('var'):
                        if proof_var.get('value') == name and proof_var.get('name') is not name:
                            #we found another var with vuln value
                            if proof_var.get('filter') == "" and proof_var.get('filter_of_value') == "":
                                if proof_var.get('echo_line') is not '':
                                    vuln_type = "xss"
                                else:
                                    vuln_type = "weakness"
                                list_val_value.append(proof_var.get('name'))
                                list_val_value.append(proof_var.get('value'))
                                list_type_line.append(vuln_type)
                                list_type_line.append(proof_var.get('echo_line'))
                                vuln_dict[str(list_type_line)] = list_val_value
                                list_val_value = []
                                list_type_line = []
        print filename+": "
        print vuln_dict
    except:
        pass