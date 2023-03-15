#### CHANGE FILENAME TO stockConsole 

import stockMain as sm
import sys

### TURN INTO A CLASS 

def remove():
    remover = input('remove file? : ')
    if remover[0] == 'y':
        sm. manage().remove()
    else:
        print('Goodbye')

def getTicker():
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
    else:
        ticker = input(" Ticker Name : ")
    df = sm.multidatadownload(ticker).year().get()
    tickerObj = sm.TAF(df,ticker)
    return tickerObj
    
def commandInputs(tickerObject):
    go = True
    while go == True:
        cmd = input('What do you want to do ? : ')
        if cmd[0] == 'p': # plot 
            tickerObject.plot()
        if cmd[0] == '': # repeat prompt
            commandInputs(tickerObject)
        if cmd[0] == 'e': # exit system
            go = False
        if cmd[0] =='l': # list options with print statements
            pass
        if cmd[0] =='c':
            tickerObject.candleplot()
        if cmd[0] =='m':
            tickerObject.multiplot()
    print('Done')

def remove():
    remover = input('remove file? : ')
    if remover[0] == 'y':
        sm. manage().remove()
    else:
        print('Goodbye')

 

if __name__=="__main__":
    tickerObj = getTicker()
    commandInputs(tickerObj) ## the loop 
    print('do some code here')
    remove()
