from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET
import re

tree = ET.parse("files.xml")
root = tree.getroot()

echo_flag = False
filter_flag = False
filter_of_value_flag = False
name = ""
value = ""

for file in root.findall('file'):
    try:
        for var in file.findall('var'):
            if var.get('echo_line') is not "":
                echo_flag = True
            if var.get('filter') is not "":
                filter_flag = True
            if var.get('filter_of_value') is not "":
                filter_of_value_flag = True
            if var.get('value') is not "":
                value = var.get('value')
            name = var.get('name')



    except:
        pass