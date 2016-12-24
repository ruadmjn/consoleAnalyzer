from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET
import re

savefunc = ["htmlspecialchars"]
brakelist = []


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
    regex = r'(?:(\w+)(?:\())*(?:(?:\'?\"?(?:\$?\w*)?\'?\"?\.?)*)?(\$_?' + var + ')'
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


def find_echo(string):
    regex = r'(echo)'
    listrez = re.findall(regex, string)
    if len(listrez) > 0:
        for rez in listrez:
            return True
    else:
        return False


def find_value(string, var):
    regex = r'(\(?\$_?' + var + '\)?)(?:\s?=\s?)(?:(\w+)(?:\())*(?:(?:\'?\"?(?:\$?\w*)?\'?\"?\.?)*)?(?:\$_?)(\w+)(?:(?:\[\')?(\w*)(?:\'\])?)'
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
var_echo = {}
var_line = {}

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
                    if var not in brakelist:
                        valuelist = find_value(line, var)
                        if valuelist:
                            for value in valuelist:
                                var_value[var] = value
                                var_line[var] = doc.index(line)+1
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
                        if not valuelist:
                            if '\'' in var:
                                var_value[var] = var
                                var_line[var] = doc.index(line) + 1
                        if find_echo(line):
                            var_echo[var] = doc.index(line) + 1
                            var_line[var] = doc.index(line) + 1
                            brakelist.append(var)

        for var in var_value:
            var_node = SubElement(file, 'var')
            var_node.attrib["name"] = var
            var_node.attrib["value"] = var_value.get(var) if var_value.get(var) else ""
            var_node.attrib["echo_line"] = str(var_echo.get(var)) if var_echo.get(var) else ""
            var_node.attrib["line"] = str(var_line.get(var)) if var_line.get(var) else ""
            for filtered_var in var_filter:
                var_node.attrib["filter"] = var_filter.get(var) if var == filtered_var else ""
                var_node.attrib["filter_of_value"] = var_filter.get(filtered_var) if var_value.get(var) and var_value.get(var) == filtered_var else ""

        var_value.clear()
        var_filter.clear()
        var_echo.clear()
        brakelist = []
        tree = ET.ElementTree(root)
        tree.write("files.xml")

    except:
        print "no access to file " + filename
