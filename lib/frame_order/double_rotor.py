###############################################################################
#                                                                             #
# Copyright (C) 2009-2012,2014 Edward d'Auvergne                              #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for the double rotor frame order model."""

# Python module imports.
from math import cos, pi, sin
from numpy import add, divide, dot, eye, float64, multiply, sinc, swapaxes, tensordot
try:
    from scipy.integrate import dblquad
except ImportError:
    pass

# relax module imports.
from lib.compat import norm
from lib.frame_order.matrix_ops import rotate_daeg


def compile_1st_matrix_double_rotor(matrix, R_eigen, smax1, smax2):
    """Generate the 1st degree Frame Order matrix for the double rotor model.

    @param matrix:      The Frame Order matrix, 1st degree to be populated.
    @type matrix:       numpy 3D, rank-2 array
    @param R_eigen:     The eigenframe rotation matrix.
    @type R_eigen:      numpy 3D, rank-2 array
    @param smax1:       The maximum torsion angle for the first rotor.
    @type smax1:        float
    @param smax2:       The maximum torsion angle for the second rotor.
    @type smax2:        float
    """

    # Repetitive trig calculations.
    sinc_smax1 = sinc(smax1/pi)
    sinc_smax2 = sinc(smax2/pi)

    # Numerical integration of phi of each element.
    matrix[0, 0] = sinc_smax1
    matrix[1, 1] = sinc_smax2
    matrix[2, 2] = sinc_smax1 * sinc_smax2

    # Rotate and return the frame order matrix.
    return rotate_daeg(matrix, R_eigen)


def compile_2nd_matrix_double_rotor(matrix, Rx2_eigen, smax1, smax2):
    """Generate the rotated 2nd degree Frame Order matrix for the double rotor model.

    The cone axis is assumed to be parallel to the z-axis in the eigenframe.


    @param matrix:      The Frame Order matrix, 2nd degree to be populated.
    @type matrix:       numpy 9D, rank-2 array
    @param Rx2_eigen:   The Kronecker product of the eigenframe rotation matrix with itself.
    @type Rx2_eigen:    numpy 9D, rank-2 array
    @param smax1:       The maximum torsion angle for the first rotor.
    @type smax1:        float
    @param smax2:       The maximum torsion angle for the second rotor.
    @type smax2:        float
    """

    # Zeros.
    matrix[:] = 0.0

    # Repetitive trig calculations.
    sinc_smax1 = sinc(smax1/pi)
    sinc_2smax1 = sinc(2.0*smax1/pi)
    sinc_2smax1p1 = sinc_2smax1 + 1.0
    sinc_2smax1n1 = sinc_2smax1 - 1.0
    sinc_smax2 = sinc(smax2/pi)
    sinc_2smax2 = sinc(2.0*smax2/pi)
    sinc_2smax2p1 = sinc_2smax2 + 1.0
    sinc_2smax2n1 = sinc_2smax2 - 1.0

    # Diagonal.
    matrix[0, 0] = sinc_2smax1 + 1.0
    matrix[1, 1] = 2.0 * sinc_smax1 * sinc_smax2
    matrix[2, 2] = sinc_smax2 * sinc_2smax1p1
    matrix[3, 3] = matrix[1, 1]
    matrix[4, 4] = sinc_2smax2p1
    matrix[5, 5] = sinc_smax1 * sinc_2smax2p1
    matrix[6, 6] = matrix[2, 2]
    matrix[7, 7] = matrix[5, 5]
    matrix[8, 8] = 0.5 * sinc_2smax1p1 * sinc_2smax2p1

    # Off diagonal set 1.
    matrix[4, 0] = 0.5 * sinc_2smax1n1 * sinc_2smax2n1
    matrix[0, 8] = -sinc_2smax1n1
    matrix[8, 0] = -0.5 * sinc_2smax1n1 * sinc_2smax2p1
    matrix[4, 8] = -0.5 * sinc_2smax1p1 * sinc_2smax2n1
    matrix[8, 4] = -sinc_2smax2n1

    # Off diagonal set 2.
    matrix[2, 6] = matrix[6, 2] = sinc_smax2 * sinc_2smax1n1
    matrix[5, 7] = matrix[7, 5] = sinc_smax1 * sinc_2smax2n1

    # Divide by 2.
    multiply(0.5, matrix, matrix)

    # Rotate and return the frame order matrix.
    return rotate_daeg(matrix, Rx2_eigen)


