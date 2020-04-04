import logging
import re
from pymprog import *
import numpy as np
import pandas as pd

#import matplotlib.pyplot as plt


def toList(NestedTuple):
    """
    function to convert a nested tuple to a nested list
    """
    return list(map(toList, NestedTuple)) if isinstance(NestedTuple, (list, tuple)) else NestedTuple


def log_in_file(content):
    logging.basicConfig(filename='Test.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')
    logging.debug(content)


def Init():
    """
    Initialization.
    """
    # add global variables
    global minSpeed
    global vehTypesEquipped
    global vehsAttributes
    global vehsAttNames
    # read the minimum Speed from the script UDA (user defined attributes)
    minSpeed = CurrentScript.AttValue('minSpeed')

    vehsAttributes = []
    vehsAttNames = {}

    # read which vehicle types are able to receive the signal information 
    # and being able to adjust their speed.
    vehTypesAttributes = Vissim.Net.VehicleTypes.GetMultipleAttributes(['No', 'ReceiveSignalInformation'])
    # list of vehicle types which are able to adjust their speed, e.g. [102, 103]
    vehTypesEquipped = [x[0] for x in vehTypesAttributes if x[1]==1]


def GetVissimDataVehicles():
    """
    this function reads vehicle attributes from PTV Vissim
    """
    global vehsAttributes
    global vehsAttNames
    vehsAttributesNames = ['No', 'VehType\\No', 'Lane\\Link\\No', 'DesSpeed',
                            'OrgDesSpeed', 'DistanceToSigHead', 'SpeedMaxForGreenStart', 
                            'SpeedMinForGreenEnd', 'Speed', 'Acceleration', 'StartTM', 'SimSec', 'Pos']
    vehsAttributes = toList(Vissim.Net.Vehicles.GetMultipleAttributes(vehsAttributesNames))

    # 'vehsAttNames' is a dictionary for the attribute names read from PTV Vissim:
    
    cnt = 0
    for att in vehsAttributesNames:
        vehsAttNames.update({att: cnt})
        cnt += 1


def OptimalSpeedMin(SpeedMinForGreenEnd, OrgDesSpeed):
    """
    A minimum speed is required to arrive during the current green.
    """
    if SpeedMinForGreenEnd < OrgDesSpeed:  
        # check if the desired speed is higher than the minimum speed
        # keep desired speed because it is faster => the vehicle will arrive at the 
        # signal within the current green
        optimalSpeed = OrgDesSpeed
    else:
        # no optimal speed in case the desired speed is larger or equal the required minimum speed
        optimalSpeed = -1 # go to OptimalSpeedMax
    return optimalSpeed


def OptimalSpeedMax(SpeedMaxForGreenStart, OrgDesSpeed):
    """
    The vehicle should not drive above the maximum speed in order to arrive just when the next green
    starts.
    """
    if SpeedMaxForGreenStart > OrgDesSpeed:  
        # check if the maximum speed is higher then the desired speed
        # keep desired speed because the desired speed to lower than the 
        # maximum speed => the vehicle will arrive after the signal turned green
        optimalSpeed = OrgDesSpeed
    else:
        optimalSpeed = SpeedMaxForGreenStart  # optimal speed for arriving at the next green
    return optimalSpeed


def SpeedAdjustment(SpeedMinForGreenEnd, SpeedMaxForGreenStart, OrgDesSpeed, diffSpeed):
    if SpeedMinForGreenEnd > SpeedMaxForGreenStart:
        # The minimum speed for arriving before the next green end is higher than the maximum speed to arriving after the next green start. This is only possible in case the next signal is green.
        # > there is green ahead!
        optimalSpeed = OptimalSpeedMin(SpeedMinForGreenEnd, OrgDesSpeed)
        if optimalSpeed == -1:  # check if no optimal speed in case the desired speed is larger or equal the required minimum speed
            optimalSpeed = OptimalSpeedMax(SpeedMaxForGreenStart, OrgDesSpeed)
    else:
        # There is red light ahead!
        # Use maximum speed:
        optimalSpeed = min(SpeedMaxForGreenStart, OrgDesSpeed) - diffSpeed
    
    return optimalSpeed


