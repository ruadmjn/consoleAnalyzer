from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET
import re

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
                POST = rez[0] + "_['" + rez[3] + "']"
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
    regex = r'(\$_?' + var + ')(?:\s?=\s?)(?:(\w+)(?:\())*(?:\$_?)(\w+)(?:(?:\[\')?(\w*)(?:\'\])?)'
    listrez = re.findall(regex, string)
    POST = ""
    var = ""
    returnlist = []
    if len(listrez) > 0:
        for rez in listrez:
            if rez[3]:
                POST = rez[2] + "_['" + rez[3] + "']"
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

for file in root.findall('file'):
    try:
        filename = file.find('name').text
        f = open(filename, 'r')
        doc = f.readlines()
        for line in doc:
            varlist = find_var(line)
            if varlist:
                for var in varlist:
                    if var in brakelist:
                        continue
                    if not var_exists('var', var):
                        var_node = SubElement(file, 'var')
                        var_node.text = var
                    #if var exists
                    valuelist = find_value(line, var)
                    if valuelist:
                        for value in valuelist:
                            funclist = find_func(line, value)
                            if funclist:
                                for func in funclist:
                                    if func in savefunc:
                                        brakelist.append(func)
                                        brakelist.append(value)
                                        continue
                                    func_node = SubElement(var_node, 'func')
                                    func_node.text = func
                            if value not in brakelist:
                                # check if var exists
                                if not var_exists('value', value):
                                    value_node = SubElement(var_node, 'value')
                                    value_node.text = value
                                    brakelist.append(value)
            tree = ET.ElementTree(root)
            tree.write("files.xml")

    except:
        print "no access to file " + filename
