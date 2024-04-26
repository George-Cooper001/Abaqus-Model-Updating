%optimization = @optimisefun;
%profile on;
% 初始猜测
%x0 = [0.00003, 0.0004, 0.000019, 0.00002];
% 约束等设置（如果有）
A = [];
b = [];
Aeq = [];
beq = [];
lb = [0.000026, 0.0002, 0.000009, 0.000005];
ub = [0.000033, 0.00072, 0.000024, 0.000035];
nonlcon = [];
% 随机生成5对初始猜测值
% initial_para = zeros(5,4);
% for i = 1:5
%     for j =1:4
%         initial_para(i,j) = round((lb(j) + (ub(j)-lb(j)) *rand),7);
%     end
% end
% disp(initial_para)
%disp(optimisefun(x0));
% initial_para = [0.0000265, 0.000225, 0.0000179, 0.00001; 0.0000275, 0.000325, 0.0000189, 0.00002; 0.0000295, 0.000485, 0.000021, 0.000028; 0.000031, 0.000585, 0.000022, 0.00003; 0.000032, 0.000685, 0.000023, 0.000032;
%                 0.00003, 0.00032, 0.000019, 0.00002; 0.00003, 0.00032, 0.000019, 0.00002; 0.00003, 0.00032, 0.000019, 0.00002];
initial_para = [0.00003, 0.00069, 0.0000095, 0.000008; 0.000028, 0.00049, 0.0000105, 0.000028; 0.0000265, 0.000225, 0.0000125, 0.00001; 0.0000295, 0.000325, 0.0000135, 0.000015; 0.0000305, 0.000525, 0.0000175, 0.00002
                0.0000315, 0.000625, 0.000019, 0.000025; 0.000032, 0.000695, 0.000021, 0.00003; 0.0000325, 0.000445, 0.000023, 0.000033];
% 设置优化选项，定义输出函数
for a = 3:8
    global nameaddnum
    nameaddnum=0;
    options = optimoptions('fmincon', 'Display', 'iter', 'Algorithm', 'sqp','MaxFunctionEvaluations',400,'FunctionTolerance',1e-4,'StepTolerance',1e-6,'UseParallel',false,'OutputFcn',@outfun);
    % 运行 fmincon
    [x,fval,exitflag,output,lambda,grad,hessian] = fmincon(@(x)optimisefun(x,a), initial_para(a,:), A, b, Aeq, beq, lb, ub, nonlcon, options);
    % 打印最终结果
    disp(['Best_Parameter:' num2str(x)]);
    disp(['Best_Assess_result:', num2str(fval)]);
end
% global nameaddnum
% nameaddnum=0;
% populationSize = 8;
% numParameters = 4;
% lowerBound = [0.000026, 0.0002, 0.000009, 0.000005];
% upperBound = [0.000033, 0.00072, 0.000024, 0.000035];
% initialPopulation = rand(populationSize, numParameters).*(upperBound - lowerBound) + lowerBound;
% 
% options = optimoptions('ga', 'PopulationSize', populationSize, 'OutputFcn', @outputFunction);
% [optimalParameters, minError] = ga(@optimisefun, numParameters, [], [], [], [], lowerBound, upperBound, [], options);

% 输出最优参数和误差
% disp('Optimal Parameters:');
% disp(optimalParameters);
% disp(['Minimum Error: ', num2str(minError)]);

% 自定义输出函数
function stop = outfun(x, optimValues, state)
    stop = false;
    switch state
        case 'iter'
        fprintf('当前迭代次数: %d', optimValues.iteration);
        fprintf('当前点x=[%f, %f]',x(1),x(2))
        fprintf('当前目标函数值：%d',optimValues.fval)
    end
end