def Calculate_TimeUntilNextGreen(OrgDesSpeed, SpeedMinForGreenEnd, SpeedMaxForGreenStart, DistanceToSigHead):
    green_time = 29
    if SpeedMinForGreenEnd > SpeedMaxForGreenStart:
        # there is green light ahead
        if OrgDesSpeed >= SpeedMinForGreenEnd:
            # TimeUntilNextGreen is the time that until next green signal starts
            # if the vehicle can pass through the signal without being overspeed, 
            # TimeUntilNextGreen is equal to current green time
            TimeUntilNextGreen = DistanceToSigHead / OrgDesSpeed
        else:
            #######################################################################
            # if the vehicle cannot pass through the signal within the speed limit, 
            # TimeUntilNextGreen is equal to current green time + 51s
            # Because the red signal continuous 51s
            #######################################################################
            TimeUntilNextGreen = DistanceToSigHead / SpeedMinForGreenEnd + 30
    else:
        # There is red light ahead
        TimeUntilNextGreen = DistanceToSigHead/SpeedMaxForGreenStart
    return TimeUntilNextGreen



def read_sol(filename, n):
    file = open(filename)
    contents_lines = file.read().split('\n')
    data = []
    for i in contents_lines[:-21-n-1]:  #minus row of u(n) and some info (21), [a,b)
        try:
            data.append(re.findall('[a?v?x?\-0.9.0-9]+',i)[3])
        except Exception:
            None
    file.close()

    x = data[-3*n-3:-2*n-2] ############### different from original script
    v = data[-2*n-2:-n-1] # we are only interested in velocity
    #a = data[-n-1:]

    '''
    # conditions 
    assert(x[0]=='0')
    assert(a[0]=='-2')
    assert(v[0]=='20')
    assert(len(a)==n+1)
    assert(len(x)==n+1)
    assert(len(v)==n+1)
    assert(a[-1]=='0')
    assert(a[-2]=='0')
    assert(a[-3]=='2')
    assert(v[-1]=='0')
    assert(v[-2]=='10')
    assert(x[-1]=='200')
    import matplotlib.pyplot as plt
    plt.plot(np.linspace(0,40,n+1),v)
    plt.show()
    '''
    
    return np.array(x).astype(float), np.array(v).astype(float) ############### different from original script


def write_speed_profile(speed_set, No):
    profile_file = open(r'C:\Users\Kaihang Zhang\Desktop\Vissim_Projects\Intersection\total_speed_profile.csv', 'a')
    profile_file.write(str(No) + ',')
    profile_file.write(','.join([str(i) for i in speed_set.tolist()]) + ',\n')
    profile_file.close()
    log_in_file('written success of # '+str(No))


def read_speed_profile(No):
    speed_profile = pd.read_csv(r'C:\Users\Kaihang Zhang\Desktop\Vissim_Projects\Intersection\total_speed_profile.csv', header=None)
    try: 
        speed_profileNo = speed_profile[speed_profile[0]==No].values.tolist()
        
        return speed_profileNo[0]

    except Exception as e:
        log_in_file(str(e) + ' read failed of #%i'%No)
        return None


def write_pos_profile(pos_set, No):
    profile_file = open(r'C:\Users\Kaihang Zhang\Desktop\Vissim_Projects\Intersection\total_pos_profile.csv', 'a')
    profile_file.write(str(No) + ',')
    profile_file.write(','.join([str(i) for i in pos_set.tolist()]) + ',\n')
    profile_file.close()
    log_in_file('written success of # '+str(No))


def read_pos_profile(No):
    pos_profile = pd.read_csv(r'C:\Users\Kaihang Zhang\Desktop\Vissim_Projects\Intersection\total_pos_profile.csv', header=None)
    try: 
        pos_profileNo = pos_profile[pos_profile[0]==No].values.tolist()
        log_in_file('read success of # '+str(No))
        return pos_profileNo[0]

    except Exception as e:
        log_in_file(str(e) + ' read failed of #%i'%No)
        return None


