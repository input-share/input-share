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
    WM_MBUTTONDOWN, WM_MBUTTONUP, WM_MBUTTONDBLCLK, WM_MOUSEWHEEL

from gen import messages_pb2

'''
msg_to_name = {WM_MOUSEMOVE : 'mouse move', WM_LBUTTONDOWN : 'mouse left down',
                 WM_LBUTTONUP : 'mouse left up', WM_LBUTTONDBLCLK : 'mouse left double',
                 WM_RBUTTONDOWN : 'mouse right down', WM_RBUTTONUP : 'mouse right up',
                 WM_RBUTTONDBLCLK : 'mouse right double',  WM_MBUTTONDOWN : 'mouse middle down',
                 WM_MBUTTONUP : 'mouse middle up', WM_MBUTTONDBLCLK : 'mouse middle double',
                 WM_MOUSEWHEEL : 'mouse wheel',  WM_KEYDOWN : 'key down',
                 WM_KEYUP : 'key up', WM_CHAR : 'key char', WM_DEADCHAR : 'key dead char',
                 WM_SYSKEYDOWN : 'key sys down', WM_SYSKEYUP : 'key sys up',
                 WM_SYSCHAR : 'key sys char', WM_SYSDEADCHAR : 'key sys dead char'}
'''

class Echo(basic.Int32StringReceiver):
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
    }
    
    def __init__(self):
        self.hook_manager = pyHook.HookManager()
        self.hook_manager.MouseAll = self.onMouseEvent
        self.hook_manager.KeyAll = self.onKeyboardEvent
        self.hook_manager.HookMouse()
        self.hook_manager.HookKeyboard()
        
    def stringReceived(self, data):
        stdout.write(data)
         
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
        ke.text = event.GetKey() + ' ' + event.GetMessageName()
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
