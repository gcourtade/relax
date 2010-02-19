###############################################################################
#                                                                             #
# Copyright (C) 2003-2009 Edward d'Auvergne                                   #
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
"""Module for interfacing with Grace (also known as Xmgrace, Xmgr, and ace)."""

# Python module imports.
from numpy import array, ndarray
from os import system
from warnings import warn

# relax module imports.
import generic_fns
from generic_fns.mol_res_spin import count_molecules, count_residues, count_spins, exists_mol_res_spin_data, generate_spin_id, spin_loop
from generic_fns import pipes
from relax_errors import RelaxError, RelaxNoSequenceError, RelaxNoSimError
from relax_io import get_file_path, open_write_file, test_binary
from relax_warnings import RelaxWarning
from specific_fns.setup import get_specific_fn


def determine_graph_type(data, x_data_type=None, plot_data=None):
    """Determine if the graph is of type xy, xydy, xydx, or xydxdy.

    @param data:            The graph numerical data.
    @type data:             list of lists of float
    @keyword x_data_type:   The category of the X-axis data.
    @type x_data_type:      str
    @keyword plot_data:     The type of the plotted data, one of 'value', 'error', or 'sim'.
    @type plot_data:        str
    @return:                The graph type, which can be one of xy, xydy, xydx, or xydxdy.
    @rtype:                 str
    """

    # Initial flags.
    x_errors = 0
    y_errors = 0

    # Loop over the data.
    for i in xrange(len(data)):
        # X-axis errors.
        if x_data_type != 'spin' and data[i][-3] != None:
            x_errors = 1

        # Y-axis errors.
        if data[i][-1] != None:
            y_errors = 1

    # Plot of values.
    if plot_data == 'value':
        # xy plot with errors along both axes.
        if x_errors and y_errors:
            graph_type = 'xydxdy'

        # xy plot with errors along the Y-axis.
        elif y_errors:
            graph_type = 'xydy'

        # xy plot with errors along the X-axis.
        elif x_errors:
            graph_type = 'xydx'

        # xy plot with no errors.
        else:
            graph_type = 'xy'

    # Plot of errors.
    elif plot_data == 'error':
        # xy plot of spin vs error.
        if x_data_type == 'spin' and y_errors:
            graph_type = 'xy'

        # xy plot of error vs error.
        elif x_errors and y_errors:
            graph_type = 'xy'

        # Invalid argument combination.
        else:
            raise RelaxError("When plotting errors, the errors must exist.")

    # Plot of simulation values.
    else:
        # xy plot with no errors.
        graph_type = 'xy'

    # Return the graph type.
    return graph_type


def determine_seq_type(spin_id=None):
    """Determine the spin sequence data type.

    The purpose is to identify systems whereby only spins or only residues exist.

    @keyword spin_id:   The spin identification string.
    @type spin_id:      str
    @return:            The spin sequence data type.  This can be one of 'spin', 'res,' or 'mixed'.
    @rtype:             str
    """

    # Count the molecules, residues, and spins.
    num_mol = count_molecules(spin_id)
    num_res = count_residues(spin_id)
    num_spin = count_spins(spin_id)

    # Only residues.
    if num_mol == 1 and num_spin == 1:
        return 'res'

    # Only spins.
    if num_mol == 1 and num_res == 1:
        return 'spin'

    # Mixed.
    return 'mixed'


