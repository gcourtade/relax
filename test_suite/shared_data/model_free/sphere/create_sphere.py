###############################################################################
#                                                                             #
# Copyright (C) 2004,2011,2014 Edward d'Auvergne                              #
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
"""relax script for creating the spherical PDB file."""

# Python module imports.
from math import acos, cos, pi, sin, sqrt

# relax module imports.
from lib.structure.pdb_write import conect, hetatm


# Number of increments.
number = 3

# U and V.
u = []
val = 1.0 / float(number)
for i in range(number):
    u.append(float(i) * val)


# Generate the spherical angles theta and phi.
##############################################

theta = []
phi = []
for i in range(len(u)):
    theta.append(acos(2.0 * (u[i] + val/2.0) - 1.0))
    phi.append(2.0 * pi * u[i])
    print("\ni: %s" % i)
    print("u: %s" % u[i])
    print("v: %s" % (u[i] + val/2.0))
    print("theta: %s" % theta[i])
    print("phi: %s" % phi[i])


# Generate the vectors:
#
#                 | sin(theta) * cos(phi) |
#      vector  =  | sin(theta) * sin(phi) |
#                 |      cos(theta)       |
#
###########################################

vectors = []
for i in range(len(u)):
    for j in range(len(u)):
        # X coordinate.
        x = sin(theta[i]) * cos(phi[j])

        # Y coordinate.
        y = sin(theta[i]) * sin(phi[j])

        # Z coordinate.
        z = cos(theta[i])

        # Append the vector.
        vectors.append([x, y, z])


# Create the PDB file.
######################

# PDB file.
file = open('sphere.pdb', 'w')

# Atom number and residue number.
atom_num = 1
res_num = 1

# Used vectors.
used = []

# Loop over the vectors. 
for i in range(len(vectors)):
    # Test if the vector has already been used.
    if vectors[i] in used:
        print("Vector %s already used." % vectors[i])
        continue

    # Nitrogen line.
    hetatm(file=file, serial=atom_num, name='N', res_seq=res_num, res_name='GLY', x=0.0, y=0.0, z=0.0)

    # Hydrogen line.
    hetatm(file=file, serial=atom_num+1, name='H', res_seq=res_num, res_name='GLY', x=vectors[i][0], y=vectors[i][1], z=vectors[i][2])

    # Increment the atom number and residue number.
    atom_num = atom_num + 2
    res_num = res_num + 1

    # Add the vector to the used vector list.
    used.append(vectors[i])

# Add a Trp indole NH for luck ;)
hetatm(file=file, serial=atom_num, name='NE1', res_seq=res_num-1, res_name='GLY', x=0.0, y=0.0, z=0.0)
hetatm(file=file, serial=atom_num+1, name='HE1', res_seq=res_num-1, res_name='GLY', x=1/sqrt(3), y=1/sqrt(3), z=1/sqrt(3))

# Connect everything.
atom_num = 1
for i in range(len(vectors)):
    conect(file=file, serial=atom_num, bonded1=atom_num+1)
    conect(file=file, serial=atom_num+1, bonded1=atom_num)
    atom_num = atom_num + 2
conect(file=file, serial=atom_num, bonded1=atom_num+1)
conect(file=file, serial=atom_num+1, bonded1=atom_num)

# End of PDB.
file.write('END\n')
