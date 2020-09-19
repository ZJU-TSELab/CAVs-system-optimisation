import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import os

result_dir = r'C:\Users\Kaihang Zhang\Desktop\Vissim_Projects\Intersection\Results\\'

# this function is used to debugging
def log_in_file(content):
    logging.basicConfig(filename='VisSim.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')
    logging.debug(content)

# record the general infomation of each simulation, into a csv file
def record_info(total_delay, energy_info, NumberOfVeh, No, result_dir):
    # VISSIM attributes extracted from VISSIM
    script = Vissim.Net.Scripts.GetMultipleAttributes(['ScriptFile'])[0][0]
    inputs = Vissim.Net.VehicleInputs.GetMultipleAttributes(['Volume(1)', 'VehComp(1)'])
    RandSeed = Vissim.Simulation.AttValue('RandSeed')

    regular_car = Vissim.Net.VehicleCompositions.GetMultipleAttributes(['RelFlow(100, 99950)'])[1][0]
    CAV = Vissim.Net.VehicleCompositions.GetMultipleAttributes(['RelFlow(120, 99950)'])[1][0]
    pen_rate = CAV / (CAV + regular_car)  # penetration rate of CAV


    info = {
        'Trial': No,
        'script': script,
        'Vehicle Input Volume': int(inputs[0][0]),
        'Penatration rate': pen_rate,
        'Vehicle composition': inputs[0][1],
        'random seed': RandSeed,
        'Total delay/sec': str(total_delay),
        'Throughput': str(NumberOfVeh),
        'CAV energy conspt': energy_info[0],
        'conventional energy conspt': energy_info[1],
        'overall energy conspt': energy_info[2]
    }

    info_df = pd.DataFrame(info, columns=info.keys(), index=[0])
    info_df.to_csv(result_dir + 'Info of ' + str(No) + '.csv', index=None, header=True)


def get_No():
    dir = r'C:\Users\Kaihang Zhang\Desktop\Vissim_Projects\Intersection\Results\\'
    No = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.split('.')[1] == 'fzp':
                No.append(int(file.split('_')[-1].split('.')[0]))
    return max(No)

No = get_No()

if No < 10:
    No = '00' + str(No)
elif No > 9 and No <100:
    No = '0' + str(No)
else:
    No = str(No)

#print('Reading file...')
filename = result_dir + 'study_network_'+ No +'.fzp'
file = open(filename)
data_in_lines = file.readlines()[25:]  # 25 depends on number of variables
# output stores the entire raw data from fzp file
output = []
for i in data_in_lines:
    output.append(i.strip('$').strip().split(';'))
titles = output[0]
output = np.array(output[1:])
output = pd.DataFrame(output, columns=titles)
file.close()

int_list = ['NO', 'VEHTYPE']
float_list = ['VEHICLE:SIMSEC', 'SPEED', 'ACCELERATION', 'POWER']
output[int_list] = output[int_list].astype('int32')
output[float_list] = output[float_list].astype('float64')

output = output.sort_values(by = [r'NO', r'VEHICLE:SIMSEC'])
output.index = pd.Series(np.arange(0, output.shape[0], 1))



vehicleNo = 1
t = []
pos = []

# #################################################################
# plot the space-time trajectories of vehicles in network
# #################################################################

plt.figure(figsize=(18, 5))
for row in range(output.shape[0]):
    if int(output.loc[row, r'NO']) == vehicleNo and (int(output.loc[row, r'LANE\LINK\NO']) == 1 or int(output.loc[row, r'LANE\LINK\NO']) == 5):
        t.append(float(output.loc[row, r'VEHICLE:SIMSEC']))
        pos.append(float(output.loc[row, r'POS']))
        #v.append(row['SPEED'])
        #v_des.append(row['SPEED'])
        #a.append(row['SPEED'])
    elif int(output.loc[row, r'NO']) == vehicleNo + 1:
        #print('NO:%i'%output.loc[row, r'NO'])
        if output.loc[row-1, r'VEHTYPE'] == 120:
            plt.plot(t, pos, linewidth = 0.5, color = 'r')
        else:
            plt.plot(t, pos, linewidth = 0.5, color = 'b')
        plt.xlabel('Time (s)')
        plt.ylabel('Position (m)')
        #plt.ion()
        #plt.pause(0.2)
        vehicleNo += 1
        t = []
        pos = []

