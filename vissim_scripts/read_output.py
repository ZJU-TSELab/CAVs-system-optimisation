import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import os

result_dir = r'C:\Users\Kaihang Zhang\Desktop\Vissim_Projects\Intersection\Results\\'


def log_in_file(content):
    logging.basicConfig(filename='VisSim.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')
    logging.debug(content)


def record_info(total_delay, VehNumber, No, result_dir):
    script = Vissim.Net.Scripts.GetMultipleAttributes(['ScriptFile'])[0][0]
    inputs = Vissim.Net.VehicleInputs.GetMultipleAttributes(['Volume(1)', 'VehComp(1)'])
    RandSeed = Vissim.Simulation.AttValue('RandSeed')

    info = {
        'Trial': No,
        'Total delay/sec': str(total_delay),
        'script': script,
        'Vehicle Input Volume': int(inputs[0][0]),
        'Vehicle composition': inputs[0][1],
        'random seed': RandSeed,
        'Throughput': str(VehNumber)
    }

    info_df = pd.DataFrame(info, columns=['Trial', 'Total delay/sec', 'script', 'Vehicle Input Volume', 'Vehicle composition', 'random seed', 'Throughput'], index=[0])
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
output = []
for i in data_in_lines:
    output.append(i.strip('$').strip().split(';'))
titles = output[0]
output = np.array(output[1:])
output = pd.DataFrame(output, columns=titles)
file.close()

output['NO'] = output['NO'].astype('int32')
output['VEHICLE:SIMSEC'] = output['VEHICLE:SIMSEC'].astype('float64')
output['VEHTYPE'] = output['VEHTYPE'].astype('int32')
output = output.sort_values(by = [r'NO', r'VEHICLE:SIMSEC'])
output.index = pd.Series(np.arange(0, output.shape[0], 1))

'''
try:
    output.to_excel('out_test.xlsx')
except Exception as e:
    print(e)
'''

vehicleNo = 1
t = []
pos = []
'''
v = []
vDic = {}
v_des = []
v_desDic = {}
a = []
aDic = {}
'''

plt.figure(figsize=(18, 5))
for row in range(output.shape[0]):
    if int(output.loc[row, r'NO']) == vehicleNo and (int(output.loc[row, r'LANE\LINK\NO']) == 1 or int(output.loc[row, r'LANE\LINK\NO']) == 5):
        t.append(float(output.loc[row, r'VEHICLE:SIMSEC']))
        pos.append(float(output.loc[row, r'POS']))
        #v.append(row['SPEED'])
        #v_des.append(row['SPEED'])
        #a.append(row['SPEED'])
    elif int(output.loc[row, r'NO']) == vehicleNo + 1:
        print('NO:%i'%output.loc[row, r'NO'])
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

travel_data_filename = result_dir + 'study_network_' + str(No) + '.rsr'
travel_data_file = open(travel_data_filename)
travel_data_in_lines = travel_data_file.readlines()[8:]
trav_output = []
for i in travel_data_in_lines:
    trav_output.append(i.strip().split(';'))
titles = trav_output[0]
trav_output = pd.DataFrame(np.array(trav_output[1:]), columns=titles)
travel_data_file.close()
trav_output[' Trav.'] = trav_output[' Trav.'].str.strip(to_strip=None).astype('float64')
total_delay = trav_output[' Trav.'].sum() - trav_output.shape[0]*300/13.89

VehNumber = trav_output.shape[0]

log_in_file('delay:%f'%total_delay)

try:
    record_info(total_delay, VehNumber, No, result_dir)
    log_in_file('successfully read')
except Exception as e:
    log_in_file(e)

plt.ioff()
plt.close()

try:
    os.remove(r'C:\Users\Kaihang Zhang\Desktop\Vissim_Projects\Intersection\total_pos_profile.csv')
    os.remove(r'C:\Users\Kaihang Zhang\Desktop\Vissim_Projects\Intersection\total_speed_profile.csv')
except Exception as e:
    log_in_file(str(e))