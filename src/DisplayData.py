#!/usr/bin/env python
## Christophe.Chnafa@gmail.com

import vtk


class VtkPointCloud:

    def __init__(self, maxNumPoints=1e6):
        self.maxNumPoints = maxNumPoints
        self.vtkPolyData = vtk.vtkPolyData()
        self.clearPoints()
        mapper = vtk.vtkPolyDataMapper()
        if vtk.VTK_MAJOR_VERSION <= 5:
            mapper.SetInput(self.vtkPolyData)
        else:
            #mapper.SetInputConnection(polyData.GetProducerPort())
            #mapper.SetInputData(polyData)
            mapper.SetInputData(self.vtkPolyData)        
        self.vtkActor = vtk.vtkActor()
        self.vtkActor.SetMapper(mapper)
        self.vtkActor.GetProperty().SetPointSize(3.)
        self.vtkActor.GetProperty().SetColor(1., .0, .0)

    def addPoint(self, point):
        if self.vtkPoints.GetNumberOfPoints() < self.maxNumPoints:
            pointId = self.vtkPoints.InsertNextPoint(point[:])
            self.vtkCells.InsertNextCell(1)
            self.vtkCells.InsertCellPoint(pointId)
        else:
            print(">>> Warning: number of points > 1e6.")
        self.vtkCells.Modified()
        self.vtkPoints.Modified()

    def clearPoints(self):
        self.vtkPoints = vtk.vtkPoints()
        self.vtkCells = vtk.vtkCellArray()
        self.vtkPolyData.SetPoints(self.vtkPoints)
        self.vtkPolyData.SetVerts(self.vtkCells)

class VtkText:

    def __init__(self, guiText=""):
        self.text = vtk.vtkTextActor()
        self.text.SetInput(guiText)
        textProperties = self.text.GetTextProperty()
        #textProperties.SetFontFamilyToArial()
        textProperties.SetFontSize(15)
        textProperties.SetColor(1, 1, 1)
        self.text.SetDisplayPosition(20, 30)


class DisplayModel(object):

    def polyDataToActor(self, polyData, opacity=.25):
        '''Wrap the provided vtkPolyData object in a mapper and an actor, 
        returning the actor. '''
        mapper = vtk.vtkPolyDataMapper()
        if vtk.VTK_MAJOR_VERSION <= 5:
            mapper.SetInput(polyData)
        else:
            #mapper.SetInputConnection(polyData.GetProducerPort())
            mapper.SetInputData(polyData)
        actor = vtk.vtkActor()
        #actor.GetProperty().LightingOff()
        actor.SetMapper(mapper)
        actor.GetProperty().SetOpacity(opacity)

        return(actor)

    def setLight(self, renderer):
        lightKit = vtk.vtkLightKit()
        lightKit.MaintainLuminanceOn()
        lightKit.SetKeyLightIntensity(0.8)
        # 0 cold blue, 0.5 neutral white, 1 is reddish
        lightKit.SetKeyLightWarmth(0.5) 
        lightKit.SetFillLightWarmth(0.5)
      
        # The function is called SetHeadLightWarmth starting from VTK 5.0
        try :
          lightKit.SetHeadLightWarmth(0.5)
        except :
          lightKit.SetHeadlightWarmth(0.5)
      
        # intensity ratios
        lightKit.SetKeyToFillRatio(2.)
        lightKit.SetKeyToHeadRatio(7.)
        lightKit.SetKeyToBackRatio(1000.)
        lightKit.AddLightsToRenderer(renderer)

    def renderWindow(self, renderer, titleWindow):
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.SetSize(700, 700)

        # Assign a control style.
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(renderWindow)
        interactorStyle = vtk.vtkInteractorStyleTrackballCamera()
        interactor.SetInteractorStyle(interactorStyle)

        # Must be after vtk.vtkRenderWindowInteractor, otherwise it'll 
        # crash on Linux machines
        renderWindow.AddRenderer(renderer)
        renderWindow.Render()
        renderWindow.SetWindowName(titleWindow)
        
        # Initialize and start the interactor.
        interactor.Initialize()
        interactor.Start()

    def DisplayProbesAndModel(self, centerline, fileNameCenterline, 
        listProbePoints, model=None):
        '''Displays a model and the corresponding probe points along 
        the centerline. '''

        if model is None:
            isDisplayingModel = False
        else:
            isDisplayingModel = True

        # Create a cloud of points from the list of probe points.
        pointCloud = VtkPointCloud()
        nPoints = len(listProbePoints)
        for i in range(0, nPoints - 1):
            pointCloud.addPoint(listProbePoints[i])

        # Create a rendering window and renderer.
        ren = vtk.vtkRenderer()
        renWindows = vtk.vtkRenderWindow()
        renWindows.AddRenderer(ren)
         
        # Create a renderwindowinteractor
        iren = vtk.vtkRenderWindowInteractor()
        iren.SetRenderWindow(renWindows)

        # Assign a control style.
        style = vtk.vtkInteractorStyleTrackballCamera()
        iren.SetInteractorStyle(style)
         
        # Assign actor to the renderer.
        ren.AddActor(pointCloud.vtkActor)
        if isDisplayingModel:
            opacity = 0.25
            ren.AddActor(self.polyDataToActor(model, opacity))
        ren.AddActor(self.polyDataToActor(centerline))
        ren.SetBackground(.2, .3, .4)
        renWindows.SetSize(700, 700)

        # Create a text actor.
        txt = vtk.vtkTextActor()
        guiText = ("Centerline file name: " 
            + repr(fileNameCenterline.rsplit('/', 1)[-1]) + "\n" 
            + "Number of probes: " + repr(len(listProbePoints)) + "\n" 
            + "Q to exit.")
        txt.SetInput(guiText)
        txtprop = txt.GetTextProperty()
        txtprop.SetFontFamilyToArial()
        txtprop.SetFontSize(15)
        txtprop.SetColor(1, 1, 1)
        txt.SetDisplayPosition(20, 30)
 
        # Assign actor to the renderer.
        ren.AddActor(txt)

        # Enable user interface interactor.
        iren.Initialize()
        renWindows.Render()
        renWindows.SetWindowName("Probe Points.")
        iren.Start()

