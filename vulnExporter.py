from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET
import re

tree = ET.parse("files.xml")
root = tree.getroot()
all_vulns = {}
vulnchannels_list = ['POST','GET','REQUEST','COOKIE']

def check_channel(POSTvar):
    regex = r'(\w+)(\[\'\w+\'\])'
    listrez = re.findall(regex, POSTvar)
    boolrez = False
    for rez in listrez:
        if rez[0] in vulnchannels_list:
            boolrez = True
    return boolrez


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
            const_name = name
            #logic

            if not filter_flag and not filter_of_value_flag:
                if '[' in value:
                    if echo_flag:
                        if not check_channel(var.get('value')):
                            vuln_type = "stored_xss"
                        else:
                            vuln_type = "xss"
                        list_val_value.append(name)
                        list_val_value.append(value)
                        list_type_line.append(vuln_type)
                        list_type_line.append(var.get('echo_line'))
                        vuln_dict[str(list_type_line)] = list_val_value
                        list_val_value = []
                        list_type_line = []
                        continue
                if not echo_flag:
                    for proof_var in file.findall('var'):
                        if (proof_var.get('value') == name) and proof_var.get('name') is not name:
                            #we found another var with vuln value
                            if proof_var.get('filter') == "" and proof_var.get('filter_of_value') == "":
                                if proof_var.get('echo_line') is not '':
                                    vuln_type = "xss"
                                else:
                                    vuln_type = "weakness"
                                list_val_value.append(proof_var.get('name'))
                                list_val_value.append(proof_var.get('value') if '[' in proof_var.get('value') else var.get('value'))
                                list_type_line.append(vuln_type)
                                list_type_line.append(var.get('echo_line') if var.get('echo_line') != '' else proof_var.get('echo_line'))
                                vuln_dict[str(list_type_line)] = list_val_value
                                list_val_value = []
                                list_type_line = []
                                continue
                if echo_flag and '[' not in value:
                    for proof_var in file.findall('var'):
                        if (proof_var.get('name') == value) and (proof_var.get('name') is not name) :
                            # we found another var with vuln value
                            if '[' not in proof_var.get('value'):
                                value = proof_var.get('value')
                            if '[' in proof_var.get('value'):
                                if proof_var.get('filter') == "" and proof_var.get('filter_of_value') == "":
                                    if not check_channel(proof_var.get('value')):
                                        vuln_type = "stored_xss"
                                    else:
                                        vuln_type = "xss"
                                    list_val_value.append(const_name)
                                    list_val_value.append(proof_var.get('value'))
                                    list_type_line.append(vuln_type)
                                    list_type_line.append(var.get('echo_line'))
                                    vuln_dict[str(list_type_line)] = list_val_value
                                    list_val_value = []
                                    list_type_line = []
                                    continue

        all_vulns[filename] = vuln_dict

    except:
        pass

    top = Element('project', {'name': '.zip'})
    for file in all_vulns:
        file_node = SubElement(top, 'file')
        file_node.attrib["name"] = file
        for vuln in all_vulns.get(file):
            vtype = vuln.split()[0].replace('\'','').replace('[','').replace(',','')
            line = vuln.split()[1].replace('\'','').replace(']','').replace(',','')
            var = all_vulns.get(file).get(vuln)[0]
            value = all_vulns.get(file).get(vuln)[1]
            vuln_node = SubElement(file_node, 'vuln')
            vuln_node.attrib["vtype"] = vtype
            vuln_node.attrib["line"] = line
            vuln_node.attrib["var"] = var
            vuln_node.attrib["value"] = value

tree = ET.ElementTree(top)
tree.write("vulns.xml")



