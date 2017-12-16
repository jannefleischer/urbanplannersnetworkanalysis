# -*- coding: utf-8 -*-
"""
/***************************************************************************
 urbanPlannersNetworkAnalysisDialog
                                 A QGIS plugin
 Tool that uses the Network Analysis Library of QGIS to build a tool that also a not well trained urban player can use.
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

import os
import collections

from PyQt4.QtCore import *
from PyQt4 import uic, QtGui

from qgis.core import *
from qgis.gui import *
from qgis.utils import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'urbanplannersnetworkanalysis_dialog_base.ui'))


class urbanPlannersNetworkAnalysisDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(urbanPlannersNetworkAnalysisDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        self.initForm()
        
        self.basicNetworkLayer.currentIndexChanged.connect(self.networkLayerChanged)
        self.basicNetworkOneWay.currentIndexChanged.connect(self.onewayFieldChanged)
        
    def initForm(self):
        self.basicNetworkLayer.addItem('-',userData=None)
        self.basicAreaOrigin.addItem('-',userData=None)
        
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.geometryType()==1:
                self.basicNetworkLayer.addItem(lyr.name(), userData=lyr)
            if lyr.geometryType()==0:
                self.basicAreaOrigin.addItem(lyr.name(), userData=lyr)
        
        self.networkLayerChanged()
    
    def networkLayerChanged(self):
        self.updateFieldList(self.basicNetworkOneWay, self.basicNetworkLayer.itemData(self.basicNetworkLayer.currentIndex()))
        self.updateFieldList(self.basicNetworkOneWayDirection, self.basicNetworkLayer.itemData(self.basicNetworkLayer.currentIndex()))
        self.updateFieldList(self.basicNetworkSpeedLimit, self.basicNetworkLayer.itemData(self.basicNetworkLayer.currentIndex()))
        self.updateFieldList(self.basicNetworkCost, self.basicNetworkLayer.itemData(self.basicNetworkLayer.currentIndex()))
        
        self.onewayFieldChanged()
    
    def onewayFieldChanged(self):
        if self.basicNetworkOneWay.itemText(self.basicNetworkOneWay.currentIndex())=='-':
            return
        self.updateAttributes(
            self.basicNetworkOneWayAttribute, 
            self.basicNetworkLayer.itemData(self.basicNetworkLayer.currentIndex()), 
            self.basicNetworkOneWay.itemData(self.basicNetworkOneWay.currentIndex())
        )
    
    def updateFieldList(self, dlgObj, lyr):
        dlgObj.clear()
        dlgObj.addItem('-', userData=None)
        if not lyr is None:
            cf = [f for f in lyr.dataProvider().fields()]
            for f in cf:
                dlgObj.addItem(f.name(), userData=(f, lyr.dataProvider().fields().indexFromName(f.name())))
    
    def updateAttributes(self, dlgObj, lyr, field):
        dlgObj.clear()
        dlgObj.addItem('-')
        if not lyr is None and not field is None:
            values = set()
            for f in lyr.getFeatures():
                values.add(f[field[0].name()])
                if len(values)>=50: break
            for v in values:
                if type(v) != QPyNullVariant:
                    dlgObj.addItem(v)
        else:
            return
        
