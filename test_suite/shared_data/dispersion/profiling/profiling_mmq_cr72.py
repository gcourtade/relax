#!/usr/bin/env python

###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
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

# relax module imports.
from base import cluster, main, NUM_SPINS_CLUSTER, NUM_SPINS_SINGLE, single, Profile
from lib.dispersion.variables import EXP_TYPE_CPMG_MQ, MODEL_MMQ_CR72


# Setup.
SINGLE = Profile(exp_type=[EXP_TYPE_CPMG_MQ], num_spins=NUM_SPINS_SINGLE, model=MODEL_MMQ_CR72, r2=5.0, dw=3.0, dwH=0.03, pA=0.9, kex=1000.0, spins_params=['r2', 'dw', 'dwH', 'pA', 'kex'])
CLUSTER = Profile(exp_type=[EXP_TYPE_CPMG_MQ], num_spins=NUM_SPINS_CLUSTER, model=MODEL_MMQ_CR72, r2=5.0, dw=3.0, dwH=0.03, pA=0.9, kex=1000.0, spins_params=['r2', 'dw', 'dwH', 'pA', 'kex'])

# Execute main function.
if __name__ == "__main__":
    main()
