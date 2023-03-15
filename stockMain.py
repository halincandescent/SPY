##
import pandas as pd
import shutil
import numpy as np
import talib
from talib import *
import os
import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import math
import mplfinance as mpf
import datetime as dt 


### CLASSES ###
class manage:
    def __init__(self,path='/Users/tate/Desktop/spy/',folder='dataframes'+'/'):
        self.path = path
        self.folder = folder
    def remove(self):
        try:
            shutil.rmtree(self.path+self.folder)
        except OSError as e:
             print("Error: %s : %s" % (dir_path, e.strerror))
## downloader
class datadownload:
    def __init__(self,ticker, period='1y',interval='1d',
                 path='/Users/tate/Desktop/spy/',folder='dataframes'+'/'):
        '''
        # 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        '''
        self.ticker = ticker
        self.period = period
        self.interval = interval
        self.path = path
        self.folder = folder + self.ticker
        self.file = self.ticker+self.period
        ## create directory if needed 
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        if not os.path.exists(self.folder+'/{}.csv'.format(self.file)):
            self.df = yf.download(self.ticker,period=self.period,interval=self.interval)
            self.df.to_csv(self.folder+'/{}.csv'.format(self.file))
        #set dataframe 
        self.df = pd.read_csv(self.path+ self.folder +'/'+self.file+'.csv',index_col=0,parse_dates=True)
    def get(self):
        return self.df
class multidatadownload:
    def __init__(self,ticker,path='/Users/tate/Desktop/spy/',
                 folder='dataframes'+'/'):
        self.ticker = ticker
        self.path = path
        self.folder = folder
    def day(self):
        '''
        downloads day data if not found
        '''
        self.day = datadownload(self.ticker,period='1d',interval='1m',
                                path=self.path,folder=self.folder)
        return self.day    
    def week(self):
        '''
        downloads week data if not found
        '''
        self.week = datadownload(self.ticker,period='5d',interval='1h',
                                path=self.path,folder=self.folder)
        return self.week
    def month(self):
        '''
        downloads month data if not found
        '''
        self.month = datadownload(self.ticker,period='1mo',interval='1d',
                                path=self.path,folder=self.folder)
        return self.month
    def year(self):
        '''
        downloads year data if not found
        '''
        self.year = datadownload(self.ticker,period='1y',interval='1d',
                                path=self.path,folder=self.folder)
        return self.year
    def multiyear(self,period='5y',interval='1d'):
        self.multiYear = datadownload(self.ticker,period=period,interval=interval,
                                path=self.path,folder=self.folder)





