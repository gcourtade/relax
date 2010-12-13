###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
"""Module for the main relax menu bar."""

# Python module imports.
import wx

# relax GUI module imports.
from gui_bieri import paths


class Menu:
    """The menu bar GUI class."""

    def __init__(self, gui):
        """Build the menu bar."""

        # Store the args.
        self.gui = gui

        # Create the menu bar GUI item and add it to the main frame.
        self.menubar = wx.MenuBar()
        self.gui.SetMenuBar(self.menubar)

        # The 'File' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_item(menu, id=0, text="&New\tCtrl+N", icon=paths.icon_16x16.new))
        menu.AppendItem(self.build_menu_item(menu, id=1, text="&Open\tCtrl+O", icon=paths.icon_16x16.open))
        menu.AppendSeparator()
        menu.AppendItem(self.build_menu_item(menu, id=2, text="S&ave\tCtrl+S", icon=paths.icon_16x16.save))
        menu.AppendItem(self.build_menu_item(menu, id=3, text="Save as...\tCtrl+Shift+S", icon=paths.icon_16x16.save_as))
        menu.AppendSeparator()
        menu.AppendItem(self.build_menu_item(menu, id=4, text="E&xit\tCtrl+Q", icon=paths.icon_16x16.exit))
        self.menubar.Append(menu, "&File")

        # The 'File' menu actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.newGUI,     id=0)
        self.gui.Bind(wx.EVT_MENU, self.gui.state_load, id=1)
        self.gui.Bind(wx.EVT_MENU, self.gui.action_state_save, id=2)
        self.gui.Bind(wx.EVT_MENU, self.gui.action_state_save_as, id=3)
        self.gui.Bind(wx.EVT_MENU, self.gui.exit_gui,   id=4)

        # The 'View' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_item(menu, id=50, text="&Controller\tCtrl+Z", icon=paths.icon_16x16.controller))
        menu.AppendItem(self.build_menu_item(menu, id=51, text="relax &prompt\tCtrl+P", icon=paths.icon_16x16.relax_prompt))
        menu.AppendItem(self.build_menu_item(menu, id=52, text="&Spin view\tCtrl+T", icon=paths.icon_16x16.spin))
        self.menubar.Append(menu, "&View")

        # The 'View' actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.show_controller,    id=50)
        self.gui.Bind(wx.EVT_MENU, self.gui.show_prompt,        id=51)
        self.gui.Bind(wx.EVT_MENU, self.gui.show_tree,          id=52)

        # The 'User functions' menu entries.
        self._user_functions()

        # The 'Molecule' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_item(menu, id=10, text="Load &PDB File", icon=paths.icon_16x16.load))
        menu.AppendItem(self.build_menu_item(menu, id=11, text="Load se&quence file", icon=paths.icon_16x16.load))
        self.menubar.Append(menu, "&Molecule")

        # The 'Molecule' menu actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.structure_pdb,  id=10)
        self.gui.Bind(wx.EVT_MENU, self.gui.import_seq,     id=11)

        # The 'Settings' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_item(menu, id=20, text="&Global relax settings", icon=paths.icon_16x16.settings_global))
        menu.AppendItem(self.build_menu_item(menu, id=21, text="&Parameter file settings", icon=paths.icon_16x16.settings))
        menu.AppendItem(self.build_menu_item(menu, id=22, text="Reset a&ll settings", icon=paths.icon_16x16.settings_reset))
        self.menubar.Append(menu, "&Settings")

        # The 'Settings' menu actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.settings,           id=20)
        self.gui.Bind(wx.EVT_MENU, self.gui.param_file_setting, id=21)
        self.gui.Bind(wx.EVT_MENU, self.gui.reset_setting,      id=22)

        # The 'Help' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_item(menu, id=40, text="relax user &manual\tF1", icon=paths.icon_16x16.manual))
        menu.AppendSeparator()
        menu.AppendItem(self.build_menu_item(menu, id=41, text="&Contact relaxGUI (relax-users@gna.org)", icon=paths.icon_16x16.contact))
        menu.AppendItem(self.build_menu_item(menu, id=42, text="&References", icon=paths.icon_16x16.ref))
        menu.AppendSeparator()
        menu.AppendItem(self.build_menu_item(menu, id=43, text="About relaxG&UI", icon=paths.icon_16x16.about_relaxgui))
        menu.AppendItem(self.build_menu_item(menu, id=44, text="About rela&x", icon=paths.icon_16x16.about_relax))
        self.menubar.Append(menu, "&Help")

        # The 'Help' menu actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.relax_manual,   id=40)
        self.gui.Bind(wx.EVT_MENU, self.gui.contact_relax,  id=41)
        self.gui.Bind(wx.EVT_MENU, self.gui.references,     id=42)
        self.gui.Bind(wx.EVT_MENU, self.gui.about_gui,      id=43)
        self.gui.Bind(wx.EVT_MENU, self.gui.about_relax,    id=44)


    def build_menu_item(self, menu, id=None, text='', tooltip='', icon=None):
        """Construct and return the menu sub-item.

        @param menu:        The menu object to place this entry in.
        @type menu:         wx.Menu instance
        @keyword id:        The element identification number.
        @type id:           int
        @keyword text:      The text for the menu entry.
        @type text:         None or str
        @keyword tooltip:   A tool tip.
        @type tooltip:      str
        @keyword icon:      The bitmap icon path.
        @type icon:         None or str
        @return:            The initialised wx.MenuItem() instance.
        @rtype:             wx.MenuItem() instance
        """

        # Initialise the GUI element.
        element = wx.MenuItem(menu, id, text, tooltip)

        # Set the icon.
        if icon:
            element.SetBitmap(wx.Bitmap(icon))

        # Return the element.
        return element


    def _create_menu(self, menu, entries):
        """Build the menu."""

        # Loop over the menu entries.
        for item in entries:
            # Build the menu entry.
            menu_item = self.build_menu_item(menu, id=item[0], text=item[1], icon=item[2])

            # A sub-menu.
            if len(item[4]):
                # The sub-menu.
                sub_menu = wx.Menu()

                # Loop over the sub-menus.
                for sub_item in item[4]:
                    # Build the menu entry.
                    sub_menu_item = self.build_menu_item(sub_menu, id=sub_item[0], text=sub_item[1], icon=sub_item[2])
                    sub_menu.AppendItem(sub_menu_item)

                    # The menu actions.
                    self.gui.Bind(wx.EVT_MENU, sub_item[3], id=sub_item[0])

                # Append the sub-menu.
                menu_item.SetSubMenu(sub_menu)

            # A normal menu item.
            else:
                # The menu actions.
                self.gui.Bind(wx.EVT_MENU, item[3], id=item[0])

            # Append the menu item.
            menu.AppendItem(menu_item)


    def _user_functions(self):
        """Build the user function sub-menu."""

        # Assign the IDs to the 10000 range.
        id_base = 10000

        # The menu.
        menu = wx.Menu()

        # The list of entries to build.
        entries = [
            [id_base + 000, "&molecule", paths.icon_16x16.molecule, None, [
                [id_base + 001, "&add", paths.icon_16x16.add, self.gui.user_functions.molecule.add],
                [id_base + 002, "&delete", paths.icon_16x16.cancel, self.gui.user_functions.molecule.delete]
            ]],
            [id_base + 100, "&pipe", paths.icon_16x16.pipe, None, [
                [id_base + 101, "&create", paths.icon_16x16.add, self.gui.user_functions.pipes.create],
                [id_base + 102, "&delete", paths.icon_16x16.cancel, self.gui.user_functions.pipes.delete]
            ]],
            [id_base + 200, "&script",   paths.icon_16x16.uf_script, self.gui.user_functions.script.run, []],
            [id_base + 100, "&spin", paths.icon_16x16.spin, None, [
                [id_base + 101, "&create", paths.icon_16x16.add, self.gui.user_functions.spin.add],
                [id_base + 102, "&delete", paths.icon_16x16.cancel, self.gui.user_functions.spin.delete]
            ]],
        ]

        # Build.
        self._create_menu(menu, entries)

        # Add the sub-menu.
        self.menubar.Append(menu, "&User functions")
