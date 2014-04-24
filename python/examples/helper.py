# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# helper.py
# Copyright (C) 2014 Fracpete (fracpete at gmail dot com)

import os


def get_data_dir():
    """
    Returns the data directory.
    :rtype: str
    """
    rootdir = os.path.split(os.path.dirname(__file__))[0]
    if os.path.exists(rootdir + os.sep + "data"):
        libdir = rootdir + os.sep + "data"
    else:
        libdir = os.path.split(rootdir)[0] + os.sep + "data"
    return libdir


def print_title(title):
    """
    Prints the title underlined.
    :param title: the title to print
    """

    print("\n" + title)
    print("=" * len(title))


def print_info(info):
    """
    Prints the info.
    :param info: the info to print
    """

    print("\n" + info)
