import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

date = [datetime.datetime(2017, 8, 24, 0, 0), datetime.datetime(2017, 8, 23, 0, 0), \
datetime.datetime(2017, 8, 22, 0, 0), datetime.datetime(2017, 8, 21, 0, 0), \
datetime.datetime(2017, 8, 18, 0, 0), datetime.datetime(2017, 8, 17, 0, 0), \
datetime.datetime(2017, 8, 16, 0, 0), datetime.datetime(2017, 8, 15, 0, 0), \
datetime.datetime(2017, 8, 14, 0, 0), datetime.datetime(2017, 8, 11, 0, 0), \
datetime.datetime(2017, 8, 10, 0, 0), datetime.datetime(2017, 8, 9, 0, 0), \
datetime.datetime(2017, 8, 8, 0, 0), datetime.datetime(2017, 8, 7, 0, 0), \
datetime.datetime(2017, 8, 4, 0, 0), datetime.datetime(2017, 8, 3, 0, 0), \
datetime.datetime(2017, 8, 2, 0, 0), datetime.datetime(2017, 8, 1, 0, 0)]



start = date[0] #is a datetime.datetime object according to type
end = date[-1]  #is a datetime.datetime object according to type   
delta = datetime.timedelta(days=1)
dates = mdates.drange(end, start, delta)
y_data = range(len(dates))
print(dates)
plt.plot_date(dates, y_data)
plt.show()