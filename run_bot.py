import upstox_client
from datetime import datetime, timedelta, timezone
from upstox_client.rest import ApiException
import time
import numpy as np
import pandas as pd
acess_token='Upstox_acess_token_here'
class queue:
    def __init__(self):
        self.array = []
    def add(self,ele):
        if (len(self.array)==0 or len(self.array)!=10):
            self.array.append(ele)
        else:
            self.array.pop(0)
            self.array.append(ele)
    def array(self):
        return self.array
    
def get_intraday_data(instrument_key):
    api_instance = upstox_client.HistoryApi()
    api_response = api_instance.get_intra_day_candle_data(instrument_key, '1minute', '2.0')
    return api_response.data.candles
def get_hist_data(instrument_key,from_date,to_date):
    api_instance = upstox_client.HistoryApi()
    api_response = api_instance.get_historical_candle_data1(instrument_key,'1minute',to_date,from_date, '2.0')
    return api_response.data.candles

def process_data(data,data_q,mov_q,vol_data_q,vol_mov_q):
    data=np.array(data)
    data=data[:,1:].astype('float32') 
    
    vol_data_q.add(np.sum(data[:,4]))
    data_q.add([data[4,0],np.max(data[:,1]),np.min(data[:,2]),data[0,3]])
    if(len(mov_q.array)==0):
        mov_q.add(data_q.array[-1][3])
        vol_mov_q.add(vol_data_q.array[-1])

    else:
        mov_q.add(round(((mov_q.array[-1]+data_q.array[-1][3])/2),2))
        vol_mov_q.add(round((vol_mov_q.array[-1]+vol_data_q.array[-1])/2))
    return mov_q.array[-1],vol_mov_q.array[-1]


def cal_p_l(data,order_value,order_status,profit,stop_loss1):
    p_l=data- order_value
    if((order_status!='') and (p_l>=profit or p_l <= -stop_loss1)):
        print('profit or stoploss hit: squareoff..')
        return True,p_l
    else:
        return False,p_l
# def cal_p_l(data,order_value,order_status,profit1,stop_loss1):
#     global stop_loss
#     global profit
#     p_l=data- order_value
#     if(order_status!='' and(profit-p_l)<=10):
#         profit+=10
#         stop_loss=stop_loss-10
#     # elif(p_l>=15 and stop_loss==10):
#     #     stop_loss=0
    
#     if((order_status!='') and (p_l>=profit or p_l <= -stop_loss)):
#         print(f'profit or stoploss hit {stop_loss}: squareoff..')
#         return True,p_l
#     else:
#         return False,p_l

def place_order(instrument_key,order_type,price):
    global acess_token
    configuration = upstox_client.Configuration()
    configuration.access_token = acess_token
    api_instance = upstox_client.OrderApi(upstox_client.ApiClient(configuration))
    body = upstox_client.PlaceOrderRequest(quantity=50,product='I',validity='DAY',price=0,instrument_token=instrument_key,order_type='MARKET',transaction_type='BUY',disclosed_quantity=0,trigger_price=0,is_amo=False) # PlaceOrderRequest | 
    api_version = '2.0'


    try:
        api_response = api_instance.place_order(body, api_version)
        print(f'{order_type} order placed{instrument_key}')
        print(api_response)
        return order_type,instrument_key,api_response.status

    except ApiException as e:
        print("Exception when calling OrderApi->place_order: %s\n" % e)
        return "",instrument_key,api_response.status
    

def squareoff(instrument_key):
    global acess_token
    configuration = upstox_client.Configuration()
    configuration.access_token = acess_token
    api_instance = upstox_client.OrderApi(upstox_client.ApiClient(configuration))
    body = upstox_client.PlaceOrderRequest(quantity=50,product='I',validity='DAY',price=0,instrument_token=instrument_key,order_type='MARKET',transaction_type='SELL',disclosed_quantity=0,trigger_price=0,is_amo=False) # PlaceOrderRequest | 
    api_version = '2.0'

    try:
        api_response = api_instance.place_order(body, api_version)
        print(f'order squred off sucessfully {instrument_key}\n')
        print(api_response)
        return api_response.status
        
    except ApiException as e:
        print("Exception when calling OrderApi->place_order: %s\n" % e)
        return api_response.status


# def check_trap():
#     global data_q,vol_data_q,pe_data_q,pe_vol_data_q
#     if((vol_data_q.array[-2]>vol_data_q.array[-1])  and (candle_type(data_q.array[-1])=='green' and  candle_type(data_q.array[-2])=='red')):
#         if( data_q.array[-1][3]> data_q.array[-2][3] and abs((data_q.array[-1][3]-data_q.array[-1][0])/(data_q.array[-2][3]-data_q.array[-2][0]))>=0.4 ):
#             return True,'CE'
#         else:
#             return False,None
#     elif((pe_vol_data_q.array[-2]>pe_vol_data_q.array[-1])  and (candle_type(pe_data_q.array[-1])=='green' and candle_type(pe_data_q.array[-2])=='red')):
#         if( pe_data_q.array[-1][3]> pe_data_q.array[-2][3] and abs((data_q.array[-1][3]-data_q.array[-1][0])/(data_q.array[-2][3]-data_q.array[-2][0]))>=0.4 ):
#             return True,'PE'
#         else:
#             return False,None
#     else:
#         return False,None

