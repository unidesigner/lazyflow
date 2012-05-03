#import sopynet

import vigra
import nose
from lazyflow import graph
from lazyflow import stype
from lazyflow import operators
import numpy

class OpGraphCut(graph.Operator):
    name = "OpGraphCut"

    InputImage = graph.InputSlot(stype.ArrayLike) # required slot
    PottsWeight = graph.InputSlot(value = 0.5) # required with default

    OutputImage = graph.OutputSlot(stype.ArrayLike)

    def __init__(self, parent):
        graph.Operator.__init__(self,parent)
        self._configured = False

    def setupOutputs(self):
        print 'Configure OpGraphCut ...'
        # output image need to have the same shape
        self.OutputImage.meta.shape = self.InputImage.meta.shape
        self.OutputImage.meta.dtype = self.InputImage.meta.dtype
        print "OpInternal shape=%r, dtype=%r" % (self.InputImage.meta.shape,
                                           self.InputImage.meta.dtype)
        self._configured = True
        print 'Configuration Done.'

    def execute(self, slot, roi, result):
        # slot is for instance OutputImage
        if slot == self.OutputImage:
            # propagate through
            # XXX: why 0?
            result[0] = self.InputImage[:].allocate().wait()[0]
        return result


class TestSopynet(object):

    def setUp(self):

        # test volume
        self.testVol = vigra.VigraArray((200,200,200))
        self.testVol[:] = numpy.random.rand(200,200,200)

        # create control graph
        self.graph = graph.Graph()

        self.oparraypiper = operators.OpArrayPiper(self.graph)
        self.oparraypiper.Input.setValue(self.testVol)

        # self.roiOp = OpRoiTest(self.graph)
        # self.roiOp.inputs["input"].setValue(self.testVol)

        # graph cut operator
        self.graphcut = OpGraphCut(self.graph)
        self.graphcut.InputImage.setValue( self.testVol )
        self.graphcut.PottsWeight.setValue( 3.4 )

        # connect the operators appropriately
        # self.graphcut.InputImage.connect(self.oparraypiper.output)

        #roi = generateRandomRoi((200,200,200))
        # result=self.op.outputs["Output"](start=roi[0], stop=roi[1]).wait()

    def tearDown(self):
        self.graph.stopGraph()

    def test_graphcut_node(self):
        print 'Output of Sopynet test ...'
        res = self.graphcut.OutputImage[:].wait()
        print 'OpGraphCut output image', res.shape, res.dtype, res
