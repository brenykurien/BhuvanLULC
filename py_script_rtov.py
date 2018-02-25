
"""                MAKE SURE YOU HAVE SAVED THE QGIS PROJECT FILE  FOR THIS SCRIPT TO WORK                     """
"""      THIS PYTHON SCRIPT CONVERTS BHUVANS LULC TIFF IMAGES TO CORRESPONDING FEATURE VECTOR FILES          """
""""
255:"Built up urban",   168:"Built up rural",   268:"Built up mining",
370:"Agriculture crop land",     276:"Agriculture Plantain",     436:"Agriculture Fallow",
142:"Forest deciduos",  288:"Forest scrub land"
505:"Barren Scrub land",    484:"Barren Sandy area",    487:"Barren rocky", 
222:"Wetland, River",   354:"Wetland, Ponds",   132:"Wetland, Inland", 
465:"Barren gullied",,  467:"Barren salt affected"
"""
"""       TO GET A FEATURE ENTER THE CORRESPONDING NUMBER BEFORE IT      """
"""    FOR EXAMPLE TO GET BUILT UP URBAN REGION RUN THE SCRIPT AND ENTER 255 WHEN THE POP UP COMES UP  """

# script to convert raster LULC from bhuvan to corresponding vector features

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import sys
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
import processing
import os


layer = iface.activeLayer()
entries = []

# Define band1
boh1 = QgsRasterCalculatorEntry()
boh1.ref = 'boh@1'
boh1.raster = layer
boh1.bandNumber = 1
entries.append(boh1)

# Define band3
boh3 = QgsRasterCalculatorEntry()
boh3.ref = 'boh@3'
boh3.raster = layer
boh3.bandNumber = 3
entries.append(boh3)

#project file path
project_file_root=QgsProject.instance().readPath("./")
# Process calculation with input extent and resolution
calc = QgsRasterCalculator('boh@1 + boh@3', project_file_root+'/raster_calculator.tif', 'GTiff', layer.extent(), layer.width(), layer.height(), entries)
result = calc.processCalculation()

# add generated image to qgis
end=0
if result == 0:
    fileName = project_file_root+"/raster_calculator.tif"
    fileInfo = QFileInfo(fileName)
    baseName = fileInfo.baseName()
    mylayer = QgsRasterLayer(fileName, baseName)
    QgsMapLayerRegistry.instance().addMapLayer(mylayer, True)
    print "Raster calculator layer created."
else:
    print "Check if bhuvan LULC data is highlighted in the layer panel!!"
    end=1
    

# convert the generated raster to vectors with the following list as enteries
classification_string={255:"Built up urban",168:"Built up rural", 268:"Built up mining", 370:"Agriculture crop land", 276:"Agriculture Plantain", 436:"Agriculture Fallow", 142:"Forest deciduos", 505:"Barren Scrub land", 484:"Barren Sandy area", 487:"Barren rocky", 222:"Wetland, River", 354:"Wetland, Ponds", 132:"Wetland, Inland", 465:"Barren gullied", 288:"Forest scrub land", 467:"Barren salt affected"}
# chose these raster values to convert to vector
if end !=1:
    qid = QInputDialog()
    title = "Enter Class Number"
    label = "Number: "
    mode = QLineEdit.Normal
    default = "<your number here>"
    try:
        text, ok = QInputDialog.getText(qid, title, label, mode, default)
        int(text)
    except:
        print "Hmm.. That ended abruptly."
        text =0
    
    if int(text) in classification_string:
        print text
        legend = [int(text)]#255, 168, 268, 370, 276, 436, 142, 505, 484, 487, 222, 354, 132, 465, 288, 467]
        fileName = project_file_root+"/raster_calculator.tif"
        fileInfo = QFileInfo(fileName)
        baseName = fileInfo.baseName()
        mylayer = QgsRasterLayer(fileName, baseName)
        entries_1eg = []

        # Define band1
        b1 = QgsRasterCalculatorEntry()
        b1.ref = 'b1@1'
        b1.raster = mylayer
        b1.bandNumber = 1
        entries_1eg.append(b1)

        # Start the seperation process
        
        expression = '( ' + entries_1eg[0].ref + ' ) = '+str(legend[0])+' '
        print expression
        ans = QgsRasterCalculator(expression, project_file_root+"/"+str(legend[0])+'.tif', 'GTiff', mylayer.extent(), mylayer.width(), mylayer.height(), entries_1eg)
        ans.processCalculation()

        # Vectorize using processing
        processing.runalg("gdalogr:polygonize", project_file_root+"/"+str(legend[0])+'.tif',"DN", project_file_root+"/"+str(legend[0])+'.shp')
        vectorLyr = QgsVectorLayer(project_file_root+"/"+str(legend[0])+'.shp',str(legend[0]), "ogr")
        selection = vectorLyr.getFeatures(QgsFeatureRequest().setFilterExpression(u'"DN" = 0'))
        array_list = [s.id() for s in selection]
        vectorLyr.startEditing()
        for a in array_list:
            vectorLyr.deleteFeature(a)
        vectorLyr.commitChanges()
        processing.runalg("qgis:dissolve", vectorLyr, False, "DN", project_file_root+"/"+str(legend[0])+"_d.shp")
        vectorLyr = QgsVectorLayer(project_file_root+"/"+str(legend[0])+'_d.shp',str(legend[0])+'_dissolved', "ogr")
        vectorLyr.dataProvider().deleteAttributes([0])
        vectorLyr.dataProvider().addAttributes([QgsField("Class", QVariant.String)])
        vectorLyr.updateFields()
        # determine class 
        vectorLyr.startEditing()
        for f in vectorLyr.getFeatures():
            vectorLyr.changeAttributeValue(f.id(), 0 , classification_string[legend[0]])
        vectorLyr.commitChanges()
        QgsMapLayerRegistry.instance().addMapLayer(vectorLyr)
        print "The raster files have been generated!!"
    else:
        print "Please enter a number corresponding to the feature class you want to seperate!!"