def pcs_numeric_qr_int_double_rotor(points=None, max_points=None, sigma_max=None, sigma_max_2=None, c=None, full_in_ref_frame=None, r_pivot_atom=None, r_pivot_atom_rev=None, r_ln_pivot=None, r_inter_pivot=None, A=None, R_eigen=None, RT_eigen=None, Ri_prime=None, Ri2_prime=None, pcs_theta=None, pcs_theta_err=None, missing_pcs=None):
    """The averaged PCS value via numerical integration for the double rotor frame order model.

    @keyword points:            The Sobol points in the torsion-tilt angle space.
    @type points:               numpy rank-2, 3D array
    @keyword max_points:        The maximum number of Sobol' points to use.  Once this number is reached, the loop over the Sobol' torsion-tilt angles is terminated.
    @type max_points:           int
    @keyword sigma_max:         The maximum opening angle for the first rotor.
    @type sigma_max:            float
    @keyword sigma_max_2:       The maximum opening angle for the second rotor.
    @type sigma_max_2:          float
    @keyword c:                 The PCS constant (without the interatomic distance and in Angstrom units).
    @type c:                    numpy rank-1 array
    @keyword full_in_ref_frame: An array of flags specifying if the tensor in the reference frame is the full or reduced tensor.
    @type full_in_ref_frame:    numpy rank-1 array
    @keyword r_pivot_atom:      The pivot point to atom vector.
    @type r_pivot_atom:         numpy rank-2, 3D array
    @keyword r_pivot_atom_rev:  The reversed pivot point to atom vector.
    @type r_pivot_atom_rev:     numpy rank-2, 3D array
    @keyword r_ln_pivot:        The lanthanide position to pivot point vector.
    @type r_ln_pivot:           numpy rank-2, 3D array
    @keyword r_inter_pivot:     The vector between the two pivots.
    @type r_inter_pivot:        numpy rank-1, 3D array
    @keyword A:                 The full alignment tensor of the non-moving domain.
    @type A:                    numpy rank-2, 3D array
    @keyword R_eigen:           The eigenframe rotation matrix.
    @type R_eigen:              numpy rank-2, 3D array
    @keyword RT_eigen:          The transpose of the eigenframe rotation matrix (for faster calculations).
    @type RT_eigen:             numpy rank-2, 3D array
    @keyword Ri_prime:          The array of pre-calculated rotation matrices for the in-frame double rotor motion for the 1st mode of motion, used to calculate the PCS for each state i in the numerical integration.
    @type Ri_prime:             numpy rank-3, array of 3D arrays
    @keyword Ri2_prime:         The array of pre-calculated rotation matrices for the in-frame double rotor motion for the 2nd mode of motion, used to calculate the PCS for each state i in the numerical integration.
    @type Ri2_prime:            numpy rank-3, array of 3D arrays
    @keyword pcs_theta:         The storage structure for the back-calculated PCS values.
    @type pcs_theta:            numpy rank-2 array
    @keyword pcs_theta_err:     The storage structure for the back-calculated PCS errors.
    @type pcs_theta_err:        numpy rank-2 array
    @keyword missing_pcs:       A structure used to indicate which PCS values are missing.
    @type missing_pcs:          numpy rank-2 array
    """

    # Clear the data structures.
    pcs_theta[:] = 0.0
    pcs_theta_err[:] = 0.0

    # Fast frame shift.
    Ri = dot(R_eigen, tensordot(Ri_prime, RT_eigen, axes=1))
    Ri = swapaxes(Ri, 0, 1)
    Ri2 = dot(R_eigen, tensordot(Ri2_prime, RT_eigen, axes=1))
    Ri2 = swapaxes(Ri2, 0, 1)

    # Unpack the points.
    sigma, sigma2 = points

    # Loop over the samples.
    num = 0
    for i in range(len(points[0])):
        # The maximum number of points has been reached (well, surpassed by one so exit the loop before it is used).
        if num == max_points:
            break

        # Outside of the distribution, so skip the point.
        if abs(sigma[i]) > sigma_max:
            continue
        if abs(sigma2[i]) > sigma_max_2:
            continue

        # Calculate the PCSs for this state.
        pcs_pivot_motion_double_rotor_qr_int(full_in_ref_frame=full_in_ref_frame, r_pivot_atom=r_pivot_atom, r_pivot_atom_rev=r_pivot_atom_rev, r_ln_pivot=r_ln_pivot, r_inter_pivot=r_inter_pivot, A=A, Ri=Ri[i], Ri2=Ri2[i], pcs_theta=pcs_theta, pcs_theta_err=pcs_theta_err, missing_pcs=missing_pcs)

        # Increment the number of points.
        num += 1

    # Default to the rigid state if no points lie in the distribution.
    if num == 0:
        # Fast identity frame shift.
        Ri_prime = eye(3, dtype=float64)
        Ri = dot(R_eigen, tensordot(Ri_prime, RT_eigen, axes=1))
        Ri = swapaxes(Ri, 0, 1)

        # Calculate the PCSs for this state.
        pcs_pivot_motion_double_rotor_qr_int(full_in_ref_frame=full_in_ref_frame, r_pivot_atom=r_pivot_atom, r_pivot_atom_rev=r_pivot_atom_rev, r_ln_pivot=r_ln_pivot, r_inter_pivot=r_inter_pivot, A=A, Ri=Ri, Ri2=Ri, pcs_theta=pcs_theta, pcs_theta_err=pcs_theta_err, missing_pcs=missing_pcs)

        # Multiply the constant.
        multiply(c, pcs_theta, pcs_theta)

    # Average the PCS.
    else:
        multiply(c, pcs_theta, pcs_theta)
        divide(pcs_theta, float(num), pcs_theta)


