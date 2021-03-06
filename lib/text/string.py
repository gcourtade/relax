###############################################################################
#                                                                             #
# Copyright (C) 2010-2012,2019 Edward d'Auvergne                              #
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
"""Module for building documentation."""

# Python module imports.
from copy import deepcopy


# Some constants.
TITLE = 3
SECTION = 2
SUBSECTION = 1
PARAGRAPH = 0
LIST = 10


def human_readable_list(data, conjunction="and"):
    """Convert the list/array object into a human readable list.

    This formats and returns a list, with the last element prefixed with the qualifier.


    @param data:            The list or array object to convert.
    @type data:             list of str
    @keyword conjunction:   The conjunction to add to the list.
    @type conjunction:      str
    @return:                The formatted list.
    @rtype:                 str
    """

    # Avoid modifying the original list.
    new_data = deepcopy(data)

    # Handle an empty list or a single element.
    if len(data) == 0:
        string = ""
    elif len(data) == 1:
        string = data[0]

    # Two elements.
    elif len(data) == 2:
        string = "%s %s %s" % (data[0], conjunction, data[1])

    # Multiple elements.
    else:
        string = "%s" % data[0]
        for i in range(1, len(data) - 1):
            string += ", %s" % data[i]
        string += ", %s %s" % (conjunction, data[-1])

    # Return the formatted list.
    return string


def strip_lead(text):
    """Strip the leading whitespace from the given text.

    @param text:    The text to strip the leading whitespace from.
    @type text:     str
    @return:        The text with leading whitespace removed.
    @rtype:         str
    """

    # Split by newline.
    lines = text.split('\n')

    # Find the minimum whitespace.
    min_white = 1000
    for line in lines:
        # Empty lines.
        if line.strip() == '':
            continue

        # Count the whitespace for the current line.
        num_white = 0
        for i in range(len(line)):
            if line[i] != ' ':
                break
            num_white = num_white + 1

        # The min value.
        min_white = min(min_white, num_white)

    # Strip the whitespace.
    new_text = ''
    for line in lines:
        new_text = new_text + line[min_white:] + '\n'

    # Return the new text.
    return new_text


def to_docstring(data):
    """Convert the text to that of a docstring, dependent on the text level.

    @param data:    The lists of constants and text to convert into a properly formatted docstring.
    @type data:     list of lists of int and str
    """

    # Init.
    doc = ''
    for i in range(len(data)):
        # The level and text.
        level, text = data[i]

        # Title level.
        if level == TITLE:
            doc += text + '\n\n'

        # Section level.
        if level == SECTION:
            doc += '\n\n' + text + '\n' + '='*len(text) + '\n\n'

        # Subsection level.
        if level == SUBSECTION:
            doc += '\n\n' + text + '\n' + '-'*len(text) + '\n\n'

        # Paragraph level.
        elif level == PARAGRAPH:
            # Starting newline.
            if i and data[i-1][0] == PARAGRAPH:
                doc += '\n'

            # The text.
            doc += text + '\n'

        # List level.
        elif level == LIST:
            # Start of list.
            if i and data[i-1][0] != LIST:
                doc += '\n'

            # The text.
            doc += "    - %s\n" % text

            # End of list.
            if i < len(data) and data[i+1][0] == PARAGRAPH:
                doc += '\n'

    # Return the docstring.
    return doc
