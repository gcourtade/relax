###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


from ri_comps import r1_comps, dr1_comps, d2r1_comps
from ri_prime import func_ri_prime


def dri(data, params):
    """Additional layer of equations to simplify the relaxation equations, gradients, and Hessians.
   """

    # Loop over the relaxation values and modify the NOE gradients.
    for i in xrange(data.num_ri):
        if data.create_dri[i]:
            data.create_dri[i](data, i, data.remap_table[i], data.get_dr1, params)


def d2ri(data, params):
    """Additional layer of equations to simplify the relaxation equations, gradients, and Hessians.
   """

    # Loop over the relaxation values and modify the NOE Hessians.
    for i in xrange(data.num_ri):
        if data.create_d2ri[i]:
            data.create_d2ri[i](data, i, data.remap_table[i], data.get_d2r1, params)



# Calculate the NOE value.
##########################

def calc_noe(data, i, frq_num, get_r1, params):
    """Calculate the NOE value.

    Half this code needs to be shifted into the function initialisation code.
    """

    # Get the r1 value either from data.ri_prime or by calculation if the value is not in data.ri_prime
    data.r1[i] = get_r1[i](data, i, frq_num, params)

    # Calculate the NOE.
    if data.r1[i] == 0.0:
        data.ri[i] = 1e99
    else:
        data.ri[i] = 1.0 + data.g_ratio*(data.ri_prime[i] / data.r1[i])


def calc_dnoe(data, i, frq_num, get_dr1, params):
    """Calculate the derivative of the NOE value.

    Half this code needs to be shifted into the function initialisation code.
    """

    # Calculate the NOE derivative.
    data.dr1[i] = get_dr1[i](data, i, frq_num, params)
    if data.r1[i] == 0.0:
        data.dri[i] = 1e99
    else:
        print "\n"
        print "r1:        %-40.66g" % data.r1[i]
        print "dri_prime: %-40.66g" % data.dri_prime[i]
        print "ri_prime:  %-40.66g" % data.ri_prime[i]
        print "dr1:       %-40.66g" % data.dr1[i]
        data.dri[i] = data.g_ratio * (1.0 / data.r1[i]**2) * (data.r1[i] * data.dri_prime[i] - data.ri_prime[i] * data.dr1[i])
        print "dri:       %-40.66g" % data.dri[i]


def calc_d2noe(data, i, frq_num, get_d2r1, params):
    """Calculate the second partial derivative of the NOE value.

    Half this code needs to be shifted into the function initialisation code.
    """

    # Calculate the NOE second derivative.
    data.d2r1[i] = get_d2r1[i](data, i, frq_num, params)
    if data.r1[i] == 0.0:
        data.d2ri[i] = 1e99
    else:
        print "Num params: " + `data.num_params`
        for j in xrange(data.num_params):
            a = data.ri_prime[i] * (2.0 * data.dr1[i, j] * data.dr1[i] - data.r1[i] * data.d2r1[i, j])
            b = data.r1[i] * (data.dri_prime[i, j] * data.dr1[i] + data.dr1[i, j] * data.dri_prime[i] - data.r1[i] * data.d2ri_prime[i, j])
            data.d2ri[i, j] = data.g_ratio * (1.0 / data.r1[i]**3) * (a - b)



# Calculate the R1 value.
#########################

def calc_r1(data, i, frq_num, params):
    """Calculate the R1 value if there is no R1 data corresponding to the NOE data.

    R1()  =  dip_const_func . dip_Jw_R1_func  +  csa_const_func . csa_Jw_R1_func
    """

    # Place data in the R1 data class.
    data.r1_data.remap_table = data.remap_table
    data.r1_data.jw = data.jw
    data.r1_data.dip_const_func = data.dip_const_func
    data.r1_data.csa_const_func = data.csa_const_func

    # Calculate the r1 components.
    r1_comps(data.r1_data, i, params)

    # Calculate the r1 value.
    func_ri_prime(data.r1_data)

    return data.r1_data.ri_prime[i]


def calc_dr1(data, i, frq_num, params):
    """Calculate the R1 value if there is no R1 data corresponding to the NOE data.

    dR1()
    -----  =  dip_const_func . dip_Jw_R1_grad  +  csa_const_func . csa_Jw_R1_grad
     dJw

    dR1()
    -----  =  0
    dRex

    dR1()
    -----  =  dip_const_grad . dip_Jw_R1_func
     dr

    dR1()
    -----  =  csa_const_grad . csa_Jw_R1_func
    dcsa
    """

    # Place data in the R1 data class.
    data.r1_data.remap_table = data.remap_table
    data.r1_data.djw = data.djw
    data.r1_data.dip_const_grad = data.dip_const_grad
    data.r1_data.csa_const_grad = data.csa_const_grad

    # Calculate the dr1 components.
    dr1_comps(data.r1_data, i, params)

    # Calculate the dr1 value.
    for j in xrange(data.num_params):
        data.r1_data.create_dri_prime[j](data.r1_data, j)

    return data.r1_data.dri_prime[i]


def calc_d2r1(data, i, frq_num, params):
    """Calculate the R1 value if there is no R1 data corresponding to the NOE data."""

    # Place data in the R1 data class.
    data.r1_data.remap_table = data.remap_table
    data.r1_data.d2jw = data.d2jw
    data.r1_data.dip_const_hess = data.dip_const_hess
    data.r1_data.csa_const_hess = data.csa_const_hess

    # Calculate the dr1 components.
    d2r1_comps(data.r1_data, i, params)

    # Calculate the dr1 value.
    for j in xrange(data.num_params):
        for k in xrange(j + 1):
            if data.r1_data.create_d2ri_prime[j][k]:
                data.r1_data.create_d2ri_prime[j][k](data.r1_data, j, k)
                # Make the Hessian symmetric.
                if i != j:
                    data.r1_data.d2ri_prime[i, k, j] = data.r1_data.d2ri_prime[i, j, k]

    return data.r1_data.d2ri_prime[i]



# Extract the R1 value.
#######################

def extract_r1(data, i, frq_num, params):
    """Get the R1 value from data.ri_prime"""

    return data.ri_prime[data.noe_r1_table[i]]


def extract_dr1(data, i, frq_num, params):
    """Get the dR1 value from data.dri_prime"""

    return data.dri_prime[data.noe_r1_table[i]]


def extract_d2r1(data, i, frq_num, params):
    """Get the d2R1 value from data.d2ri_prime"""

    return data.d2ri_prime[data.noe_r1_table[i]]
