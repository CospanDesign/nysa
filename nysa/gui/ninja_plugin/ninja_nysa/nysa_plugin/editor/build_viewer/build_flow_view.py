# -*- coding: utf-8 *-*

# Distributed under the MIT licesnse.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

'''
Log
  07/20/2013: Initial commit
'''

import os
import sys
import json

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from graphics_view import GraphicsView
from graphics_scene import GraphicsScene
from build_box import BuildBox

from link import side_type as st

from build_status import STATUS as BUILD_STATUS

from defines import GEN_COLOR
from defines import GEN_POS
from defines import GEN_RECT
from defines import GEN_NAME
from defines import GEN_ID
from defines import GEN_DESC

from defines import SYNTHESIZER_COLOR
from defines import SYNTHESIZER_POS
from defines import SYNTHESIZER_RECT
from defines import SYNTHESIZER_NAME
from defines import SYNTHESIZER_ID
from defines import SYNTHESIZER_DESC

from defines import TRANSLATOR_COLOR
from defines import TRANSLATOR_POS
from defines import TRANSLATOR_RECT
from defines import TRANSLATOR_NAME
from defines import TRANSLATOR_ID
from defines import TRANSLATOR_DESC

from defines import MAP_COLOR
from defines import MAP_POS
from defines import MAP_RECT
from defines import MAP_NAME
from defines import MAP_ID
from defines import MAP_DESC

from defines import PAR_COLOR
from defines import PAR_POS
from defines import PAR_RECT
from defines import PAR_NAME
from defines import PAR_ID
from defines import PAR_DESC

from defines import BITGEN_COLOR
from defines import BITGEN_POS
from defines import BITGEN_RECT
from defines import BITGEN_NAME
from defines import BITGEN_ID
from defines import BITGEN_DESC

from defines import TRACE_COLOR
from defines import TRACE_POS
from defines import TRACE_RECT
from defines import TRACE_NAME
from defines import TRACE_ID
from defines import TRACE_DESC

class BuildFlowView(QWidget):
    def __init__(self, builder_view):
        QWidget.__init__(self)
        layout = QHBoxLayout()
        self.buider_viewer = builder_view
        self.view = GraphicsView(self)
        self.scene = GraphicsScene(self.view, builder_view)
        self.view.setScene(self.scene)

        layout.addWidget(self.view)
        self.setLayout(layout)
        self.builders = {}
        self.initialize_view()
        #self.view._scale_fit()
        self.view._scale_view(.5)
        #self.view.update_links()


    def initialize_view(self):
        #Add project generator box
        project_gen = BuildBox(self.scene,
                               GEN_POS,
                               GEN_NAME,
                               GEN_ID,
                               GEN_COLOR,
                               GEN_DESC,
                               GEN_RECT)

        #Add the synthesis box
        synthesis = BuildBox(self.scene,
                             SYNTHESIZER_POS,
                             SYNTHESIZER_NAME,
                             SYNTHESIZER_ID,
                             SYNTHESIZER_COLOR,
                             SYNTHESIZER_DESC,
                             SYNTHESIZER_RECT)

        #Add the translate box
        translate = BuildBox(self.scene,
                             TRANSLATOR_POS,
                             TRANSLATOR_NAME,
                             TRANSLATOR_ID,
                             TRANSLATOR_COLOR,
                             TRANSLATOR_DESC,
                             TRANSLATOR_RECT)
        #Add the map box
        mapper = BuildBox(self.scene,
                          MAP_POS,
                          MAP_NAME,
                          MAP_ID,
                          MAP_COLOR,
                          MAP_DESC,
                          MAP_RECT)

        #Add the par box
        par = BuildBox(self.scene,
                       PAR_POS,
                       PAR_NAME,
                       PAR_ID,
                       PAR_COLOR,
                       PAR_DESC,
                       PAR_RECT)


        #Add the bitgen box
        bitgen = BuildBox(self.scene,
                          BITGEN_POS,
                          BITGEN_NAME,
                          BITGEN_ID,
                          BITGEN_COLOR,
                          BITGEN_DESC,
                          BITGEN_RECT)


        #Add the trce box
        trce = BuildBox(self.scene,
                        TRACE_POS,
                        TRACE_NAME,
                        TRACE_ID,
                        TRACE_COLOR,
                        TRACE_DESC,
                        TRACE_RECT)

        #Add the link between generator and synthesis
        l = project_gen.add_link(synthesis, from_side = st.bottom, to_side = st.top)
        l.set_directed(True)
        
        #Add the link between synthesis and translate
        l = synthesis.add_link(translate)
        l.set_directed(True)
        #Add the link between translate and map
        l = translate.add_link(mapper)
        l.set_directed(True)
        #Add the link between map and par
        l = mapper.add_link(par)
        l.set_directed(True)
        #Add the link between par and bitgen
        l = par.add_link(bitgen)
        l.set_directed(True)
        #Add the link between par and trce
        l = par.add_link(trce)
        l.set_directed(True)

        self.builders[GEN_ID] = project_gen
        self.builders[SYNTHESIZER_ID] = synthesis
        self.builders[TRANSLATOR_ID] = translate
        self.builders[MAP_ID] = mapper
        self.builders[PAR_ID] = par
        self.builders[BITGEN_ID] = bitgen
        self.builders[TRACE_ID] = trce

    def reset_status(self):
        self.builders[GEN_ID].set_status(BUILD_STATUS.unknown)
        self.builders[SYNTHESIZER_ID].set_status(BUILD_STATUS.unknown)
        self.builders[TRANSLATOR_ID].set_status(BUILD_STATUS.unknown)
        self.builders[MAP_ID].set_status(BUILD_STATUS.unknown)
        self.builders[PAR_ID].set_status(BUILD_STATUS.unknown)
        self.builders[BITGEN_ID].set_status(BUILD_STATUS.unknown)
        self.builders[TRACE_ID].set_status(BUILD_STATUS.unknown)

    def set_status(self, builder, status):
        self.builders[builder].set_status(status)

    def get_status(self, builder):
        return self.builders[builder].get_status()

    def set_build_callback(self, build_cb):
        for builder in self.builders:
            self.builders[builder].set_build_callback(build_cb)

