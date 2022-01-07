
import pandas as pd
import numpy as np

def get_gift_tax_couple(gift_price, couple_gift_deduction):

   # couple_gift_deduction = 6e8

   tax_basis = gift_price - couple_gift_deduction

   if tax_basis <= 0:
      tax = 0
   elif tax_basis <= 1e8:
      tax = tax_basis * 0.1
   elif tax_basis <= 5e8:
      tax = tax_basis * 0.2 - 1e7
   elif tax_basis <= 10e8:
      tax = tax_basis * 0.3 - 6e7
   elif tax_basis <= 30e8:
      tax = tax_basis * 0.4 - 1.6e8
   else:
      tax = tax_basis * 0.5 - 4.6e8

   return tax

'''
function [gift_tax] = get_gift_tax_couple(gift_price)

couple_gift_deduction = 6e8;

tax_basis = gift_price - couple_gift_deduction;

if tax_basis <= 0
    gift_tax = 0;
elseif tax_basis <= 1e8
    gift_tax = tax_basis * 0.1;
elseif tax_basis <= 5e8
    gift_tax = tax_basis * 0.2 - 1e7;
elseif tax_basis <= 1e9
    % =(D8-600000000)*30%-60000000
    gift_tax = tax_basis * 0.3 - 6e7;
elseif tax_basis <= 3e9
    gift_tax = tax_basis * 0.4 - 1.6e8;
else
    gift_tax = tax_basis * 0.5 - 4.6e8;
end

end
'''

def get_land_transfer_tax_asess(tax_basis):

   if tax_basis <= 0.12e8:
      tax = tax_basis * 0.16
   elif tax_basis <= 0.46e8:
      tax = tax_basis * 0.25 - 1.08e6
   elif tax_basis <= 0.88e8:
      tax = tax_basis * 0.34 - 5.22e6
   elif tax_basis <= 1.5e8:
      tax = tax_basis * 0.45 - 1.49e7
   elif tax_basis <= 3e8:
      tax = tax_basis * 0.48 - 1.94e7
   elif tax_basis <= 5e8:
      tax = tax_basis * 0.5 - 2.54e7
   else:
      tax = tax_basis * 0.52 - 3.54e7

   return tax

'''
function [transfer_tax] = get_land_transfer_tax_asess(tax_basis)
% only valid for land, not building

if tax_basis <= 0.12e8
    transfer_tax = tax_basis * 0.16;
elseif tax_basis <= 0.46e8
    transfer_tax = tax_basis * 0.25 - 1.08e6;
elseif tax_basis <= 0.88e8
    transfer_tax = tax_basis * 0.34 - 5.22e6;
elseif tax_basis <= 1.5e8
    transfer_tax = tax_basis * 0.45 - 1.49e7;
elseif tax_basis <= 3e8
    transfer_tax = tax_basis * 0.48 - 1.94e7;
elseif tax_basis <= 5e8
    transfer_tax = tax_basis * 0.5 - 2.54e7;
else
    transfer_tax = tax_basis * 0.52 - 3.54e7;
end
'''

def compute_optimum_gift_ratio(hy_ratio, gift_price, transfer_price_2027):

   sh_ratio = 1 - hy_ratio

   acquisition_tax_rate = 0.04
   long_keep_deduction_rate = 0.02
   local_tax_rate = 0.1

   transfer_income_basic_deduction = 2.5e6
   couple_gift_deduction = 6e8

   initial_acquisition_price = 157380335
   initial_necessary_expense = 3385243
   standard_price_2021 = 599092200

   sh_keep_year = 15
   hy_keep_year = 5

   # gift_price = current_market_price

   t = pd.DataFrame( \
      index=['transfer price', 'acquisition price', 'necessary expense', 'transfer margin', \
         'long keep deduction', 'total transfer income', 'transfer income basic deduction', \
            'tax basis', 'asess tax', 'pay tax', 'local tax'], columns=['sh', 'hy'])
   
   # tax_table.loc['transfer price', 'sh'] = transfer_price_2027 * sh_ratio
   # tax_table.loc['transfer price', 'hy'] = transfer_price_2027 * hy_ratio
   t.iloc[0, 0] = transfer_price_2027 * sh_ratio
   t.iloc[0, 1] = transfer_price_2027 * hy_ratio

   # tax_table.loc['acquisition price', 'sh'] = initial_acquisition_price * sh_ratio
   # tax_table.loc['acquisition price', 'hy'] = gift_price * hy_ratio
   t.iloc[1, 0] = initial_acquisition_price * sh_ratio
   t.iloc[1, 1] = gift_price * hy_ratio

   # tax_table.loc['necessary expense', 'sh'] = initial_necessary_expense * sh_ratio
   # tax_table.loc['necessary expense', 'hy'] = standard_price_2021 * acquisition_tax_rate * hy_ratio
   t.iloc[2, 0] = initial_necessary_expense * sh_ratio
   t.iloc[2, 1] = standard_price_2021 * acquisition_tax_rate * hy_ratio

   hy_acquisition_tax = t.iloc[2, 1]

   # transfer margin
   t.iloc[3, 0] = t.iloc[0, 0] - t.iloc[1, 0] - t.iloc[2, 0]
   t.iloc[3, 1] = t.iloc[0, 1] - t.iloc[1, 1] - t.iloc[2, 1]

   # long keep deduction
   t.iloc[4, 0] = t.iloc[3, 0] * long_keep_deduction_rate * sh_keep_year
   t.iloc[4, 1] = t.iloc[3, 1] * long_keep_deduction_rate * hy_keep_year

   # total transfer income
   t.iloc[5, 0] = t.iloc[3, 0] - t.iloc[4, 0]
   t.iloc[5, 1] = t.iloc[3, 1] - t.iloc[4, 1]

   # transfer income basic deduction
   t.iloc[6, 0] = transfer_income_basic_deduction
   t.iloc[6, 1] = transfer_income_basic_deduction

   # tax basis
   t.iloc[7, 0] = t.iloc[5, 0] - t.iloc[6, 0]
   if t.iloc[7, 0] <= 0:
      t.iloc[7, 0] = 0
   t.iloc[7, 1] = t.iloc[5, 1] - t.iloc[6, 1]
   if t.iloc[7, 1] <= 0:
      t.iloc[7, 1] = 0

   # asess tax
   t.iloc[8, 0] = get_land_transfer_tax_asess(t.iloc[7, 0])
   t.iloc[8, 1] = get_land_transfer_tax_asess(t.iloc[7, 1])

   # pay tax
   t.iloc[9, 0] = t.iloc[8, 0]
   t.iloc[9, 1] = t.iloc[8, 1]

   # local tax
   t.iloc[10, 0] = t.iloc[9, 0] * local_tax_rate
   t.iloc[10, 1] = t.iloc[9, 1] * local_tax_rate

   # total transfer tax
   total_transfer_tax = np.sum(t.iloc[9:11, 0:2].values)

   sh_gift_price = gift_price * hy_ratio
   sh_gift_tax = get_gift_tax_couple(sh_gift_price, couple_gift_deduction)
   
   return total_transfer_tax, hy_acquisition_tax, sh_gift_tax


