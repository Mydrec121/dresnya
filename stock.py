#%%

import yfinance as yf
import numpy as np

start = '2010-01-01'
#start = '2016-01-01'
end = '2020-01-01'

usdrub = yf.download('USDRUB=X', start, end, interval='1mo', progress=False)
eurrub = yf.download('EURRUB=X', start, end, interval='1mo', progress=False)

usdrub.Close.plot()
eurrub.Close.plot()

#print(np.corrcoef(usdrub.Close.array, eurrub.Close.array))

#%%

usdraw = usdrub.Close.array
eurraw = eurrub.Close.array



rub_balance = 0
usd_balance = 0
eur_balance = 0

rub_only_balance = 0
usd_only_balance = 0
eur_only_balance = 0

spread = 5

for i in range(len(usdraw)):

    rub_only_balance += 100000.0 - (500.0 * usdraw[i])
    #rub_balance += 34000
    #usd_balance += 33000.0 / (usdraw[i] + spread)
    #eur_balance += 33000.0 / (eurraw[i] + spread)
    rub_balance += 50000 - (500.0 * usdraw[i])
    usd_balance += 50000.0 / (usdraw[i] + spread)

    eur_only_balance += 100000.0 / (eurraw[i] + spread)
    usd_only_balance += (100000.0 - (500.0 * usdraw[i])) / (usdraw[i] + spread)

final_balance = rub_balance + usd_balance * usdraw[-1] + eur_balance * eurraw[-1]
print('RUB:        ', "{:,}".format(int(rub_only_balance)))
print('RUB + hedge:', "{:,}".format(int(final_balance)))
print('USD only:   ', "{:,}".format(int(usd_only_balance * usdraw[-1])))
#print('EUR only:   ', "{:,}".format(int(eur_only_balance * eurraw[-1])))