def get_data(spin_id=None, x_data_type=None, y_data_type=None, plot_data=None):
    """Get all the xy data.

    @keyword spin_id:       The spin identification string.
    @type spin_id:          str
    @keyword x_data_type:   The category of the X-axis data.
    @type x_data_type:      str
    @keyword y_data_type:   The category of the Y-axis data.
    @type y_data_type:      str
    @keyword plot_data:     The type of the plotted data, one of 'value', 'error', or 'sim'.
    @type plot_data:        str
    @return:                The graph numerical data.
    @rtype:                 list of lists of float
    """

    # Initialise the data structure.
    data = []

    # Specific x and y value returning functions.
    x_return_value = y_return_value = get_specific_fn('return_value', pipes.get_type())
    x_return_conversion_factor = y_return_conversion_factor = get_specific_fn('return_conversion_factor', pipes.get_type())

    # Test if the X-axis data type is a minimisation statistic.
    if x_data_type != 'spin' and generic_fns.minimise.return_data_name(x_data_type):
        x_return_value = generic_fns.minimise.return_value
        x_return_conversion_factor = generic_fns.minimise.return_conversion_factor

    # Test if the Y-axis data type is a minimisation statistic.
    if y_data_type != 'spin' and generic_fns.minimise.return_data_name(y_data_type):
        y_return_value = generic_fns.minimise.return_value
        y_return_conversion_factor = generic_fns.minimise.return_conversion_factor

    # Loop over the spins.
    for spin, mol_name, res_num, res_name, spin_id in spin_loop(full_info=True, return_id=True):
        # Skip deselected spins.
        if not spin.select:
            continue

        # Number of data points per spin.
        if plot_data == 'sim':
            points = cdp.sim_number
        else:
            points = 1

        # Loop over the data points.
        for j in xrange(points):
            # Initialise an empty array for the individual spin data.
            spin_data = [mol_name, res_num, res_name, spin.num, spin.name, None, None, None, None]

            # FIXME:  Need to work out how the spin_id string can be handled in Grace.
            # Spin ID string on the x-axis.
            #if x_data_type == 'spin':
            #    spin_data[-4] = spin_id
            # Residue number.
            if x_data_type == 'spin':
                spin_data[-4] = res_num

            # Parameter value for the x-axis.
            else:
                # Get the x-axis values and errors.
                if plot_data == 'sim':
                    spin_data[-4], spin_data[-3] = x_return_value(spin, x_data_type, sim=j)
                else:
                    spin_data[-4], spin_data[-3] = x_return_value(spin, x_data_type)

            # Get the y-axis values and errors.
            if plot_data == 'sim':
                spin_data[-2], spin_data[-1] = y_return_value(spin, y_data_type, sim=j)
            else:
                spin_data[-2], spin_data[-1] = y_return_value(spin, y_data_type)

            # Go to the next spin if there is missing data.
            if spin_data[-4] == None or spin_data[-2] == None:
                continue

            # X-axis conversion factors.
            if x_data_type != 'spin':
                spin_data[-4] = array(spin_data[-4]) / x_return_conversion_factor(x_data_type, spin)
                if spin_data[-3]:
                    spin_data[-3] = array(spin_data[-3]) / x_return_conversion_factor(x_data_type, spin)

            # Y-axis conversion factors.
            spin_data[-2] = array(spin_data[-2]) / y_return_conversion_factor(y_data_type, spin)
            if spin_data[-1]:
                spin_data[-1] = array(spin_data[-1]) / y_return_conversion_factor(y_data_type, spin)

            # Append the array to the full data structure.
            data.append(spin_data)

    # Return the data.
    return data


def view(file=None, dir=None, grace_exe='xmgrace'):
    """Execute Grace.

    @keyword file:      The name of the file to open in Grace.
    @type file:         str
    @keyword dir:       The optional directory containing the file.
    @type dir:          str
    @keyword grace_exe: The name of the Grace executable file.  This should be located within the
                        system path.
    @type grace_exe:    str
    """

    # Test the binary file string corresponds to a valid executable.
    test_binary(grace_exe)

    # File path.
    file_path = get_file_path(file, dir)

    # Run Grace.
    system(grace_exe + " " + file_path + " &")


