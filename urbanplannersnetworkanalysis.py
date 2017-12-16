# -*- coding: utf-8 -*-
"""
/***************************************************************************
 urbanPlannersNetworkAnalysis
                                 A QGIS plugin
 Tool that uses the Network Analysis Library of QGIS to build a tool that even 
 an in geoinformatics not well trained urban planner can use.
                              -------------------
        begin                : 2017-12-15
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Janne Jakob Fleischer
        email                : janne.fleischer@googlemail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Janne Jakob Fleischer'
__date__ = '2017-12-16'
__copyright__ = '(C) 2017 by Janne Jakob Fleischer'

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from PyQt4.QtCore import *
from PyQt4 import uic, QtGui

from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from qgis.networkanalysis import *

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterVector
from processing.core.outputs import OutputVector
from processing.core.Processing import Processing
from processing.tools import dataobjects, vector

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from urbanplannersnetworkanalysis_dialog import urbanPlannersNetworkAnalysisDialog
# Import the code for the processing algorithm
from urbanplannersnetworkanalysisProcessingModule_provider import urbanplannersnetworkanalysisProcessingProvider

#this is from the processing plugin template. What does it do?
# import os.path
# cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
# if cmd_folder not in sys.path:
#     sys.path.insert(0, cmd_folder)

class urbanPlannersNetworkAnalysis:
    """QGIS Plugin Implementation."""
        
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'urbanPlannersNetworkAnalysis_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'Urban Planners Network Analysis Tools')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'urbanPlannersNetworkAnalysis')
        self.toolbar.setObjectName(u'urbanPlannersNetworkAnalysis')
        
        self.provider = urbanplannersnetworkanalysisProcessingProvider()
    # noinspection PyMethodMayBeStatic

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('urbanPlannersNetworkAnalysis', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = urbanPlannersNetworkAnalysisDialog()

        icon = QtGui.QIcon(icon_path)
        action = QtGui.QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/urbanPlannersNetworkAnalysis/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Urban Planners Network Analysis'),
            callback=self.run,
            parent=self.iface.mainWindow())
        
        Processing.addProvider(self.provider)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&An Urban Planners Network Analysis Tools'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        Processing.removeProvider(self.provider)

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            self.stuffFromCookbook()
    
    def stuffFromCookbook(self):
#         vl = qgis.utils.iface.mapCanvas().currentLayer()
        vl = self.dlg.basicNetworkLayer.itemData(self.dlg.basicNetworkLayer.currentIndex())
        onewayfield = self.dlg.basicNetworkOneWay.itemData(self.dlg.basicNetworkLayer.currentIndex())
        onewayattribute= self.dlg.basicNetworkOneWayAttribute.itemText(self.dlg.basicNetworkOneWayAttribute.currentIndex())
        
#         director = QgsLineVectorLayerDirector(vl, -1, '', '', '', 3)
        if self.dlg.basicNetworkExplode.isChecked():
            vl_exploded = processing.runalg('qgis:explodelines', vl, None)['OUTPUT']
            vl_expl_lyr = self.iface.addVectorLayer(vl_exploded, 'network_exploded', 'ogr')
            director = QgsLineVectorLayerDirector(vl_expl_lyr, onewayfield[1], onewayattribute, '', '', 3)
        director = QgsLineVectorLayerDirector(vl, onewayfield[1], onewayattribute, '', '', 3)
        properter = QgsDistanceArcProperter()
        director.addProperter(properter)
        crs = iface.mapCanvas().mapRenderer().destinationCrs()
        builder = QgsGraphBuilder(crs)
        
        origins = self.dlg.basicAreaOrigin.itemData(self.dlg.basicAreaOrigin.currentIndex())
        for p in origins.getFeatures():
            ps = {}
#             pStart = QgsPoint(65.5462, 57.1509)
            pStart = p.geometry().asPoint()
            delta = iface.mapCanvas().getCoordinateTransform().mapUnitsPerPixel() * 1
            
            """wofür ist das? """
            rb = QgsRubberBand(iface.mapCanvas(), True) #TODO: in version 3 a geometry ist given as second parameter instead of bool
            rb.setColor(Qt.green)
            rb.addPoint(QgsPoint(pStart.x() - delta, pStart.y() - delta))
            rb.addPoint(QgsPoint(pStart.x() + delta, pStart.y() - delta))
            rb.addPoint(QgsPoint(pStart.x() + delta, pStart.y() + delta))
            rb.addPoint(QgsPoint(pStart.x() - delta, pStart.y() + delta))
            
            ps[p.id()]=pStart
            
        tiedPoints = director.makeGraph(builder, ps.values())
        graph = builder.graph()
        tStart = tiedPoints[0]
        
        idStart = graph.findVertex(tStart)
        
        (tree, cost) = QgsGraphAnalyzer.dijkstra(graph, idStart, 0)
        
        upperBound = []
        distances = [int(e.strip()) for e in self.dlg.basicAreaLimitDistance.text().split(',')]
        for d in distances:
#             r = 300.0
            try:
                former_r = r
            except:
                former_r = 0.0
            r = float(d)
            i = 0
            while i < len(cost):
                if cost[i] > r and tree[i] != -1:
                  outVertexId = graph.arc(tree [i]).outVertex()
                  if cost[outVertexId] < r and cost[outVertexId] >= former_r:
                    upperBound.append(i)
                i = i + 1
            
            for i in upperBound:
                centerPoint = graph.vertex(i).point()
                rb = QgsRubberBand(iface.mapCanvas(), True)
                if former_r==0.0: rb.setColor(Qt.red)
                else: rb.setColor(Qt.blue)
                rb.addPoint(QgsPoint(centerPoint.x() - delta, centerPoint.y() - delta))
                rb.addPoint(QgsPoint(centerPoint.x() + delta, centerPoint.y() - delta))
                rb.addPoint(QgsPoint(centerPoint.x() + delta, centerPoint.y() + delta))
                rb.addPoint(QgsPoint(centerPoint.x() - delta, centerPoint.y() + delta))
    