if __name__ == "__main__":

   hy_ratio = .5
   gift_price = 12.5e8 
   transfer_price_2027 = 13.5e8

   total_transfer_tax, hy_acquisition_tax, sh_gift_tax = \
      compute_optimum_gift_ratio(hy_ratio, gift_price, transfer_price_2027)

'''
function [total_tax, total_transfer_tax, sh_gift_tax, hy_acquisition_tax] = ...
    compute_optimum_gift_ratio(hy_ratio, current_market_price, transfer_price_2027)
% compute optimum gift ratio
%
% [input]
% - hy_ratio: hy ratio for gift, 0 ~ 1
% - current_market_price: current market price, same as gift price
% [usage]
% compute_optimum_gift_ratio(.5, 12e8, 15e8)
% 

% hy_ratio = 0.5;
sh_ratio = 1 - hy_ratio;

acquisition_tax_rate = 0.04;
longterm_posession_rate = 0.02;
local_tax_rate = 0.1;

transfer_income_basic_deduction = 2.5e6;

initial_acquisition_price = 157380335; 
initial_necessary_expense = 3385243;
standard_price_2021 = 599092200;

sh_posession_year = 15;
hy_posession_year = 5;

% sell price after 5 years
% transfer_price_2027 = 15e8;
% current market price at gift time
% current_market_price = 1.2e9;
gift_price = current_market_price;

sh_transfer_price = transfer_price_2027 * sh_ratio;
hy_transfer_price = transfer_price_2027 * hy_ratio;

sh_acquisition_price = initial_acquisition_price * sh_ratio;
hy_acquisition_price = current_market_price * hy_ratio;

sh_necessary_expense = initial_necessary_expense * sh_ratio;
hy_necessary_expense = standard_price_2021 * acquisition_tax_rate * hy_ratio;
hy_acquisition_tax = hy_necessary_expense;

sh_transfer_margin = sh_transfer_price - sh_acquisition_price - sh_necessary_expense;
hy_transfer_margin = hy_transfer_price - hy_acquisition_price - hy_necessary_expense;

sh_longterm_posession_deduction = sh_transfer_margin * longterm_posession_rate * sh_posession_year;
hy_longterm_posession_deduction = hy_transfer_margin * longterm_posession_rate * hy_posession_year;

sh_total_transfer_income_price = sh_transfer_margin - sh_longterm_posession_deduction;
hy_total_transfer_income_price = hy_transfer_margin - hy_longterm_posession_deduction;

sh_tax_basis = sh_total_transfer_income_price - transfer_income_basic_deduction;
if sh_tax_basis <= 0
    sh_tax_basis = 0;
end
    
hy_tax_basis = hy_total_transfer_income_price - transfer_income_basic_deduction;
if hy_tax_basis <= 0
    hy_tax_basis = 0;
end

% get_transfer_tax_asess: only valid for land, not building
sh_asess_tax = get_land_transfer_tax_asess(sh_tax_basis);
hy_asess_tax = get_land_transfer_tax_asess(hy_tax_basis);

sh_pay_tax = sh_asess_tax;
hy_pay_tax = hy_asess_tax;

sh_local_tax = sh_pay_tax * local_tax_rate;
hy_local_tax = hy_pay_tax * local_tax_rate;

total_transfer_tax = sh_pay_tax + hy_pay_tax + sh_local_tax + hy_local_tax;
fprintf('##### total transfer tax(sh + hy) = %.0f\n', total_transfer_tax);
fprintf('##### acquisition tax(hy) = %.0f\n', hy_acquisition_tax);

sh_gift_price = gift_price * hy_ratio;
sh_gift_tax = get_gift_tax_couple(sh_gift_price);

fprintf('##### gift tax(sh) = %.0f\n', sh_gift_tax);

total_tax = total_transfer_tax + hy_acquisition_tax + sh_gift_tax;
fprintf('##### total tax(sh + hy) = %.0f\n', total_tax);

end

'''