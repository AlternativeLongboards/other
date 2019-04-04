from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.text import Label as ButtonText
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.text import Label as CoreLabel
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.clock import Clock
import math
import serial
import time
from pymongo import MongoClient
import datetime
import threading
import socket
import json
from datetime import datetime

f = open("press.log", 'a')

MasterModule = serial.Serial('/dev/ttyACM0', 115200)
time.sleep(2)

MasterModule.write("AE".encode('utf-8'))
MasterModule.flush()
time.sleep(1)
if (MasterModule.inWaiting() > 0):
    MasterModule.read(MasterModule.inWaiting())
    MasterModule.flush()
time.sleep(1)

client = MongoClient('mongodb://192.168.1.200:27017/')
print('conneted to mongodb')

db = client['production']
molds = db['molds']

message = ""
readData = ""

inp = [0, 0, 0, 0, 0, 0]
rel = [0, 0, 0, 0, 0, 0, 0]
how_many_press = [0,0,0,0,0,0]
trigger = [0, 0, 0, 0, 0, 0]

total_left = [0,0,0,0,0,0]
is_opening = [0,0,0,0,0,0]
opening_stage = [0,0,0,0,0,0]
some_shit = 0

set_pressing_time = 7200			# pressing time in [s]

Builder.load_string("""

<MainWindow>:
    BoxLayout:
        canvas.before:
            Color:
                rgba: 1,1,1, .80
            Rectangle:
                pos: root.pos
                size: root.size
        orientation: 'vertical'
        color: (1,1,1,0)
        orientation: 'vertical'
        BoxLayout:
            orientation: 'vertical'
            BoxLayout:
                canvas.before:
                    Color:
                        rgba: 0,0,0, 0.75
                    Rectangle:
                        pos: self.pos
                        size: self.size
                orientation: 'horizontal'
                size_hint: 1, .18
                Label:
                    text: '[b]PRESS SYSTEM[b]'                                                                     # tu zmienic !!!
                    markup: 'True'
                    font_size: self.parent.width/20
                Label:
                    size_hint: 0.3 , 1
                Image:
                    source: 'logo.png'
                    size_hint: 0.5 , 1
                Label:
                    size_hint: .1, 1
            BoxLayout:
                orientation: 'horizontal'
                BoxLayout:
                    orientation: 'vertical'
                    Label:
                        size_hint: 1, .1
                    BoxLayout:
                        orientation: 'horizontal'
    #-----------------------------------------------------------------------------------------------------------------------
                        BoxLayout:
                            orientation: 'vertical'
                            Label:
                                text: '[b]PRESS 1[b]'
                                color: 0, 0, 0, 1
                                font_size: self.parent.width/7
                                text_size: self.size
                                halign: 'center'
                                markup: 'True'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'MOLD:'
#                                    color: 0, 0, 0, .6
#                                    font_size: self.parent.width/13
#                                    text_size: self.size
#                                    halign: 'right'
                                Label:
                                    id: press_1_mold_label
                                    text: 'NONE'
                                    color: 0, 0, 0, .5
                                    font_size: self.parent.width/10
                                    text_size: self.size
                                    halign: 'center'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'STATUS:'
#                                    color: 0, 0, 0, 1
#                                    font_size: self.parent.width/13
#                                    text_size: self.size
#                                    halign: 'right'
                                Label:
                                    id: press_1_state_label
                                    text: 'CLOSE'
                                    color: 0, 0, 0, 1
                                    font_size: self.parent.width/10
                                    text_size: self.size
                                    halign: 'center'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'TIME LEFT:'
#                                    color: 0, 0, 0, 1
#                                    font_size: self.parent.width/10
#                                    halign: 'right'
#                                    text_size: self.size
                                Label:
                                    id: press_1_time_label
                                    text: '02:00:00'
                                    color: 1, 0, 0, 1
                                    font_size: self.parent.width/8
                                    text_size: self.size
                                    halign: 'center'
    #-----------------------------------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------
                        BoxLayout:
                            orientation: 'vertical'
                            Label:
                                text: '[b]PRESS 2[b]'
                                color: 0, 0, 0, 1
                                font_size: self.parent.width/7
                                text_size: self.size
                                halign: 'center'
                                markup: 'True'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'MOLD:'
#                                    color: 0, 0, 0, .6
#                                    font_size: self.parent.width/10
#                                    text_size: self.size
#                                    halign: 'right'
                                Label:
                                    id: press_2_mold_label
                                    text: 'NONE'
                                    color: 0, 0, 0, .5
                                    font_size: self.parent.width/10
                                    text_size: self.size
                                    halign: 'center'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'STATUS:'
#                                    color: 0, 0, 0, 1
#                                    font_size: self.parent.width/10
#                                    text_size: self.size
#                                    halign: 'right'
                                Label:
                                    id: press_2_state_label
                                    text: 'CLOSE'
                                    color: 0, 0, 0, 1
                                    font_size: self.parent.width/10
                                    text_size: self.size
                                    halign: 'center'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'TIME LEFT:'
#                                    color: 0, 0, 0, 1
#                                    font_size: self.parent.width/10
#                                    halign: 'right'
#                                    text_size: self.size
                                Label:
                                    id: press_2_time_label
                                    text: '02:00:00'
                                    color: 1, 0, 0, 1
                                    font_size: self.parent.width/8
                                    text_size: self.size
                                    halign: 'center'
    #-----------------------------------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------
                        BoxLayout:
                            orientation: 'vertical'
                            Label:
                                text: '[b]PRESS 3[b]'
                                color: 0, 0, 0, 1
                                font_size: self.parent.width/7
                                text_size: self.size
                                halign: 'center'
                                markup: 'True'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'MOLD:'
#                                    color: 0, 0, 0, .6
#                                    font_size: self.parent.width/10
#                                    text_size: self.size
#                                    halign: 'right'
                                Label:
                                    id: press_3_mold_label
                                    text: 'NONE'
                                    color: 0, 0, 0, .5
                                    font_size: self.parent.width/10
                                    text_size: self.size
                                    halign: 'center'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'STATUS:'
#                                    color: 0, 0, 0, 1
#                                    font_size: self.parent.width/10
#                                    text_size: self.size
#                                    halign: 'right'
                                Label:
                                    id: press_3_state_label
                                    text: 'CLOSE'
                                    color: 0, 0, 0, 1
                                    font_size: self.parent.width/10
                                    text_size: self.size
                                    halign: 'center'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'TIME LEFT:'
#                                    color: 0, 0, 0, 1
#                                    font_size: self.parent.width/10
#                                    halign: 'right'
#                                    text_size: self.size
                                Label:
                                    id: press_3_time_label
                                    text: '02:00:00'
                                    color: 1, 0, 0, 1
                                    font_size: self.parent.width/8
                                    text_size: self.size
                                    halign: 'center'
    #-----------------------------------------------------------------------------------------------------------------------
                    BoxLayout:
                        size_hint: 1,.2
                        Label:

                    BoxLayout:
                        orientation: 'horizontal'
    #-----------------------------------------------------------------------------------------------------------------------
                        BoxLayout:
                            orientation: 'vertical'
                            Label:
                                text: '[b]PRESS 4[b]'
                                color: 0, 0, 0, 1
                                font_size: self.parent.width/7
                                text_size: self.size
                                halign: 'center'
                                markup: 'True'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'MOLD:'
#                                    color: 0, 0, 0, .6
#                                    font_size: self.parent.width/10
#                                    text_size: self.size
#                                    halign: 'right'
                                Label:
                                    id: press_4_mold_label
                                    text: 'NONE'
                                    color: 0, 0, 0, .5
                                    font_size: self.parent.width/10
                                    text_size: self.size
                                    halign: 'center'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                   text: 'STATUS:'
#                                    color: 0, 0, 0, 1
#                                    font_size: self.parent.width/10
#                                    text_size: self.size
#                                    halign: 'right'
                                Label:
                                    id: press_4_state_label
                                    text: 'CLOSE'
                                    color: 0, 0, 0, 1
                                    font_size: self.parent.width/10
                                    text_size: self.size
                                    halign: 'center'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'TIME LEFT:'
#                                    color: 0, 0, 0, 1
#                                    font_size: self.parent.width/10
#                                    halign: 'right'
#                                    text_size: self.size
                                Label:
                                    id: press_4_time_label
                                    text: '02:00:00'
                                    color: 1, 0, 0, 1
                                    font_size: self.parent.width/8
                                    text_size: self.size
                                    halign: 'center'
    #-----------------------------------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------
                        BoxLayout:
                            orientation: 'vertical'
                            Label:
                                text: '[b]PRESS 5[b]'
                                color: 0, 0, 0, 1
                                font_size: self.parent.width/7
                                text_size: self.size
                                halign: 'center'
                                markup: 'True'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'MOLD:'
#                                    color: 0, 0, 0, .6
#                                    font_size: self.parent.width/10
#                                    text_size: self.size
#                                    halign: 'right'
                                Label:
                                    id: press_5_mold_label
                                    text: 'NONE'
                                    color: 0, 0, 0, .5
                                    font_size: self.parent.width/10
                                    text_size: self.size
                                    halign: 'center'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'STATUS:'
#                                    color: 0, 0, 0, 1
#                                   font_size: self.parent.width/10
#                                    text_size: self.size
#                                    halign: 'right'
                                Label:
                                    id: press_5_state_label
                                    text: 'CLOSE'
                                    color: 0, 0, 0, 1
                                    font_size: self.parent.width/10
                                    text_size: self.size
                                    halign: 'center'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'TIME LEFT:'
#                                    color: 0, 0, 0, 1
#                                    font_size: self.parent.width/10
#                                    halign: 'right'
#                                    text_size: self.size
                                Label:
                                    id: press_5_time_label
                                    text: '02:00:00'
                                    color: 1, 0, 0, 1
                                    font_size: self.parent.width/8
                                    text_size: self.size
                                    halign: 'center'
    #-----------------------------------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------
                        BoxLayout:
                            orientation: 'vertical'
                            Label:
                                text: '[b]PRESS 6[b]'
                                color: 0, 0, 0, 1
                                font_size: self.parent.width/7
                                text_size: self.size
                                halign: 'center'
                                markup: 'True'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'MOLD:'
#                                    color: 0, 0, 0, .6
#                                    font_size: self.parent.width/10
#                                    text_size: self.size
#                                    halign: 'right'
                                Label:
                                    id: press_6_mold_label
                                    text: 'FLAMINGO'
                                    color: 0, 0, 0, .5
                                    font_size: self.parent.width/10
                                    text_size: self.size
                                    halign: 'center'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'STATUS:'
#                                    color: 0, 0, 0, 1
#                                    font_size: self.parent.width/10
#                                    text_size: self.size
#                                    halign: 'right'
                                Label:
                                    id: press_6_state_label
                                    text: 'CLOSE'
                                    color: 0, 0, 0, 1
                                    font_size: self.parent.width/10
                                    text_size: self.size
                                    halign: 'center'
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1, 1
#                                Label:
#                                    text: 'TIME LEFT:'
#                                    color: 0, 0, 0, 1
#                                    font_size: self.parent.width/10
#                                    halign: 'right'
#                                    text_size: self.size
                                Label:
                                    id: press_6_time_label
                                    text: '02:00:00'
                                    color: 1, 0, 0, 1
                                    font_size: self.parent.width/8
                                    text_size: self.size
                                    halign: 'center'
    #-----------------------------------------------------------------------------------------------------------------------
                    Label:
                        size_hint: 1, .15
                    BoxLayout:
                        size_hint: 1,.4
                        orientation: 'horizontal'
                        Label:
                            size_hint: .075, 1
                        Button:
                            size_hint: .475,1
                            text: 'EXIT'
                            background_color: 0, .6156, .48235, 1
                            background_normal: ''
                            font_size: self.parent.width/40
                            on_press: dupa
                        Label:
                            size_hint: .05, 1
                        Button:
                            size_hint: .475,1
                            text: 'SYS INFO'
                            font_size: self.parent.width/40
                            on_press: root.show_info()
                        Label:
                            size_hint: .05, 1
                        Button:
                            size_hint: .475,1
                            text: 'SWITCHGEAR'
                            font_size: self.parent.width/40
                            on_press: root.show_prod()
                        BoxLayout:
                            orientation: 'vertical'
                            Label:
                                id: system_status
                                text: 'STEADY'
                                color: 0, .6156, .48235, 1
                                font_size: self.parent.width/8
                            Label:
                                size_hint: 1,.1

                    Label:
                        size_hint: 1, .075

<SysInfo>:
    size_hint: 0.6, 1
    title_align: 'center'
    title: 'MODULES STATUS'
    BoxLayout:
        orientation: 'horizontal'
        BoxLayout:
            orientation: 'vertical'
            Label:
                text: 'INP12CH 1:'
            Label:
                text: 'INP12CH 2:'
            Label:
                text: 'INP12CH 3:'
            Label:
                text: 'INP12CH 4:'
            Label:
                text: 'INP12CH 5:'
            Label:
                text: 'INP12CH 6:'
            Label:
                text: 'REL6CH 1:'
            Label:
                text: 'REL6CH 2:'
            Label:
                text: 'REL6CH 3:'
            Label:
                text: 'REL6CH 4:'
            Label:
                text: 'REL6CH 5:'
            Label:
                text: 'REL6CH 6:'
            Label:
                text: 'SWITCHGEAR:'
            Label:
                text: 'PUMP:'
        BoxLayout:
            orientation: 'vertical'
            Label:
                id: INP12CH_1
            Label:
                id: INP12CH_2
            Label:
                id: INP12CH_3
            Label:
                id: INP12CH_4
            Label:
                id: INP12CH_5
            Label:
                id: INP12CH_6
            Label:
                id: REL6CH_1
                text: 'NOT PRESENT'
            Label:
                id: REL6CH_2
            Label:
                id: REL6CH_3
            Label:
                id: REL6CH_4
            Label:
                id: REL6CH_5
            Label:
                id: REL6CH_6
            Label:
                id: REL6CH_switchgear
            Label:
                id: REL6CH_pump

<Production>:
    size_hint: 0.6, 1
    title_align: 'center'
    title: 'BOARD PRESSED SINCE SYSTEM BOOT'
    BoxLayout:
        orientation: 'horizontal'
        BoxLayout:
            orientation: 'vertical'
            Label:
                text: 'PRESS 1:'
            Label:
                text: 'PRESS 2:'
            Label:
                text: 'PRESS 3:'
            Label:
                text: 'PRESS 4:'
            Label:
                text: 'PRESS 5:'
            Label:
                text: 'PRESS 6:'
            Label:
                text: 'TOTAL:'
                color: 1,0,0,1
        BoxLayout:
            orientation: 'vertical'
            Label:
                id: count_1
            Label:
                id: count_2
            Label:
                id: count_3
            Label:
                id: count_4
            Label:
                id: count_5
            Label:
                id: count_6
            Label:
                id: count_total
                color: 1,0,0,1


""")

