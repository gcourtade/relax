# Script for optimising the rigid frame order test model of CaM.

# Python module imports.
from numpy import array, float64, transpose, zeros
from os import sep

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from maths_fns.rotation_matrix import euler_to_R_zyz
from status import Status; status = Status()


# Some variables.
BASE_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'+sep
DATA_PATH = BASE_PATH + 'rigid'


class Analysis:
    def __init__(self, exec_fn):
        """Execute the frame order analysis."""

        # Alias the user function executor method.
        self._execute_uf = exec_fn

        # Optimise.
        self.optimisation()

        # Load the original structure.
        self.original_structure()

        # Domain transformation.
        self.transform()

        # Display in pymol.
        self.pymol_display()

        # Save the state.
        state.save('devnull', force=True)


    def optimisation(self):
        """Optimise the frame order model."""

        # Create the data pipe.
        self._execute_uf(uf_name='pipe.create', pipe_name='frame order', pipe_type='frame order')

        # Read the structures.
        structure.read_pdb('1J7O_1st_NH.pdb', dir=BASE_PATH, set_mol_name='N-dom')
        structure.read_pdb('1J7P_1st_NH_rot.pdb', dir=BASE_PATH, set_mol_name='C-dom')

        # Load the spins.
        structure.load_spins('@N')
        structure.load_spins('@H')

        # Load the NH vectors.
        structure.vectors(spin_id='@N', attached='H', ave=False)

        # Set the values needed to calculate the dipolar constant.
        value.set(1.041 * 1e-10, 'r', spin_id="@N")
        value.set('15N', 'heteronuc_type', spin_id="@N")
        value.set('1H', 'proton_type', spin_id="@N")

        # Loop over the alignments.
        ln = ['dy', 'tb', 'tm', 'er']
        for i in range(len(ln)):
            # Load the RDCs.
            if ds.flag_rdc:
                rdc.read(align_id=ln[i], file='rdc_%s.txt'%ln[i], dir=DATA_PATH, res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

            # The PCS.
            if ds.flag_pcs:
                pcs.read(align_id=ln[i], file='pcs_%s.txt'%ln[i], dir=DATA_PATH, res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

            # The temperature and field strength.
            temperature(id=ln[i], temp=303)
            frq.set(id=ln[i], frq=900e6)

        # Load the N-domain tensors (the full tensors).
        script(BASE_PATH + 'tensors.py')

        # Define the domains.
        domain(id='N', spin_id=":1-78")
        domain(id='C', spin_id=":80-148")

        # The tensor domains and reductions.
        full = ['Dy N-dom', 'Tb N-dom', 'Tm N-dom', 'Er N-dom']
        red =  ['Dy C-dom', 'Tb C-dom', 'Tm C-dom', 'Er C-dom']
        for i in range(len(full)):
            # Initialise the reduced tensor.
            align_tensor.init(tensor=red[i], params=(0,0,0,0,0))

            # Set the domain info.
            align_tensor.set_domain(tensor=full[i], domain='N')
            align_tensor.set_domain(tensor=red[i], domain='C')

            # Specify which tensor is reduced.
            align_tensor.reduction(full_tensor=full[i], red_tensor=red[i])

        # Select the model.
        self._execute_uf(uf_name='frame_order.select_model', model='rigid')

        # Set the reference domain.
        self._execute_uf(uf_name='frame_order.ref_domain', ref='N')

        # Set the initial pivot point.
        pivot = array([ 37.254, 0.5, 16.7465])
        frame_order.pivot(pivot, fix=True)

        # Set the paramagnetic centre.
        paramag.centre(pos=[35.934, 12.194, -4.206])

        # Check the minimum.
        value.set(val=4.3434999280669997, param='ave_pos_alpha')
        value.set(val=0.43544332764249905, param='ave_pos_beta')
        value.set(val=3.8013235235956007, param='ave_pos_gamma')
        calc()
        print("\nchi2: %s" % cdp.chi2)

        # Optimise.
        if ds.flag_opt:
            grid_search(inc=11)
            minimise('simplex', constraints=False)

            # Test Monte Carlo simulations.
            monte_carlo.setup(number=3)
            monte_carlo.create_data()
            monte_carlo.initial_values()
            minimise('simplex', constraints=False)
            eliminate()
            monte_carlo.error_analysis()

        # Write the results.
        self._execute_uf(uf_name='results.write', file='devnull', dir=None, force=True)


    def original_structure(self):
        """Load the original structure into a dedicated data pipe."""

        # Create a special data pipe for the original rigid body position.
        self._execute_uf(uf_name='pipe.create', pipe_name='orig pos', pipe_type='frame order')

        # Load the structure.
        structure.read_pdb('1J7P_1st_NH_rot.pdb', dir=BASE_PATH)


    def pymol_display(self):
        """Display the results in PyMOL."""

        # Switch back to the main data pipe.
        pipe.switch('frame order')

        # Load the PDBs of the 2 domains.
        structure.read_pdb('1J7O_1st_NH.pdb', dir='..')
        structure.read_pdb('1J7P_1st_NH_rot.pdb', dir='..')

        # Create the cone PDB file.
        #frame_order.cone_pdb(file='cone.pdb', force=True)

        # Set the domains.
        frame_order.domain_to_pdb(domain='N', pdb='1J7O_1st_NH.pdb')
        frame_order.domain_to_pdb(domain='C', pdb='1J7P_1st_NH_rot.pdb')



    def transform(self):
        """Transform the domain to the average position."""

        # Switch back to the main data pipe.
        pipe.switch('frame order')

        # The rotation matrix.
        R = zeros((3, 3), float64)
        euler_to_R_zyz(cdp.ave_pos_alpha, cdp.ave_pos_beta, cdp.ave_pos_gamma, R)
        print("Rotation matrix:\n%s\n" % R)
        R = transpose(R)
        print("Inverted rotation:\n%s\n" % R)
        pivot = cdp.pivot

        # Create a special data pipe for the average rigid body position.
        self._execute_uf(uf_name='pipe.create', pipe_name='ave pos', pipe_type='frame order')

        # Load the structure.
        structure.read_pdb('1J7P_1st_NH_rot.pdb', dir=BASE_PATH)

        # Rotate all atoms.
        self._execute_uf(uf_name='structure.rotate', R=R, origin=pivot)

        # Write out the new PDB.
        self._execute_uf(uf_name='structure.write_pdb', file='devnull')


# Execute the analysis.
Analysis(self._execute_uf)
