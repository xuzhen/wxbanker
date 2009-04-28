#    https://launchpad.net/wxbanker
#    localization.py: Copyright 2007, 2008 Mike Rooney <mrooney@ubuntu.com>
#
#    This file is part of wxBanker.
#
#    wxBanker is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    wxBanker is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with wxBanker.  If not, see <http://www.gnu.org/licenses/>.

# Set the default locale.
import locale
locale.setlocale(locale.LC_ALL, '')

# Define the domain and localedir.
import os
APP = 'wxbanker'
# Figure out the directory...
if os.path.exists('/usr/share/locale/es/LC_MESSAGES/wxbanker.mo'):
    DIR = '/usr/share/locale'
elif os.path.exists('/usr/local/share/locale/es/LC_MESSAGES/wxbanker.mo'):
    DIR = '/usr/local/share/locale'
else:
    DIR = os.path.join(os.path.dirname(__file__), 'locale')

# Install gettext.
import gettext
gettext.install(APP, DIR, unicode=True)

# Check if the user forced a language with --lang=XX.
import sys
larg = '--lang='
for arg in sys.argv[1:]:
    if arg.startswith(larg):
        lang = arg[len(larg):]
        trans = gettext.translation(APP, DIR, languages=[lang])
        trans.install()
        break
