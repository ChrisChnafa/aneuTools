#!/usr/bin/env python
## Christophe.Chnafa@gmail.com

import argparse
import numpy
import vtk


import src.ImportData as ImportData
from src.DisplayData import DisplayModel, VtkText
from src.NetworkBoundaryConditions import FlowSplitting


def Program(fileNameCenterline, fileNameModel, outputFlowrates, 
    displayModel, localRadii, verboseprint):

    print  
    print "--- Input files:" 
    print "Input centerline file name: ", fileNameCenterline.rsplit('/', 1)[-1]
    if not(fileNameModel == ''):
        print "Input model file name: ", fileNameModel.rsplit('/', 1)[-1]
    print 

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
    ImportData.SetNetworkStructure(centerline, network, verboseprint, 
        isConnectivityNeeded=True, isLocalRadiiNeeded=PowerLawUsesLocalRadii,
        localRadii=localRadii)

    # Compute the outlet boundary conditions.
    flowSplitting = FlowSplitting()
    flowSplitting.ComputeAlphas(network, verboseprint, 
        PowerLawUsesLocalRadii=PowerLawUsesLocalRadii)
    flowSplitting.ComputeBetas(network, verboseprint)
    flowSplitting.CheckTotalFlowRate(network, verboseprint)

    # Outlets coords and outlets %.
    points = vtk.vtkPoints()
    scalar = vtk.vtkDoubleArray()
    scalarBis = vtk.vtkDoubleArray()
    scalar.SetNumberOfComponents(1)
    for element in network.elements:
        if not(element.IsAnOutlet()):
            continue
        points.InsertNextPoint(element.GetOutPointsx1()[0])
        scalar.InsertNextValue(100.0*element.GetBeta())
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.GetPointData().SetScalars(scalar)

    if outputFlowrates:
        npoints = polydata.GetNumberOfPoints()
        print '{:^12}  {:^12}  {:^12} {:^12}'.format('X', 'Y', 'Z', '% outflow')
        for i in range(0, npoints):
            x = [0.0, 0.0, 0.0]
            polydata.GetPoints().GetPoint(i, x)
            print '{:^12.4f}  {:^12.4f}  {:^12.4f} {:^12.2f}'. \
                format(x[0], x[1], x[2], polydata.GetPointData(). \
                    GetScalars().GetTuple(i)[0])
        print

    if displayModel:
        labelMapper = vtk.vtkLabeledDataMapper()
        if vtk.VTK_MAJOR_VERSION <= 5:
            labelMapper.SetInputConnection(polydata.GetProducerPort())
        else:
            labelMapper.SetInputData(polydata)
        labelMapper.SetLabelModeToLabelScalars()

        labelProperties = labelMapper.GetLabelTextProperty()
        labelProperties.SetFontFamilyToArial()
        #tprop.SetColor(0.0,0.0,0.0)

        labels = vtk.vtkActor2D()
        labels.SetMapper(labelMapper)
        labelMapper.SetLabelFormat("%2.2f %%")

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
        if not(fileNameModel == ''):
            model = ImportData.loadFile(fileNameModel)
            opacity = 0.3
            renderer.AddActor(DisplayModel().polyDataToActor(model, opacity))
        else:
            renderer.AddActor(DisplayModel().polyDataToActor(centerline, 1.0))
        renderer.SetBackground(.2, .3, .4)

        # Set the lights of the renderer
        DisplayModel().setLight(renderer)

        # Create the RenderWindow and RenderWindowInteractor
        windowTitle = "Percents of the inflow - AneuTool version 0.0.1."
        DisplayModel().renderWindow(renderer, windowTitle)

if __name__ == "__main__":
        
    '''Command-line arguments.'''
    parser = argparse.ArgumentParser(
        description = "GetMeProbePoints: get probe points along the centerline.")
    parser.add_argument('-v', '--verbosity',  action = "store_true", dest='verbosity', 
        default = False, help = "Activates the verbose mode.")
    parser.add_argument('-i', '--inputCenterline', type = str, required = True, dest = 'fileNameCenterline',
        help = "Input file containing the centerlines data in a vtk compliant format.")
    parser.add_argument('-iModel', '--inputModel', type = str, required = False, default = '', dest='fileNameModel',
        help = "Input file containing the 3D model. It is for vizualization purpose only and it is not required.")
    parser.add_argument('-nw', '--notWritePoints', required = False, default = True, 
        dest = 'writePoints', action = "store_false", 
        help = "Set this argument to true if you want the script to display as an output the outlet flowrates.")
    parser.add_argument('-nd', '--notDisplayModel', required = False, default = True, 
        dest='displayModel', action = "store_false", 
        help = "Set this argument to true if you want to display the outlets flow of the model.")
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
        args.displayModel, args.localRadii, verboseprint)