class TAF:

    def __init__(self,df,ticker='stock'):
        '''
        Initiates a TAF object with dataframe df 
        '''
        self.df = df
        ## convert index to datetime
        self.df.index = pd.to_datetime(self.df.index, utc=True).tz_convert('US/Eastern')
        self.ticker = ticker
        self.bbdf = None
        
    def __repr__(self): ## not checked
        '''
        String represation
        '''
        return f"TAF({self.ticker!r})"

    def __str__(self):## not checked 
        '''
        print function 
        '''
        return f"Technical Analysis : {self.ticker}"

    
    # indicator methods     

    def getBBands(self, period,nStd = 2):
        '''
        uses df, period and standard deviation multiple
        to return upper, middle and lower bollinger bands
        in a dataframe
        '''
        try:
            close = self.df['Close']
        except Exception as ex:
            return None

        try:
            upper, middle, lower = talib.BBANDS(
                                close.values, 
                                timeperiod=period,
                                # number of non-biased standard deviations from the mean
                                nbdevup=stdNbr,
                                nbdevdn=stdNbr,
                                # Moving average type: simple moving average here
                                matype=0)
        except Exception as ex:
            return None

        data = dict(upper=upper, middle=middle, lower=lower)
        bbdf = pd.DataFrame(data, index=bbdf.index, columns=['upper', 'middle', 'lower']).dropna()

        self.bbdf = bbdf

        return bbdf

    def sma(self,period):
        '''
        creates a SMA using Closing prices from dataframe subject to
        the period parameter
        '''
        return talib.SMA(self.df['Close'],period)

    def ema(self,period):
        '''
        creates exponential moving average like SMA 
        '''
        return talib.EMA(self.df['Close'],period)

    # momentum indicators 

    def macd(self): # momentum 
        '''
        creates moving average convergence/divergence with
        periods currently preset 
        '''
        macd, macdsignal, macdhist = talib.MACD(self.df['Close'],
                                                       fastperiod=12,
                                                       slowperiod=26,
                                                       signalperiod=9)
        return macd, macdsignal, macdhist

    def rsi(self):
        '''
        Relative Strength Indicator 
        '''
        real = RSI(self.df['Close'], timeperiod=14)
        return real


    # VWAP                                                
    def vwap(self):
        '''
        adds vwap to df for the entire period of dataframe 
        '''
        v = self.df['Volume'].values
        tp = (self.df['Low'] + self.df['Close'] + self.df['High']).div(3).values
        self.df = self.df.assign(VWAP=(tp * v).cumsum() / v.cumsum())
        ## not sure if this even works 

    def atr(self,period=14):
        high = self.df['High']
        low = self.df['Low']
        close = self.df['Close']
        real = talib.ATR(high,low,close,period)
        return real


    ### plot methods

    def candleplot(self): ### add optional arguments for MA's
        # needs work 
        '''
        -plots data based on lookback period in a candlestick chart
        -plots volume below in red/green color indicators
        - also plots moving averages, currently just 3 and 9 period
        '''
        data_select = self.df 
        ## new plots
        slowma = self.sma(3)
        fastma = self.sma(9)
        rsi = self.rsi()
        ## set up macd
        macd , signal, histogram = self.macd()
        hist = macd - signal 
        ## add plots to dictionary 
        apdict = [
                  #mpf.make_addplot(slowma,color='fuchsia'),
                  #mpf.make_addplot(fastma,color='b'),
                  mpf.make_addplot(hist,type='bar',width=0.7,panel=1,
                                   color='dimgray',alpha=1,secondary_y=False),
                  mpf.make_addplot(macd,color='fuchsia',panel=1,secondary_y=True),
                  mpf.make_addplot(signal,panel=1,color='b',secondary_y=True),
                  ]
         
        mpf.plot(data_select,type='candle',style='yahoo',
             title = self.ticker ,ylabel = 'Price',
             ylabel_lower = 'Shares \nTraded',
             volume=True,volume_panel=2, addplot=apdict, panel_ratios=(6,3,2))

    def plot(self): 
        '''
        Simple price plot method using matplotlib 
        '''
        # labels
        plt.suptitle(self.ticker)
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.plot(self.df['Close'],color='k')
        plt.show()
        #closeC = input("Close window? : ")
        #if closeC[0] == 'y':
         #   plt.close()
        
        
    def multiplot(self):
        '''
        multiple plots
        edit this 
        '''
        # indicators
        fifty = self.sma(50)
        twoHundred = self.sma(200)
        relative = self.rsi()
        vol = self.volume/1000000
        # plot 
        fig, (ax0, ax1,ax2) = plt.subplots(nrows=3, sharex=True)
        plt.suptitle(self.ticker)
        plt.xlabel('Time')
        ax0.set_ylabel('Price') 
        ax0.plot(self.df['Close'], color='k') # close plot price 
        ax0.plot(fifty, color='r')
        ax0.plot(twoHundred, color='b')
        ax1.set_ylabel('RSI') ## figure out how to set the fadded lines at 70 & 30 ? 
        ax1.plot(relative, color='g')
        ax2.set_ylabel('Volume') 
        ax2.bar(self.df.index,vol,color='r') ## scale by 1e6 
        plt.show()
    
    def help(self):
        '''
        print out different function names
        and their uses 
        '''
        ### write this ###
        pass 


class relativeStrength:
    '''
    Compares two indices, stock/indices, for relative strength
    can plot info
    '''
    def __init__(self,ticker=None,benchmark='SPY'):
        '''
        XLC (communication) 
        XLP (staples)
        XLY (discr) 
        XLE (energy)
        XLF (finance)
        XLV (health)
        XLI (industrial)
        XLB (materials) 
        XLRE (real estate) 
        XLK (tech) 
        XLU (utilities)
        SPY (Totality of SPDR) 
        '''
        self.ticker = ticker
        self.benchmark = benchmark
        self.set = False 
        self.tickDf = None
        self.benchDf = None
        self.rs = pd.DataFrame()
        
    def dfDownload(self):
        if self.ticker != None and self.benchmark != None:
            self.tickDf = multidatadownload(self.ticker).year().get()
            self.benchDf = multidatadownload(self.benchmark).year().get()
            self.set = True 
        elif self.ticker == None:
            print('Must set asset')
            self.set = False
        elif self.benchmark == None:
            print('Must set bench')
            self.set = False
        else:
            self.set = False 
    def setBenchmark(self,ticker):
        self.benchmark = benchmark
    def setTicker(self,bench):
        self.ticker = ticker
    def pctChange(self):
        if self.set == True:
            self.tickDf['Returns Daily'] = self.tickDf['Adj Close'].pct_change()
            self.benchDf['Returns Daily'] = self.benchDf['Adj Close'].pct_change()
            self.tickDf['Cum Returns'] = (self.tickDf['Returns Daily'] + 1).cumprod()
            self.benchDf['Cum Returns'] = (self.benchDf['Returns Daily'] + 1).cumprod()
        else:
            print('we got issues')
    def plotTicker(self):
        plt.suptitle(self.ticker)
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.plot(self.tickDf['Adj Close'],color='k')
        plt.show()
    def plotBenchmark(self):
        plt.suptitle(self.benchmark)
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.plot(self.benchDf['Adj Close'],color='k')
        plt.show()
    def plotRS(self):
        plt.suptitle('Relative Strength ' +self.ticker+'/'+self.benchmark)
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.plot(self.rs['Relative Strength'],color='k')
        plt.show()
    def plotRSCum(self):
        plt.suptitle('Relative Strength Cumulative ' +self.ticker+'/'+self.benchmark)
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.plot(self.rs['Relative Strength Cumulative'],color='k')
        plt.show()
    def relativeStrength(self):
        '''
        Daily returns
        '''
        if self.set ==True:
            self.pctChange()
        else:
            self.dfDownload()
            self.relativeStrength()
        #self.rs = pd.DataFrame()
        self.rs['Relative Strength'] = self.tickDf['Returns Daily']/self.benchDf['Returns Daily']  
    def relativeStrengthCum(self):
        '''
        Cumulative returns 
        '''
        if self.set ==True:
            self.pctChange()
        else:
            self.dfDownload()
            self.relativeStrengthCum()
        #self.rs = pd.DataFrame()
        self.rs['Relative Strength Cumulative'] = self.tickDf['Cum Returns']/self.benchDf['Cum Returns']
    def run(self):
        self.relativeStrength()
        self.relativeStrengthCum()

    def plotter(self):
        # combo of plots 
        fig, (ax0, ax1) = plt.subplots(nrows=2, sharex=True, gridspec_kw={'height_ratios':[2,1]})
        fig.suptitle('Stock and cumulative relative strength')
        plt.xlabel('Time')
        ax0.set_ylabel('Price')
        ax1.set_ylabel('RS')
        ax1.plot(self.rs['Relative Strength Cumulative'],color='k')
        ax0.plot(self.tickDf['Adj Close'],color='b')
        plt.show()

            
#########################################

## testing relative strength to understand

ticker = 'TSLA'
rs = relativeStrength(ticker=ticker)