class Production(Popup):

    def __init__(self, **kwargs):
        super(Production,self).__init__(**kwargs)
        self.count_it()

    def count_it(self,*args):

        global how_many_press

        c_1 = self.ids['count_1']
        c_2 = self.ids['count_2']
        c_3 = self.ids['count_3']
        c_4 = self.ids['count_4']
        c_5 = self.ids['count_5']
        c_6 = self.ids['count_6']
        c_total = self.ids['count_total']

        c_1.text = str(how_many_press[0])
        c_2.text = str(how_many_press[1])
        c_3.text = str(how_many_press[2])
        c_4.text = str(how_many_press[3])
        c_5.text = str(how_many_press[4])
        c_6.text = str(how_many_press[5])

        to = 0
        for each in how_many_press:
            to = each + to

        c_total.text = str(to)

class SysInfo(Popup):

    def __init__(self,**kwargs):
        super(SysInfo, self).__init__(**kwargs)
        self.label_handle()

    def label_handle(self,*args):

        global inp

        INP12_1 = self.ids['INP12CH_1']
        INP12_2 = self.ids['INP12CH_2']
        INP12_3 = self.ids['INP12CH_3']
        INP12_4 = self.ids['INP12CH_4']
        INP12_5 = self.ids['INP12CH_5']
        INP12_6 = self.ids['INP12CH_6']

        REL6_1 = self.ids['REL6CH_1']
        REL6_2 = self.ids['REL6CH_2']
        REL6_3 = self.ids['REL6CH_3']
        REL6_4 = self.ids['REL6CH_4']
        REL6_5 = self.ids['REL6CH_5']
        REL6_6 = self.ids['REL6CH_6']

        REL6CH_switchgear = self.ids['REL6CH_switchgear']
        REL6CH_pump = self.ids['REL6CH_pump']

        if (inp[0] > 0):
            INP12_1.text = "GOOD"
            INP12_1.color = [0, .6156, .48235, 1]
        if (inp[0] == 0):
            INP12_1.text = "BAD"
            INP12_1.color = [1, 0, 0, 1]

        if (inp[1] > 0):
            INP12_2.text = "GOOD"
            INP12_2.color = [0, .6156, .48235, 1]
        if (inp[1] == 0):
            INP12_2.text = "BAD"
            INP12_2.color = [1, 0, 0, 1]

        if (inp[2] > 0):
            INP12_3.text = "GOOD"
            INP12_3.color = [0, .6156, .48235, 1]
        if (inp[2] == 0):
            INP12_3.text = "BAD"
            INP12_3.color = [1, 0, 0, 1]

        if (inp[3] > 0):
            INP12_4.text = "GOOD"
            INP12_4.color = [0, .6156, .48235, 1]
        if (inp[3] == 0):
            INP12_4.text = "BAD"
            INP12_4.color = [1, 0, 0, 1]

        if (inp[4] > 0):
            INP12_5.text = "GOOD"
            INP12_5.color = [0, .6156, .48235, 1]
        if (inp[4] == 0):
            INP12_5.text = "BAD"
            INP12_5.color = [1, 0, 0, 1]

        if (inp[5] > 0):
            INP12_6.text = "GOOD"
            INP12_6.color = [0, .6156, .48235, 1]
        if (inp[5] == 0):
            INP12_6.text = "BAD"
            INP12_6.color = [1, 0, 0, 1]

        if (rel[0] > 0):
            REL6CH_switchgear.text = "GOOD"
            REL6CH_switchgear.color = [0, .6156, .48235, 1]
        if (rel[0] == 0):
            REL6CH_switchgear.text = "BAD"
            REL6CH_switchgear.color = [1, 0, 0, 1]

        if (rel[1] > 0):
            REL6CH_pump.text = "GOOD"
            REL6CH_pump.color = [0, .6156, .48235, 1]
        if (rel[1] == 0):
            REL6CH_pump.text = "BAD"
            REL6CH_pump.color = [1, 0, 0, 1]

        if (rel[2] > 0):
            REL6_2.text = "GOOD"
            REL6_2.color = [0, .6156, .48235, 1]
        if (rel[2] == 0):
            REL6_2.text = "BAD"
            REL6_2.color = [1, 0, 0, 1]

        if (rel[3] > 0):
            REL6_3.text = "GOOD"
            REL6_3.color = [0, .6156, .48235, 1]
        if (rel[3] == 0):
            REL6_3.text = "BAD"
            REL6_3.color = [1, 0, 0, 1]

        if (rel[4] > 0):
            REL6_4.text = "GOOD"
            REL6_4.color = [0, .6156, .48235, 1]
        if (rel[4] == 0):
            REL6_4.text = "BAD"
            REL6_4.color = [1, 0, 0, 1]

        if (rel[5] > 0):
            REL6_5.text = "GOOD"
            REL6_5.color = [0, .6156, .48235, 1]
        if (rel[5] == 0):
            REL6_5.text = "BAD"
            REL6_5.color = [1, 0, 0, 1]

        if (rel[6] > 0):
            REL6_6.text = "GOOD"
            REL6_6.color = [0, .6156, .48235, 1]
        if (rel[6] == 0):
            REL6_6.text = "BAD"
            REL6_6.color = [1, 0, 0, 1]

