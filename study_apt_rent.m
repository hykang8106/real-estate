function [rent] = study_apt_rent(rent_filename, estimation_date_str)
% study apt rent in moonji-dong for comparison with dual use house
%
% [input]
% - rent_filename: 
% - estimation_date_str: '20211207', yyyymmdd
%
% [usage]
% study_apt_rent('moonji_hyosung_apt_rent_20211129.xlsx', '20211207');
% study_apt_rent('jeonmin_expo_apt_rent_20211128.xlsx', '20211207');
% study_apt_rent('jeonmin_narae_apt_rent_20211119.xlsx', '20211207');
% study_apt_rent('jeonmin_samsung_apt_rent_20211112.xlsx', '20211207');
% study_apt_rent('jeonmin_sejong_apt_rent_20211125.xlsx', '20211207');

plot_graph = 1;

% get apt name from filename
idx = strfind(rent_filename, '_apt');
apt_name = rent_filename(1 : idx - 1);

% rent(deposit, month) conversion rate
% https://kosis.kr/statHtml/statHtml.do?orgId=408&tblId=DT_30404_N0010
conv_filename = 'daejeon_yuseong_apt_rent_conversion_rate.xls';
% open excel file to get range
xlrange = 'D1:BJ2';
[conv_percent, conv_txt, conv_raw] = xlsread(conv_filename, xlrange);
conv_percent;
conv_txt;
conv_raw;

conv_len = length(conv_txt);
conv_yyyymm = zeros(conv_len, 1);
for n = 1 : conv_len
    a = conv_txt{n};
    % 'a' example: '2016. 11'
    conv_yyyymm(n) = str2double([a(1:4), a(7:8)]);
