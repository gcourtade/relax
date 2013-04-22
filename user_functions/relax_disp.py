###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
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
"""The relax_disp user function definitions."""

# Python module imports.
import dep_check
if dep_check.wx_module:
    from wx import FD_OPEN, FD_SAVE
else:
    FD_OPEN = -1
    FD_SAVE = -1

# relax module imports.
from pipe_control import spectrum
from pipe_control.mol_res_spin import get_spin_ids
from graphics import WIZARD_IMAGE_PATH
from specific_analyses.setup import relax_disp_obj
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container

# The model names.
R2EFF = 'R2eff'
FAST_2SITE = 'fast 2-site'
SLOW_2SITE = 'slow 2-site'


# The user function class.
uf_class = uf_info.add_class('relax_disp')
uf_class.title = "Class for relaxation curve fitting."
uf_class.menu_text = "&relax_disp"
uf_class.gui_icon = "relax.relax_disp"


# The relax_disp.calc_r2eff user function.
uf = uf_info.add_uf('relax_disp.calc_r2eff')
uf.title = "Calculate the effective transversal relaxation rate from the peak intensities."
uf.title_short = "R2eff calculation."
uf.add_keyarg(
    name = "exp_type",
    default = "CPMG",
    py_type = "str",
    desc_short = "experiment type",
    desc = "The relaxation dispersion experiment type, either 'cpmg' or 'r1rho'.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "CPMG",
        "R1rho"
    ],
    wiz_combo_data = [
        "cpmg",
        "r1rho"
    ],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "id",
    py_type = "str",
    desc_short = "experiment ID",
    desc = "The experiment identification string."
)
uf.add_keyarg(
    name = "delayT",
    py_type = "num",
    desc_short = "CPMG time delay",
    desc = "The CPMG constant time delay (T) in s."
)
uf.add_keyarg(
    name = "int_cpmg",
    default = "1.0",
    py_type = "num",
    desc_short = "CPMG peak intensity",
    desc = "Intensity of the peak in the CPMG spectrum.."
)
uf.add_keyarg(
    name = "int_ref",
    default = "1.0",
    py_type = "num",
    desc_short = "reference peak intensity",
    desc = "Intensity of the peak in the reference spectrum.."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows one to extract 'r2eff' values from peak intensities.")
uf.desc[-1].add_paragraph("If 'cpmg' is chosen, the equation used is:")
uf.desc[-1].add_verbatim("""
    r2eff = - ( 1 / delayT ) * log ( int_cpmg / int_ref )
""")
uf.desc[-1].add_paragraph("If 'r1rho' is chosen, nothing happens yet, as the code is not implemented.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To calculate r2eff from a CPMG experiment, for experiment named '600', a constant time delay T of 20 ms (0.020 s) and intensities of CPMG and reference peak of, respectively, 0.742 and 0.9641, type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.calc_r2eff('cpmg', '600', 0.020, 0.742, 0.9641)")
uf.desc[-1].add_prompt("relax> relax_disp.calc_r2eff(exp_type='cpmg', id='600', delayT=0.020, int_cpmg=0.742, int_ref=0.9641)")
uf.desc[-1].add_paragraph("ANOTHER EXAMPLE FOR BATCH USE (FROM PEAK INTENSITY LISTS) WILL SOON BE ADDED.")
uf.backend = relax_disp_obj._calc_r2eff
uf.menu_text = "&calc_r2eff"
uf.wizard_size = (900, 600)


# The relax_disp.cluster user function.
uf = uf_info.add_uf('relax_disp.cluster')
uf.title = "Define clusters of spins for joint optimisation."
uf.title_short = "Spin clustering."
uf.add_keyarg(
    name = "cluster_id",
    py_type = "str",
    desc_short = "cluster ID",
    desc = "The cluster identification string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_disp_obj._cluster_ids
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin identifier string for the spin or group of spins to add to the cluster.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_spin_ids,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("In a relaxation dispersion analysis, the parameters of the model of dispersion can either be optimised for each spin system separately or a number of spins can be grouped or clustered and the dispersion model parameters optimised for all spins in the cluster together.  Clusters are identified by unique ID strings.  Any spins not within a cluster will be optimised separately and individually.")
uf.desc[-1].add_paragraph("If the cluster ID string already exists, the spins will be added to that pre-existing cluster.  If no spin ID is given, then all spins will be added to the cluster.")
uf.desc[-1].add_paragraph("The special cluster ID string 'free spins' is reserved for the pool of non-clustered spins.  This can be used to remove a spin system from an already existing cluster by specifying this cluster ID and the desired spin ID.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To add the spins ':1@N' and ':3@N' to a new cluster called 'cluster', type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.cluster('cluster', ':1,3@N)")
uf.desc[-1].add_prompt("relax> relax_disp.cluster(cluster_id='cluster', spin_id=':1,3@N)")
uf.backend = relax_disp_obj._cluster
uf.menu_text = "c&luster"
uf.wizard_height_desc = 500
uf.wizard_size = (800, 600)


# The relax_disp.cpmg_frq user function.
uf = uf_info.add_uf('relax_disp.cpmg_frq')
uf.title = "Set the CPMG frequency associated with a given spectrum."
uf.title_short = "CPMG frequency setting."
uf.add_keyarg(
    name = "spectrum_id",
    py_type = "str",
    desc_short = "spectrum ID string",
    desc = "The spectrum ID string to associate the CPMG frequency to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = spectrum.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "cpmg_frq",
    py_type = "num",
    desc_short = "CPMG frequency (Hz)",
    desc = "The frequency, in Hz, of the CPMG pulse train.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows the CPMG pulse train frequency of a given spectrum to be set.  If None is given for frequency, then the spectrum will be treated as a reference spectrum.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To identify the reference spectrum called 'reference_spectrum', type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.cpmg_frq(None, 'reference_spectrum')")
uf.desc[-1].add_prompt("relax> relax_disp.cpmg_frq(cpmg_frq=None, spectrum_id='reference_spectrum')")
uf.desc[-1].add_paragraph("To set a frequency of 200 Hz for the spectrum '200_Hz_spectrum', type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.cpmg_frq(200, '200_Hz_spectrum')")
uf.desc[-1].add_prompt("relax> relax_disp.cpmg_frq(cpmg_frq=200, spectrum_id='200_Hz_spectrum')")
uf.backend = relax_disp_obj._cpmg_frq
uf.menu_text = "&cpmg_frq"
uf.wizard_size = (800, 500)


# The relax_disp.exp_type user function.
uf = uf_info.add_uf('relax_disp.exp_type')
uf.title = "Select the type of relaxation dispersion experiments to be analysed."
uf.title_short = "Relaxation dispersion experiment type selection."
uf.add_keyarg(
    name = "exp_type",
    default = "cpmg",
    py_type = "str",
    desc_short = "experiment type",
    desc = "The type of relaxation dispersion experiment performed.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "CPMG",
        "CPMG, fixed time",
        "R1rho"
    ],
    wiz_combo_data = [
        "cpmg",
        "cpmg fixed",
        "r1rho"
    ],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The currently supported experiments include:")
uf.desc[-1].add_item_list_element("'cpmg'", "The CPMG family of experiments whereby spectra consist of exponential curves by varying the total time of the CPMG block of pulses,")
uf.desc[-1].add_item_list_element("'cpmg fixed'", "The CPMG family of experiments whereby the time period for the block of CPMG pulses is fixed and a reference spectrum is present,")
uf.desc[-1].add_item_list_element("'r1rho'", "The R1rho family of experiments whereby spectra consist of exponential curves by varying the total time in which the spin-lock field is applied.")
uf.desc[-1].add_paragraph("For the 'cpmg' and 'r1rho' experiment types, 2-parameter exponentials will be fit to obtain R2,eff for each spin system as part of the optimisation of the dispersion model.")
uf.desc[-1].add_paragraph("For the 'cpmg fixed' experiment type, the R2,eff values are directly calculated prior to optimisation using the formula:")
uf.desc[-1].add_verbatim("""
                        -1         / I1(nu_CPMG) \ 
    R2,eff(nu_CPMG) = ------- * ln | ----------- |,
                      relax_T      \     I0      /
""")
uf.desc[-1].add_paragraph("where nu_CPMG is the CPMG frequency in Hz, relax_T is the fixed delay time, I0 is the reference peak intensity when relax_T is zero, and I1 is the peak intensity in a spectrum for a given nu_CPMG frequency.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To pick the experiment type 'cpmg' for all selected spins, type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.exp_type('cpmg')")
uf.desc[-1].add_prompt("relax> relax_disp.exp_type(exp_type='cpmg')")
uf.backend = relax_disp_obj._exp_type
uf.menu_text = "&exp_type"
uf.wizard_height_desc = 500
uf.wizard_size = (1000, 700)
uf.wizard_apply_button = False


# The relax_disp.plot_exp_curves user function.
uf = uf_info.add_uf('relax_disp.plot_exp_curves')
uf.title = "Create 2D Grace plots of the exponential curves."
uf.title_short = "Exponential curve plotting."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file.",
    wiz_filesel_wildcard = "Grace files (*.agr)|*.agr;*.AGR",
    wiz_filesel_style = FD_SAVE
)
uf.add_keyarg(
    name = "dir",
    default = "grace",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory name.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which, if set to True, will cause the file to be overwritten."
)
uf.add_keyarg(
    name = "norm",
    default = False,
    py_type = "bool",
    desc_short = "normalisation flag",
    desc = "A flag which, if set to True, will cause all graphs to be normalised to a starting value of 1.  This is for the normalisation of series type data."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This is used to created 2D Grace plots of the individual exponential curves used to find the R2eff values.  This supplements the grace.write user function which is not capable of generating these curves in a reasonable format.")
uf.backend = relax_disp_obj._plot_exp_curves
uf.menu_text = "&plot_exp_curves"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'grace.png'


# The relax_disp.relax_time user function.
uf = uf_info.add_uf('relax_disp.relax_time')
uf.title = "Set the relaxation delay time associated with each spectrum."
uf.title_short = "Relaxation delay time setting."
uf.add_keyarg(
    name = "spectrum_id",
    py_type = "str",
    desc_short = "spectrum ID string",
    desc = "The spectrum ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = spectrum.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "time",
    default = 0.0,
    py_type = "num",
    desc_short = "relaxation time",
    desc = "The time, in seconds, of the relaxation period."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("Peak intensities should be loaded before calling this user function via the spectrum.read_intensities user function.  The intensity values will then be associated with a spectrum identifier.  To associate each spectrum identifier with a time point in the relaxation curve prior to optimisation, this user function should be called.")
uf.backend = relax_disp_obj._relax_time
uf.menu_text = "&relax_time"
uf.gui_icon = "oxygen.actions.chronometer"
uf.wizard_size = (800, 500)


# The relax_disp.select_model user function.
uf = uf_info.add_uf('relax_disp.select_model')
uf.title = "Select the relaxation dispersion model."
uf.title_short = "Relaxation dispersion model setup."
uf.display = True
uf.add_keyarg(
    name = "model",
    default = R2EFF,
    py_type = "str",
    desc_short = "dispersion model",
    desc = "The type of relaxation dispersion model to fit.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "%s: {R2eff, I0}" % R2EFF,
        "%s: {R2, Rex, kex}" % FAST_2SITE,
        "%s: {R2A, kA, dw}" % SLOW_2SITE
    ],
    wiz_combo_data = [
        R2EFF,
        FAST_2SITE,
        SLOW_2SITE
    ],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("A number of different dispersion models will be supported, from the numerical integration of the Bloch-McConnell equations, the 2-site fast, intermediate and slow exchange, 3-site exchange, to the most basic model of simply fitting the exponential curves.  The currently supported models include:")
uf.desc[-1].add_item_list_element("'%s'" % R2EFF, "This is the model used to determine the R2eff values and errors required as the base data for all other models,")
uf.desc[-1].add_item_list_element("'%s'" % FAST_2SITE, "The 2-site fast exchange equation with parameters {R2, Rex, kex},")
uf.desc[-1].add_item_list_element("'%s'" % SLOW_2SITE, "The 2-site slow exchange equation with parameters {R2A, kA, dw}.")
uf.desc[-1].add_paragraph("Except for '%s', these models are fit to clusterings of spins, or spin blocks." % R2EFF)
# R2eff model.
uf.desc.append(Desc_container("The R2eff model"))
uf.desc[-1].add_paragraph("This is the simplest of all models in that the dispersion part is not modelled.  It is used to determine the R2eff values and errors which are required as the base data for all other models.  It can be selected by setting the model to '%s'.  Depending on the experiment type, this model will be handled differently.  The R2eff values determined can be later copied to the data pipes of the other dispersion models using the appropriate value user function." % R2EFF)
uf.desc[-1].add_paragraph("For the fixed relaxation time period type experiments, the R2eff values are determined by direct calculation using the formula:")
uf.desc[-1].add_verbatim("""
                        -1         / I1(nu_CPMG) \ 
    R2,eff(nu_CPMG) = ------- * ln | ----------- |,
                      relax_T      \     I0      /
""")
uf.desc[-1].add_paragraph("where nu_CPMG is the CPMG frequency in Hz, relax_T is the fixed delay time, I0 is the reference peak intensity when relax_T is zero, and I1 is the peak intensity in a spectrum for a given nu_CPMG frequency.  Errors are determined via bootstrapping.  The values and errors are determined with a single call of the calc user function.")
uf.desc[-1].add_paragraph("For the variable relaxation time period type experiments, the R2eff values are determined by fitting to the simple two parameter exponential as in a R1 or R2 analysis.  Both R2eff and the initial peak intensity I0 are optimised using the minimise user function for each exponential curve separately.  Monte Carlo simulations are used to obtain the R2eff errors.")
# 2-site fast exchange model.
uf.desc.append(Desc_container("The 2-site fast exchange model"))
uf.desc[-1].add_paragraph("This is selected by setting the model to '%s'.  The equation for fast exchange is:" % FAST_2SITE)
uf.desc[-1].add_verbatim("""
                       /              /        kex       \   4 * cpmg_frq \ 
    R2eff = R2 + Rex * | 1 - 2 * tanh | ---------------- | * ------------ |
                       \              \ 2 * 4 * cpmg_frq /        kex     /
""")
uf.desc[-1].add_paragraph("The references for this equation are:")
uf.desc[-1].add_list_element("Millet et al., JACS, 2000, 122, 2867-2877 (equation 19),")
uf.desc[-1].add_list_element("Kovrigin et al., J. Mag. Res., 2006, 180, 93-104 (equation 1).")
# 2-site slow exchange model.
uf.desc.append(Desc_container("The 2-site slow exchange model"))
uf.desc[-1].add_paragraph("This is selected by setting the model to '%s'.  The equation for slow exchange is:" % SLOW_2SITE)
uf.desc[-1].add_verbatim("""
                       /     /      dw      \   4 * cpmg_frq \ 
    R2eff = R2A + kA - | sin | ------------ | * ------------ |
                       \     \ 4 * cpmg_frq /        dw      /
""")
uf.desc[-1].add_paragraph("where:")
uf.desc[-1].add_verbatim("""
    cpmg_frq = 1 / ( 4 * cpmg_tau )
""")
uf.desc[-1].add_paragraph("The reference for this equation is:")
uf.desc[-1].add_list_element("Tollinger et al., JACS, 2001, 123: 11341-11352 (equation 2).")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To pick the 2-site fast exchange model for all selected spins, type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.select_model('%s')" % FAST_2SITE)
uf.desc[-1].add_prompt("relax> relax_disp.select_model(model='%s')" % FAST_2SITE)
uf.backend = relax_disp_obj._select_model
uf.menu_text = "&select_model"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_height_desc = 500
uf.wizard_size = (1000, 700)
uf.wizard_apply_button = False


# The relax_disp.spin_lock_field user function.
uf = uf_info.add_uf('relax_disp.spin_lock_field')
uf.title = "Set the relaxation dispersion spin-lock field strength (nu1)."
uf.title_short = "Spin-lock field strength."
uf.add_keyarg(
    name = "spectrum_id",
    py_type = "str",
    desc_short = "spectrum ID string",
    desc = "The spectrum ID string to associate the spin-lock field strength to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = spectrum.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "field",
    py_type = "num",
    desc_short = "field strength nu1 (Hz)",
    desc = "The spin-lock field strength, nu1, in Hz."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This sets the spin-lock field strength, nu1, for the specified R1rho spectrum in Hertz.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To set a spin-lock field strength of 2.1 kHz for the spectrum 'nu1_2.1kHz_relaxT_0.010', type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.spin_lock_field(2100, 'nu1_2.1kHz_relaxT_0.010')")
uf.desc[-1].add_prompt("relax> relax_disp.spin_lock_field(field=2100, spectrum_id='nu1_2.1kHz_relaxT_0.010')")
uf.backend = relax_disp_obj._spin_lock_field
uf.menu_text = "spin_lock_&field"
uf.wizard_size = (800, 500)