def check_trap():
    global data_q,vol_data_q,pe_data_q,pe_vol_data_q
    
    if((vol_data_q.array[-2]>vol_data_q.array[-1] and vol_data_q.array[-2]>vol_data_q.array[-3] )  and (candle_type(data_q.array[-1])=='green' and  candle_type(data_q.array[-2])=='red')):
        if( data_q.array[-1][3]> data_q.array[-2][3] and abs(data_q.array[-1][3]-data_q.array[-1][0])/abs(data_q.array[-2][3]-data_q.array[-2][0])>=0.2 ):
            print("ratio: ",abs(data_q.array[-1][3]-data_q.array[-1][0])/abs(data_q.array[-2][3]-data_q.array[-2][0]))
            return True,'CE'
        else:
            return False,None
    elif((pe_vol_data_q.array[-2]>pe_vol_data_q.array[-1] and pe_vol_data_q.array[-2]>pe_vol_data_q.array[-3])  and (candle_type(pe_data_q.array[-1])=='green' and candle_type(pe_data_q.array[-2])=='red')):
        if( pe_data_q.array[-1][3]> pe_data_q.array[-2][3] and abs(pe_data_q.array[-1][3]-pe_data_q.array[-1][0])/abs(pe_data_q.array[-2][3]-pe_data_q.array[-2][0])>=0.2 ):
            return True,'PE'
        else:
            return False,None
    else:
        return False,None

def candle_type(data):
    if(data[0]>data[-1]):
        return 'red'
    else:
        return 'green'
    
def stop_loss_min(instrument_key):
    global order_value,order_status,profit,order_key,points,date
    stop_loss1=17.5
    api_instance = upstox_client.HistoryApi()
    max_time=time1()+timedelta(minutes=4)
    while(time1()<=max_time):
        api_response = api_instance.get_intra_day_candle_data(instrument_key, '1minute', '2.0')
        data=api_response.data.candles
        data=data[0][4]
        a,p_l=cal_p_l(data,order_value,order_status,profit,stop_loss1)
        if(a):
            squareoff(order_key)
            print("P&L: ",p_l)
            order_status=''
            points+=p_l
            order_value=0
        time.sleep(20)
    return None
    
def get_instrument_key(expiry):
    nifty=get_intraday_data("NSE_INDEX|Nifty 50")
    # strike_price=int(nifty[0][4]/50)*50
    strike_price=nifty[0][4]
    data=pd.read_csv(r"https://assets.upstox.com/market-quote/instruments/exchange/NSE.csv.gz",header=0)    
    data['expiry']= pd.to_datetime(data['expiry']).apply(lambda x:x.date())
    opt_idx=data[(data.instrument_type=="OPTIDX") & (data.tradingsymbol.str.startswith('NIFTY')) ]
    opt_idx=opt_idx[opt_idx.expiry==expiry.date()]
    opt_idx= opt_idx.sort_values(by=['expiry','strike'])
    pe=opt_idx[(opt_idx.option_type =='PE') & (opt_idx.strike==round(strike_price+150,-2))]['instrument_key'].values[0]
    ce=opt_idx[(opt_idx.option_type =='CE') & (opt_idx.strike==round(strike_price-150,-2))]['instrument_key'].values[0]
    return ce,pe
        
mov_q= queue()
data_q= queue()
vol_mov_q=queue()
vol_data_q=queue()

pe_mov_q= queue()
pe_data_q= queue()
pe_vol_mov_q=queue()
pe_vol_data_q=queue()

order_status=''
order_value=0
order_key=''

points=0
num_trades=0
stop_loss=10
profit=25
date=30
instrument_key1,instrument_key2="",""
get_key=True

start_time=datetime(2023, 10, date, 9, 30, 5,tzinfo=timezone(timedelta(seconds=19800)))
end_time=datetime(2023, 10, date, 15, 15, 5,tzinfo=timezone(timedelta(seconds=19800)))

