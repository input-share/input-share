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

import pyHook, pythoncom

from twisted.protocols import basic
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.internet.task import LoopingCall

from win32con import WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP,\
    WM_LBUTTONDBLCLK, WM_RBUTTONDOWN, WM_RBUTTONUP, WM_RBUTTONDBLCLK,\
    WM_MBUTTONDOWN, WM_MBUTTONUP, WM_MBUTTONDBLCLK, WM_MOUSEWHEEL, WM_KEYDOWN,\
    WM_KEYUP, WM_CHAR, WM_DEADCHAR, WM_SYSKEYDOWN, WM_SYSKEYUP, WM_SYSCHAR,\
    WM_SYSDEADCHAR, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN

from gen import messages_pb2

'''
Protocol handshake process
1. Client sends credentials to server
2. Server validates credentials if correct
3. Client submits desktop screen dimensions
4. Server adds the client screen to its virtual screenspace
5. Server subscribes the client to input updates

 
'''

class Echo(basic.Int16StringReceiver):
    password = 'client'
    
    __event_pb_map = {
        WM_MOUSEMOVE: messages_pb2.MouseEvent.MOUSE_MOVE, #@UndefinedVariable
        WM_LBUTTONDOWN: messages_pb2.MouseEvent.MOUSE_LEFT_DOWN, #@UndefinedVariable
        WM_LBUTTONUP: messages_pb2.MouseEvent.MOUSE_LEFT_UP, #@UndefinedVariable
        WM_LBUTTONDBLCLK: messages_pb2.MouseEvent.MOUSE_LEFT_DOUBLE, #@UndefinedVariable
        WM_RBUTTONDOWN: messages_pb2.MouseEvent.MOUSE_RIGHT_DOWN, #@UndefinedVariable
        WM_RBUTTONUP: messages_pb2.MouseEvent.MOUSE_RIGHT_UP, #@UndefinedVariable
        WM_RBUTTONDBLCLK: messages_pb2.MouseEvent.MOUSE_RIGHT_DOUBLE, #@UndefinedVariable
        WM_MBUTTONDOWN: messages_pb2.MouseEvent.MOUSE_MIDDLE_DOWN, #@UndefinedVariable
        WM_MBUTTONUP: messages_pb2.MouseEvent.MOUSE_MIDDLE_UP, #@UndefinedVariable
        WM_MBUTTONDBLCLK: messages_pb2.MouseEvent.MOUSE_MIDDLE_DOUBLE, #@UndefinedVariable
        WM_MOUSEWHEEL: messages_pb2.MouseEvent.MOUSE_WHEEL, #@UndefinedVariable
        
        WM_KEYDOWN: messages_pb2.KeyEvent.KEY_DOWN, #@UndefinedVariable
        WM_KEYUP: messages_pb2.KeyEvent.KEY_UP, #@UndefinedVariable
        WM_CHAR: messages_pb2.KeyEvent.CHAR, #@UndefinedVariable
        WM_DEADCHAR: messages_pb2.KeyEvent.DEAD_CHAR, #@UndefinedVariable
        WM_SYSKEYDOWN: messages_pb2.KeyEvent.SYS_KEY_DOWN, #@UndefinedVariable
        WM_SYSKEYUP: messages_pb2.KeyEvent.SYS_KEY_UP, #@UndefinedVariable
        WM_SYSCHAR: messages_pb2.KeyEvent.SYS_CHAR, #@UndefinedVariable
        WM_SYSDEADCHAR: messages_pb2.KeyEvent.SYS_DEAD_CHAR, #@UndefinedVariable
    }
    
    def __init__(self):
        self.hook_manager = pyHook.HookManager()
        self.hook_manager.MouseAll = self.onMouseEvent
        self.hook_manager.KeyAll = self.onKeyboardEvent
        self.hook_manager.HookMouse()
        self.hook_manager.HookKeyboard()
        
    def stringReceived(self, data):
        event = messages_pb2.ServerEvent()
        event.ParseFromString(data)
        print " ".join("{:02x}".format(ord(c)) for c in data)
        print event
        if event.HasField('authenticate_response_event'):
            self.onAuthenticateResponse(event.authenticate_response_event)
            return
        if event.HasField('subscribe_screen_response_event'):
            self.onSubscribeScreenResponse(event.subscribe_screen_response_event)
            return
        
    def connectionMade(self):
        self.authenticate()
        
    def authenticate(self):
        evt = messages_pb2.Event()
        evt.authenticate_event.password = self.password
        self.sendString(evt.SerializeToString())
        
    def onAuthenticateResponse(self, event):
        if event.authenticated:
            self.onAuthenticateSuccess(event)
        else:
            self.onAuthenticateFailure(event)
            
    def onAuthenticateSuccess(self, event):
        self.sendSubscribeScreenEvent()
    
    def onAuthenticateFailure(self, event):
        # TODO
        pass
    
    def onSubscribeScreenResponse(self, event):
        pass
    
    def sendSubscribeScreenEvent(self):
        width, height = GetSystemMetrics(SM_CXVIRTUALSCREEN), GetSystemMetrics(SM_CYVIRTUALSCREEN)
        outgoing = messages_pb2.Event()
        outgoing.subscribe_screen_event.width = width
        outgoing.subscribe_screen_event.height = height
        self.sendString(outgoing.SerializeToString())
         
    def onMouseEvent(self, event):
        evt = messages_pb2.Event()
        me = evt.mouse_events.add()
        me.position.x = event.Position[0]
        me.position.y = event.Position[1]
        me.type = self.__event_pb_map.get(event.Message)
        self.sendString(evt.SerializeToString())
        return True
    
    def onKeyboardEvent(self, event):
        evt = messages_pb2.Event()
        ke = evt.key_events.add()
        ke.ascii = event.GetKey().upper()
        ke.type = self.__event_pb_map.get(event.Message)
        self.sendString(evt.SerializeToString())
        return True
    
    def pumpMessages(self):
        pythoncom.PumpWaitingMessages() #@UndefinedVariable

class ShareClientFactory(ReconnectingClientFactory):
    def startedConnecting(self, connector):
        print 'Started to connect.'
        
    def buildProtocol(self, addr):
        print 'Connected.'
        print 'Resetting reconnection delay'
        print ''
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

if __name__ == '__main__':
    from win32api import GetSystemMetrics
    reactor.connectTCP('localhost', 1020, ShareClientFactory()) #@UndefinedVariable
    reactor.run() #@UndefinedVariable
