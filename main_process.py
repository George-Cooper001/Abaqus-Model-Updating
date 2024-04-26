# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 11:47:00 2024

@author: George Cooper
"""
import numpy as np
import itertools
import json
import math
from odbAccess import *
from abaqus import mdb
np.set_printoptions(precision=8)
Four_Floor_disp = 10.26
top_floor_strain = 0.0003127
Freq_r = np.array([2.9919, 9.0705, 14.2041, 17.2253])
# print(Freq_r)
z = np.array([[0.0059-0.0090j, 0.0055-0.0009j, -0.0098-0.0047j, -0.0190-0.0110j, -0.0106+0.0023j, 0.0088-0.0023j],
    [0.0123-0.0141j, 0.0052-0.0006j, 0.0048+0.0015j, 0.0068+0.0039j, 0.0161-0.0037j, -0.0133+0.0033j],
    [0.0173-0.0179j, -0.0003+0.0001j, 0.0080+0.0039j, 0.0157+0.0091j, -0.0150+0.0035j, 0.0123-0.0031j],
    [0.0198-0.0203j, -0.0053+0.0007j, -0.0068-0.0030j, -0.0123-0.0071j, 0.0066-0.0016j, -0.0054+0.0014j]])
z1 = z[:, [0, 1, 3, 4]]
z2 = np.zeros((4, 4))
# a=np.abs(z)
a1 = np.abs(z1)
# print(a)
# print(a1)
# 归一化处理实验振幅magnitude数据
scaled_magnitude_r = np.zeros((4, 4), dtype=complex)
for i in range(4):
    for j in range(4):
        Max_Index = np.argmax(a1[:, i])
        scaled_magnitude_r[j, i] = z1[j, i]/z1[Max_Index, i]
        scaled_magnitude_r[j, i] = np.real(scaled_magnitude_r[j, i])
scaled_magnitude_r = np.abs(scaled_magnitude_r)
# (scaled_magnitude_r)
# print(scaled_magnitude_r)

# 设置参数集路径和导入参数信息
# print(sys.argv[1])
# PathParams = sys.argv[1]
PathParams = r'F:\pythonProject\FE_model_test\Batch\iter_params\GAI1'

with open(PathParams, 'r') as ParaFile:
    All_data = json.load(ParaFile)
materials = All_data
# print(materials)
# 修改参数
BaseInpFilepath = r'F:\pythonProject\FE_model_test\py_abaqus_obd_7\modal2.inp'
# InpFilePath = r'F:\pythonProject\FE_model_test\Batch\iter_inp\GAI2'
# 打开inp文件
with open(BaseInpFilepath, 'r') as file:
    FileLines = file.readlines()
# 重写入inp文件
with open(BaseInpFilepath, 'w') as ChangeFile:
    skip_next_line = False
    for line in FileLines:
        updated = False
        for materials_name, props in materials.items():
            if '*Material, name={}'.format(materials_name) in line:
                next_line = '*Material, name={}\n*Density\n {},\n'.format(materials_name, round(props[0], 4)*1e-9)  # 示例密度值
                next_next_line = '*Elastic\n{}, {}\n'.format(round(props[1]*1e8, 2), round(props[2], 2))
                ChangeFile.write(next_line)
                ChangeFile.write(next_next_line)
                updated = True
                break
        if updated:
            continue
        if skip_next_line:
            skip_next_line = False
            continue
        if '*Density' in line or '*Elastic' in line:
            skip_next_line = True
            continue
        ChangeFile.write(line)

# 提交job
myJob = mdb.JobFromInputFile(name='modal2', inputFileName=BaseInpFilepath)
myJob.submit()
myJob.waitForCompletion()

# 定义ODB文件的路径和实例名
odbPath = r'F:\pythonProject\FE_model_test\py_abaqus_obd_7\modal2.odb'
instance_names = ['SLAB-1-LIN-1-2', 'SLAB-1-LIN-1-2-LIN-1-2', 'SLAB-1-LIN-1-2-LIN-1-2-1',
                  'SLAB-1-LIN-1-2-LIN-1-2-LIN-1-2']
# 定义输出文件路径
# outputFilePath = 'F:\pythonProject\FE_model_test\py_abaqus_obd\output.txt'
OutPutFilePath = r'F:\pythonProject\FE_model_test\Batch\OutPut\GAI4'
# 打开ODB文件
odb = openOdb(path=odbPath)
# 创建magnitude&freq库
Frequency = [0]*6
Magnitude = np.zeros((4, 6))
# 打开输出文件准备写入
# with open(outputFilePath, 'w') as outFile:
with open(OutPutFilePath, 'w') as outFile:
    # 获取特定实例和最后一帧
    for m in range(1, 7):
        # if i != 3 and i != 5:
        for n, instanceName in enumerate(instance_names):
            instance = odb.rootAssembly.instances[instanceName]
            FrameStep = odb.steps['Step-freq']
            Frame = FrameStep.frames[m]
            # 获取位移数据
            # frequency = Frame.frequency
            Frequency[m-1] = Frame.frequency
            displacementField = Frame.fieldOutputs['U']
            # 为第1747节点写入位移数据
            for node in instance.nodes[180:181]:
                displacement = displacementField.getSubset(region=node).values
                if displacement:
                    # 提取位移magnitude
                    Magnitude[n, m-1] = displacement[0].data[1]
                    # outFile.write('Frame{},Frequency:{}\n instaname:{},Node {}:\n magnitude={}\n'.format(i,
                    #             frequency,instanceName,node.label,displacement[0].magnitude))
    # 获取柱子节点集合
    elemset = odb.rootAssembly.elementSets['SET-7']
    # 获取顶层节点集合
    top_surface_nodes = odb.rootAssembly.instances['SLAB-1-LIN-1-2-LIN-1-2-LIN-1-2'].nodes[180]
    # 选取步骤
    FrameStep_2 = odb.steps['ADD']
    # 获取位移数据
    Frame_1 = FrameStep_2.frames[-1]
    Displacements = Frame_1.fieldOutputs['U'].getSubset(region=top_surface_nodes).values
    Strain = Frame_1.fieldOutputs['LE'].getSubset(region=elemset).values
    if Strain:
        Strain = Strain[0].maxPrincipal
        Strain_str = str(Strain)
    if Displacements:
        Displacements = Displacements[0].data[1]
        Displacements_str = str(Displacements)
    Magnitude_list = Magnitude.tolist()
    All_data = {'Freq_list': Frequency, 'Magni_matrix': Magnitude_list, 'Displacement': Displacements_str, 'Strain': Strain_str}
    json.dump(All_data, outFile)
    # outFile.write('{}\n{}'.format(Frequency,Magnitude))
# 关闭ODB文件
odb.close()

# 获得GET_nodes中提取的数据
with open(OutPutFilePath, 'r') as f:
    All_data = json.load(f)

StrainData = All_data['Strain']
StrainData = float(StrainData)
DispData = All_data['Displacement']
DispData = float(DispData)
Frequency = All_data['Freq_list']
Frequency = np.array(Frequency)
Magnitude_list = All_data['Magni_matrix']
Magnitude = np.array(Magnitude_list)
Magnitude = np.abs(Magnitude)
# print(Frequency)
# print(Magnitude)
# 将所有的振型magnitude归一化
scaled_Magnitude_t = np.zeros((4, 6))
for b in range(6):
    for c in range(4):
        MaxCo_t = np.max(Magnitude[:, b])
        MinCo_t = 0
        scaled_Magnitude_t[c, b] = (Magnitude[c, b] - MinCo_t) / (MaxCo_t - MinCo_t)
# print(scaled_Magnitude_t)
# 从前6个模态中随机抽取四个模态的振型数据
MacList = np.zeros((15, 4))
all_rowSum = {}
all_column_combination = list(itertools.combinations(range(6),4))
# print(all_column_combination)
for d, columns in enumerate(all_column_combination):
    new_Magnitude_t = scaled_Magnitude_t[:, columns]
    for e in range(4):
        # 计算MAC贡献值
        mac = (((np.dot(scaled_magnitude_r[:, e].T, new_Magnitude_t[:, e])).item())**2)/(np.sum(scaled_magnitude_r[:, e]**2) * np.sum(new_Magnitude_t[:, e]**2))
        MacList[d, e] = (np.arccos(math.sqrt(mac)))/(np.pi/2)
    # 生成字典，key值为每行的总和，value值为对应的模态编号
    all_rowSum[np.sum(MacList[d, :])] = columns
# 取出最小的总和，key值
Min_SuMac = min(all_rowSum.keys())
# 总和最小行对应的模态编号数据
column_selected = all_rowSum[Min_SuMac]
# 提取出选中模态编号对应的频率数据
Freq_selected = Frequency[list(column_selected)]
# 最小行在MacList中对应的行的编号
f = all_column_combination.index(column_selected)
# 最小行的详细参数
detail_Min_SuMac = MacList[f, :]
detail_Min_SuMac = detail_Min_SuMac.tolist()
# print(MacList)
# print(Min_SuMac)
# print(column_selected)
# print(Freq_selected)
# eta = np.array([75, 80, 100, 80])
detail_Sum_F_object = ((Freq_r-Freq_selected)/Freq_r)**2
detail_Sum_F_object = detail_Sum_F_object.tolist()
Sum_F_object = np.dot(((Freq_r-Freq_selected)/Freq_r), ((Freq_r-Freq_selected)/Freq_r).T)
# print(Sum_F_object)
# 位移误差
DispIndex = abs((Four_Floor_disp - DispData)/Four_Floor_disp)
# 应变误差
StrainIndex = abs((top_floor_strain-StrainData)/top_floor_strain)
Assessment_Index = Min_SuMac + Sum_F_object + DispIndex + StrainIndex
# Assessment_Index = str(Assessment_Index)
# print(Assessment_Index)
# 分析指标输出txt文件
# OutPath_Index = '{}'.format(sys.argv[2])
OutPath_Index = r'F:\pythonProject\FE_model_test\Batch\output_index\GAI3'
with open(OutPath_Index, 'w') as file2:
    data = {'part1': Min_SuMac, 'part2': Sum_F_object, 'part3': DispIndex, 'part4': StrainIndex, 'value': Assessment_Index, 'detail_part1': detail_Min_SuMac
            , 'detail_part2': detail_Sum_F_object}
    json.dump(data, file2)
#    file2.write(Assessment_Index)
# print(Assessment_Index)
# print(selected_column)