end
conv_yyyymm;
conv = [conv_yyyymm, conv_percent'];
conv;
% as of 20211208, last conv_yyyymm downloaded from kosis.kr was 202109, 
% so add assumed conv 
% ####### must update every month when real data is available
assume_conv = [202110, 4.6; 202111, 4.6];
conv = [conv; assume_conv];

% to get rent file, run "study_apt_rent.py"
% rent_filename = 'apt_rent_20211129.xlsx';
[rent, rent_txt, rent_raw] = xlsread(rent_filename);
rent;
rent_txt;
rent_raw;
[row_len, col_len] = size(rent);

% "rent" array column meaning:  
% 1: {'rent_type'} = 0(deposit rent only), 1(mixed)   
% 2: {'area_m2'}    
% 3: {'contract_yyyymm'}    
% 4: {'contract_dd'}
% 5: {'deposit_rent_1e4'}    
% 6: {'month_rent_1e4'}    
% 7: {'floor'}

% add "converted deposit rent" column
rent_type = rent(:, 1);
area_m2 = rent(:, 2);
deposit_rent_1e4 = rent(:, 5);
month_rent_1e4 = rent(:, 6);
contract_yyyymm = rent(:, 3);
contract_dd = rent(:, 4);

conv_deposit_rent_1e4 = zeros(row_len, 1);
for n = 1 : row_len
    switch rent_type(n)
        case 0
            conv_deposit_rent_1e4(n) = deposit_rent_1e4(n);
        case 1
            conv_percent = get_rent_conversion_rate(conv, contract_yyyymm(n));
            conv_deposit_rent_1e4(n) = deposit_rent_1e4(n) + month_rent_1e4(n) * 12 / (conv_percent / 100);
    end
end

[deposit_rent_1e4, month_rent_1e4, conv_deposit_rent_1e4];

% add "converted deposit rent per m2" column
conv_deposit_rent_m2_1e4 = conv_deposit_rent_1e4 ./ area_m2;
conv_deposit_rent_m2_1e4;

rent = [rent, conv_deposit_rent_m2_1e4];
% rent array column meaning: 
% 8: conv_deposit_rent_m2_1e4
size(rent);

curve_fit_and_plot(conv_deposit_rent_m2_1e4, contract_yyyymm, contract_dd, ...
    estimation_date_str, plot_graph, apt_name);

plot_monthly_transaction_count(contract_yyyymm, rent_type, apt_name);

% plot_rent_area(area_m2, contract_yyyymm, contract_dd);

plot_rent_area_histogram(area_m2, apt_name);

% print contract data of anomaly case to check why
% rent(752, 4:5)
% rent(103, 4:5)

end

function [] = plot_rent_area(area_m2, contract_yyyymm, contract_dd)

contract_date_str = [num2str(contract_yyyymm), num2str(contract_dd, '%02d')];

contract_datenum = datenum(contract_date_str, 'yyyymmdd');

figure;
plot(contract_datenum, area_m2);
datetick('x', 'yy/mm', 'keepticks');
xlim([contract_datenum(1) contract_datenum(end)]);
xlabel('transaction date (yy/mm)');
ylabel('m2');
grid on;
title('apt rent area');

end

function [] = plot_rent_area_histogram(area_m2, apt_name)

figure;
histogram(area_m2);
xlabel('rent area (m2)');
ylabel('count');
grid on;
title(sprintf('[%s] apt rent area distribution', apt_name), 'Interpreter','none');

end

function [] = plot_monthly_transaction_count(contract_yyyymm, rent_type, apt_name)

% get year, month sequence (= "yyyymm")
start_yyyymm = contract_yyyymm(1);
end_yyyymm = contract_yyyymm(end);
yyyymm = start_yyyymm:end_yyyymm;
idx = (mod(yyyymm, 100) <= 12) & (mod(yyyymm, 100) ~= 0);
yyyymm = yyyymm(idx);

yyyymm_len = length(yyyymm);
% "count_per_month" column meaning:
% 1: deposit rent only
% 2: mixed rent (= deposit + month) 
count_per_month = zeros(yyyymm_len, 2);
for n = 1 : yyyymm_len
    count_per_month(n, 1) = sum((contract_yyyymm == yyyymm(n)) & (rent_type == 0));
    count_per_month(n, 2) = sum((contract_yyyymm == yyyymm(n)) & (rent_type == 1));
end
count_per_month;

% must make "yyyymm" to column vector
yyyymm = yyyymm(:);
% add half month string(= '15' days) to use "datetick" function in x axis
date_str = num2str(yyyymm * 100 + 15);
x = datenum(date_str, 'yyyymmdd');
length(x);

figure;
plot(x, [count_per_month, sum(count_per_month, 2)]);
datetick('x', 'yy/mm', 'keepticks');
xlabel('transaction year/month (yy/mm)');
ylabel('count');
grid on;
title(sprintf('[%s] apt monthly rent transaction count', apt_name), 'Interpreter','none');
legend('deposit only', 'mixed', 'sum');

end

function [] = curve_fit_and_plot(conv_deposit_rent_m2_1e4, ...
    contract_yyyymm, contract_dd, estimation_date_str, plot_graph, apt_name)

% use curve fit to get linear estimation
% use exact "x"
% contract_yyyymm = rent(:, 4);
% contract_dd = rent(:, 5);
contract_date_str = [num2str(contract_yyyymm), num2str(contract_dd, '%02d')];
x_tick = num2str(contract_yyyymm - 200000);

contract_datenum = datenum(contract_date_str, 'yyyymmdd');

estimation_datenum_0 = datenum(estimation_date_str, 'yyyymmdd') - contract_datenum(1);
contract_datenum_0 = contract_datenum - contract_datenum(1);
average_transaction_delta_day = round(mean(diff(contract_datenum_0)));
x = contract_datenum_0;
y = conv_deposit_rent_m2_1e4;
f = fit(x, y, 'poly1');
f;

coeff_values = coeffvalues(f);
conf_int = confint(f);
x = estimation_datenum_0;
p1 = [coeff_values(1); conf_int(:, 1)];
p2 = [coeff_values(2); conf_int(:, 2)];
y = p1 * x + p2;
fprintf('#### [estimation date: %s] converted deposit rent per m2 (1e4): %f (%f ~ %f)\n', ...
    estimation_date_str, y(1), y(2), y(3));

if plot_graph
    % use "smooth" function to remove outlier
    % "average_transaction_delta_day" * "span" is moving average duration
    % "average_transaction_delta_day" is 2 days,
    % so "15" mean moving average duration is 30 days
    span = 15;
    smoothed = smooth(conv_deposit_rent_m2_1e4, span);
    fprintf('### moving average duration = %d days\n', average_transaction_delta_day * span);
    
    figure;
    % plot(rent(:, 9));
    plot(contract_datenum, [conv_deposit_rent_m2_1e4, smoothed]);
    % xlim([contract_datenum(1) contract_datenum(end)]);
    datetick('x', 'yy/mm', 'keepticks');
    xlim([contract_datenum(1) contract_datenum(end)]);
    xlabel('transaction date (yy/mm)');
    ylabel('1e4 KRW');
    grid on;
    title(sprintf('[%s] apt converted deposit rent per m2 (MA = %d days)', ...
        apt_name, average_transaction_delta_day * span), 'Interpreter','none');   
end

end

function [conv_percent] = get_rent_conversion_rate(conv, contract_yyyymm)

% "conv" array column meaning:
% 1: conv_yyyymm 
% 2: conv_percent

conv_yyyymm = conv(:, 1);

idx = conv_yyyymm == contract_yyyymm;
conv_percent = conv(idx, 2);

end
