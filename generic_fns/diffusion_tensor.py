###############################################################################
#                                                                             #
# Copyright (C) 2003-2005 Edward d'Auvergne                                   #
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

from copy import deepcopy
from math import cos, pi, sin
from Numeric import Float64, array


class Diffusion_tensor:
    def __init__(self, relax):
        """Class containing the function for setting up the diffusion tensor."""

        self.relax = relax


    def anisotropic(self):
        """Function for setting up fully anisotropic diffusion."""

        # The diffusion type.
        self.relax.data.diff[self.run].type = 'aniso'

        # (tm, Da, Dr, alpha, beta, gamma).
        if self.param_types == 0:
            # Unpack the tuple.
            tm, Da, Dr, alpha, beta, gamma = self.params

            # Scaling.
            tm = tm * self.time_scale
            Da = Da * self.d_scale

            # Diffusion tensor eigenvalues: Diso, Da, Dr, Dx, Dy, Dz.
            self.relax.data.diff[self.run].Diso = 1.0 / (6.0*tm)
            self.relax.data.diff[self.run].Da = Da
            self.relax.data.diff[self.run].Dr = Dr
            self.relax.data.diff[self.run].Dx = self.relax.data.diff[self.run].Diso - Da + Dr
            self.relax.data.diff[self.run].Dy = self.relax.data.diff[self.run].Diso - Da - Dr
            self.relax.data.diff[self.run].Dz = self.relax.data.diff[self.run].Diso + 2.0*Da

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = tm

        # (Diso, Da, Dr, alpha, beta, gamma).
        elif self.param_types == 1:
            # Unpack the tuple.
            Diso, Da, Dr, alpha, beta, gamma = self.params

            # Scaling.
            Diso = Diso * self.d_scale
            Da = Da * self.d_scale

            # Diffusion tensor eigenvalues: Diso, Da, Dr, Dx, Dy, Dz.
            self.relax.data.diff[self.run].Diso = Diso
            self.relax.data.diff[self.run].Da = Da
            self.relax.data.diff[self.run].Dr = Dr
            self.relax.data.diff[self.run].Dx = Diso - Da + Dr
            self.relax.data.diff[self.run].Dy = Diso - Da - Dr
            self.relax.data.diff[self.run].Dz = Diso + 2.0*Da

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = 1.0 / (6.0*Diso)

        # (Dx, Dy, Dz, alpha, beta, gamma).
        elif self.param_types == 2:
            # Unpack the tuple.
            Dx, Dy, Dz, alpha, beta, gamma = self.params

            # Scaling.
            Dx = Dx * self.d_scale
            Dy = Dy * self.d_scale
            Dz = Dz * self.d_scale

            # Diffusion tensor eigenvalues: Dx, Dy, Dz.
            self.relax.data.diff[self.run].Dx = Dx
            self.relax.data.diff[self.run].Dy = Dy
            self.relax.data.diff[self.run].Dz = Dz
            self.relax.data.diff[self.run].Diso = (Dx + Dy + Dz) / 3.0
            self.relax.data.diff[self.run].Da = (Dz - (Dx + Dy)/2.0) / 3.0
            self.relax.data.diff[self.run].Dr = (Dx - Dy) / 2.0

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = 1.0 / (6.0*self.relax.data.diff[self.run].Diso)

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError, ('param_types', self.param_types)

        # Convert the angles to radians.
        if self.angle_units == 'deg':
            alpha = (alpha / 360.0) * 2.0 * pi
            beta = (beta / 360.0) * 2.0 * pi
            gamma = (gamma / 360.0) * 2.0 * pi

        # Make sure the angles are within their defined ranges.
        self.relax.data.diff[self.run].alpha = self.relax.generic.angles.wrap_angles(alpha, 0.0, 2.0*pi)
        self.relax.data.diff[self.run].beta = self.relax.generic.angles.wrap_angles(beta, 0.0, pi)
        self.relax.data.diff[self.run].gamma = self.relax.generic.angles.wrap_angles(gamma, 0.0, 2.0*pi)


    def axial(self):
        """Function for setting up axially symmetric diffusion."""

        # The diffusion type.
        self.relax.data.diff[self.run].type = 'axial'

        # Axial diffusion type.
        allowed_types = [None, 'oblate', 'prolate']
        if self.axial_type not in allowed_types:
            raise RelaxError, "The 'axial_type' argument " + `self.axial_type` + " should be 'oblate', 'prolate', or None."
        self.relax.data.diff[self.run].axial_type = self.axial_type

        # (tm, Da, theta, phi).
        if self.param_types == 0:
            # Unpack the tuple.
            tm, Da, theta, phi = self.params

            # Scaling.
            tm = tm * self.time_scale
            Da = Da * self.d_scale

            # Diffusion tensor eigenvalues: Dpar, Dper, Diso, Dratio.
            self.relax.data.diff[self.run].Diso = 1.0 / (6.0*tm)
            self.relax.data.diff[self.run].Da = Da
            self.relax.data.diff[self.run].Dpar = self.relax.data.diff[self.run].Diso + 2.0*Da
            self.relax.data.diff[self.run].Dper = self.relax.data.diff[self.run].Diso - Da
            self.relax.data.diff[self.run].Dratio = self.relax.data.diff[self.run].Dpar / self.relax.data.diff[self.run].Dper

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = tm

        # (Diso, Da, theta, phi).
        elif self.param_types == 1:
            # Unpack the tuple.
            Diso, Da, theta, phi = self.params

            # Scaling.
            Diso = Diso * self.d_scale
            Da = Da * self.d_scale

            # Diffusion tensor eigenvalues: Dpar, Dper, Diso, Dratio.
            self.relax.data.diff[self.run].Diso = Diso
            self.relax.data.diff[self.run].Da = Da
            self.relax.data.diff[self.run].Dpar = Diso + 2.0*Da
            self.relax.data.diff[self.run].Dper = Diso - Da
            self.relax.data.diff[self.run].Dratio = self.relax.data.diff[self.run].Dpar / self.relax.data.diff[self.run].Dper

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = 1.0 / (6.0 * self.relax.data.diff[self.run].Diso)

        # (tm, Dratio, theta, phi).
        elif self.param_types == 2:
            # Unpack the tuple.
            tm, Dratio, theta, phi = self.params

            # Scaling.
            tm = tm * self.time_scale

            # Diffusion tensor eigenvalues: Dpar, Dper, Diso, Dratio.
            self.relax.data.diff[self.run].Diso = 1.0 / (6.0 * tm)
            self.relax.data.diff[self.run].Dratio = Dratio
            self.relax.data.diff[self.run].Da = self.relax.data.diff[self.run].Diso * (Dratio - 1.0) / (Dratio + 2.0)
            self.relax.data.diff[self.run].Dpar = 3.0 * self.relax.data.diff[self.run].Diso * Dratio / (Dratio + 2.0)
            self.relax.data.diff[self.run].Dper = 3.0 * self.relax.data.diff[self.run].Diso / (Dratio + 2.0)

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = tm

        # (Dpar, Dper, theta, phi).
        elif self.param_types == 3:
            # Unpack the tuple.
            Dpar, Dper, theta, phi = self.params

            # Scaling.
            Dpar = Dpar * self.d_scale
            Dper = Dper * self.d_scale

            # Diffusion tensor eigenvalues: Dpar, Dper, Diso, Dratio.
            self.relax.data.diff[self.run].Dpar = Dpar
            self.relax.data.diff[self.run].Dper = Dper
            self.relax.data.diff[self.run].Diso = (Dpar + 2.0*Dper) / 3.0
            self.relax.data.diff[self.run].Da = (Dpar - Dper) / 3.0
            self.relax.data.diff[self.run].Dratio = Dpar / Dper

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = 1.0 / (6.0 * self.relax.data.diff[self.run].Diso)

        # (Diso, Dratio, theta, phi).
        elif self.param_types == 4:
            # Unpack the tuple.
            Diso, Dratio, theta, phi = self.params

            # Scaling.
            Diso = Diso * self.d_scale

            # Diffusion tensor eigenvalues: Dpar, Dper, Diso, Dratio.
            self.relax.data.diff[self.run].Diso = Diso
            self.relax.data.diff[self.run].Dratio = Dratio
            self.relax.data.diff[self.run].Da = Diso * (Dratio - 1.0) / (Dratio + 2.0)
            self.relax.data.diff[self.run].Dpar = 3.0 * Diso * Dratio / (Dratio + 2.0)
            self.relax.data.diff[self.run].Dper = 3.0 * Diso / (Dratio + 2.0)

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = 1.0 / (6.0 * Diso)

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError, ('param_types', self.param_types)

        # Convert the angles to radians.
        if self.angle_units == 'deg':
            theta = (theta / 360.0) * 2.0 * pi
            phi = (phi / 360.0) * 2.0 * pi

        # Make sure the angles are within their defined ranges.
        self.relax.data.diff[self.run].theta = self.relax.generic.angles.wrap_angles(theta, 0.0, pi)
        self.relax.data.diff[self.run].phi = self.relax.generic.angles.wrap_angles(phi, 0.0, 2.0*pi)

        # Unit symmetry axis vector.
        #x = cos(self.relax.data.diff[self.run].theta) * sin(self.relax.data.diff[self.run].phi)
        #y = sin(self.relax.data.diff[self.run].theta) * sin(self.relax.data.diff[self.run].phi)
        #z = cos(self.relax.data.diff[self.run].phi)
        #self.relax.data.diff[self.run].axis_unit = array([x, y, z], Float64)

        # Full symmetry axis vector.
        #self.relax.data.diff[self.run].axis_vect = self.relax.data.diff[self.run].Dpar * self.relax.data.diff[self.run].axis_unit


    def copy(self, run1=None, run2=None):
        """Function for copying diffusion tensor data from run1 to run2."""

        # Test if run1 exists.
        if not run1 in self.relax.data.run_names:
            raise RelaxNoRunError, run1

        # Test if run2 exists.
        if not run2 in self.relax.data.run_names:
            raise RelaxNoRunError, run2

        # Test if run1 contains diffusion tensor data.
        if not self.relax.data.diff.has_key(run1):
            raise RelaxNoTensorError, run1

        # Test if run2 contains diffusion tensor data.
        if self.relax.data.diff.has_key(run2):
            raise RelaxTensorError, run2

        # Copy the data.
        self.relax.data.diff[run2] = deepcopy(self.relax.data.diff[run1])


    def data_names(self):
        """Function for returning a list of names of data structures associated with the sequence."""

        names = [ 'diff_type',
                  'diff_params' ]

        return names


    def delete(self, run=None):
        """Function for deleting diffusion tensor data."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if diffusion tensor data for the run exists.
        if not self.relax.data.diff.has_key(run):
            raise RelaxNoTensorError, run

        # Delete the diffusion data.
        del(self.relax.data.diff[run])

        # Clean up the runs.
        self.relax.generic.runs.eliminate_unused_runs()


    def display(self, run=None):
        """Function for displaying the diffusion tensor."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if diffusion tensor data for the run exists.
        if not self.relax.data.diff.has_key(run):
            raise RelaxNoTensorError, run

        # Isotropic diffusion.
        if self.relax.data.diff[run].type == 'iso':
            # Tensor type.
            print "Type:  Isotropic diffusion"

            # Parameters.
            print "\nParameters {tm}."
            print "tm (s):  " + `self.relax.data.diff[run].tm`

            # Alternate parameters.
            print "\nAlternate parameters {Diso}."
            print "Diso (1/s):  " + `self.relax.data.diff[run].Diso`

            # Fixed flag.
            print "\nFixed:  " + `self.relax.data.diff[run].fixed`

        # Anisotropic diffusion.
        elif self.relax.data.diff[run].type == 'axial':
            # Tensor type.
            print "Type:  Axially symmetric anisotropic diffusion"

            # Parameters.
            print "\nParameters {Dpar, Dper, theta, phi}."
            print "Dpar (1/s):  " + `self.relax.data.diff[run].Dpar`
            print "Dper (1/s):  " + `self.relax.data.diff[run].Dper`
            print "theta (rad):  " + `self.relax.data.diff[run].theta`
            print "phi (rad):  " + `self.relax.data.diff[run].phi`

            # Alternate parameters.
            print "\nAlternate parameters {tm, Dratio, theta, phi}."
            print "tm (s):  " + `self.relax.data.diff[run].tm`
            print "Dratio:  " + `self.relax.data.diff[run].Dratio`
            print "theta (rad):  " + `self.relax.data.diff[run].theta`
            print "phi (rad):  " + `self.relax.data.diff[run].phi`

            # Fixed flag.
            print "\nFixed:  " + `self.relax.data.diff[run].fixed`

        # Anisotropic diffusion.
        elif self.relax.data.diff[run].type == 'aniso':
            # Tensor type.
            print "Type:  Anisotropic diffusion"

            # Parameters.
            print "\nParameters {Dx, Dy, Dz, alpha, beta, gamma}."
            print "Dx (1/s):  " + `self.relax.data.diff[run].Dx`
            print "Dy (1/s):  " + `self.relax.data.diff[run].Dy`
            print "Dz (1/s):  " + `self.relax.data.diff[run].Dz`
            print "alpha (rad):  " + `self.relax.data.diff[run].alpha`
            print "beta (rad):  " + `self.relax.data.diff[run].beta`
            print "gamma (rad):  " + `self.relax.data.diff[run].gamma`

            # Fixed flag.
            print "\nFixed:  " + `self.relax.data.diff[run].fixed`


    def isotropic(self):
        """Function for setting up isotropic diffusion."""

        # The diffusion type.
        self.relax.data.diff[self.run].type = 'iso'

        # tm.
        if self.param_types == 0:
            # Correlation times.
            self.relax.data.diff[self.run].tm = self.params * self.time_scale

            # Diffusion tensor eigenvalues.
            self.relax.data.diff[self.run].Diso = 6.0 / self.relax.data.diff[self.run].tm

        # Diso
        elif self.param_types == 1:
            # Diffusion tensor eigenvalues.
            self.relax.data.diff[self.run].Diso = self.params * self.d_scale

            # Correlation times.
            self.relax.data.diff[self.run].tm = 1.0 / (6.0 * self.relax.data.diff[self.run].Diso)

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError, ('param_types', self.param_types)


    def set(self, run=None, params=None, time_scale=1.0, d_scale=1.0, angle_units='deg', param_types=0, axial_type=None, fixed=1):
        """Function for setting up the diffusion tensor."""

        # Arguments.
        self.run = run
        self.params = params
        self.time_scale = time_scale
        self.d_scale = d_scale
        self.angle_units = angle_units
        self.param_types = param_types
        self.axial_type = axial_type

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if diffusion tensor data corresponding to the run already exists.
        if self.relax.data.diff.has_key(self.run):
            raise RelaxTensorError, self.run

        # Check the validity of the angle_units argument.
        valid_types = ['deg', 'rad']
        if not angle_units in valid_types:
            raise RelaxError, "The diffusion tensor 'angle_units' argument " + `angle_units` + " should be either 'deg' or 'rad'."

        # Add the run to the diffusion tensor data structure.
        self.relax.data.diff.add_item(self.run)

        # Set the fixed flag.
        self.relax.data.diff[self.run].fixed = fixed

        # Isotropic diffusion.
        if type(params) == float:
            num_params = 1
            self.isotropic()

        # Axially symmetric anisotropic diffusion.
        elif (type(params) == tuple or type(params) == list) and len(params) == 4:
            num_params = 4
            self.axial()

        # Fully anisotropic diffusion.
        elif (type(params) == tuple or type(params) == list) and len(params) == 6:
            num_params = 6
            self.anisotropic()

        # Unknown.
        else:
            raise RelaxError, "The diffusion tensor parameters " + `params` + " are of an unknown type."

        # Test the validity of the parameters.
        self.test_params(num_params)


    def test_params(self, num_params):
        """Function for testing the validity of the input parameters."""

        # tm.
        if self.relax.data.diff[self.run].tm <= 0.0 or self.relax.data.diff[self.run].tm > 1e-6:
            raise RelaxError, "The tm value of " + `self.relax.data.diff[self.run].tm` + " should be between zero and 1 microsecond."

        # Da.
#        if num_params > 1:
#            if self.relax.data.diff[self.run].Da <= 0.0 or self.relax.data.diff[self.run].tm > 1e-6:
