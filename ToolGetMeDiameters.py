#!/usr/bin/env python
## Christophe.Chnafa@gmail.com

import argparse
import numpy
import vtk

import src.ImportData as ImportData
from src.DisplayData import DisplayModel, VtkText, VtkPointCloud

def Program(fileNameCenterline, fileNameModel, writeProbePoints, 
    localRadii, verboseprint):

    print ">" 
    print "> --- Input files:" 
    print "> Input centerline file name: ", fileNameCenterline.rsplit('/', 1)[-1]
    if not(fileNameModel == ''):
        print "> Input model file name: ", fileNameModel.rsplit('/', 1)[-1]
    print ">"
    # Check if the radii used for the flow splitting are computed locally.
    localRadii = float(localRadii)
    if localRadii > 0.0:
        PowerLawUsesLocalRadii = True
    else:
        PowerLawUsesLocalRadii = False

    # Load the centerline vtk data from the file 'fileNameCenterline'.
    centerline = ImportData.loadFile(fileNameCenterline)

    # Set the corresponding 0D network.
    network = ImportData.Network()
    ptIntegration=[]
    ImportData.SetNetworkStructure(centerline, network, verboseprint, 
        isConnectivityNeeded=True, isLocalRadiiNeeded=PowerLawUsesLocalRadii,
        localRadii=localRadii)

    # Extract the mid points coords and Diameters.
    points = vtk.vtkPoints()
    scalar = vtk.vtkDoubleArray()
    scalar.SetNumberOfComponents(1)
    for element in network.elements:
        if element.IsBlanked():
            continue
        desiredLength = element.GetLength() * 0.666
        branchId = element.GetVtkCellIdList()[0]
        midPointId = ImportData.GetIndexCenterlineForADefinedLength(centerline, 
            branchId, desiredLength, verboseprint)
        midPoint = [0.0, 0.0, 0.0]
        centerline.GetCell(branchId).GetPoints().GetPoint(midPointId, midPoint)
        points.InsertNextPoint(midPoint)
        if localRadii:
            scalar.InsertNextValue(2.0 * element.GetLocalRadius())
        else:
            scalar.InsertNextValue(2.0 * element.GetMeanRadius())
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.GetPointData().SetScalars(scalar)

    labelMapper = vtk.vtkLabeledDataMapper()
    if vtk.VTK_MAJOR_VERSION <= 5:
        labelMapper.SetInputConnection(polydata.GetProducerPort())
    else:
        labelMapper.SetInputData(polydata)
    labelMapper.SetLabelModeToLabelScalars()
    labelProperties = labelMapper.GetLabelTextProperty()
    labelProperties.SetFontFamilyToArial()
    #labelProperties.SetColor(0, 1, 0)

    labels = vtk.vtkActor2D()
    labels.SetMapper(labelMapper)
    labelMapper.SetLabelFormat("%2.2f mm")

    # GUI text.
    text = ''
    if not(fileNameModel == ''):
        text = ("Model file name: "  
             + repr(fileNameModel.rsplit('/', 1)[-1]) + "\n")
    else:
        text = ("Centerline file name: "  
             + repr(fileNameCenterline.rsplit('/', 1)[-1]) + "\n")
    text = (text 
         + "Q to exit.")
    guiText = VtkText(text)

    # Create the renderer
    renderer = vtk.vtkRenderer()
    renderer.AddActor(guiText.text)
    renderer.AddActor(labels)
    # Read 3D model if necessary.
    opacity = 1.0
    if not(fileNameModel == ''):
        model = ImportData.loadFile(fileNameModel)
        renderer.AddActor(DisplayModel().polyDataToActor(model, opacity))
    else:
        renderer.AddActor(DisplayModel().polyDataToActor(centerline, opacity))
    renderer.SetBackground(.2, .3, .4)

    listProbePoints = ptIntegration
    pointCloud = VtkPointCloud()
    nPoints = len(listProbePoints)
    for i in range(0, nPoints):
        print listProbePoints[i]
        pointCloud.addPoint(listProbePoints[i])
    # Assign actor to the renderer.
    renderer.AddActor(pointCloud.vtkActor)



    # Set the lights of the renderer
    DisplayModel().setLight(renderer)

    # Create the RenderWindow and RenderWindowInteractor
    windowTitle = "Mean diameters - AneuTools version 0.0.1."
    DisplayModel().renderWindow(renderer, windowTitle)


if __name__ == "__main__":
        
    '''Command-line arguments.'''
    parser = argparse.ArgumentParser(
        description = "GetMeProbePoints: get probe points along the centerline.")
    parser.add_argument('-v', '--verbosity',  action = "store_true", dest='verbosity', 
        default = False, help = "Activates the verbose mode.")
    parser.add_argument('-i', '--inputCenterline', type=str, required = True, dest='fileNameCenterline',
        help = "Input file containing the centerlines data in a vtk compliant format.")
    parser.add_argument('-iModel', '--inputModel', type=str, required = False, default = '', dest='fileNameModel',
        help = "Input file containing the 3D model. It is for vizualization purpose only and it is not required.")
    parser.add_argument('-w', '--writePoints', required = False, default = False, 
        dest='writePoints', action = "store_true", 
        help = "Set this argument to true if you want the script to write an output file with the outlet flowrates.")
    parser.add_argument('-localRadii', '--localRadii', required = False, default = 0, type=int,
        dest='localRadii', 
        help = "Instead of averaging a radius along the branches, a local radius can be computed.")
    args = parser.parse_args()

    if args.verbosity:
        print(">")
        print("> --- VERBOSE MODE ACTIVATED ---")
        def verboseprint(*args):
            for arg in args:
                print arg,
                print
    else:
        verboseprint = lambda *a: None

    # Start the script.    
    Program(args.fileNameCenterline, args.fileNameModel, args.writePoints, 
        args.localRadii, verboseprint)