def pcs_numeric_quad_int_double_rotor(sigma_max=None, sigma_max_2=None, c=None, r_pivot_atom=None, r_ln_pivot=None, r_inter_pivot=None, A=None, R_eigen=None, RT_eigen=None, Ri_prime=None, Ri2_prime=None):
    """Determine the averaged PCS value via SciPy quadratic numerical integration.

    @keyword sigma_max:         The maximum opening angle for the first rotor.
    @type sigma_max:            float
    @keyword sigma_max_2:       The maximum opening angle for the second rotor.
    @type sigma_max_2:          float
    @keyword c:                 The PCS constant (without the interatomic distance and in Angstrom units).
    @type c:                    numpy rank-1 array
    @keyword r_pivot_atom:      The pivot point to atom vector.
    @type r_pivot_atom:         numpy rank-1, 3D array
    @keyword r_ln_pivot:        The lanthanide position to pivot point vector.
    @type r_ln_pivot:           numpy rank-1, 3D array
    @keyword r_inter_pivot:     The vector between the two pivots.
    @type r_inter_pivot:        numpy rank-1, 3D array
    @keyword A:                 The full alignment tensor of the non-moving domain.
    @type A:                    numpy rank-2, 3D array
    @keyword R_eigen:           The eigenframe rotation matrix.
    @type R_eigen:              numpy rank-2, 3D array
    @keyword RT_eigen:          The transpose of the eigenframe rotation matrix (for faster calculations).
    @type RT_eigen:             numpy rank-2, 3D array
    @keyword Ri_prime:          The array of pre-calculated rotation matrices for the in-frame double rotor motion for the 1st mode of motion, used to calculate the PCS for each state i in the numerical integration.
    @type Ri_prime:             numpy rank-2, 3D array
    @keyword Ri2_prime:         The array of pre-calculated rotation matrices for the in-frame double rotor motion for the 2nd mode of motion, used to calculate the PCS for each state i in the numerical integration.
    @type Ri2_prime:            numpy rank-2, 3D array
    """

    # Preset the 1st rotation matrix elements for state i.
    Ri_prime[0, 1] = 0.0
    Ri_prime[1, 0] = 0.0
    Ri_prime[1, 1] = 1.0
    Ri_prime[1, 2] = 0.0
    Ri_prime[2, 1] = 0.0

    # Preset the 2nd rotation matrix elements for state i.
    Ri2_prime[0, 0] = 1.0
    Ri2_prime[0, 1] = 0.0
    Ri2_prime[0, 2] = 0.0
    Ri2_prime[1, 0] = 0.0
    Ri2_prime[2, 0] = 0.0

    # Perform numerical integration.
    result = dblquad(pcs_pivot_motion_double_rotor_quad_int, -sigma_max, sigma_max, lambda sigma2: -sigma_max_2, lambda sigma2: sigma_max_2, args=(r_pivot_atom, r_ln_pivot, r_inter_pivot, A, R_eigen, RT_eigen, Ri_prime, Ri2_prime))

    # The surface area normalisation factor.
    SA = 4.0 * sigma_max * sigma_max_2

    # Return the value.
    return c * result[0] / SA


