from core import *
from numpy import *
import sys
import LDP3840B 
import InfiniiumScope
import base
import matplotlib.pyplot as plt
import time
from time import strftime
import ipywidgets
import os
import pyvisa
import pylab
import shutil

LDP3840B_dd = ipywidgets.Dropdown(description='LDP3840B :', options=res_list, value=res_list[0])
InfiniiumScope_dd = ipywidgets.Dropdown(description='Infiniium_scope:', options=res_list, value=res_list[0])

channel1_t_A = ipywidgets.Dropdown(description='Channel_CM_A:', options=[1,2,3,4], value = 1)
channel2_t = ipywidgets.Dropdown(description='Channel_PD:', options=[1,2,3,4], value = 2)

s_i = 0
e_i = 1.5
points = 101
fn = 'outputFolder'
PW = 1.0
Inc_t = 1
I_limit = 3000

fn_t = ipywidgets.Text(description='Filename:',value = fn)
I_start_t = ipywidgets.FloatText(description='Start (A):',value = s_i)
I_stop_t = ipywidgets.FloatText(description='Stop (A):',value = e_i)
pnt_t = ipywidgets.IntText(description='Points:',value = points)
I_limit = ipywidgets.IntText(description='Limit (mA):',value = I_limit)
delay_t = ipywidgets.FloatText(description='Delay (ms):',value = 0)
PW_t = ipywidgets.FloatText(description='PW:',value = PW)

#sample number
device_no = 10
trial = 1
device_no_t = ipywidgets.IntText(description='device_no:',value = device_no)
trial_t = ipywidgets.IntText(description='trial:',value = trial)

print(device_no_t.value)

@btn_dec
def Start(btn):
    fn = fn_t.value
    s_i = I_start_t.value
    e_i = I_stop_t.value
    i_limit = I_limit.value
    points = pnt_t.value
    current_scale_1_A = 0.02
    current_scale_2 = 0.02
    pw = PW_t.value
    scale = [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1,2, 5, 10] # Vertical scale range for oscilloscope
    rm = visa.ResourceManager() # PyVisa
  
    # Oscilloscope settings
    scope = rm.open_resource(host + InfiniiumScope_dd.value)
    scope.write("*CLS")
    scope.write(r'SINGLE;*OPC;:CHANNEL%d:SCALe %.3f' %(channel1_t_A.value, float(current_scale_1_A)))  
    scope.write(r'SINGLE;*OPC;:CHANNEL%d:SCALe %.3f' %(channel2_t.value, float(current_scale_2)))
   
    scope.write(":CHANnel%d:DISPlay ON" %channel1_t_A.value)
    scope.write(":CHANnel%d:DISPlay ON" %channel2_t.value)
    
    scale_index1_A = 0
    scale_index1_C = 0
    scale_index2 = 0
    print("V_division (channel1_A):"+ ''+ str(current_scale_1_A))
    print("V_division (channel2):"+ ''+ str(current_scale_2))
    
    # Pulser settings
    SM = rm.open_resource(host + LDP3840B_dd.value)
    SM1 = LDP3840B.LDP3840B(host + LDP3840B_dd.value)
    SM.write(":PW %.2f" %pw)
    SM.write(":DIS:LDI")
    SM.write("LIMit:I %d" %i_limit)

#------------------------ Variable settings ----------------
    for intermid_scale in scale:  
        if intermid_scale == current_scale_1_A:
            break
        scale_index1_A = scale_index1_A + 1
        
    for intermid_scale in scale:  
        if intermid_scale == current_scale_2:
            break
        scale_index2 = scale_index2 + 1
    
    vmax = 100; # Maximum voltage for oscilloscope
    Is = [s_i + (0 if not i else ((e_i-s_i) / (points - 1) * i)) for i in range(int(points))]
    i_r = list()
    iMeas = list()
    pd_r1_A = list()
    pd_r1_C = list()
    pd_r2 = list()
    i = 0              
  
    #---------------------- File directory --------------------------------
    datafolder = 'data_text'+'/'+fn_t.value+'/'+'no'+str(device_no_t.value) # Folder that store data in text file
    pltfolder = 'plots'+'/'+ fn_t.value +'/'+'no'+str(device_no_t.value)
    
    #---------------------- Start measurement ----------------------------
#     SM.write("OUT ON")
# #     print(current_scale_1)
# #     print(current_scale_1*0.1)
# #     scope.write("TRIGger:EDGE:LEVel %e;"%(current_scale_1))
#     for i_t_2 in Is:
#         i_t_3 = int(i_t_2*1000)
#         i_r.append(i_t_3)
#         SM.write(r'LDI %d'%(i_t_3))
#         SM.write(r'DELAY 500')
       
#         pd_out1_A = scope.query_ascii_values(r'SINGLE;*OPC;:MEASure:VMAX? CHANNEL%d;'%channel1_t_A.value)[0]
#    #    pd_out1_C = scope.query_ascii_values(r'SINGLE;*OPC;:MEASure:VMAX? CHANNEL%d;'%channel1_t_C.value)[0]
#         pd_out2 = scope.query_ascii_values(r'SINGLE;*OPC;:MEASure:VMAX? CHANNEL%d;'%channel2_t.value)[0]
       
#         if pd_out1_A > vmax:
#            # SM.write(r'DELAY 1000')
#             scale_index1 = scale_index1 + 1
#             scope.write(r'SINGLE;*OPC;:CHANNEL%d:SCALe %.2f'%(channel1_t_A.value,float(scale[scale_index1])))
#          #  scope.write(r'SINGLE;*OPC;:CHANNEL%d:SCALe %.2f'%(channel1_t_C.value,float(scale[scale_index1])))
#             pd_out1_A = max(pd_r1_A)
#                # pd_out1_C = pd_r1_C[i-1]
#             pd_out2 = pd_r2[i-1]
          
                
#         if pd_out2 > vmax:
            
