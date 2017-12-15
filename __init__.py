# -*- coding: utf-8 -*-
"""
/***************************************************************************
 urbanPlannersNetworkAnalysis
                                 A QGIS plugin
 Tool that uses the Network Analysis Library of QGIS to build a tool that also a not well trained urban player can use.
                             -------------------
        begin                : 2017-12-15
        copyright            : (C) 2017 by Janne Jakob Fleischer
        email                : janne.fleischer@googlemail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load urbanPlannersNetworkAnalysis class from file urbanPlannersNetworkAnalysis.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .networkAnalysisForUrbanPlanners import urbanPlannersNetworkAnalysis
    return urbanPlannersNetworkAnalysis(iface)
