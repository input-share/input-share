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
from client import Echo
from collections import OrderedDict

class Screen(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

class PubProtocol(basic.Int16StringReceiver):
    def __init__(self, factory):
        self.factory = factory
        
    def connectionLost(self, reason):
        if self in self.factory.clients:
            self.factory.clients.remove(self)
        if self.factory.screens.has_key(self):
            del self.factory.screens[self]
        
    def stringReceived(self, string):
        print " ".join("{:02x}".format(ord(c)) for c in string)
        event = messages_pb2.Event()
        event.ParseFromString(string)
        print event
        if event.HasField('authenticate_event'):
            self.onAuthenticateEvent(event.authenticate_event)
            return
        if event.HasField('subscribe_screen_event'):
            self.onSubscribeScreenEvent(event.subscribe_screen_event)
            
        for c in self.factory.clients:
                pass
                
    def onAuthenticateEvent(self, event):
            if event.password == Echo.password:
                self.onAuthenticationSuccess()
            else:
                self.onAuthenticationFailure()
        
    
    def onAuthenticationSuccess(self):
        self.factory.clients.add(self)
        evt = messages_pb2.ServerEvent()
        evt.authenticate_response_event.authenticated = True
        self.sendString(evt.SerializeToString())
                
    def onAuthenticationFailure(self):
        evt = messages_pb2.ServerEvent()
        evt.authenticate_response_event.authenticated = True
        evt.authenticate_response_event.message = "Password incorrect"
        self.sendString(evt.SerializeToString())
        self.transport.loseConnection()
    
    def onSubscribeScreenEvent(self, event):
        if self not in self.factory.clients:
            response = messages_pb2.ServerEvent()
            response.subscribe_screen_response_event.subscribed = False
            response.subscribe_screen_response_event.message = "Unauthenticated"
            self.sendString(response.SerializeToString())
            return
        screen = Screen(event.width, event.height)
        self.factory.screens[self] = screen
        response = messages_pb2.ServerEvent()
        response.subscribe_screen_response_event.subscribed = True
        self.sendString(response.SerializeToString())
        

class PubFactory(protocol.Factory):
    def __init__(self):
        self.clients = set()
        self.screens = OrderedDict()
        
    def buildProtocol(self, addr):
        return PubProtocol(self)

if __name__ == '__main__':
    endpoints.serverFromString(reactor, "tcp:1020").listen(PubFactory())
    reactor.run() #@UndefinedVariable