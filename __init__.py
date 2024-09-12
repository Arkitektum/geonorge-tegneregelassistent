# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Arkitektum AS
                                 A QGIS plugin
 Implementering av Geonorge tegneregler
                              -------------------
        start date           : 2023-06-20
        copyright            : (C) 2023 by Arkitektum AS
        email                : apps@arkitektum.no
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software: you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation, either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *   This program is distributed in the hope that it will be useful,       *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          *
 *   GNU General Public License for more details.                          *
 *                                                                         *
 *   You should have received a copy of the GNU General Public License     *
 *   along with this program. If not, see <http://www.gnu.org/licenses/>.  *
 *                                                                         *
 ***************************************************************************/

 This script initializes the Geonorge plugin, making it known to QGIS.
 The Geonorge plugin allows users to implement and apply Geonorge's
 standardized styles (tegneregler) to GML layers within QGIS, based on
 predefined schemas and configurations. This enhances the visualization
 and ensures consistency with national cartographic standards.
"""

from .tegneregelassistent import GeonorgeTegneregelassistent
# from debugpy import configure
# from shutil import which


# Initialize the Geonorge plugin
def classFactory(iface):
    """Load Geonorge class from file tegneregelassistent.py."""
    # Enable debugging
    # configure(python=which('python'))

    return GeonorgeTegneregelassistent(iface)
