import win32com.client as com
import os
import pandas as pd
import time
import logging

Vissim = com.Dispatch('Vissim.Vissim.1100')
Vissim.LoadNet(r'C:\\Users\\Kaihang Zhang\\Desktop\\Vissim_Projects\\Intersection\\study_network.inpx')

result_dir = r'C:\Users\Kaihang Zhang\Desktop\Vissim_Projects\Intersection\Results\\'

ScriptFile_KZ = r'C:\Users\Kaihang Zhang\Desktop\Vissim_Projects\Intersection\vissim_scripts\CAV_algorithm_zkh_modified-2020.py'
ScriptFile_SH = r'C:\Users\Kaihang Zhang\Desktop\Vissim_Projects\Intersection\CAV_algorithm.py'
ReadOutputFile = r'C:\Users\Kaihang Zhang\Desktop\Vissim_Projects\Intersection\vissim_scripts\read_output.py'


def log_in_file(content):
    logging.basicConfig(filename='VisSim.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')
    logging.debug(content)


def run(ScriptFiles, Volume, VehComp, Random_Seed, SimPeriod, period):
    #Volume = float(raw_input('set Volume: (vehicles/hr):\n'))
    #VehComp = int(raw_input('set Vehicle composition(1: Default(all HV), 2: Mixed, 3: All CAV):\n'))
    Vissim.Simulation.SetAttValue('SimPeriod', SimPeriod)
    Vissim.Net.Scripts.SetMultipleAttributes(['ScriptFile'], ScriptFiles)
    Vissim.Net.Scripts.SetMultipleAttributes(['Period'], [[5], [period],[1]])
    Vissim.Net.VehicleInputs.SetMultipleAttributes(['Volume(1)', 'VehComp(1)'], [[Volume, VehComp]])
    Vissim.Simulation.SetAttValue('RandSeed', Random_Seed)
    Vissim.Graphics.CurrentNetworkWindow.SetAttValue("QuickMode", 1)
    Vissim.Simulation.RunContinuous()

#Vissim.Net.Vehicles.GetMultipleAttributes([''])


def get_No():
    dir = r'C:\Users\Kaihang Zhang\Desktop\Vissim_Projects\Intersection\Results\\'
    No = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.split('.')[1] == 'fzp':
                No.append(int(file.split('_')[-1].split('.')[0]))
    return max(No)


SimPeriod = 600
Simulation_Steps = [1.0]  # second
Volumes = [600]
Random_Seeds = [42]

ScriptFiles1 = [[ScriptFile_KZ], [ScriptFile_KZ], [ReadOutputFile]]
ScriptFiles2 = [[ScriptFile_SH], [ScriptFile_SH], [ReadOutputFile]]

totalNo = len(Volumes)*len(Random_Seeds)*len(Simulation_Steps)*3  # how many senarios

i = 0
for Volume in Volumes:
    for VehComp in [1, 2]:
        for Random_Seed in Random_Seeds:
            for Simulation_Step in Simulation_Steps:
                period = Simulation_Step/(1.0/Vissim.Simulation.AttValue('SimRes'))
                t1 = time.time()
                run(ScriptFiles1, Volume, VehComp, Random_Seed, SimPeriod, period)
                t2 = time.time()
                i += 1
                print('No. %i/%i was finished, time spent:%f' % (i, totalNo, t2-t1))

for Volume in Volumes:
    VehComp = 2
    for Random_Seed in Random_Seeds:
        for Simulation_Step in Simulation_Steps:
            period = Simulation_Step/(1.0/Vissim.Simulation.AttValue('SimRes'))
            t1 = time.time()
            run(ScriptFiles2, Volume, VehComp, Random_Seed, SimPeriod, period)
            t2 = time.time()
            i += 1
            print('No. %i/%i was finished, time spent:%f' % (i, totalNo, t2-t1))


Trial_end = get_No()
Trial_start = Trial_end - totalNo + 1

df = None
for No in range(Trial_start, Trial_end+1):
    try:
        if No < 10:
            No = '00' + str(No)
        elif No > 9 and No <100:
            No = '0' + str(No)
        else:
            No = str(No)
        df = pd.concat([df, pd.read_csv(result_dir + 'Info of ' + No + '.csv')])
    except Exception as e:
        log_in_file('Error at file:No%i, %s'%(int(No),e))
        print('Error occured')

df.to_csv(r'C:\Users\Kaihang Zhang\Desktop\Vissim_Projects\Intersection\DelayTime.csv', index=None, header=True)