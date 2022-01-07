function [] = study_rent(rent_filename, estimation_date_str, road)
% study rent in moonji-dong
%
% [input]
% - rent_filename: rent filename. to get rent file, run "study_rent.py"
% - estimation_date_str: '20211207', yyyymmdd
% - road: road condition. one of '12m', '25m', 'all'
%
% [usage]
% study_rent('mooji_house_rent_20211127.xlsx', '20211207', 'all');

plot_graph = 1;

switch road
    case {'12m', '25m', 'all'}
    otherwise
        fprintf("#### road: one of '12m', '25m', 'all'\n");
        return;
end

% rent(deposit, month) conversion rate
% https://kosis.kr/statHtml/statHtml.do?orgId=408&tblId=DT_30404_N0010
conv_filename = 'daejeon_yuseong_rent_conversion_rate.xls';
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
assume_conv = [202110, 6.7; 202111, 6.7];
conv = [conv; assume_conv];

% to get rent file, run "study_rent.py"
% rent_filename = 'rent_20211127.xlsx';
[rent, rent_txt, rent_raw] = xlsread(rent_filename);
rent;
rent_txt;
rent_raw;
[row_len, col_len] = size(rent);

% "rent" array column meaning:
% 1: {'road_under_m'} = 15, 25, 0(na)  
% 2: {'area_m2'}    
% 3: {'rent_type'} = 0(deposit rent only), 1(mixed), 2(month rent only)    
% 4: {'contract_yyyymm'}    
% 5: {'contract_dd'}
% 6: {'deposit_rent_1e4'}    
% 7: {'month_rent_1e4'}    
% 8: {'build_yyyy'} = 0(na)

% add "converted deposit rent" column
conv_deposit_rent_1e4 = zeros(row_len, 1);
for n = 1 : row_len
    switch rent(n, 3)
        case 0
            conv_deposit_rent_1e4(n) = rent(n, 6);
        case {1, 2}
            conv_percent = get_rent_conversion_rate(conv, rent(n, 4));
            conv_deposit_rent_1e4(n) = rent(n, 6) + rent(n, 7) * 12 / (conv_percent / 100);
    end
end

[rent(:, 6), rent(:, 7), conv_deposit_rent_1e4];

% add "converted deposit rent per m2" column
conv_deposit_rent_m2_1e4 = conv_deposit_rent_1e4 ./ rent(:, 2);
conv_deposit_rent_m2_1e4;

rent = [rent, conv_deposit_rent_m2_1e4];
% rent array column meaning: 
% 9: conv_deposit_rent_m2_1e4
size(rent);

switch road
    case {'12m'}
        idx = rent(:, 1) == 12;
        curve_fit_and_plot(rent(idx, :), estimation_date_str, road, plot_graph);
    case {'25m'}
        idx = rent(:, 1) == 25;
        curve_fit_and_plot(rent(idx, :), estimation_date_str, road, plot_graph);
    otherwise
        curve_fit_and_plot(rent, estimation_date_str, road, plot_graph);
end

plot_monthly_transaction_count(rent);

plot_rent_area(rent);

plot_rent_area_histogram(rent);

% print contract data of anomaly case to check why
% rent(752, 4:5)
% rent(103, 4:5)

end

function [] = plot_rent_area(rent)

contract_yyyymm = rent(:, 4);
contract_dd = rent(:, 5);
contract_date_str = [num2str(contract_yyyymm), num2str(contract_dd, '%02d')];

contract_datenum = datenum(contract_date_str, 'yyyymmdd');

figure;
plot(contract_datenum, rent(:, 2));
datetick('x', 'yy/mm', 'keepticks');
xlim([contract_datenum(1) contract_datenum(end)]);
xlabel('transaction date (yy/mm)');
ylabel('m2');
grid on;
title('[mooji house] rent area');

end

function [] = plot_rent_area_histogram(rent)

area_m2 = rent(:, 2);

edges = min(area_m2):10:max(area_m2);
figure;
histogram(area_m2, edges);
xlabel('rent area (m2)');
ylabel('count');
grid on;
title('[mooji house] rent area distribution');

end

function [] = plot_monthly_transaction_count(rent)

contract_yyyymm = rent(:, 4);

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
% 3: month rent only 
count_per_month = zeros(yyyymm_len, 3);
for n = 1 : yyyymm_len
    count_per_month(n, 1) = sum((rent(:, 4) == yyyymm(n)) & (rent(:, 3) == 0));
    count_per_month(n, 2) = sum((rent(:, 4) == yyyymm(n)) & (rent(:, 3) == 1));
    count_per_month(n, 3) = sum((rent(:, 4) == yyyymm(n)) & (rent(:, 3) == 2));
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
title('[mooji house] monthly rent transaction count');
legend('deposit only', 'mixed', 'monthly only', 'sum');


end

function [] = curve_fit_and_plot(rent, estimation_date_str, road, plot_graph)

% use curve fit to get linear estimation
% use exact "x"
contract_yyyymm = rent(:, 4);
contract_dd = rent(:, 5);
contract_date_str = [num2str(contract_yyyymm), num2str(contract_dd, '%02d')];
x_tick = num2str(contract_yyyymm - 200000);

contract_datenum = datenum(contract_date_str, 'yyyymmdd');

estimation_datenum_0 = datenum(estimation_date_str, 'yyyymmdd') - contract_datenum(1);
contract_datenum_0 = contract_datenum - contract_datenum(1);
average_transaction_delta_day = round(mean(diff(contract_datenum_0)));
x = contract_datenum_0;
y = rent(:, 9);
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
    smoothed = smooth(rent(:, 9), span);
    fprintf('### moving average duration = %d days\n', average_transaction_delta_day * span);
    
    figure;
    % plot(rent(:, 9));
    plot(contract_datenum, [rent(:, 9), smoothed]);
    % xlim([contract_datenum(1) contract_datenum(end)]);
    datetick('x', 'yy/mm', 'keepticks');
    xlim([contract_datenum(1) contract_datenum(end)]);
    xlabel('transaction date (yy/mm)');
    ylabel('1e4');
    grid on;
    title(sprintf('[moonji house] converted deposit rent per m2 (road = %s, MA = %d days)', ...
        road, average_transaction_delta_day * span));   
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