def pcs_pivot_motion_double_rotor_qr_int(full_in_ref_frame=None, r_pivot_atom=None, r_pivot_atom_rev=None, r_ln_pivot=None, r_inter_pivot=None, A=None, Ri=None, Ri2=None, pcs_theta=None, pcs_theta_err=None, missing_pcs=None):
    """Calculate the PCS value after a pivoted motion for the double rotor model.

    @keyword full_in_ref_frame: An array of flags specifying if the tensor in the reference frame is the full or reduced tensor.
    @type full_in_ref_frame:    numpy rank-1 array
    @keyword r_pivot_atom:      The pivot point to atom vector.
    @type r_pivot_atom:         numpy rank-2, 3D array
    @keyword r_pivot_atom_rev:  The reversed pivot point to atom vector.
    @type r_pivot_atom_rev:     numpy rank-2, 3D array
    @keyword r_ln_pivot:        The lanthanide position to pivot point vector.
    @type r_ln_pivot:           numpy rank-2, 3D array
    @keyword r_inter_pivot:     The vector between the two pivots.
    @type r_inter_pivot:        numpy rank-1, 3D array
    @keyword A:                 The full alignment tensor of the non-moving domain.
    @type A:                    numpy rank-2, 3D array
    @keyword Ri:                The frame-shifted, pre-calculated rotation matrix for state i for the 1st mode of motion.
    @type Ri:                   numpy rank-2, 3D array
    @keyword Ri2:               The frame-shifted, pre-calculated rotation matrix for state i for the 2nd mode of motion.
    @type Ri2:                  numpy rank-2, 3D array
    @keyword pcs_theta:         The storage structure for the back-calculated PCS values.
    @type pcs_theta:            numpy rank-2 array
    @keyword pcs_theta_err:     The storage structure for the back-calculated PCS errors.
    @type pcs_theta_err:        numpy rank-2 array
    @keyword missing_pcs:       A structure used to indicate which PCS values are missing.
    @type missing_pcs:          numpy rank-2 array
    """

    # Rotate the first pivot to atomic position vectors.
    rot_vect = dot(r_pivot_atom, Ri)

    # Add the inter-pivot vector to obtain the 2nd pivot to atomic position vectors.
    add(r_inter_pivot, rot_vect, rot_vect)

    # Rotate the 2nd pivot to atomic position vectors.
    rot_vect = dot(rot_vect, Ri2)

    # Add the lanthanide to pivot vector.
    add(rot_vect, r_ln_pivot, rot_vect)

    # The vector length (to the 5th power).
    length = 1.0 / norm(rot_vect, axis=1)**5

    # The reverse vectors and lengths.
    if min(full_in_ref_frame) == 0:
        rot_vect_rev = dot(r_pivot_atom_rev, Ri)
        add(r_inter_pivot, rot_vect_rev, rot_vect_rev)
        rot_vect_rev = dot(rot_vect_rev, Ri2)
        add(rot_vect_rev, r_ln_pivot, rot_vect_rev)
        length_rev = 1.0 / norm(rot_vect_rev, axis=1)**5

    # Loop over the atoms.
    for j in range(len(r_pivot_atom[:, 0])):
        # Loop over the alignments.
        for i in range(len(pcs_theta)):
            # Skip missing data.
            if missing_pcs[i, j]:
                continue

            # The projection.
            if full_in_ref_frame[i]:
                proj = dot(rot_vect[j], dot(A[i], rot_vect[j]))
                length_i = length[j]
            else:
                proj = dot(rot_vect_rev[j], dot(A[i], rot_vect_rev[j]))
                length_i = length_rev[j]

            # The PCS.
            pcs_theta[i, j] += proj * length_i


