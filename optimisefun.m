function result = optimisefun(x,a)
global nameaddnum
nameaddnum = nameaddnum+1;
AA = ['-',num2str(a)];
%设置变量集
SS = ['-',num2str(nameaddnum)];
fout1 = strcat('Iter_params',SS,'.json');
fout2 = strcat('modal2', SS,'.inp');
fout3 = strcat('Out_Index', SS,'.json');
fout6 = strcat('output', SS,'.json');
fout4 = strcat('Batch',AA);
fout5 = strcat('Out_Index',SS,'.json');
%设置参数信息
materials = struct;
materials.Aluminum = [x(1)*1e5, x(1), 0.33];
materials.PE = [x(3)*1e5 ,x(4), 0.44];
% 将'materials' 结构体转换为JSON字符串
jsonData = jsonencode(materials);
filepath1 = fullfile('F:\pythonProject\FE_model_test', fout4, 'iter_params', fout1);
file = fopen(filepath1, 'w');
% 检查文件是否成功打开
if file == -1
    error('Cannot open file for writing.');
end
% 将JSON字符串写入文件
fwrite(file, jsonData, 'char');
% 关闭文件
fclose(file);
% 重新写入py文件
findfile = fopen('main_process.py','r');
writefilename = strcat('main_process',SS,'.py');
writefilepath = fullfile('F:\pythonProject\FE_model_test', fout4, 'iter_main_process',writefilename);
writefile = fopen(writefilepath,'w');
i=0;
while ~feof(findfile)
    tline=fgetl(findfile);%读取一行
    i=i+1;
    tline = strrep(tline,'Batch',fout4);
    tline=strrep(tline,'GAI1',fout1);
    tline=strrep(tline,'GAI2',fout2);
    tline=strrep(tline,'GAI3',fout3);
    tline=strrep(tline,'GAI4',fout6);
    % if a >= 3 && a <= 8
    % %if a == 8
    % fout7 = 'Assessment_Index = Min_SuMac + 6*Sum_F_object + 6*DispIndex + 6*StrainIndex';
    % tline = strrep(tline, 'Assessment_Index = Min_SuMac + Sum_F_object + DispIndex + StrainIndex', fout7);
    % elseif a == 5
    % fout7 = 'Assessment_Index = Min_SuMac + 3*Sum_F_object + 3*DispIndex + 3*StrainIndex';
    % tline = strrep(tline, 'Assessment_Index = Min_SuMac + Sum_F_object + DispIndex + StrainIndex', fout7);
    % elseif a == 9
    % fout7 = 'Assessment_Index = Min_SuMac + 8*Sum_F_object + 8*DispIndex + 8*StrainIndex';
    % tline = strrep(tline, 'Assessment_Index = Min_SuMac + Sum_F_object + DispIndex + StrainIndex', fout7);
    % elseif a == 10
    % fout7 = 'Assessment_Index = Min_SuMac + 9*Sum_F_object + 9*DispIndex + 9*StrainIndex';
    % tline = strrep(tline, 'Assessment_Index = Min_SuMac + Sum_F_object + DispIndex + StrainIndex', fout7);
    % end
    fprintf(writefile,'%s \n',tline);
end
fclose(findfile);
fclose(writefile);
% 导入并运行Python 模块
%processpath = strcat('F:\pythonProject\FE_model_test\iter_main_process\main_process', SS,'.py');
command=['ABAQUS cae noGUI=',writefilepath];
disp(command)
%command=cat(2,command,fout);
command=strcat(command);
disp(command)
%commandStr = sprintf('abaqus cae noGUI=main_process.py -- %s %s %s',filepath1,filepath2,filepath3);
%disp(commandStr)
[status,cmdout]=system(command);
%展示cmd输出结果
disp(status)
disp(cmdout)
% 读取结果文件
outputpath = fullfile('F:\pythonProject\FE_model_test', fout4, 'output_index',fout5);
result = fileread(outputpath);
% 读取文件中的数字
result = jsondecode(result);
result = double(result.value);
%result = str2double(result);
%Py_Data_Process = py.importlib.import_module('data_process');
% 调用 Python 函数
%result = Py_Data_Process.Assessment_Index;