class MainWindow(Screen):

    def __init__(self, **kwargs):
        super(MainWindow,self).__init__(**kwargs)
        Clock.schedule_interval(self.mold_label, 300)
        Clock.schedule_interval(self.ask_data,0.5)
        Clock.schedule_interval(self.opening, 1)
        self.mold_label()

    def mold_label(self,*args):

        molds_name = ["OSTRICH","","JUNKO","CHAUMA","","BUNTING","WROBEL","FLAMINGO","","FANTAIL","VERDIN","STARLING","ERGET"]

        mold_label_1 = self.ids['press_1_mold_label']
        mold_label_2 = self.ids['press_2_mold_label']
        mold_label_3 = self.ids['press_3_mold_label']
        mold_label_4 = self.ids['press_4_mold_label']
        mold_label_5 = self.ids['press_5_mold_label']
        mold_label_6 = self.ids['press_6_mold_label']

        m = [0,0,0,0,0,0,0]
        labels = [mold_label_1,mold_label_2,mold_label_3,mold_label_4,mold_label_5,mold_label_6]
        search_result = []
        for each in search_result:
            try:
                m[0] = each['mold01']
            except:
                try:
                    m[1] = each['mold02']
                except:
                    try:
                        m[2] = each['mold03']
                    except:
                        try:
                            m[3] = each['mold04']
                        except:
                            try:
                                m[4] = each['mold05']
                            except:
                                try:
                                    m[5] = each['mold06']
                                except:
                                    pass
        for each in labels:
            each.text = str( molds_name[int(m[labels.index(each)])] )

    def ask_data(self,*args):

        global readData
        global how_many_press
        global total_left
        global is_opening
        global opening_stage
        global some_shit

        state_label_1 = self.ids['press_1_state_label']
        state_label_2 = self.ids['press_2_state_label']
        state_label_3 = self.ids['press_3_state_label']
        state_label_4 = self.ids['press_4_state_label']
        state_label_5 = self.ids['press_5_state_label']
        state_label_6 = self.ids['press_6_state_label']

        time_label_1 = self.ids['press_1_time_label']
        time_label_2 = self.ids['press_2_time_label']
        time_label_3 = self.ids['press_3_time_label']
        time_label_4 = self.ids['press_4_time_label']
        time_label_5 = self.ids['press_5_time_label']
        time_label_6 = self.ids['press_6_time_label']

        switchgear_label = self.ids['system_status']
        switchgear_status = 0
        press_1_status = 0
        press_2_status = 0
        press_3_status = 0
        press_4_status = 0
        press_5_status = 0
        press_6_status = 0
        press_1_time = 0
        press_2_time = 0
        press_3_time = 0
        press_4_time = 0
        press_5_time = 0
        press_6_time = 0
        variable = 0

        sec = 0
        str_sec = ""
        min = 0
        str_min = ""
        hour = 0
        str_hour = ""
        time_lab = ""


        press_state = ["READY", "CLOSING", "OPENING", "PRESSING","OPEN"]
        switchgear_state = ["NONE", "PRESS 1", "PRESS 2", "PRESS 3", "PRESS 4", "PRESS 5", "PRESS 6", "SWITCHING"]
        readData = ""
        self.serial_clear()
        self.serial_write('AE')
        time.sleep(0.1)
        readData = self.serial_read().decode()
        if "S0A0Z0B0Y0C0X0D0W0E0V0F0U0L" in readData:
            to_print = "good"
        else:
            to_print = readData
        str_to_log = str(datetime.now().strftime("%H:%M:%S"))+" "+str(to_print)+"\n"
        f.write(str_to_log)
        f.flush()
        if (readData != ""):

            variable = int(readData.index("S"))
            switchgear_status = int(readData[variable+1:variable+2])
            switchgear_label.text = switchgear_state[switchgear_status]

            variable = int(readData.index("A"))
            press_1_status = int(readData[variable+1:variable+2])
            state_label_1.text = press_state[press_1_status]
            if (press_1_status == 0):
                state_label_1.color = [0,0,0,1]
                if (trigger[0] == 1):
                    trigger[0] = 2
                else:
                    trigger[0] = 0
            elif (press_1_status == 1):
                state_label_1.color = [1,0,0,1]
                if (trigger[0] == 1):
                    trigger[0] = 2
                else:
                    trigger[0] = 0
            elif (press_1_status == 2):
                state_label_1.color = [0, .6156, .48235, 1]
                if (trigger[0] == 1):
                    trigger[0] = 2
                else:
                    trigger[0] = 0
            elif (press_1_status == 3):
                state_label_1.color = [0,0,1,1]
                if (trigger[0] == 1):
                    trigger[0] = 2
                else:
                    trigger[0] = 0
            elif (press_1_status == 4):
                state_label_1.color = [1,1,1,1]

            variable = int(readData.index("B"))
            press_2_status = int(readData[variable+1:variable+2])
            state_label_2.text = press_state[press_2_status]
            if (some_shit == 2):
                state_label_2.text = "AUTO"
                state_label_2.color = [0,0,0,1]
            if (press_2_status == 0):
                state_label_2.color = [0,0,0,1]
                if (trigger[1] == 1):
                    trigger[1] = 2
                else:
                    trigger[1] = 0
            elif (press_2_status == 1):
                state_label_2.color = [1,0,0,1]
                if (trigger[1] == 1):
                    trigger[1] = 2
                else:
                    trigger[1] = 0
            elif (press_2_status == 2):
                state_label_2.color = [0, .6156, .48235, 1]
                if (trigger[1] == 1):
                    trigger[1] = 2
                else:
                    trigger[1] = 0
            elif (press_2_status == 3):
                state_label_2.color = [0,0,1,1]
                if (trigger[1] == 1):
                    trigger[1] = 2
                else:
                    trigger[1] = 0
            elif (press_2_status == 4):
                state_label_2.color = [1,1,1,1]
                if (opening_stage[1] > 35 and opening_stage[1] < 41):
                    opening_stage[1] = opening_stage[1] + 1

            variable = int(readData.index("C"))
            press_3_status = int(readData[variable+1:variable+2])
            state_label_3.text = press_state[press_3_status]
            if (some_shit == 3):
                state_label_3.text = "AUTO"
                state_label_3.color = [0,0,0,1]
            if (press_3_status == 0):
                state_label_3.color = [0,0,0,1]
                if (trigger[2] == 1):
                    trigger[2] = 2
                else:
                    trigger[2] = 0
            elif (press_3_status == 1):
                state_label_3.color = [1,0,0,1]
                if (trigger[2] == 1):
                    trigger[2] = 2
                else:
                    trigger[2] = 0
            elif (press_3_status == 2):
                state_label_3.color = [0, .6156, .48235, 1]
                if (trigger[2] == 1):
                    trigger[2] = 2
                else:
                    trigger[2] = 0
            elif (press_3_status == 3):
                state_label_3.color = [0,0,1,1]
                if (trigger[2] == 1):
                    trigger[2] = 2
                else:
                    trigger[2] = 0
            elif (press_3_status == 4):
                state_label_3.color = [1,1,1,1]
                if (opening_stage[2] > 35 and opening_stage[2] < 41):
                    opening_stage[2] = opening_stage[2] + 1

            variable = int(readData.index("D"))
            press_4_status = int(readData[variable+1:variable+2])
            state_label_4.text = press_state[press_4_status]
            if (some_shit == 4):
                state_label_4.text = "AUTO"
                state_label_4.color = [0,0,0,1]
            if (press_4_status == 0):
                state_label_4.color = [0,0,0,1]
                if (trigger[3] == 1):
                    trigger[3] = 2
                else:
                    trigger[3] = 0
            elif (press_4_status == 1):
                state_label_4.color = [1,0,0,1]
                if (trigger[3] == 1):
                    trigger[3] = 2
                else:
                    trigger[3] = 0
            elif (press_4_status == 2):
                state_label_4.color = [0, .6156, .48235, 1]
                if (trigger[3] == 1):
                    trigger[3] = 2
                else:
                    trigger[3] = 0
            elif (press_4_status == 3):
                state_label_4.color = [0,0,1,1]
                if (trigger[3] == 1):
                    trigger[3] = 2
                else:
                    trigger[3] = 0
            elif (press_4_status == 4):
                state_label_4.color = [1,1,1,1]
                if (opening_stage[3] > 35 and opening_stage[3] < 41):
                    opening_stage[3] = opening_stage[3] + 1

            variable = int(readData.index("E"))
            press_5_status = int(readData[variable+1:variable+2])
            state_label_5.text = press_state[press_5_status]
            if (some_shit == 5):
                state_label_5.text = "AUTO"
                state_label_5.color = [0,0,0,1]
            if (press_5_status == 0):
                state_label_5.color = [0,0,0,1]
                if (trigger[4] == 1):
                    trigger[4] = 2
                else:
                    trigger[4] = 0
            elif (press_5_status == 1):
                state_label_5.color = [1,0,0,1]
                if (trigger[4] == 1):
                    trigger[4] = 2
                else:
                    trigger[4] = 0
            elif (press_5_status == 2):
                state_label_5.color = [0, .6156, .48235, 1]
                if (trigger[4] == 1):
                    trigger[4] = 2
                else:
                    trigger[4] = 0
            elif (press_5_status == 3):
                state_label_5.color = [0,0,1,1]
                if (trigger[4] == 1):
                    trigger[4] = 2
                else:
                    trigger[4] = 0
            elif (press_5_status == 4):
                state_label_5.color = [1,1,1,1]
                if (opening_stage[4] > 35 and opening_stage[4] < 41):
                    opening_stage[4] = opening_stage[4] + 1

            variable = int(readData.index("F"))
            press_6_status = int(readData[variable+1:variable+2])
            state_label_6.text = press_state[press_6_status]
            if (some_shit == 6):
                state_label_6.text = "AUTO"
                state_label_6.color = [0,0,0,1]
            if (press_6_status == 0):
                state_label_6.color = [0,0,0,1]
                if (trigger[5] == 1):
                    trigger[5] = 2
                else:
                    trigger[5] = 0
            elif (press_6_status == 1):
                state_label_6.color = [1,0,0,1]
                if (trigger[5] == 1):
                    trigger[5] = 2
                else:
                    trigger[5] = 0
            elif (press_6_status == 2):
                state_label_6.color = [0, .6156, .48235, 1]
                if (trigger[5] == 1):
                    trigger[5] = 2
                else:
                    trigger[5] = 0
            elif (press_6_status == 3):
                state_label_6.color = [0,0,1,1]
                if (trigger[5] == 1):
                    trigger[5] = 2
                else:
                    trigger[5] = 0
            elif (press_6_status == 4):
                state_label_6.color = [1,1,1,1]
                if (opening_stage[5] > 35 and opening_stage[5] < 41):
                    opening_stage[5] = opening_stage[5] + 1

            variable = int(readData.index("Z"))
            variable2 = int(readData.index("B"))
            press_1_time = int(readData[variable+1:variable2])
            total_left[0] = set_pressing_time - press_1_time
            if (press_1_time > (set_pressing_time - 5)):
                if (trigger[0] == 0):
                    how_many_press[0] = how_many_press[0] + 1
                    trigger[0] = 1
            hour = math.trunc(total_left[0] / 3600)
            min = math.trunc((total_left[0] - (3600*hour))/60)
            sec = total_left[0] - hour*3600 - 60*min
            if (hour < 0):
                hour = 0
            if (min < 0):
                min = 0
            if (sec <0):
                sec = 0
            str_hour = str(hour)
            if (min < 10):
                str_min = "0"+str(min)
            elif (min >=10):
                str_min = str(min)
            if (sec < 10):
                str_sec = "0"+str(sec)
            elif (sec >=10):
                str_sec = str(sec)
            if (total_left[0] > 0):
                time_lab = "0"+str_hour+":"+str_min+":"+str_sec
            else:
                time_lab = "00:00:00"
                is_opening[0] = 1
            time_label_1.text = time_lab

            variable = int(readData.index("Y"))
            variable2 = int(readData.index("C"))
            press_2_time = int(readData[variable+1:variable2])
            total_left[1] = set_pressing_time - press_2_time
            if (press_2_time > (set_pressing_time - 5)):
                if (trigger[1] == 0):
                    how_many_press[1] = how_many_press[1] + 1
                    trigger[1] = 1
            hour = math.trunc(total_left[1] / 3600)
            min = math.trunc((total_left[1] - (3600*hour))/60)
            sec = total_left[1] - hour*3600 - 60*min
            if (hour < 0):
                hour = 0
            if (min < 0):
                min = 0
            if (sec <0):
                sec = 0
            str_hour = str(hour)
            if (min < 10):
                str_min = "0"+str(min)
            elif (min >=10):
                str_min = str(min)
            if (sec < 10):
                str_sec = "0"+str(sec)
            elif (sec >=10):
                str_sec = str(sec)
            if (total_left[1] > 0):
                time_lab = "0"+str_hour+":"+str_min+":"+str_sec
            else:
                time_lab = "00:00:00"
                is_opening[1] = 1
            time_label_2.text = time_lab

            variable = int(readData.index("X"))
            variable2 = int(readData.index("D"))
            press_3_time = int(readData[variable+1:variable2])
            total_left[2] = set_pressing_time - press_3_time
            if (press_3_time > (set_pressing_time -5)):
                if (trigger[2] == 0):
                    how_many_press[2] = how_many_press[2] + 1
                    trigger[2] = 1
            hour = math.trunc(total_left[2] / 3600)
            min = math.trunc((total_left[2] - (3600*hour))/60)
            sec = total_left[2] - hour*3600 - 60*min
            if (hour < 0):
                hour = 0
            if (min < 0):
                min = 0
            if (sec <0):
                sec = 0
            str_hour = str(hour)
            if (min < 10):
                str_min = "0"+str(min)
            elif (min >=10):
                str_min = str(min)
            if (sec < 10):
                str_sec = "0"+str(sec)
            elif (sec >=10):
                str_sec = str(sec)
            if (total_left[2] >0):
                time_lab = "0"+str_hour+":"+str_min+":"+str_sec
            else:
                time_lab = "00:00:00"
                is_opening[2] = 1
            time_label_3.text = time_lab

            variable = int(readData.index("W"))
            variable2 = int(readData.index("E"))
            press_4_time = int(readData[variable+1:variable2])
            total_left[3] = set_pressing_time - press_4_time
            if (press_4_time > (set_pressing_time -5)):
                if (trigger[3] == 0):
                    how_many_press[3] = how_many_press[3] + 1
                    trigger[3] = 1
            hour = math.trunc(total_left[3] / 3600)
            min = math.trunc((total_left[3] - (3600*hour))/60)
            sec = total_left[3] - hour*3600 - 60*min
            if (hour < 0):
                hour = 0
            if (min < 0):
                min = 0
            if (sec <0):
                sec = 0
            str_hour = str(hour)
            if (min < 10):
                str_min = "0"+str(min)
            elif (min >=10):
                str_min = str(min)
            if (sec < 10):
                str_sec = "0"+str(sec)
            elif (sec >=10):
                str_sec = str(sec)
            if (total_left[3] > 0):
                time_lab = "0"+str_hour+":"+str_min+":"+str_sec
            else:
                time_lab = "00:00:00"
                is_opening[3] = 1
            time_label_4.text = time_lab

            variable = int(readData.index("V"))
            variable2 = int(readData.index("F"))
            press_5_time = int(readData[variable+1:variable2])
            total_left[4] = set_pressing_time - press_5_time
            if (press_5_time > (set_pressing_time - 5)):
                if (trigger[4] == 0):
                    how_many_press[4] = how_many_press[4] + 1
                    trigger[4] = 1
            hour = math.trunc(total_left[4] / 3600)
            min = math.trunc((total_left[4] - (3600*hour))/60)
            sec = total_left[4] - hour*3600 - 60*min
            if (hour < 0):
                hour = 0
            if (min < 0):
                min = 0
            if (sec <0):
                sec = 0
            str_hour = str(hour)
            if (min < 10):
                str_min = "0"+str(min)
            elif (min >=10):
                str_min = str(min)
            if (sec < 10):
                str_sec = "0"+str(sec)
            elif (sec >=10):
                str_sec = str(sec)
            if (total_left[4] > 0):
                time_lab = "0"+str_hour+":"+str_min+":"+str_sec
            else:
                time_lab = "00:00:00"
                is_opening[4] = 1
            time_label_5.text = time_lab

            variable = int(readData.index("U"))
            variable2 = int(readData.index("L"))
            press_6_time = int(readData[variable+1:variable2])
            total_left[5] = set_pressing_time - press_6_time
            if (press_6_time > (set_pressing_time - 5)):
                if (trigger[5] == 0):
                    how_many_press[5] = how_many_press[5] + 1
                    trigger[5] = 1
            hour = math.trunc(total_left[5] / 3600)
            min = math.trunc((total_left[5] - (3600*hour))/60)
            sec = total_left[5] - hour*3600 - 60*min
            if (hour < 0):
                hour = 0
            if (min < 0):
                min = 0
            if (sec <0):
                sec = 0
            str_hour = str(hour)
            if (min < 10):
                str_min = "0"+str(min)
            elif (min >=10):
                str_min = str(min)
            if (sec < 10):
                str_sec = "0"+str(sec)
            elif (sec >=10):
                str_sec = str(sec)
            if (total_left[5] > 0):
                time_lab = "0"+str_hour+":"+str_min+":"+str_sec
            else:
                time_lab = "00:00:00"
                is_opening[5] = 1
            time_label_6.text = time_lab
        else:
            switchgear_label.text = "COMM ERROR"

    def message_read(self, *args):

        global message

        try:
            message = s.recv(512)
            message = message.decode('utf-8')
            message = str(message)
        except:
            pass

    def opening(self, *args):

        global is_opening
        global opening_stage
        global some_shit

        if ( some_shit == 0):
            if (is_opening[1] == 1):
                some_shit = 2
            elif (is_opening[2] == 1):
                some_shit = 3
            elif (is_opening[3] == 1):
                some_shit = 4
            elif (is_opening[4] == 1):
                some_shit = 5
            elif (is_opening[5] == 1):
                some_shit = 6

        if ( some_shit == 2 ):
            if (opening_stage[1] == 0):
                self.serial_write('Z02')
                opening_stage[1] = 1
            if (opening_stage[1] == 1):
                self.serial_write('R02')
                opening_stage[1] = 2
            if (opening_stage[1] > 1 and opening_stage[1] < 31):
                opening_stage[1] = opening_stage[1] + 1
            if (opening_stage[1] == 31):
                self.serial_write('A02')
                opening_stage[1] = 32
            if (opening_stage[1] > 31 and opening_stage[1] < 37):
                opening_stage[1] = opening_stage[1] + 1
            if (opening_stage[1] == 36):
                self.serial_write('B02')
            if (opening_stage[1] == 41):
                self.serial_write('Z01')
                opening_stage[1] = 0
                is_opening[1] = 0
                some_shit = 0


        if ( some_shit == 3 ):
            if (opening_stage[2] == 0):
                self.serial_write('Z02')
                opening_stage[2] = 1
            if (opening_stage[2] == 1):
                self.serial_write('R03')
                opening_stage[2] = 2
            if (opening_stage[2] > 1 and opening_stage[2] < 31):
                opening_stage[2] = opening_stage[2] + 1
            if (opening_stage[2] == 31):
                self.serial_write('A03')
                opening_stage[2] = 32
            if (opening_stage[2] > 31 and opening_stage[2] < 37):
                opening_stage[2] = opening_stage[2] + 1
            if (opening_stage[2] == 36):
                self.serial_write('B02')
            if (opening_stage[2] == 41):
                self.serial_write('Z01')
                opening_stage[2] = 0
                is_opening[2] = 0
                some_shit = 0

        if ( some_shit == 4 ):
            if (opening_stage[3] == 0):
                self.serial_write('Z02')
                opening_stage[3] = 1
            if (opening_stage[3] == 1):
                self.serial_write('R04')
                opening_stage[3] = 2
            if (opening_stage[3] > 1 and opening_stage[3] < 31):
                opening_stage[3] = opening_stage[3] + 1
            if (opening_stage[3] == 31):
                self.serial_write('A04')
                opening_stage[3] = 32
            if (opening_stage[3] > 31 and opening_stage[3] < 37):
                opening_stage[3] = opening_stage[3] + 1
            if (opening_stage[3] == 36):
                self.serial_write('B02')
            if (opening_stage[3] == 41):
                self.serial_write('Z01')
                opening_stage[3] = 0
                is_opening[3] = 0
                some_shit = 0

        if ( some_shit == 5 ):
            if (opening_stage[4] == 0):
                self.serial_write('Z02')
                opening_stage[4] = 1
            if (opening_stage[4] == 1):
                self.serial_write('R05')
                opening_stage[4] = 2
            if (opening_stage[4] > 1 and opening_stage[4] < 31):
                opening_stage[4] = opening_stage[4] + 1
            if (opening_stage[4] == 31):
                self.serial_write('A05')
                opening_stage[4] = 32
            if (opening_stage[4] > 31 and opening_stage[4] < 37):
                opening_stage[4] = opening_stage[4] + 1
            if (opening_stage[4] == 36):
                self.serial_write('B02')
            if (opening_stage[4] == 41):
                self.serial_write('Z01')
                opening_stage[4] = 0
                is_opening[4] = 0
                some_shit = 0

        if ( some_shit == 6 ):
            if (opening_stage[5] == 0):
                self.serial_write('Z02')
                opening_stage[5] = 1
            if (opening_stage[5] == 1):
                self.serial_write('R06')
                opening_stage[5] = 2
            if (opening_stage[5] > 1 and opening_stage[5] < 31):
                opening_stage[5] = opening_stage[5] + 1
            if (opening_stage[5] == 31):
                self.serial_write('A06')
                opening_stage[5] = 32
            if (opening_stage[5] > 31 and opening_stage[5] < 37):
                opening_stage[5] = opening_stage[5] + 1
            if (opening_stage[5] == 36):
                self.serial_write('B02')
            if (opening_stage[5] == 41):
                self.serial_write('Z01')
                opening_stage[5] = 0
                is_opening[5] = 0
                some_shit = 0


    def serial_write(self,data_to_send):
        MasterModule.write(str(data_to_send).encode('utf-8'))
        MasterModule.flush()
        time.sleep(0.01)

    def serial_clear(self):
        if (MasterModule.inWaiting() > 0):
            MasterModule.read(MasterModule.inWaiting())
            MasterModule.flush()

    def serial_read(self):
        myData = MasterModule.read(MasterModule.inWaiting())
        return myData

    def show_info(self, *args):

        global int
        global rel
        data = ""

        inp_read = 0
        rel_read = 0
        self.serial_clear()
        self.serial_write('ST')
        time.sleep(0.1)
        data = self.serial_read().decode()
        print("sys info is: ", data)

        if (data != ""):
            variable = int(data.index("I"))
            variable2 = int(data.index("R"))
            variable3 = int(data.index("L"))
            inp_read = int(data[variable+1:variable2])
            rel_read = int(data[variable2+1:variable3])
        a = 0
        while (a < 6):
            inp[a] = inp_read % 2
            inp_read = math.trunc(inp_read/2)
            a = a + 1

        a = 0
        while (a < 7):
            rel[a] = rel_read % 2
            rel_read = math.trunc(rel_read/2)
            a = a + 1

        SysInfo().open()

    def show_prod(self,*args):

#        Production().open()
        global total_left
        
        if (sum(total_left) == 43200):
            self.serial_write('Z02')
            time.sleep(0.5)
            self.serial_write('B00')
            time.sleep(0.5)
            self.serial_write('C00')
            time.sleep(1)
            repeat_t = 5
            wait_time = 0.5
            for i in range(1,7):
                for each in range(0,repeat_t):
                    message = "C0"+str(i)
                    self.serial_write(message)
                    time.sleep(wait_time)
                    self.serial_write('C00')
                    time.sleep(wait_time)
            self.serial_write('Z01')

class ScanApp(App):

    def build(self):
        return MainWindow()


if __name__ == '__main__':
    ScanApp().run()
