import zipfile, os
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET

PROJECT_FOLDER = "target"


zip = zipfile.ZipFile('file.zip')
zip.extractall(PROJECT_FOLDER)

rootDir = PROJECT_FOLDER
top = Element('project', {'name':'.zip'})
for dirName, subdirList, fileList in os.walk(rootDir):
    for fname in fileList:
        file_node = SubElement(top, 'file')
        name_node = SubElement(file_node, 'name')
        name_node.text = os.path.join(dirName,fname)
tree = ET.ElementTree(top)
tree.write("files.xml")