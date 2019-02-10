import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# DICOMwebInterface
#

class DICOMwebInterface(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "DICOMwebInterface" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Informatics"]
    self.parent.dependencies = []
    self.parent.contributors = ["Steve Pieper (Isomics, Inc.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    Builds an interface to servers supporting DICOMweb RS API
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# DICOMwebInterfaceWidget
#

class DICOMwebInterfaceWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

#
# DICOMwebInterfaceLogic
#

class DICOMwebInterfaceLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """


  # TODO: convert to DICOMweb
  def fetchAndLoadSeries(self,seriesUID):
    tmpdir = tempfile.mkdtemp()

    api = "/_design/instances/_view/seriesInstances?reduce=false"
    args = '&key="%s"' % seriesUID
    seriesInstancesURL = self.db.resource().url + api + args
    urlFile = urllib.urlopen(seriesInstancesURL)
    instancesJSON = urlFile.read()
    instances = json.loads(instancesJSON)
    filesToLoad = []
    for instance in instances['rows']:
      classUID,instanceUID = instance['value']
      if classUID in self.imageClasses:
        doc = self.db[instanceUID]
        print("need to download ", doc['_id'])
        instanceURL = self.db.resource().url + '/' + doc['_id'] + "/object.dcm"
        instanceFileName = doc['_id']
        instanceFilePath = os.path.join(tmpdir, instanceFileName)
        urllib.urlretrieve(instanceURL, instanceFilePath)
        filesToLoad.append(instanceFilePath);
      else:
        print('this is not an instance we can load')
    node = None
    if filesToLoad != []:
      status, node = slicer.util.loadVolume(filesToLoad[0], {}, returnNode=True)
    return node

  def fetchAndLoadDICOMwebStudy(self,dicomWebServer, studyUID):
    """Download the study data from DICOM Web
    """
    import urllib
    import json
    import os
    import tempfile
    url = os.path.join(dicomWebServer, "studies", studyUID, "instances")
    instanceListFile = urllib.urlopen(url)
    instanceListJSON = instanceListFile.read()
    instanceList = json.loads(instanceListJSON)
    tmpdir = tempfile.mkdtemp()
    for instance in instanceList:
      instanceURL = instance['00081190']['Value'][0]
      print(instanceURL)
      instanceFilePath = os.path.join(tmpdir, os.path.basename(instanceURL))
      urllib.urlretrieve(instanceURL, instanceFilePath)


class DICOMwebInterfaceTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_DICOMwebInterface1()

  # TODO: click callback
  def webViewLinkClickedCallback(self,qurl):
    url = qurl.toString()
    print(url)
    if url == 'reslicing':
      self.reslicing()
    if url == 'chart':
      self.chartTest()

  def loadDICOMwebStudy(self,studyUID):
    logic = DICOMwebInterfaceLogic()
    print(self.dicomWebServer, studyUID)
    logic.fetchAndLoadDICOMwebStudy(self.dicomWebServer, studyUID)

  def test_DICOMwebInterface1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test", 50)

    webPath = os.path.dirname(os.path.dirname(slicer.modules.dicomwebinterface.path))
    url = 'file://' + os.path.join(webPath, 'StudyBrowser/index.html')

    webWidget = slicer.qSlicerWebWidget()
    slicerGeometry = slicer.util.mainWindow().geometry
    webWidget.size = qt.QSize(900,600)
    webWidget.pos = qt.QPoint(slicerGeometry.x() + 256, slicerGeometry.y() + 128)

    self.dicomWebServer = 'https://server.dcmjs.org/dcm4chee-arc/aets/DCM4CHEE/rs'

    webWidget.url = url+"?server="+self.dicomWebServer
    print(url)
    webWidget.show()

    slicer.modules.DICOMwebInterfaceWidget.webWidget = webWidget
