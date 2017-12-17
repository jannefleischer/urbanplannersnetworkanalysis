# -*- coding: utf-8 -*-

"""
/***************************************************************************
 urbanplannersnetworkanalysisProcessing
                                 A QGIS plugin
 urbanplannersnetworkanalysisProcessing
                              -------------------
        begin                : 2017-12-16
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

from PyQt4.QtCore import QSettings
from qgis.core import QgsVectorFileWriter

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import *

from processing.core.outputs import OutputVector
from processing.tools import dataobjects, vector


class urbanplannersnetworkanalysisProcessingAlgorithm(GeoAlgorithm):
    """This is an example algorithm that takes a vector layer and
    creates a new one just with just those features of the input
    layer that are selected.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the GeoAlgorithm class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT_LAYER = 'OUTPUT_LAYER'
    INPUT_LAYER = 'INPUT_LAYER'
    
    basicNetworkLayer = 'basicNetworkLayer'
    basicNetworkOneWay = 'basicNetworkOneWay'
    basicNetworkOneWayAttribute = 'basicNetworkOneWayAttribute'
    basicNetworkOneWayDirection = 'basicNetworkOneWayDirection'
    basicNetworkSpeedLimit = 'basicNetworkSpeedLimit'
    basicNetworkCost = 'basicNetworkCost'
    basicNetworkExplode = 'basicNetworkExplode'
    basicNetworkSpeedLimitUnit = 'basicNetworkSpeedLimitUnit'
    
    basicAreaOrigin = 'basicAreaOrigin'
    basicAreaDefaultSpeed = 'basicAreaDefaultSpeed'
    basicAreaDefaultSpeedUnit = 'basicAreaDefaultSpeedUnit'
    basicAreaLimitDistance = 'basicAreaLimitDistance'
    basicAreaLimitTime = 'basicAreaLimitTime'
    
    specialResolution = 'specialResolution'

    def defineCharacteristics(self):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The name that the user will see in the toolbox
        self.name = 'Create Areas of Service'

        # The branch of the toolbox under which the algorithm will appear
        self.group = 'An Urban Planners Network Analysis'

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument
        self.addParameter(
            ParameterVector(
                self.basicNetworkLayer, 
                self.tr('Select Polyline-Layer that will be used as a street-network'), 
                [
                    ParameterVector.VECTOR_TYPE_LINE
                ], 
                False
            )
        )
        
        basicNetworkExplodeParam = ParameterBoolean(
            self.basicNetworkExplode,
            self.tr('Is the provided polyline-layer perfectly noded? If yes, please set this parameter to False. If set to True, the algorithm will explode your linestring-network to a line-network'),
            True,
            False
        )
#         basicNetworkExplodeParam.isAdvanced=True
        self.addParameter( basicNetworkExplodeParam )
        
        basicNetworkOneWayParam = ParameterTableField(
                self.basicNetworkOneWay,
                self.tr('Select a field that holds an information weather the street is one-way'),
                self.basicNetworkLayer,
                ParameterTableField.DATA_TYPE_ANY,
                True
            )
#         basicNetworkOneWayParam.isAdvanced=True
        self.addParameter(basicNetworkOneWayParam)
        
        self.addParameter(
            ParameterString(
                self.basicNetworkOneWayAttribute,
                self.tr('Whats the attribute for identifing an one-way street'),
                'yes',
                False,
                False
            )
        )
        
        self.addParameter(
            ParameterTableField(
                self.basicNetworkOneWayDirection,
                self.tr('Select a field that is used for identifing the direction of a one-way street (coded as 1, 2, 3 or Null as stated in QgsLineVectorLayerDirector(...))'),
                self.basicNetworkLayer,
                ParameterTableField.DATA_TYPE_ANY,
                True
            )
        )
        
        self.addParameter(
            ParameterTableField(
                self.basicNetworkSpeedLimit,
                self.tr('Select a field that holds an information what speed limit exists on a street (calculated to "cost")'),
                self.basicNetworkLayer,
                ParameterTableField.DATA_TYPE_ANY,
                True
            )
        )
        
        self.addParameter(
            ParameterTableField(
                self.basicNetworkCost,
                self.tr('Select a field that is already a cost-factor (the overseeds the speedlimit-field above)'),
                self.basicNetworkLayer,
                ParameterTableField.DATA_TYPE_ANY,
                True
            )
        )
        
        self.addParameter(
            ParameterString(
                self.basicNetworkSpeedLimitUnit,
                self.tr('Whats the unit of that speed limit field? (please type one of the following: kph, mph, m/s)'),
                self.tr('kph'),
                False,
                False
            )
        )
        
        self.addParameter(
            ParameterVector(
                self.basicAreaOrigin, 
                self.tr('Select a point-layer that will be used to identify places where a service area is originated from. Every point will be an origin of one area. If there is a selection active, only that one will be used.'), 
                [
                    ParameterVector.VECTOR_TYPE_POINT
                ], 
                False
            )
        )
        
        self.addParameter(
            ParameterNumber(
                self.basicAreaDefaultSpeed,
                self.tr('How fast can a car/pedestrian/whatever go, if there is no street to go on (if no field for speed limit is chosen above, this is the default speed). Minimum Value is 1.'),
                1,
                None,
                10,
                False
            )
        )
        
        self.addParameter(
            ParameterString(
                self.basicAreaDefaultSpeedUnit,
                self.tr('Whats the unit of that default speed field? (please type one of the following: kph, mph, m/s)'),
                self.tr('kph'),
                False,
                False
            )
        )
        
        self.addParameter(
            ParameterString(
                self.basicAreaLimitDistance,
                self.tr('How far is the DISTANCE limit / are the DISTANCE limits of traveling? A comma-seperated list of integers (Map-Units) will create a number of polygons (second one and further will be "donut"-shaped) traveling that far. First one is from origin to first border, second one is a donut from first border to next border and so on.'),
                self.tr('300 , 600'),
                False,
                False
            )
        )
        
        basicAreaLimitTimeParam = ParameterString(
                self.basicAreaLimitTime,
                self.tr('How far is the TIME limit / are the TIME limits of traveling? A comma-seperated list of integers (minutes) will create a number of polygons (second one and further will be "donut"-shaped) traveling that far. First one is from origin to first border, second one is a donut from first border to next border and so on.'),
                self.tr('5,10'),
                False,
                False
            )