# plot the signal
try:
    for i in range(int(Vissim.Simulation.AttValue('SimPeriod'))/30):
        time = (np.array([0, 1]) + i)*30
        Sig = [200, 200]
        if i % 2==0:
            plt.plot(time, Sig, color = 'g', linewidth = 1)
        else:
            plt.plot(time, Sig, color = 'r', linewidth = 2)
    plt.savefig(result_dir + str(No) + '.png')
except Exception as e:
    log_in_file(e)


# #################################################
# Calculate the delay per vehicle
# #################################################

travel_data_filename = result_dir + 'study_network_' + str(No) + '.rsr'
travel_data_file = open(travel_data_filename)
travel_data_in_lines = travel_data_file.readlines()[8:]
trav_output = []
for i in travel_data_in_lines:
    trav_output.append(i.strip().split(';'))
titles = trav_output[0]
trav_output = pd.DataFrame(np.array(trav_output[1:]), columns=titles)
travel_data_file.close()
# the time spent for each vehicle
trav_output[' Trav.'] = trav_output[' Trav.'].str.strip(to_strip=None).astype('float64')
trav_output['  Dist'] = trav_output['  Dist'].str.strip(to_strip=None).astype('float64')
# delay equals to time spent minus the time under free flow speed condition
total_delay = trav_output[' Trav.'].sum() - trav_output.shape[0]*300/13.89
# the throughput
NumberOfVeh = trav_output.shape[0]
distance_traveled_avg = np.sum(trav_output['  Dist'])/NumberOfVeh



# #################################################
# Calculate the energy consumption
# #################################################

# Calculate the power, algorithm borrowed from Ms. Qingyun Liu
# raw data: output
Num_of_rows = output.shape[0]
for i in range(Num_of_rows):
    if output.loc[i, 'ACCELERATION']<0:  # acceleration is 0
        output.loc[i, 'POWER'] = 0  # power set to be 0
    else:  # acceleration is not 0
        if output.loc[i, 'SPEED'] == 0:  # speed is 0
            if output.loc[i, 'VEHTYPE'] == 100:  # vehicle type is conventional vehicles
               output.loc[i, 'POWER'] = 3400  # let power equal to 3400
            else:  # it is a CAV
               output.loc[i, 'POWER'] = 25  # let power equal to 25

        else:  # speed is not 0
            if output.loc[i, 'VEHTYPE'] == 100:  # vehicle type is conventional vehicles
                output.loc[i, 'POWER'] = (0.015*1770*9.81/0.339+0.5*0.31*1.2041*2.321*output.loc[i, 'SPEED']**2+1770*output.loc[i,'ACCELERATION'])*output.loc[i,'SPEED']/0.30
            else:  # it is a CAV
                output.loc[i, 'POWER'] = (0.015*1674*9.81/0.316+0.5*0.28*1.2041*2.304*output.loc[i, 'SPEED']**2+1674*output.loc[i,'ACCELERATION'])*output.loc[i,'SPEED']/0.87

# CAV energy
CAV_data = output.loc[output['VEHTYPE']==120]
num_CAV = CAV_data.shape[0]
CAV_avg_energy = np.sum(CAV_data['POWER'])*0.2 / (distance_traveled_avg / 1000) / 3600  # average CAV energy consumption per kilometer; Wh

# conventional vehicles
con_data = output.loc[output['VEHTYPE']==100]
num_con = con_data.shape[0]
con_avg_energy = np.sum(con_data['POWER']) * 0.2 / (distance_traveled_avg / 1000) / 3600  # average conventional vehicles energy consumption per kilometer; Wh

# overall
avg_energy = ( num_CAV * CAV_avg_energy + num_con * con_avg_energy ) / (num_CAV + num_con)

energy_info = [CAV_avg_energy, con_avg_energy, avg_energy]



try:
    record_info(total_delay, energy_info, NumberOfVeh, No, result_dir)
    #log_in_file('successfully read')
except Exception as e:
    log_in_file(e)

plt.ioff()
plt.close()