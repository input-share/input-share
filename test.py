# This file is part of InputShare
#
# Copyright � 2015 Patrick VanDusen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

if __name__ == '__main__':
    from pymouse import PyMouse
    from pykeyboard import PyKeyboard
    
    m = PyMouse();
    k = PyKeyboard();
    x_dim, y_dim = m.screen_size()
    print (x_dim, y_dim)
    #while True:
    #    x_dim, y_dim = m.position();
    #    print(x_dim, y_dim)
    
    input("Press to continue")