def Cal_LP(No, n, t_set, aL, aU, vf, L, v_tf):
    begin('Speed Optimization')

    # initialize control parameters
    x_set = np.array(var('x', n+1))
    v_set = np.array(var('v', n+1))
    a_set = np.array(var('a', n+1))
    u_set = np.array(var('u', n+1))  # u_set>0
    # https://www.zhihu.com/question/47954261

    # objective function:
    minimize(np.sum(u_set[0:-2]*t_set[:-1]))  # [a,b)

    # eliminate absolute operation
    u_set >= a_set
    u_set >= -1 * a_set

    # constraints:
    # acceleration boundary
    for i in a_set:
        i.reset(aL, aU)
    # velocity limitation
    #for i in v_set:
    #    i.reset(0,vf)

    # velocity:
    v_set[0:-1] == (x_set[1:]-x_set[0:-1])/t_set  # Eqn (6a)
    # acceleration:
    a_set[0:-2] == (v_set[1:-1]-v_set[0:-2])/t_set[0:-1]  # Eqn (6b)

    # condition at t=0
    x_set[0] == 0  # Eqn (7a)
    v_set[0] == vf  # Eqn (7b), initial speed, free flow speed
    # condition at t=tf
    x_set[-1] == L  # Eqn (8a)
    v_set[-2] == v_tf  # Eqn (8b)

    solve()
    save(sol='_save.sol')
    
    #sensitivity()
    end()
    #print('objective value %f'%vobj())

    [x_res, v_profile] = read_sol('_save.sol', n) ############### different from original script

    if int(No) == 1:
        dif = 60-len(v_profile)
        nan_set = np.ones(dif)
        v_profile = np.append(v_profile, nan_set)
        ##log_in_file(v_profile)

    write_speed_profile(v_profile, No)
    write_pos_profile(x_res, No)

    return x_res, v_profile


