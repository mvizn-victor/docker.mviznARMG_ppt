#version:1
import glob
preset_folder=glob.glob('/home/mvizn/Preset')[0]
folder=preset_folder
import configparser
def read_seoho_preset_folder(folder):
    pan=dict()
    tilt=dict()
    config=configparser.ConfigParser()
    config.read(f'{folder}/LS_Center_Preset.ini')
    pan['cnlsbc']=float(config['Center']['LS_Center_Pan_Offset'])
    tilt['cnlsbc']=float(config['Center']['LS_Center_Tilt_Offset'])
    config=configparser.ConfigParser()
    config.read(f'{folder}/LS_Front_Preset.ini')
    pan['cnlsbf']=float(config['Front']['LS_Front_Pan_Offset'])
    tilt['cnlsbf']=float(config['Front']['LS_Front_Tilt_Offset'])
    config=configparser.ConfigParser()
    config.read(f'{folder}/LS_Rear_Preset.ini')
    pan['cnlsbb']=float(config['Rear']['LS_Rear_Pan_Offset'])
    tilt['cnlsbb']=float(config['Rear']['LS_Rear_Tilt_Offset'])
    config=configparser.ConfigParser()
    config=configparser.ConfigParser()
    config.read(f'{folder}/SS_Center_Preset.ini')
    pan['cnssbc']=float(config['Center']['SS_Center_Pan_Offset'])
    tilt['cnssbc']=float(config['Center']['SS_Center_Tilt_Offset'])
    config=configparser.ConfigParser()
    config.read(f'{folder}/SS_Front_Preset.ini')
    pan['cnssbf']=float(config['Front']['SS_Front_Pan_Offset'])
    tilt['cnssbf']=float(config['Front']['SS_Front_Tilt_Offset'])
    config=configparser.ConfigParser()
    config.read(f'{folder}/SS_Rear_Preset.ini')
    pan['cnssbb']=float(config['Rear']['SS_Rear_Pan_Offset'])
    tilt['cnssbb']=float(config['Rear']['SS_Rear_Tilt_Offset'])
    config=configparser.ConfigParser()
    config.read(f'{folder}/Misc_Preset.ini')
    pan['ovls']=float(config['PM_Camera']['LS_PM_Pan'])
    tilt['ovls']=float(config['PM_Camera']['LS_PM_Tilt'])
    pan['ovss']=float(config['PM_Camera']['SS_PM_Pan'])
    tilt['ovss']=float(config['PM_Camera']['SS_PM_Tilt'])
    return pan,tilt


import os
pan,tilt=read_seoho_preset_folder(preset_folder)
os.makedirs('config/seoho_offsets/tcds',exist_ok=True)
os.makedirs('config/seoho_offsets/clps',exist_ok=True)
os.makedirs('config/seoho_offsets/pmnrs',exist_ok=True)
def getcamname(f):
    for camname in ['cnlsbf','cnlsbb','cnlsbc','cnssbf','cnssbb','cnssbc','ovls','ovss']:
        if camname in f:
            return camname
    raise Exception(f'{f} does not contain camname')
def getptz(f):
    p,t,z=open(f).read().split('\n')[:3]
    p=float(p.split('=')[1])
    t=float(t.split('=')[1])
    z=int(float(z.split('=')[1]))
    return p,t,z
for f in glob.glob('config/pmnrs/*.txt')+glob.glob('config/clps/*.txt')+glob.glob('config/tcds/*.txt'):
    if 'pan' in f:continue
    print(f)
    camname=getcamname(f)
    p,t,z=getptz(f)
    p='%.2f'%(p-pan[camname])
    t='%.2f'%(t-tilt[camname])
    z=z
    ptz=f'pan={p}\ntilt={t}\nzoom={z}'
    print(f,camname)    
    fout=f.replace('config/','config/seoho_offsets/')
    assert 'seoho' in fout
    print(ptz)
    print(ptz,file=open(fout,'w'))
