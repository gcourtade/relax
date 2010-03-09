###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Module containing all the different cone type classes."""


class Iso_cone:
    """The class for the isotropic cone."""

    def __init__(self, angle):
        """Set up the cone object.

        @param angle:   The cone angle.
        @type angle:    float
        """

        # Store the cone angle.
        self._angle = angle


    def phi_max(self, theta):
        """Return the maximum polar angle phi for the given azimuthal angle theta.

        @param theta:   The azimuthal angle.
        @type theta:    float
        @return:        The maximum polar angle phi for the value of theta.
        @rtype:         float
        """

        # The polar angle is fixed!
        return self._angle