def pcs_pivot_motion_double_rotor_quad_int(sigma_i, sigma2_i, r_pivot_atom, r_ln_pivot, r_inter_pivot, A, R_eigen, RT_eigen, Ri_prime, Ri2_prime):
    """Calculate the PCS value after a pivoted motion for the double rotor model.

    @param sigma_i:             The 1st torsion angle for state i.
    @type sigma_i:              float
    @param sigma2_i:            The 1st torsion angle for state i.
    @type sigma2_i:             float
    @param r_pivot_atom:        The pivot point to atom vector.
    @type r_pivot_atom:         numpy rank-2, 3D array
    @param r_ln_pivot:          The lanthanide position to pivot point vector.
    @type r_ln_pivot:           numpy rank-2, 3D array
    @param r_inter_pivot:       The vector between the two pivots.
    @type r_inter_pivot:        numpy rank-1, 3D array
    @param A:                   The full alignment tensor of the non-moving domain.
    @type A:                    numpy rank-2, 3D array
    @param R_eigen:             The eigenframe rotation matrix.
    @type R_eigen:              numpy rank-2, 3D array
    @param RT_eigen:            The transpose of the eigenframe rotation matrix (for faster calculations).
    @type RT_eigen:             numpy rank-2, 3D array
    @param Ri_prime:            The empty rotation matrix for state i.
    @type Ri_prime:             numpy rank-2, 3D array
    @param Ri2_prime:           The 2nd empty rotation matrix for state i.
    @type Ri2_prime:            numpy rank-2, 3D array
    @return:                    The PCS value for the changed position.
    @rtype:                     float
    """

    # The 1st rotation matrix.
    c_sigma = cos(sigma_i)
    s_sigma = sin(sigma_i)
    Ri_prime[0, 0] =  c_sigma
    Ri_prime[0, 2] =  s_sigma
    Ri_prime[2, 0] = -s_sigma
    Ri_prime[2, 2] =  c_sigma

    # The 2nd rotation matrix.
    c_sigma = cos(sigma2_i)
    s_sigma = sin(sigma2_i)
    Ri2_prime[1, 1] =  c_sigma
    Ri2_prime[1, 2] = -s_sigma
    Ri2_prime[2, 1] =  s_sigma
    Ri2_prime[2, 2] =  c_sigma

    # The rotations.
    Ri = dot(R_eigen, dot(Ri_prime, RT_eigen))
    Ri2 = dot(R_eigen, dot(Ri2_prime, RT_eigen))

    # Rotate the first pivot to atomic position vectors.
    rot_vect = dot(r_pivot_atom, Ri)

    # Add the inter-pivot vector to obtain the 2nd pivot to atomic position vectors.
    add(r_inter_pivot, rot_vect, rot_vect)

    # Rotate the 2nd pivot to atomic position vectors.
    rot_vect = dot(rot_vect, Ri2)

    # Add the lanthanide to pivot vector.
    add(rot_vect, r_ln_pivot, rot_vect)

    # The vector length.
    length = norm(rot_vect)

    # The projection.
    proj = dot(rot_vect, dot(A, rot_vect))

    # The PCS.
    pcs = proj / length**5

    # Return the PCS value (without the PCS constant).
    return pcs