def write(x_data_type='spin', y_data_type=None, spin_id=None, plot_data='value', file=None, dir=None, force=False, norm=True):
    """Writing data to a file.

    @keyword x_data_type:   The category of the X-axis data.
    @type x_data_type:      str
    @keyword y_data_type:   The category of the Y-axis data.
    @type y_data_type:      str
    @keyword spin_id:       The spin identification string.
    @type spin_id:          str
    @keyword plot_data:     The type of the plotted data, one of 'value', 'error', or 'sim'.
    @type plot_data:        str
    @keyword file:          The name of the Grace file to create.
    @type file:             str
    @keyword dir:           The optional directory to place the file into.
    @type dir:              str
    @param force:           Boolean argument which if True causes the file to be overwritten if it
                            already exists.
    @type force:            bool
    @keyword norm:          The normalisation flag which if set to True will cause all graphs to be
                            normalised to a starting value of 1.
    @type norm:             bool
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if the plot_data argument is one of 'value', 'error', or 'sim'.
    if plot_data not in ['value', 'error', 'sim']:
        raise RelaxError("The plot data argument " + repr(plot_data) + " must be set to either 'value', 'error', 'sim'.")

    # Test if the simulations exist.
    if plot_data == 'sim' and not hasattr(cdp, 'sim_number'):
        raise RelaxNoSimError

    # Open the file for writing.
    file = open_write_file(file, dir, force)

    # Get the data.
    data = get_data(spin_id, x_data_type=x_data_type, y_data_type=y_data_type, plot_data=plot_data)

    # Generate the spin_ids for all the data.
    spin_ids = []
    for line in data:
        spin_ids.append(generate_spin_id(line[0], line[1], line[2], line[3], line[4]))

    # No data, so close the empty file and exit.
    if data == None or data == []:
        warn(RelaxWarning("No data could be found, creating an empty file."))
        file.close()
        return

    # Determine the graph type (ie xy, xydy, xydx, or xydxdy).
    graph_type = determine_graph_type(data, x_data_type=x_data_type, plot_data=plot_data)

    # Test for multiple data sets.
    multi = False
    sets = 1
    set_names = None
    if isinstance(data[0][-4], list) or isinstance(data[0][-4], ndarray):
        multi = True
        sets = len(data)
        set_names = spin_ids

    # Determine the sequence data type.
    seq_type = determine_seq_type(spin_id=spin_ids[0])

    # Write the header.
    write_xy_header(sets=sets, file=file, data_type=[x_data_type, y_data_type], seq_type=[seq_type, None], set_names=set_names, norm=norm)

    # Write the data.
    write_xy_data(data, file=file, graph_type=graph_type, norm=norm)

    # Close the file.
    file.close()


def write_xy_data(data, file=None, graph_type=None, norm=False):
    """Write the data into the Grace xy-scatter plot.

    The numerical data should be supplied as a 4 dimensional list or array object.  The first dimension corresponds to the graphs, Gx.  The second corresponds the sets of each graph, Sx.  The third corresponds to the data series (i.e. each data point).  The forth is a list of the information about each point, it is a list where the first element is the x value, the second is the y value, the third is the optional dx or dy error (either dx or dy dependent upon the graph_type arg), and the forth is the optional dy error when graph_type is xydxdy (the third position is then dx).


    @param data:            The 4D structure of numerical data to graph (see docstring).
    @type data:             list of lists of lists of float
    @keyword file:          The file object to write the data to.
    @type file:             file object
    @keyword graph_type:    The graph type which can be one of xy, xydy, xydx, or xydxdy.
    @type graph_type:       str
    @keyword norm:          The normalisation flag which if set to True will cause all graphs to be normalised to 1.
    @type norm:             bool
    """

    # Loop over the graphs.
    for gi in range(len(data)):
        # Loop over the data sets of the graph.
        for si in range(len(data[gi])):
            # The target and type.
            file.write("@target G%s.S%s\n" % (gi, si))
            file.write("@type %s\n" % graph_type)
    
            # Normalisation (to the first data point y value!).
            norm_fact = 1.0
            if norm:
                norm_fact = data[gi][si][0][1]
    
            # Loop over the data points.
            for point in data[gi][si]:
                # X and Y data.
                file.write("%-30s %-30s" % (point[0], point[1]/norm_fact))

                # The dx and dy errors.
                if graph_type in ['xydx', 'xydy']:
                    # Catch x or y-axis errors of None.
                    error = point[2]
                    if error == None:
                        error = 0.0
    
                    # Write the error.
                    file.write(" %-30s" % (error/norm_fact))
    
                # The dy errors of xydxdy.
                if graph_type == 'xydxdy':
                    # Catch y-axis errors of None.
                    error = point[3]
                    if error == None:
                        error = 0.0
    
                    # Write the error.
                    file.write(" %-30s" % (error/norm_fact))
    
                # End the point.
                file.write("\n")

            # End of the data set i.
            file.write("&\n")


def write_xy_header(file=None, sets=1, set_names=None, data_type=[None, None], seq_type=[None, None], axis_labels=[None, None], axis_min=[None, None], axis_max=[None, None], norm=False):
    """Write the grace header for xy-scatter plots.

    Many of these keyword arguments should be supplied in a [X, Y] list format, where the first element corresponds to the X data, and the second the Y data.  Defaults will be used for any non-supplied args (or lists with elements set to None).


    @keyword file:                  The file object to write the data to.
    @type file:                     file object
    @keyword sets:                  The number of data sets in the graph G0.
    @type sets:                     int
    @keyword set_names:             The names associated with each graph data set G0.Sx.  For example this can be a list of spin identification strings.
    @type set_names:                list of str
    @keyword data_type:             The axis data category (in the [X, Y] list format).
    @type data_type:                list of str
    @keyword seq_type:              The sequence data type (in the [X, Y] list format).  This is for molecular sequence specific data and can be one of 'res', 'spin', or 'mixed'.
    @type seq_type:                 list of str
    @keyword axis_labels:           The labels for the axes (in the [X, Y] list format).
    @type axis_labels:              list of str
    @keyword axis_min:              The minimum values for specifying the graph ranges (in the [X, Y] list format).
    @type axis_min:                 list of str
    @keyword axis_max:              The maximum values for specifying the graph ranges (in the [X, Y] list format).
    @type axis_max:                 list of str
    @keyword norm:                  The normalisation flag which if set to True will cause all graphs to be normalised to 1.
    @type norm:                     bool
    """

    # Graph G0.
    file.write("@with g0\n")

    # Axis specific settings.
    axes = ['x', 'y']
    for i in range(2):
        # Analysis specific methods for making labels.
        analysis_spec = False
        if pipes.cdp_name():
            # Flag for making labels.
            analysis_spec = True

            # Specific value and error, conversion factor, and units returning functions.
            return_units = get_specific_fn('return_units', pipes.get_type())
            return_grace_string = get_specific_fn('return_grace_string', pipes.get_type())

            # Test if the axis data type is a minimisation statistic.
            if data_type[i] != 'spin' and generic_fns.minimise.return_data_name(data_type[i]):
                return_units = generic_fns.minimise.return_units
                return_grace_string = generic_fns.minimise.return_grace_string

        # Some axis default values for spin data.
        if data_type[i] == 'spin':
            # Residue only data.
            if seq_type[i] == 'res':
                # Axis limits.
                if not axis_min[i]:
                    axis_min[i] = repr(cdp.mol[0].res[0].num - 1)
                if not axis_max[i]:
                    axis_max[i] = repr(cdp.mol[0].res[-1].num + 1)

                # X-axis label.
                if not axis_labels[i]:
                    axis_labels[i] = "Residue number"

            # Spin only data.
            if seq_type[i] == 'spin':
                # Axis limits.
                if not axis_min[i]:
                    axis_min[i] = repr(cdp.mol[0].res[0].spin[0].num - 1)
                if not axis_max[i]:
                    axis_max[i] = repr(cdp.mol[0].res[0].spin[-1].num + 1)

                # X-axis label.
                if not axis_labels[i]:
                    axis_labels[i] = "Spin number"

            # Mixed data.
            if seq_type[i] == 'mixed':
                # X-axis label.
                if not axis_labels[i]:
                    axis_labels[i] = "Spin identification string"

        # Some axis default values for other data types.
        else:
            # Label.
            if analysis_spec and not axis_labels[i]:
                # Get the units.
                units = return_units(data_type[i])

                # Set the label.
                axis_labels[i] = return_grace_string(data_type[i])

                # Add units.
                if units:
                    axis_labels[i] = axis_labels[i] + "\\N (" + units + ")"

                # Normalised data.
                if norm:
                    axis_labels[i] = axis_labels[i] + " \\N\\q(normalised)\\Q"

        # Write out the data.
        if axis_min[i]:
            file.write("@    world %smin %s\n" % (axes[i], axis_min[i]))
        if axis_max[i]:
            file.write("@    world %smin %s\n" % (axes[i], axis_max[i]))
        if axis_labels[i]:
            file.write("@    %saxis  label \"%s\"\n" % (axes[i], axis_labels[i]))
        file.write("@    %saxis  label char size 1.48\n" % axes[i])
        file.write("@    %saxis  tick major size 0.75\n" % axes[i])
        file.write("@    %saxis  tick major linewidth 0.5\n" % axes[i])
        file.write("@    %saxis  tick minor linewidth 0.5\n" % axes[i])
        file.write("@    %saxis  tick minor size 0.45\n" % axes[i])
        file.write("@    %saxis  ticklabel char size 1.00\n" % axes[i])

    # Legend box.
    file.write("@    legend off\n")

    # Frame.
    file.write("@    frame linewidth 0.5\n")

    # Loop over each graph set.
    for i in range(sets):
        # Symbols.
        file.write("@    s%i symbol %i\n" % (i, i+1))
        file.write("@    s%i symbol size 0.45\n" % i)
        file.write("@    s%i symbol fill pattern 1\n" % i)
        file.write("@    s%i symbol linewidth 0.5\n" % i)
        file.write("@    s%i line linestyle 0\n" % i)

        # Error bars.
        file.write("@    s%i errorbar size 0.5\n" % i)
        file.write("@    s%i errorbar linewidth 0.5\n" % i)
        file.write("@    s%i errorbar riser linewidth 0.5\n" % i)

        # Legend.
        if set_names:
            file.write("@    s%i legend \"Spin %s\"\n" % (i, set_names[i]))
