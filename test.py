import time
t=time.time()
print(t)
ct=time.ctime()
print(ct)
lt=time.localtime()
print(lt)
print('which year:',lt.tm_year) #现在是哪一年
print('month of the year',lt.tm_mon) #现在是一年中的哪个月份
print('day of the month:',lt.tm_mday) #今天是几号（一个月中的第几天）
print('hour of the day:',lt.tm_hour) #现在是几点（一天中的第几个小时）
print('second of the minute:',lt.tm_sec) #现在是一分钟的第几秒
print('minute of the hour:',lt.tm_min) #现在是哪一个分钟（10点18分）
print('day of the week:',lt.tm_wday) #现在是周几（0表示周一）
print('day of the year:',lt.tm_yday) #现在是一年中的第189天（感叹一下大半年过去了……）
print(lt.tm_isdst) #现在是否是夏令时（－1为是，0表示不是，中国好像没有夏令时制）

time.sleep(3) #后面的语句要等3秒才会显示出来
ts=time.strftime('%Y-%m-%d-%H:%M:%S')
print(ts)