#             scale_index2 = scale_index2 + 1
#             scope.write(r'SINGLE;*OPC;:CHANNEL%d:SCALe %.2f'%(channel2_t.value,float(scale[scale_index2])))
#             pd_out1_A = pd_r1_A[i-1]
#           # pd_out1_C = pd_r1_C[i-1]
#             pd_out2 = pd_r2[i-1]
           
        
#         i = i+1
            
#         #adjust triggering
#         scope.write("TRIGger:EDGE:LEVel %e;"%(scale[scale_index1]))
            
#        #Append output
#         pd_r1_A.append(pd_out1_A)
#        #pd_r1_C.append(pd_out1_C)
#         pd_r2.append(pd_out2)# V changed to Watt

#     # The following code utilizes LDP 3840B python extension file uncommend if you want to use

    with SM1.LD_OUTPUT(I_mA = Is[0]*1000):
        for i_t in SM1.sweep_LDI(Is, delay = delay_t.value):
            i_r.append(i_t)
            pd_out1_A = scope.query_ascii_values(r'SINGLE;*OPC;:MEASure:VPP? CHANNEL%d;'%channel1_t_A.value)[0]
            pd_out2 = scope.query_ascii_values(r'SINGLE;*OPC;:MEASure:VPP? CHANNEL%d;'%channel2_t.value)[0]
            
            if pd_out1_A > vmax:
                scale_index1_A = scale_index1_A + 1
                scope.write(r'SINGLE;*OPC;:CHANNEL%d:SCALe %.2f' %(channel1_t_A.value, float(scale[scale_index1_A])))
                pd_out1_A = pd_r1_A[i-1]
                pd_out2 = pd_r2[i-1]
                
            if pd_out2 > vmax:
                scale_index2 = scale_index2 + 1
                scope.write(r'SINGLE;*OPC;:CHANNEL%d:SCALe %.2f' %(channel2_t.value, float(scale[scale_index2])))
                pd_out1_A = pd_r1_A[i-1]
                pd_out2 = pd_r2[i-1]
                
            i = i + 1
#             # Adjust triggering
#             triglevel = pd_out1_A*0.6 #set the trigger level to 60% of the Vmax
#             if scale[scale_index1_A] > 0.02:
#                  scope.write("TRIGger:EDGE:LEVel %e;"%(scale[scale_index1_A]))
            scope.write("TRIGger:EDGE:LEVel %e;" %(scale[scale_index1_A]*0.7))
            
            # Record measured current
            iMeas.append(pd_out1_A)

            # Record measured photodetector output       
            pd_r1_A.append(pd_out1_A)
            pd_r2.append(pd_out2) # V changed to Watt

# #-----------------TECHNICAL INFORMATION-------------------
#             #note (for DET 10D2): 
#            # photodetector loss
#            #     0.1985 area detected
#           #      0.94 glass loss
#           #  convert V to watt: 55
            
            
# #--------------- Terminate device operation -------------
#     SM1.write('*CLS;:STOP;*OPC?')
    SM.write("OUT OFF")
    SM.write('*CLS;:STOP;*OPC?')
    scope.write(':STOP;*OPC?')
    
# #----------------- Save file ------------------------------
    try:
        if not os.path.exists('./'+datafolder):
            os.makedirs('./'+datafolder)
    except:
        print('Error: Creating directory.'+datafolder)
        
    filename = strftime("%Y%m%d_%HH%MM") + '.txt'
    filesave1 = os.path.join(datafolder,filename)
    filesave2 = os.path.join(datafolder,'no'+ str(trial_t.value)+'.txt')
    i = 1
    
    while(os.path.exists(filesave2)):
        filesave2 = os.path.join(datafolder,'no'+ str(trial_t.value+i)+'.txt')
        i = i+1
     
    f = open(filesave2,'w+')
   # f.write('MODEL = ' + str(fn))
    f.writelines('\n')
    f.writelines('I, L\n')
    for i in range(0,pnt_t.value):
        f.write (str(iMeas[i]))
        f.writelines(' ')
        f.writelines(str(pd_r2[i]))
        f.writelines('\r\n')
    f.close()
    print(filesave2)
    print(filesave1)
    shutil.copy(filesave2,filesave1)
    
# #------------------------- Plotting ---------------------------
    fig = plt.figure()
    ax1 = plt.axes()
    ax1.plot(iMeas, pd_r2, 'b-')
    ax1.set_xlabel('Current (mA)')
    ax1.set_ylabel('L (u.t.)')
    plt.show(block = False)
   
    try: 
        if not os.path.exists('./'+pltfolder):
            os.makedirs('./'+pltfolder)
    except:
        print('Error: Creating directory./'+pltfolder)
        
    fig.savefig(os.path.join(pltfolder,strftime('no'+ str(trial_t.value)+'-'+ "%Y%m%d_%HH%MM") + '.png'))

    
start_btn = ipywidgets.Button(description='Start')
start_btn.on_click(Start)

Pages.append(ipywidgets.Box(children=[LDP3840B_dd, InfiniiumScope_dd, channel1_t_A,channel2_t, I_start_t, I_stop_t, pnt_t,I_limit, delay_t, fn_t,PW_t,device_no_t,trial_t,start_btn],layout=ipywidgets.Layout(
    #display='flex',
    flex_flow='column',
    align_items='stretch',
    width='50%'
)))
Names.append("LI_Pulse")
    

    

