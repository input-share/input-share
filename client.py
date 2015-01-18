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

from sys import stdout
from threading import Thread

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ReconnectingClientFactory
import pyHook, pythoncom
from twisted.internet.task import LoopingCall



class Echo(Protocol):
    def __init__(self):
        self.hook_manager = pyHook.HookManager()
        self.hook_manager.MouseAll = self.onMouseEvent
        self.hook_manager.KeyAll = self.onKeyboardEvent
        self.hook_manager.HookMouse()
        self.hook_manager.HookKeyboard()
        
    def dataReceived(self, data):
        stdout.write(data)
         
    def onMouseEvent(self, event):
        #print event.Position
        self.transport.write(str(event.Position) + ' ' + event.GetMessageName() + '\r\n')
        return True
    
    def onKeyboardEvent(self, event):
        self.transport.write(event.GetKey() + ' ' + event.GetMessageName() + '\r\n')
        return True
    
    def pumpMessages(self):
        pythoncom.PumpWaitingMessages() #@UndefinedVariable

class ShareClientFactory(ReconnectingClientFactory):
    def startedConnecting(self, connector):
        print 'Started to connect.'
        
    def buildProtocol(self, addr):
        print 'Connected.'
        print 'Resetting reconnection delay'
        self.resetDelay()
        p = Echo()
        lc = LoopingCall(p.pumpMessages)
        lc.start(0.01)
        return p
        
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason: ', reason
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        
    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason: ', reason
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason) 

reactor.connectTCP('localhost', 1020, ShareClientFactory()) #@UndefinedVariable
reactor.run() #@UndefinedVariable
