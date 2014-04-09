###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
"""The module for the relaxation dispersion analysis parameter list object."""

# relax module imports.
from specific_analyses.parameter_object import Param_list


class Relax_disp_params(Param_list):
    """The relaxation dispersion analysis parameter list singleton."""

    # Class variable for storing the class instance (for the singleton).
    _instance = None

    def __init__(self):
        """Define all the parameters of the analysis."""

        # Execute the base class __init__() method.
        Param_list.__init__(self)

        # Add the base data for the 'R2eff' model.
        self.add_peak_intensity()

        # Add the base information for the dispersion analysis.
        self.add('relax_times', scope='spin', py_type=dict, grace_string='\\qRelaxation time period (s)\\Q')
        self.add('cpmg_frqs', scope='spin', py_type=dict, grace_string='\\qCPMG pulse train frequency (Hz)\\Q')
        self.add('spin_lock_nu1', scope='spin', py_type=dict, grace_string='\\qSpin-lock field strength (Hz)\\Q')

        # Add the parameters of the 'R2eff' model.
        self.add('r2eff', scope='spin', default=15.0, desc='The effective transversal relaxation rate', set='params', py_type=dict, grace_string='\\qR\\s2,eff\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.add('i0', scope='spin', default=10000.0, desc='The initial intensity', py_type=dict, set='params', grace_string='\\qI\\s0\\Q', err=True, sim=True)

        # Add the parameters of all dispersion models.
        self.add('r2', scope='spin', default=15.0, desc='The transversal relaxation rate', set='params', py_type=dict, grace_string='\\qR\\s2\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.add('r2a', scope='spin', default=15.0, desc='The transversal relaxation rate for state A in the absence of exchange', set='params', py_type=dict, grace_string='\\qR\\s2,A\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.add('r2b', scope='spin', default=15.0, desc='The transversal relaxation rate for state B in the absence of exchange', set='params', py_type=dict, grace_string='\\qR\\s2,B\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.add('pA', scope='spin', default=0.5, desc='The population for state A', set='params', py_type=float, grace_string='\\qp\\sA\\N\\Q', err=True, sim=True)
        self.add('pB', scope='spin', default=0.5, desc='The population for state B', set='params', py_type=float, grace_string='\\qp\\sB\\N\\Q', err=True, sim=True)
        self.add('pC', scope='spin', default=0.5, desc='The population for state C', set='params', py_type=float, grace_string='\\qp\\sC\\N\\Q', err=True, sim=True)
        self.add('phi_ex', scope='spin', default=5.0, desc='The phi_ex = pA.pB.dw**2 value (ppm^2)', set='params', py_type=float, grace_string='\\xF\\B\\sex\\N = \\q p\\sA\\N.p\\sB\\N.\\xDw\\B\\S2\\N\\Q  (ppm\\S2\\N)', err=True, sim=True)
        self.add('phi_ex_B', scope='spin', default=5.0, desc='The fast exchange factor between sites A and B (ppm^2)', set='params', py_type=float, grace_string='\\xF\\B\\sex,B\\N (ppm\\S2\\N)', err=True, sim=True)
        self.add('phi_ex_C', scope='spin', default=5.0, desc='The fast exchange factor between sites A and C (ppm^2)', set='params', py_type=float, grace_string='\\xF\\B\\sex,C\\N (ppm\\S2\\N)', err=True, sim=True)
        self.add('padw2', scope='spin', default=1.0, desc='The pA.dw**2 value (ppm^2)', set='params', py_type=float, grace_string='\\qp\\sA\\N.\\xDw\\B\\S2\\N\\Q  (ppm\\S2\\N)', err=True, sim=True)
        self.add('dw', scope='spin', default=0.0, desc='The chemical shift difference between states A and B (in ppm)', set='params', py_type=float, grace_string='\\q\\xDw\\B\\Q (ppm)', err=True, sim=True)
        self.add('dw_AB', scope='spin', default=0.0, desc='The chemical shift difference between states A and B for 3-site exchange (in ppm)', set='params', py_type=float, grace_string='\\q\\xDw\\B\\Q\\SAB\\N (ppm)', err=True, sim=True)
        self.add('dw_AC', scope='spin', default=0.0, desc='The chemical shift difference between states A and C for 3-site exchange (in ppm)', set='params', py_type=float, grace_string='\\q\\xDw\\B\\Q\\SAC\\N (ppm)', err=True, sim=True)
        self.add('dw_BC', scope='spin', default=0.0, desc='The chemical shift difference between states B and C for 3-site exchange (in ppm)', set='params', py_type=float, grace_string='\\q\\xDw\\B\\Q\\SBC\\N (ppm)', err=True, sim=True)
        self.add('dwH', scope='spin', default=0.0, desc='The proton chemical shift difference between states A and B (in ppm)', set='params', py_type=float, grace_string='\\q\\xDw\\B\\sH\\N\\Q (ppm)', err=True, sim=True)
        self.add('dwH_AB', scope='spin', default=0.0, desc='The proton chemical shift difference between states A and B for 3-site exchange (in ppm)', set='params', py_type=float, grace_string='\\q\\xDw\\B\\sH\\N\\Q\\SAB\\N (ppm)', err=True, sim=True)
        self.add('dwH_AC', scope='spin', default=0.0, desc='The proton chemical shift difference between states A and C for 3-site exchange (in ppm)', set='params', py_type=float, grace_string='\\q\\xDw\\B\\sH\\N\\Q\\SAC\\N (ppm)', err=True, sim=True)
        self.add('dwH_BC', scope='spin', default=0.0, desc='The proton chemical shift difference between states B and C for 3-site exchange (in ppm)', set='params', py_type=float, grace_string='\\q\\xDw\\B\\sH\\N\\Q\\SBC\\N (ppm)', err=True, sim=True)
        self.add('kex', scope='spin', default=10000.0, desc='The exchange rate', set='params', py_type=float, grace_string='\\qk\\sex\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.add('kex_AB', scope='spin', default=10000.0, desc='The exchange rate between sites A and B for 3-site exchange with kex_AB = k_AB + k_BA (rad.s^-1)', set='params', py_type=float, grace_string='\\qk\\sex\\N\\Q\\SAB\\N (rad.s\\S-1\\N)', err=True, sim=True)
        self.add('kex_AC', scope='spin', default=10000.0, desc='The exchange rate between sites A and C for 3-site exchange with kex_AC = k_AC + k_CA (rad.s^-1)', set='params', py_type=float, grace_string='\\qk\\sex\\N\\Q\\SAC\\N (rad.s\\S-1\\N)', err=True, sim=True)
        self.add('kex_BC', scope='spin', default=10000.0, desc='The exchange rate between sites B and C for 3-site exchange with kex_BC = k_BC + k_CB (rad.s^-1)', set='params', py_type=float, grace_string='\\qk\\sex\\N\\Q\\SBC\\N (rad.s\\S-1\\N)', err=True, sim=True)
        self.add('kB', scope='spin', default=10000.0, desc='Approximate chemical exchange rate constant between sites A and B (rad.s^-1)', set='params', py_type=float, grace_string='\\qk\\sB\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.add('kC', scope='spin', default=10000.0, desc='Approximate chemical exchange rate constant between sites A and C (rad.s^-1)', set='params', py_type=float, grace_string='\\qk\\sC\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.add('tex', scope='spin', default=1.0/10000.0, desc='The time of exchange (tex = 1/kex)', set='params', py_type=float, grace_string='\\q\\xt\\B\\sex\\N\\Q (s.rad\\S-1\\N)', err=True, sim=True)
        self.add('theta', scope='spin', desc='Rotating frame tilt angle : ( theta = arctan(w_1 / Omega) ) (rad)', set='params', grace_string='Rotating frame tilt angle (rad)', py_type=dict, err=False, sim=False)
        self.add('w_eff', scope='spin', desc='Effective field in rotating frame : ( w_eff = sqrt(Omega^2 + w_1^2) ) (rad.s^-1)', grace_string='Effective field in rotating frame (rad.s\\S-1\\N)', set='params', py_type=dict, err=False, sim=False)
        self.add('k_AB', scope='spin', default=10000.0, desc='The exchange rate from state A to state B', set='params', py_type=float, grace_string='\\qk\\sAB\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.add('k_BA', scope='spin', default=10000.0, desc='The exchange rate from state B to state A', set='params', py_type=float, grace_string='\\qk\\sBA\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)

        # Add the model variables.
        self.add_model_info()

        # Add the minimisation data.
        self.add_min_data(min_stats_global=False, min_stats_spin=True)