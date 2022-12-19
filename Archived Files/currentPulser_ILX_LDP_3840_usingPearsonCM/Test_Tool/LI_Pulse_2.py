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

LDP3840B_dd = ipywidgets.Dropdown(description='LDP3840B :', options=res_list, value=res_list[0])
InfiniiumScope_dd = ipywidgets.Dropdown(description='Infiniium_scope:', options=res_list, value=res_list[0])

channel1_t = ipywidgets.Dropdown(description='Channel_CM:', options=[1,2,3,4], value=1)
channel2_t = ipywidgets.Dropdown(description='Channel_PD:', options=[1,2,3,4], value=1)

s_i = 0
e_i = 0.09
points = 91
fn = 'LI_Pulse'
PW = 0.5
Inc_t = 1
I_limit = 1000

fn_t = ipywidgets.Text(description='Filename:',value=fn)
I_start_t = ipywidgets.FloatText(description='Start(A):',value=s_i)
I_stop_t = ipywidgets.FloatText(description='Stop(A):',value=e_i)
pnt_t = ipywidgets.IntText(description='Points:',value=points)
I_limit = ipywidgets.IntText(description='Limit(mA):',value=I_limit)
delay_t = ipywidgets.FloatText(description='Delay(ms):',value=0)
PW_t = ipywidgets.FloatText(description='PW:',value=PW)


@btn_dec
def Start(btn):
    fn = fn_t.value
    s_i = I_start_t.value
    e_i = I_stop_t.value
    i_limit = I_limit.value
    points = pnt_t.value
    current_scale = 0.02
    pw = PW_t.value
    scale = [0.005,0.01,0.02,0.05,0.1,0.2,0.5,1,2,5]#vertical scale range for oscilloscope
    rm = visa.ResourceManager()#py visa
  
   
    
    #oscilloscope setting
    scope = rm.open_resource(host+InfiniiumScope_dd.value)
    scope.write("*CLS")
    scope.write(r'SINGLE;*OPC;:CHANNEL%d:SCALe %.2f'%(channel1_t.value,float(current_scale)))
    scope.write(r'SINGLE;*OPC;:CHANNEL%d:SCALe %.2f'%(channel2_t.value,float(current_scale)))
    scope.write(":CHANnel%d:DISPlay ON"%channel1_t.value)
    scope.write(":CHANnel%d:DISPlay ON"%channel2_t.value)
    scope.write(":CHANnel%d:SCALe %.3f"%(channel1_t.value,current_scale))
    scope.write(":CHANnel%d:SCALe %.3f"%(channel2_t.value,current_scale))
    scale_index = 0
    print("V_division (channel1):"+ ''+ str(current_scale))
    print("V_division (channel2):"+ ''+ str(current_scale))
   
    #Pulser setting
    SM = rm.open_resource(host+LDP3840B_dd.value)
    SM1 = LDP3840B.LDP3840B(host + LDP3840B_dd.value)
    SM.write(":PW %.2f"%pw)
    SM.write(":DIS:LDI")
    SM.write("LIMit:I %d"%i_limit)
    
    
    
    for intermid_scale in scale:  
        if intermid_scale == current_scale:
            break
        scale_index = scale_index + 1
    vmax = 7;#maximum voltage for oscilloscope
    change = 0
   
    
   
    Is = [s_i + (0 if not i else ((e_i-s_i) / (points - 1) * i)) for i in range(int(points))]
    i_r = list()
    pd_r = list() 
    i =0 
    
    
    
    
    
    
    with SM.LD_OUTPUT(I_mA=Is[0]*1000):
        for i_t in SM.sweep_LDI(Is,delay=delay_t.value):
            i_r.append(i_t)
            scope.write(":TRIGger:FORCe")
            pd_out1 = scope.query_ascii_values(r'SINGLE;*OPC;:MEASure:VMAX? CHANNEL%d;'%channel1_t.value)[0]
            pd_out2 = scope.query_ascii_values(r'SINGLE;*OPC;:MEASure:VMAX? CHANNEL%d;'%channel2_t.value)[0]
            if pd_out1 > vmax:
                scale_index = scale_index + 1
                scope.write(r'SINGLE;*OPC;:CHANNEL%d:SCALe %.2f'%(channel1_t.value,float(scale[scale_index])))
                pd_out1 = pd_r[i-1]
            if pd_out2 > vmax:
                scale_index = scale_index + 1
                scope.write(r'SINGLE;*OPC;:CHANNEL%d:SCALe %.2f'%(channel2_t.value,float(scale[scale_index])))
                pd_out2 = pd_r[i-1]
            i = i+1
            pd_r.append(pd_out2/(55*0.1985*0.94))# V changed to Watt
            #note: 
            #photodetector loss
                #0.1985 area detected
                #0.94 glass loss
            #convert V to watt:55
            
    #stop device operation
    SM.write('*CLS;:STOP;*OPC?')
    scope.write(':STOP;*OPC?')
    
    #save file
    datafolder = 'data_text'#folder that store data in text file
    filename = strftime(fn+'-'+"%Y%m%d_%HH%MM") + '.txt'
    filesave = os.path.join(datafolder,filename)
    f = open(filesave,'w+')
    f.write('MODEL = ' + str(fn))
    f.writelines('\n')
    for i in range(0,pnt_t.value):
        f.write (str(i_r[i]))
        f.writelines(' ')
        f.writelines(str(pd_r[i]))
        f.writelines('\r\n')
    f.close()
    
    #plotting
    fig = plt.figure()
    ax1 = plt.axes()
    ax1.plot(i_r,pd_r, 'b-')
    ax1.set_xlabel('Current (mA)')
    ax1.set_ylabel('L (W)')
    plt.show(block=False)
    pltfolder = 'plots'
    fig.savefig(os.path.join(pltfolder,strftime(fn + '-' + "%Y%m%d_%HH%MM") + '.png'))

start_btn = ipywidgets.Button(description='Start')
start_btn.on_click(Start)

Pages.append(ipywidgets.Box(children=[LDP3840B_dd, InfiniiumScope_dd, channel1_t,channel2_t, I_start_t, I_stop_t, pnt_t,I_limit, delay_t, fn_t,PW_t,start_btn],layout=ipywidgets.Layout(
    #display='flex',
    flex_flow='column',
    align_items='stretch',
    width='50%'
)))
Names.append("LI_Pulse")
    
