from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET
import re, string

savefunc = ["htmlspecialchars"]
brakelist = []


# find var -------
# find value of var. may contains func (if contains - proof in list if filtered-func.
# if filtered - value=safe and listofskip-vars.append var)
# go down until echo or EOF
# foreach xml and if value=save/savevar - remove

def find_var(string):
    regex = r'(?:\$_?)(\w+)((\[\')(\w+)(\'\]))?'
    listrez = re.findall(regex, string)
    POST = ""
    var = ""
    returnlist = []
    if len(listrez) > 0:
        for rez in listrez:
            if rez[3]:
                POST = rez[0] + "['" + rez[3] + "']"
            if not rez[3]:
                var = rez[0]
            if (POST is not "") and (POST not in returnlist):
                returnlist.append(POST)
            if (var is not "") and (var not in returnlist):
                returnlist.append(var)
    if returnlist:
        return returnlist
    else:
        return False


def find_func(string, var):
    if '[' in var:
        var = var.replace("[", "\[")
    regex = r'(?:(\w+)(?:\())*(\$_?' + var + ')'
    listrez = re.findall(regex, string)
    func = ""
    returnlist = []
    if len(listrez) > 0:
        for rez in listrez:
            if rez[0]:
                func = rez[0]
            if func is not "":
                if func not in brakelist:
                    returnlist.append(func)
    if returnlist:
        return returnlist
    else:
        return False


def find_value(string, var):
    regex = r'(\(?\$_?' + var + '\)?)(?:\s?=\s?)(?:(\w+)(?:\())*(?:\$_?)(\w+)(?:(?:\[\')?(\w*)(?:\'\])?)'
    listrez = re.findall(regex, string)
    POST = ""
    var = ""
    returnlist = []
    if len(listrez) > 0:
        for rez in listrez:
            if rez[3]:
                POST = rez[2] + "['" + rez[3] + "']"
            if not rez[3]:
                var = rez[2]
            if (POST is not "") and (POST not in returnlist) and POST not in brakelist:
                returnlist.append(POST)
            if (var is not "") and (var not in returnlist) and var not in brakelist:
                returnlist.append(var)
    if returnlist:
        return returnlist
    else:
        return False


def var_exists(what, var):
    tree = ET.parse("files.xml")
    root = tree.getroot()
    for file in root.findall('file'):
        try:
            for item in file.findall(what):
                if item.text == var:
                    return True
        except:
            pass


tree = ET.parse("files.xml")
root = tree.getroot()
var_value = {}
var_filter = {}

for file in root.findall('file'):
    try:
        filename = file.find('name').text
        f = open(filename, 'r')
        doc = f.readlines()
        #open file from xml and do magic
        for line in doc:
            varlist = find_var(line)
            if varlist:
                for var in varlist:
                    valuelist = find_value(line, var)
                    if valuelist:
                        for value in valuelist:
                            if '\'' in value:
                                var_value[var] = value
                                brakelist.append(var)
                            if '\'' not in value:
                                var_value[var] = value
                            func_value_list = find_func(line, value)
                            if func_value_list:
                                for func in func_value_list:
                                    if func in savefunc:
                                        var_filter[value] = func
                                        break
                                    else:
                                        var_filter[value] = func
                    func_var_list = find_func(line, var)
                    if func_var_list:
                        for func in func_var_list:
                            if func in savefunc:
                                var_filter[var] = func
                                break
                            else:
                                var_filter[var] = func

        for var in var_value:
            for filtered_var in var_filter:
                var_node = SubElement(file, 'var')
                var_node.attrib["name"] = var
                var_node.attrib["filtered"] = var_filter.get(var) if var == filtered_var else ""
                var_node.attrib["value"] = var_value.get(var) if var_value.get(var) else ""
                var_node.attrib["filtered_value"] = var_filter.get(filtered_var) if var_value.get(var) and var_value.get(var) == filtered_var else ""
        var_value.clear()
        var_filter.clear()
        tree = ET.ElementTree(root)
        tree.write("files.xml")

    except:
        print "no access to file " + filename
