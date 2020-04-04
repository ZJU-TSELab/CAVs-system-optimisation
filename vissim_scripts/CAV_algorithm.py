'''
# -------------------------------------------------------------------------------
# Name:        CAV Traj Opt
# Purpose:
#
# Author:      Simon Hu
#
# Created:     06/09/2019
# Copyright:   (c) ZJU 2019
# Licence:     ZJU license
# -------------------------------------------------------------------------------

This script is to create trajectory optimisation for CAVs!
'''


def main():
    """
    If this script is started externally, this functions calls the required sub-functions
    to run the example externally.
    """
    StartVissim()  # Start PTV Vissim via COM
    Initialization()
    SimulateExternally()


def StartVissim():
    '''two ways of open the model:
    1. If the file is in the working directory, then it can autoload the file in directory and just put in the file name;
    2. if the file is not in the working dir, then you can input your path and load it manually.
    '''

    import win32com.client as com
    import os

    # Define vissim object, choose appropriate vissim version in bracket
    Vissim = com.gencache.EnsureDispatch("Vissim.Vissim")

    # 1. open automatically
    # Define directory of the vissim model (require: user input)
    Path_of_VISSIM_network = os.getcwd()
    # Load a Vissim Network:
    Filename = os.path.join(
        Path_of_VISSIM_network, 'study_network.inpx')
    # you can read network(elements) additionally, in this case set "flag_read_additionally" to true
    flag_read_additionally = False
    Vissim.LoadNet(Filename, flag_read_additionally)

    # 2. open manually
    Filename = r'D:\WorkCluster\13_MOST-Project on CAV\T01-trajectory optimisation\Test network\study_network.inpx'
    # you can read network(elements) additionally, in this case set "flag_read_additionally" to true
    flag_read_additionally = False
    Vissim.LoadNet(Filename, flag_read_additionally)
    # Vissim.Simulation.RunContinuous()


def Initialization():
    '''
    Initialization
    '''
    # add global variable
    global minSpeed
    global vehTypesEquipped
    global vehsAttributes
    global vehsAttNames
    # read the minimum speed from the script UDA
    minSpeed = CurrentScript.AttValue('minSpeed')

    vehsAttributes = []
    vehsAttNames = []

    # read which vehicle types are able to receive the signal information and being able to ajust their speed
    vehTypesAttributes = Vissim.Net.VehicleTypes.GetMultipleAttributes(
        ['No', 'ReceiveSignalInformation'])
    # list of vehicle types which are able to adjust their speed, e.g. [102, 103]
    vehTypesEquipped = [x[0] for x in vehTypesAttributes if x[1]]


def toList(NestedTuple):
    """
    function to convert a nested tuple to a nested list
    """
    return list(map(toList, NestedTuple)) if isinstance(NestedTuple, (list, tuple)) else NestedTuple


def Init():
    """
    Initialization.
    """
    # add global variables
    global minSpeed
    global vehTypesEquipped
    global vehsAttributes
    global vehsAttNames
    # read the minimum Speed from the script UDA
    minSpeed = CurrentScript.AttValue('minSpeed')

    vehsAttributes = []
    vehsAttNames = []

    # read which vehicle types are able to receive the signal information and being able to adjust their speed.
    vehTypesAttributes = Vissim.Net.VehicleTypes.GetMultipleAttributes(
        ['No', 'ReceiveSignalInformation'])
    # list of vehicle types which are able to adjust their speed, e.g. [102, 103]
    vehTypesEquipped = [x[0] for x in vehTypesAttributes if x[1]]


def OptimalSpeedMin(minSpeed, desSpeed):
    """
    A minimum speed is required to arrive during the current green.
    """
    if minSpeed < desSpeed:  # check if the desired speed is higher then the minimum speed
        # keep desired speed because it is faster => the vehicle will arrive at the signal within the current green
        optimalSpeed = desSpeed
    else:
        # no optimal speed in case the desired speed is larger or equal the required minimum speed
        optimalSpeed = -1
    return optimalSpeed


def OptimalSpeedMax(maxSpeed, desSpeed):
    """
    The vehicle should not drive above the maximum speed in order to arrive just when the next green starts.
    """
    if maxSpeed > desSpeed:  # check if the maximum speed is higher then the desired speed
        # keep desired speed because the desired speed to lower than the maximum speed => the vehicle will arrive after the signal turned green
        optimalSpeed = desSpeed
    else:
        optimalSpeed = maxSpeed  # optimal speed for arriving at the next green
    return optimalSpeed