# instrument_key1='NSE_FO|44154'
# instrument_key2='NSE_FO|44167'
def main(current='',Time_up=False):
    global date
    global data_q
    global mov_q
    global vol_mov_q
    global vol_data_q
    global pe_mov_q,pe_data_q,pe_vol_mov_q,pe_vol_data_q
    
    global order_status
    global order_value
    global start_time
    global end_time
    global profit 
    global stop_loss
    global num_trades,instrument_key1,instrument_key2,get_key,points,order_key


    order=True

    if(points>=25 or points<=-25):
        order=False
    # if(points<=-17.5 and time1()<=datetime(2023, 10, date, 13,0, 5,tzinfo=timezone(timedelta(seconds=19800)))):
    #     wait=True
    # else:
    #     wait=False

    if(time1()>=datetime(2023, 10, date, 14, 45, 0,tzinfo=timezone(timedelta(seconds=19800)))):
        profit=10
        order=False

    if(get_key):
        instrument_key1,instrument_key2=get_instrument_key(datetime(2023,11,2))  #change expiry here
        get_key=False
        data_ce=get_hist_data(instrument_key1,f"2023-10-{date-3}",f"2023-10-{date-3}")[:35]
        data_pe=get_hist_data(instrument_key2,f"2023-10-{date-3}",f"2023-10-{date-3}")[:35]
        for i in range(0,len(data_ce),5):
            mov_avg,vol_mov_avg=process_data(data_ce[i:i+5],data_q,mov_q,vol_data_q,vol_mov_q)
            pe_mov_avg,pe_vol_mov_avg = process_data(data_pe[i:i+5],pe_data_q,pe_mov_q,pe_vol_data_q,pe_vol_mov_q)
            
    data=get_intraday_data(instrument_key1)
    data2=get_intraday_data(instrument_key2)
    
    mov_avg,vol_mov_avg=process_data(data[0:5],data_q,mov_q,vol_data_q,vol_mov_q)
    pe_mov_avg,pe_vol_mov_avg = process_data(data2[0:5],pe_data_q,pe_mov_q,pe_vol_data_q,pe_vol_mov_q)   #data,data_q,mov_q,vol_data_q,vol_mov_q

    print('volume',vol_data_q.array[-1])
    
    if(order_status=='' and time1()>=start_time and order and num_trades<2):
        if (time1()<=datetime(2023, 10, date, 9, 35, 5,tzinfo=timezone(timedelta(seconds=19800)))):
            check,types=False,None
        else:
            check,types=check_trap()
            
        if ( (data_q.array[-1][3]>mov_avg or (check and types=='CE')) and vol_data_q.array[-1]>vol_mov_avg):
            print('cutted')
            order_status,order_key,res=place_order(instrument_key1,'CE',0)
            while(res!='success'):
                print("someting is wrong with placing order\ncheck.....")
                time.sleep(5)
                order_status,order_key,res=place_order(instrument_key1,'CE',0)
            order_value=data_q.array[-1][3]
            num_trades+=1
            print("placed at: ",order_value)
            print("Trapping",check,types)
        elif( (pe_data_q.array[-1][3]>pe_mov_avg or(check and types=='PE')) and pe_vol_data_q.array[-1]>pe_vol_mov_avg):
            print('cutted')
            order_status,order_key,res2=place_order(instrument_key2,'PE',0)
            while(res2!='success'):
                print("someting is wrong with placing order\ncheck.....")
                time.sleep(5)
                order_status,order_key,res2=place_order(instrument_key2,'PE',0)
            order_value=pe_data_q.array[-1][3]
            print("placed at: ",order_value)
            print("Trapping",check,types)
            num_trades+=1
        else:
            print('.')
    
    if(order_status=='PE'):
        val,P_L=cal_p_l(pe_data_q.array[-1][3],order_value,order_status,profit,stop_loss)
    else:
        val,P_L=cal_p_l(data_q.array[-1][3],order_value,order_status,profit,stop_loss)


    if(val or (Time_up and order_status!='')):
        sqf=squareoff(order_key)
        while(sqf!='success'):
            print("someting is wrong with squareoff\ncheck.....")
            time.sleep(5)
            sqf=squareoff(order_key)
        print("P&L: ",P_L)
        order_status=''
        points+=P_L
        order_value=0
    else:
        print("P&L: ",P_L)
        if(order_status=='CE'):
            try:
                stop_loss_min(instrument_key1)
            except:
                print("some error.............")
        elif(order_status=='PE'):
            try:
                stop_loss_min(instrument_key2)
            except:
                print("some error.............")
        else:
            print("")

    # time.sleep(0.5)   
    
def time1():
    dt = datetime.now(tz=timezone(timedelta(hours=5.5)))
    return dt


temp=datetime(2023, 10, date, 9, 20, 5,tzinfo=timezone(timedelta(seconds=19800)))
next_time=temp
while(time1()<=end_time):
    if(time1()>=next_time ):
        if(time1()>=datetime(2023, 10, date, 15, 10, 5,tzinfo=timezone(timedelta(seconds=19800)))):
            print(time1())
            main(Time_up=True)
            next_time=next_time+timedelta(minutes=5)
        elif(time1()>=temp):
            print("\n",time1())
            main()
            next_time=next_time+timedelta(minutes=5)
        else:
            time.sleep(10)
    else:
        time.sleep(10)
