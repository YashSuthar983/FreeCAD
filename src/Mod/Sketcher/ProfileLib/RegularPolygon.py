# SPDX-License-Identifier: LGPL-2.1-or-later

# ***************************************************************************
# *   Copyright (c) 2014 Johan Kristensen                                   *
# *   Copyright (c) 2014 Juergen Riegel <FreeCAD@juergen-riegel.net>        *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

import FreeCAD, FreeCADGui, Sketcher, Part, math


__title__ = "Regular polygon profile lib"
__author__ = "Johan Kristensen"
__url__ = "https://www.freecad.org"

App = FreeCAD
Gui = FreeCADGui


def makeRegularPolygon(
    sketch,
    sides,
    centerPoint=App.Vector(0, 0, 0),
    firstCornerPoint=App.Vector(-20.00, 34.64, 0),
    construction=False,
):

    if not sketch:
        App.Console.PrintError("No sketch specified in 'makeRegularPolygon'")
        return
    if sides < 3:
        App.Console.PrintError("Number of sides must be at least 3 in 'makeRegularPolygon'")
        return

    diffVec = firstCornerPoint - centerPoint
    diffVec.z = 0
    angular_diff = 2 * math.pi / sides
    pointList = []
    for i in range(0, sides):
        cos_v = math.cos(angular_diff * i)
        sin_v = math.sin(angular_diff * i)
        pointList.append(
            centerPoint
            + App.Vector(
                cos_v * diffVec.x - sin_v * diffVec.y, cos_v * diffVec.y + sin_v * diffVec.x, 0
            )
        )

    geoList = []
    for i in range(0, sides - 1):
        geoList.append(Part.LineSegment(pointList[i], pointList[i + 1]))
    geoList.append(Part.LineSegment(pointList[sides - 1], pointList[0]))
    for i in range(0, sides):
        geoList.append(Part.LineSegment(centerPoint, pointList[i]))
    geoList.append(Part.Circle(centerPoint, App.Vector(0, 0, 1), diffVec.Length))
    geoIndices = sketch.addGeometry(geoList, construction)

    radial_start = sides
    circle_idx = geoIndices[-1]
    for i in range(radial_start, radial_start + sides):
        sketch.setConstruction(geoIndices[i], True)
    sketch.setConstruction(circle_idx, True)

    conList = []
    for i in range(0, sides):
        edge_idx = geoIndices[i]
        radial_i = geoIndices[radial_start + i]
        radial_next = geoIndices[radial_start + ((i + 1) % sides)]
        conList.append(Sketcher.Constraint("Coincident", edge_idx, 1, radial_i, 2))
        conList.append(Sketcher.Constraint("Coincident", edge_idx, 2, radial_next, 2))

    for i in range(0, sides):
        conList.append(
            Sketcher.Constraint("Coincident", geoIndices[radial_start + i], 1, circle_idx, 3)
        )
    for i in range(1, sides):
        conList.append(
            Sketcher.Constraint("Equal", geoIndices[radial_start], geoIndices[radial_start + i])
        )

    central_angle = App.Units.Quantity(f"{360.0 / sides} deg")
    for i in range(0, sides - 1):
        conList.append(
            Sketcher.Constraint(
                "Angle",
                geoIndices[radial_start + i],
                1,
                geoIndices[radial_start + i + 1],
                1,
                central_angle,
            )
        )
    conList.append(Sketcher.Constraint("PointOnObject", geoIndices[radial_start], 2, circle_idx))

    sketch.addConstraint(conList)
    return