def GetVissimDataVehicles():
    """
    this function reads vehicle attributes from PTV Vissim
    """
    global vehsAttributes
    global vehsAttNames
    vehsAttributesNames = ['No', 'VehType\\No', 'Lane\\Link\\No', 'DesSpeed',
                           'OrgDesSpeed', 'DistanceToSigHead', 'SpeedMaxForGreenStart', 'SpeedMinForGreenEnd']
    vehsAttributes = toList(
        Vissim.Net.Vehicles.GetMultipleAttributes(vehsAttributesNames))

    # create dictionary for the attribute names read from PTV Vissim:
    vehsAttNames = {}
    cnt = 0
    for att in vehsAttributesNames:
        vehsAttNames.update({att: cnt})
        cnt += 1


def V2I():
    # keep speed a little smaller so that vehicle arrive shortly before the signal head.
    diffSpeed = 2
    # read vehicle attributes from PTV Vissim to global variable "vehsAttributes"
    GetVissimDataVehicles()

    if len(vehsAttributes) > 1:  # if there are any vehicles in the network
        for vehAttributes in vehsAttributes:  # loop over all vehicles in the network
            # check if vehicle is able to receive signal information
            if vehAttributes[vehsAttNames['VehType\\No']] in vehTypesEquipped:
                # set easier variables of the current vehicle:
                DesSpeed = vehAttributes[vehsAttNames['DesSpeed']]
                OrgDesSpeed = vehAttributes[vehsAttNames['OrgDesSpeed']]
                DistanceToSigHead = vehAttributes[vehsAttNames['DistanceToSigHead']]
                # Maximum speed to arrive at the next green start. If the vehicle drives faster it would arrive at the signal before the next green time.
                SpeedMaxForGreenStart = vehAttributes[vehsAttNames['SpeedMaxForGreenStart']]
                # Minimum speed to arrive at the next green end. If the vehicle drives slower, it would not make it in the current / next green time.
                SpeedMinForGreenEnd = vehAttributes[vehsAttNames['SpeedMinForGreenEnd']]

                if OrgDesSpeed is None:  # if the original desired speed has not yet saved, save it to the UDA "OrgDesSpeed"
                    OrgDesSpeed = DesSpeed
                    # OrgDesSpeed = DesSpeed;  save original desired speed
                    vehAttributes[vehsAttNames['OrgDesSpeed']] = DesSpeed

                # if the vehicle does not have a upcoming signal: set original desired speed
                if DistanceToSigHead <= 0:
                    vehAttributes[vehsAttNames['DesSpeed']
                                  ] = OrgDesSpeed  # DesSpeed = OrgDesSpeed
                    continue  # jump to next vehicle

                # ---------------------------------------
                #  Decide about the optimal speed      |
                # ---------------------------------------
                if SpeedMinForGreenEnd > SpeedMaxForGreenStart:
                    # The minimum speed for arriving before the next green end is higher than the maximum speed to arriving after the next green start. This is only possible in case the next signal is green.
                    # > there is green ahead!
                    optimalSpeed = OptimalSpeedMin(
                        SpeedMinForGreenEnd, OrgDesSpeed)
                    if optimalSpeed == -1:  # check if no optimal speed in case the desired speed is larger or equal the required minimum speed
                        optimalSpeed = OptimalSpeedMax(
                            SpeedMaxForGreenStart, OrgDesSpeed)
                else:
                    # There is red light ahead!
                    # Use maximum speed:
                    optimalSpeed = max(
                        min(SpeedMaxForGreenStart, OrgDesSpeed) - diffSpeed, minSpeed)

                # set optimal speed to the vehicles attributes
                vehAttributes[vehsAttNames['DesSpeed']] = optimalSpeed

        # ----------------------------------------------------------------------------
        #  After iterating though all vehicles, update the speeds in PTV Vissim     |
        # ----------------------------------------------------------------------------
        vehicleNumDesiredSpeeds = [
            [x[vehsAttNames['DesSpeed']], x[vehsAttNames['OrgDesSpeed']]] for x in vehsAttributes]
        Vissim.Net.Vehicles.SetMultipleAttributes(
            ('DesSpeed', 'OrgDesSpeed'), vehicleNumDesiredSpeeds)
