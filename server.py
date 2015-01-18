# This Python file uses the following encoding: utf-8

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

from twisted.protocols import basic
from twisted.internet import protocol, endpoints, reactor

from gen import messages_pb2

class PubProtocol(basic.Int32StringReceiver):
    def __init__(self, factory):
        self.factory = factory
        
    def connectionMade(self):
        self.factory.clients.add(self)
        
    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        
    def stringReceived(self, string):
        print " ".join("{:02x}".format(ord(c)) for c in string)
        event = messages_pb2.Event()
        event.ParseFromString(string)
        for c in self.factory.clients:
                c.sendString("<{}> {}".format(self.transport.getHandle().getpeername(), str(event)))

class PubFactory(protocol.Factory):
    def __init__(self):
        self.clients = set()
        
    def buildProtocol(self, addr):
        return PubProtocol(self)

endpoints.serverFromString(reactor, "tcp:1020").listen(PubFactory())
reactor.run() #@UndefinedVariable