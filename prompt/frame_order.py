###############################################################################
#                                                                             #
# Copyright (C) 2009-2010 Edward d'Auvergne                                   #
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
"""Module containing the user function class of the Frame Order theories."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class
import arg_check
from specific_fns.setup import frame_order_obj


class Frame_order(User_fn_class):
    """Class containing the user functions of the Frame Order theories."""

    def cone_pdb(self, size=30.0, inc=40, file='cone.pdb', dir=None, force=False):
        """Create a PDB file representing the Frame Order cone models.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        size:  The size of the geometric object in Angstroms.

        inc:  The number of increments used to create the geometric object.

        file:  The name of the PDB file to create.

        dir:  The directory where the file is to be located.

        force:  A flag which, if set to True, will overwrite the any pre-existing file.


        Description
        ~~~~~~~~~~~

        This function creates a PDB file containing an artificial geometric structure representing
        the Frame Order cone models.

        There are four different types of residue within the PDB.  The pivot point is represented as
        as a single carbon atom of the residue 'PIV'.  The cone consists of numerous H atoms of the
        residue 'CON'.  The cone axis vector is presented as the residue 'AXE' with one carbon atom
        positioned at the pivot and the other x Angstroms away on the cone axis (set by the size
        argument).  Finally, if Monte Carlo have been performed, there will be multiple 'MCC'
        residues representing the cone for each simulation, and multiple 'MCA' residues representing
        the multiple cone axes.

        To create the diffusion in a cone PDB representation, a uniform distribution of vectors on a
        sphere is generated using spherical coordinates with the polar angle defined by the cone
        axis.  By incrementing the polar angle using an arccos distribution, a radial array of
        vectors representing latitude are created while incrementing the azimuthal angle evenly
        creates the longitudinal vectors.  These are all placed into the PDB file as H atoms and are
        all connected using PDB CONECT records.  Each H atom is connected to its two neighbours on
        the both the longitude and latitude.  This creates a geometric PDB object with longitudinal
        and latitudinal lines representing the filled cone.
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "frame_order.cone_pdb("
            text = text + "size=" + repr(size)
            text = text + ", inc=" + repr(inc)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_num(size, 'geometric object size')
        arg_check.is_int(inc, 'increment number')
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        frame_order_obj._cone_pdb(size=size, inc=inc, file=file, dir=dir, force=force)


    def domain_to_pdb(self, domain=None, pdb=None):
        """Match the domains to PDB files.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        domain:  The domain to associate the PDB file to.

        pdb:  The PDB file to associate the domain to.


        Description
        ~~~~~~~~~~~

        To display the frame order cone models within Pymol, the two domains need to be associated
        with PDB files.  Then the reference domain will be fixed in the PDB frame, and the moving
        domain will be rotated to its average position.


        Examples
        ~~~~~~~~

        To set the 'N' domain to the PDB file 'bax_N_1J7O_1st.pdb', type one of:

        relax> frame_order.domain_to_pdb('N', 'bax_N_1J7O_1st.pdb')
        relax> frame_order.domain_to_pdb(domain='N', pdb='bax_N_1J7O_1st.pdb')
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "frame_order.domain_to_pdb("
            text = text + "domain=" + repr(domain)
            text = text + ", pdb=" + repr(pdb) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(domain, 'domain')
        arg_check.is_str(pdb, 'PDB file')

        # Execute the functional code.
        frame_order_obj._domain_to_pdb(domain=domain, pdb=pdb)


    def pivot(self, pivot=None, fix=False):
        """Set the pivot point for the two body motion in the structural coordinate system.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pivot:  The pivot point for the motion (e.g. the position between the 2 domains in PDB
            coordinates).

        fix:  A flag specifying if the pivot point should be fixed during optimisation.


        Examples
        ~~~~~~~~

        To set the pivot point, type one of:

        relax> frame_order.pivot([12.067, 14.313, -3.2675])
        relax> frame_order.pivot(pivot=[12.067, 14.313, -3.2675])
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "frame_order.pivot("
            text = text + "pivot=" + repr(pivot)
            text = text + ", fix=" + repr(fix) + ")"
            print(text)

        # The argument checks.
        arg_check.is_num_list(pivot, 'pivot point', size=3)
        arg_check.is_bool(fix, 'fix flag')

        # Execute the functional code.
        frame_order_obj._pivot(pivot=pivot, fix=fix)


    def ref_domain(self, ref=None):
        """Set the reference domain for the '2-domain' Frame Order theories.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        ref:  The domain which will act as the frame of reference.  This is only valid for the
        '2-domain' Frame Order theories.


        Description
        ~~~~~~~~~~~

        Prior to optimisation of the '2-domain' Frame Order theories, which of the two domains will
        act as the frame of reference must be specified.  This is important for the attachment of
        cones to domains, etc.


        Examples
        ~~~~~~~~

        To set up the isotropic cone frame order model with 'centre' domain being the frame of reference, type:

        relax> frame_order.ref_domain(ref='centre')
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "frame_order.ref_domain("
            text = text + "ref=" + repr(ref) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(ref, 'reference frame')

        # Execute the functional code.
        frame_order_obj._ref_domain(ref=ref)


    def select_model(self, model=None):
        """Select and set up the Frame Order model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the preset Frame Order model.


        Description
        ~~~~~~~~~~~

        Prior to optimisation, the Frame Order model should be selected.  These models consist of
        three parameter categories:

            - The average domain position.  This includes the parameters ave_pos_alpha,
            ave_pos_beta, and ave_pos_gamma.  These Euler angles rotate the tensors from the
            arbitrary PDB frame of the moving domain to the average domain position.

            - The frame order eigenframe.  This includes the parameters eigen_alpha, eigen_beta, and
            eigen_gamma.  These Euler angles define the major modes of motion.  The cone central
            axis is defined as the z-axis.  The pseudo-elliptic cone x and y-axes are defined as the
            x and y-axes of the eigenframe.

            - The cone parameters.  These are defined as the tilt-torsion angles cone_theta_x,
            cone_theta_y, and cone_sigma_max.  The cone_theta_x and cone_theta_y parameters define
            the two cone opening angles of the pseudo-ellipse.  The amount of domain torsion is
            defined as the average domain position, plus and minus cone_sigma_max.  The isotropic
            cones are defined by setting cone_theta_x = cone_theta_y and converting the single
            parameter into a 2nd rank order parameter.

        The list of available models are:

            'pseudo-ellipse' - The pseudo-elliptic cone model.  This is the full model consisting of
            the parameters ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta,
            eigen_gamma, cone_theta_x, cone_theta_y, and cone_sigma_max.

            'pseudo-ellipse, torsionless' - The pseudo-elliptic cone with the torsion angle
            cone_sigma_max set to zero.

            'pseudo-ellipse, free rotor' - The pseudo-elliptic cone with no torsion angle
            restriction.

            'iso cone' - The isotropic cone model.  The cone is defined by a single order parameter
            s1 which is related to the single cone opening angle cone_theta_x = cone_theta_y.  Due
            to rotational symmetry about the cone axis, the average position alpha Euler angle
            ave_pos_alpha is dropped from the model.  The symmetry also collapses the eigenframe to
            a single z-axis defined by the parameters axis_theta and axis_phi.

            'iso cone, torsionless' - The isotropic cone model with the torsion angle cone_sigma_max
            set to zero.

            'iso cone, free rotor' - The isotropic cone model with no torsion angle restriction.

            'line' - The line cone model.  This is the pseudo-elliptic cone with one of the cone
            angles, cone_theta_y, assumed to be statistically negligible.  I.e. the cone angle is
            so small that it cannot be distinguished from noise.

            'line, torsionless' - The line cone model with the torsion angle cone_sigma_max set to
            zero.

            'line, free rotor' - The line cone model with no torsion angle restriction.

            'rotor' - The only motion is a rotation about the cone axis restricted by the torsion
            angle cone_sigma_max.

            'rigid' - No domain motions.

            'free rotor' - The only motion is free rotation about the cone axis.


        Examples
        ~~~~~~~~

        To select the isotropic cone model, type:

        relax> frame_order.select_model(model='iso cone')
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "frame_order.select_model("
            text = text + "model=" + repr(model) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(model, 'Frame Order model')

        # Execute the functional code.
        frame_order_obj._select_model(model=model)