def Linear_Optimize(StartTM, SimSec, Time_Simulated, DistanceToSigHead, L, aL, aU, v_tf, vf, v_0, TimeUntilNextGreen, simulation_time_step, No):
    # ---------------------------------------
    #  Decide about the optimal speed (desired speed)      |
    # ---------------------------------------

    '''
    try:
        assert(TimeUntilNextGreen * v_0 + 1/2 * aU * TimeUntilNextGreen**2 > DistanceToSigHead)
    except Exception:
        #log_in_file('\n'+'##################################'+'\n'+'Cannot reach!'+'\n'+'##################################')
        #log_in_file('Cannot reach; Time remain: %f, Distance remain: %f, current velocity: %f, time: %f' % (TimeUntilNextGreen, DistanceToSigHead, v_0, SimSec) + '   vechicle#' + str(No))
        return vf
    '''
    
    #DistanceToSigHead -= 5

    # n need to be discussed
    n = int(TimeUntilNextGreen/simulation_time_step) 
    t_set = np.ones(n)*(TimeUntilNextGreen-0)/n  # t_final - t_0
    try:
        profile_file = open(r'C:\Users\Kaihang Zhang\Desktop\Vissim_Projects\Intersection\total_speed_profile.csv')
        speed_profile = profile_file.readlines()
        profile_file.close()
        if_gen = No > float(int(speed_profile[-1].split(',')[0]))
        log_in_file('No:%f, %f'%(1.0*No, int(float(speed_profile[-1].split(',')[0]))))
    except Exception as e: # No==1
        if_gen = 1
        log_in_file('No is %i'%No + str(e))
    

    if  if_gen == 1:

        Cal_LP(No, n, t_set, aL, aU, vf, L, v_tf)
        

    v_profile = read_speed_profile(No)

    ##log_in_file(v_profile)

    
    len_v = 0
    for i in v_profile:
        len_v += 1
        if i==0:
            break        
    
    # t = np.arange(0, 42.02069385270846, (42.02069385270846)/(len(v_profile)+1))
    '''
    if int(No) == 1:
        x_res = read_pos_profile(No)
        t = np.arange(0,42,42/(len(x_res)+1))
        #dx = 197.5 - DistanceToSigHead
        dx=0
        plt.plot(t, x_res + dx)
        #plt.plot(t[int((simulation_time_step)/ t_set[0])], x_res[int((simulation_time_step)/ t_set[0])]+dx, 'r*')
        plt.xlim([0,50])
        plt.xlabel('time/s')
        plt.ylim([0,210])
        plt.ylabel('x/m')
        plt.savefig('./vissim_scripts/test43/%.2f'%SimSec+str(No)+'.png')
        plt.close()
    '''

    index = min((simulation_time_step + SimSec - StartTM)// t_set[0], len(t_set))
    current_index = min(int((L - DistanceToSigHead)/L * len_v), len_v - 2) # round down; len_v was applied to represent len(v_profile) that excludes nan
    #log_in_file('current_index:%f'%current_index)
    #current_index = int(current_index)
    avg_expct_speed = 0.5*(v_profile[current_index] + v_profile[current_index + int(simulation_time_step/t_set[0])])
    index = min(int((L - DistanceToSigHead + t_set[0]*(avg_expct_speed))/L * len_v), len_v - 2)
    log_in_file('%i, %i, so index:%i'%(int((L - DistanceToSigHead + t_set[0]*(avg_expct_speed))/L * len_v), len_v - 2, index))
    #index = int(index)

    try:
        #  Optimal_Speed(desired speed) is the speed in 1 seconds
        Optimal_Speed = v_profile[index]
        log_in_file('Current time: %f, read success of # %i, optimanlSpeed is %.2f in %f s'%(SimSec, No, Optimal_Speed, simulation_time_step))
        log_in_file('Success at line 319: index:%i, avg_expct_speed:%.2f, current_index:%i'%(index, avg_expct_speed, current_index))
    except Exception as e:
        log_in_file('len(v_profile) (excludes nan) is %i, index is %i'%(len_v, index))
        log_in_file('Cannot get optimal speed, current velocity is %f, distance remain: %f, vehicle#%i, velocity number: %i, t_set[0] is %f, time until next green is %f error:' % (v_0, DistanceToSigHead, int(No), int((simulation_time_step)/ t_set[0]), t_set[0], TimeUntilNextGreen) + str(e))
        log_in_file('Fail at line 323: index:%i, avg_expct_speed:%.2f, current_index:%i'%(index, avg_expct_speed, current_index))
        Optimal_Speed = None

    return Optimal_Speed


def V2I():
    # keep diffspeed a little smaller so that vehicle arrive shortly before the signal head.
    diffSpeed = -2

    # read vehicle attributes from PTV Vissim to global variable "vehsAttributes"
    GetVissimDataVehicles()

    if len(vehsAttributes) > 1:  # if there are any vehicles in the network
        for vehAttributes in vehsAttributes:  # loop over all vehicles in the network
            # check if vehicle is able to receive signal information
            if vehAttributes[vehsAttNames['VehType\\No']] in vehTypesEquipped:
                # set easier variables of the current vehicle:
                No = vehAttributes[vehsAttNames['No']]
                DesSpeed = vehAttributes[vehsAttNames['DesSpeed']]/3.6
                
                OrgDesSpeed = vehAttributes[vehsAttNames['OrgDesSpeed']]
                if OrgDesSpeed is None:  
                    # if the original desired speed has not yet saved, save 
                    #it to the UDA "OrgDesSpeed"
                    vehAttributes[vehsAttNames['OrgDesSpeed']] = DesSpeed*3.6
                    OrgDesSpeed = DesSpeed*3.6
                OrgDesSpeed = OrgDesSpeed/3.6

                DistanceToSigHead = vehAttributes[vehsAttNames['DistanceToSigHead']]
                Pos = vehAttributes[vehsAttNames['Pos']]
                Acceleration = vehAttributes[vehsAttNames['Acceleration']]/3.6
                Speed = vehAttributes[vehsAttNames['Speed']]/3.6

                # Maximum speed to arrive at the next green start. If the vehicle drives faster 
                # it would arrive at the signal before the next green time.
                SpeedMaxForGreenStart = vehAttributes[vehsAttNames['SpeedMaxForGreenStart']]/3.6
                #log_in_file('SpeedMaxForGreenStart is %f'%SpeedMaxForGreenStart)

                # Minimum speed to arrive at the next green end. If the vehicle drives slower, 
                # it would not make it in the current / next green time.
                SpeedMinForGreenEnd = vehAttributes[vehsAttNames['SpeedMinForGreenEnd']]/3.6

                StartTM = vehAttributes[vehsAttNames['StartTM']]
                SimSec = vehAttributes[vehsAttNames['SimSec']]


                # if the vehicle does not have a upcoming signal (passed the signal): set back to original desired speed
                if DistanceToSigHead <= 0:
                    vehAttributes[vehsAttNames['DesSpeed']] = OrgDesSpeed*3.6  # DesSpeed = OrgDesSpeed
                    continue  # jump to next vehicle

                # ---------------------------------------
                #  Decide about the optimal speed      |
                # ---------------------------------------
                TimeUntilNextGreen = Calculate_TimeUntilNextGreen(OrgDesSpeed, SpeedMinForGreenEnd, SpeedMaxForGreenStart, DistanceToSigHead)

                #TimeUntilNextGreen = TimeUntilNextGreen - SimSec + StartTM
                #log_in_file('TimeUntilNextGreen:'+ str(TimeUntilNextGreen))

                link_number = 5
                aL = -2
                aU = 2
                v_tf = OrgDesSpeed
                vf = OrgDesSpeed  # the free flow speed is set to be the original desired speed 
                v_0 = Speed
                simulation_time_step = 1.0
                Time_Simulated = SimSec - StartTM
                L = Vissim.Net.Links.GetMultipleAttributes(['Length2D'])[link_number-1][0]
                
                '''
                log_in_file(Current_time)
                log_in_file(DistanceToSigHead)
                log_in_file(L)
                log_in_file(aL)
                log_in_file(aU)
                log_in_file(v_tf)
                log_in_file(vf)
                log_in_file(v_0)
                log_in_file(TimeUntilNextGreen)
                log_in_file(simulation_time_step)
                '''

                try:
                    Time_Simulated = SimSec - StartTM
                    optimalSpeed = Linear_Optimize(StartTM, SimSec, Time_Simulated, DistanceToSigHead, L, aL, aU, v_tf, vf, v_0, TimeUntilNextGreen, simulation_time_step, No)
                    log_in_file('optimalSpeed is %f'%optimalSpeed)
                    if np.isnan(optimalSpeed) or optimalSpeed > 13.9:
                        optimalSpeed = SpeedAdjustment(SpeedMinForGreenEnd, SpeedMaxForGreenStart, OrgDesSpeed, diffSpeed)
                        log_in_file('SpeedAdjustment used at time %f'%SimSec)
                        #optimalSpeed = v_tf
                    #optimalSpeed = max(optimalSpeed, 4)  # minimum speed is 4
                    optimalSpeed = min(optimalSpeed, OrgDesSpeed)
                    # set optimal speed to the vehicles attributes
                    vehAttributes[vehsAttNames['DesSpeed']] = optimalSpeed*3.6
                except Exception as e:
                    log_in_file('Optimization Error! (Already reached stopline) line 344 ' + str(e) + ' Current time: %f'%(SimSec))

        # ----------------------------------------------------------------------------
        #  After iterating though all vehicles, update the speeds in PTV Vissim     |
        # ----------------------------------------------------------------------------
        vehicleNumDesiredSpeeds = [[x[vehsAttNames['DesSpeed']], x[vehsAttNames['OrgDesSpeed']]] for x in vehsAttributes]
        try:
            Vissim.Net.Vehicles.SetMultipleAttributes(('DesSpeed', 'OrgDesSpeed'), vehicleNumDesiredSpeeds)
        except Exception as e:
            log_in_file(str(e))
        