#         basicAreaLimitTimeParam.isAdvanced=True
        self.addParameter(basicAreaLimitTimeParam)
        
        specialResolutionParam = ParameterNumber(
                self.specialResolution,
                self.tr('Please select a "resolution" of how exact the walking distance from the graph should be calculated. The resolution is implemented by slicing the network-polylines into pieces of line by the length of the resolution and generating points at the slicing location. from those points a buffer of left over cost is calculated. Please don\'t try to be too precise, it will calculate forever. If the value is 0, only existing end- and mid-points of the polylines will be used.'),
                None,
                None,
                0,
                True
            )
#         specialResolutionParam.isAdvanced=True
        self.addParameter( specialResolutionParam )
        

        # We add a vector layer as output
        self.addOutput(OutputVector(self.OUTPUT_LAYER,
            self.tr('Output layer with selected features')))

    def processAlgorithm(self, progress):
        """Here is where the processing itself takes place."""

        # The first thing to do is retrieve the values of the parameters
        # entered by the user
        inputFilename = self.getParameterValue(self.INPUT_LAYER)
        output = self.getOutputValue(self.OUTPUT_LAYER)
        
        basicNetworkLayerParamValue = self.getParameterValue(self.basicNetworkLayer)
        basicNetworkOneWayParamValue = self.getParameterValue(self.basicNetworkOneWay)
        basicNetworkOneWayAttributeParamValue = self.getParameterValue(self.basicNetworkOneWayAttribute)
        basicNetworkOneWayDirectionParamValue = self.getParameterValue(self.basicNetworkOneWayDirection)
        basicNetworkSpeedLimitParamValue = self.getParameterValue(self.basicNetworkSpeedLimit)
        basicNetworkCostParamValue = self.getParameterValue(self.basicNetworkCost)
        basicNetworkExplodeParamValue = self.getParameterValue(self.basicNetworkExplode)
        basicNetworkSpeedLimitUnitParamValue = self.getParameterValue(self.basicNetworkSpeedLimitUnit)
        
        basicAreaOriginParamValue = self.getParameterValue(self.basicAreaOrigin)
        basicAreaDefaultSpeedParamValue = self.getParameterValue(self.basicAreaDefaultSpeed)
        basicAreaDefaultSpeedUnitParamValue = self.getParameterValue(self.basicAreaDefaultSpeedUnit)
        basicAreaLimitDistanceParamValue = self.getParameterValue(self.basicAreaLimitDistance)
        basicAreaLimitTimeParamValue = self.getParameterValue(self.basicAreaLimitTime)
        
        specialResolutionParamValue = self.getParameterValue(self.specialResolution)

        # Input layers vales are always a string with its location.
        # That string can be converted into a QGIS object (a
        # QgsVectorLayer in this case) using the
        # processing.getObjectFromUri() method.
        basicNetworkLayerParamValueLayer = dataobjects.getObjectFromUri(basicNetworkLayerParamValue)
        basicAreaOriginParamValueLayer = dataobjects.getObjectFromUri(basicAreaOriginParamValue)
        
#         vectorLayer = dataobjects.getObjectFromUri(inputFilename)

        # And now we can process

        # First we create the output layer. The output value entered by
        # the user is a string containing a filename, so we can use it
        # directly
        settings = QSettings()
        systemEncoding = settings.value('/UI/encoding', 'System')
        
        basicNetworkLayerParamValueProvider = basicNetworkLayerParamValueLayer.dataProvider()
        basicAreaOriginParamValueProvider = basicAreaOriginParamValueLayer.dataProvider()
        
        outputProvider = basicNetworkLayerParamValueLayer.dataProvider() #same as input!
        
        writer = QgsVectorFileWriter(output, systemEncoding,
                                     outputProvider.fields(), #TODO: change if we gained knowledge about the fields our output will have...
                                     outputProvider.geometryType(), #TODO: change to polygon!
                                     provider.crs())

        # Now we take the features from input layer and add them to the
        # output. Method features() returns an iterator, considering the
        # selection that might exist in layer and the configuration that
        # indicates should algorithm use only selected features or all
        # of them
        features = vector.features(basicNetworkLayerParamValueLayer) #TODO: Right now this copies all Lines from basicNetworkLayerParamValueLayer to the output.
        for f in features:
            writer.addFeature(f)

        # There is nothing more to do here. We do not have to open the
        # layer that we have created. The framework will take care of
        # that, or will handle it if this algorithm is executed within
        # a complex model
