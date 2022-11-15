from breeze_connect import BreezeConnect
import time
from datetime import datetime, timedelta, time as dtime
import urllib
import pyttsx3
import pandas as pd
from tabulate import tabulate
import os

# appkey: 3C8+53q6f5=8718A568z90Z9a5*0B879
# session key url: https://api.icicidirect.com/apiuser/login?api_key=%33%43%38%2b%35%33%71%36%66%35%3d%38%37%31%38%41%35%36%38%7a%39%30%5a%39%61%35%2a%30%42%38%37%39
# secretkey: u9+8J4j14A95(06367U661S4i22G613)


def sayOutLoud(sentence):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id)
    engine.say(sentence)
    engine.runAndWait()


def ttsRunForever(openTime, closeTime):
    print("running1")

    i = 0
    print("running2")
    x = 0
    ordersAtRuntime = breeze.get_order_list(
        exchange_code="BSE", from_date=openTime, to_date=closeTime
    )["Success"]
    ongoingLimitOrders = []
    ongoingOrders = []
    if ordersAtRuntime != None:
        i = len(ordersAtRuntime)

    while 1:
        time.sleep(5)
        orderList = breeze.get_order_list(
            exchange_code="BSE",
            from_date=openTime,
            to_date=closeTime,
        )["Success"]

        print(f"i:{i}, x:{x}")
        print(f"{openTime} , {closeTime}")

        if orderList != None:
            x = len(orderList)

        if x != i:
            orderList.reverse()
            newOrder = orderList[x - 1]
            tts = f"{newOrder['stock_code']} {newOrder['action']} quantity {newOrder['quantity']} {newOrder['status']} at rate {newOrder['price']}"
            sayOutLoud(tts)
            i += 1

        for order in orderList:
            if order["status"] == "Ordered" and order["order_type"] == "Limit":
                ongoingLimitOrders.append(order)
            if order["status"] != "Executed":
                ongoingOrders.append(order)

        for order in ongoingLimitOrders:
            if order["status"] == "Executed":
                tts = f"""{order['stock_code']} {order['order_type']} quantity {order['quantity']} executed at rate {order['price']} total price is 
                    {int(order['quantity'])*float(order['price'])}"""
                sayOutLoud(tts)
                ongoingLimitOrders.remove(order)

        for order in ongoingOrders:
            if order["status"] == "Cancelled":
                tts = f"""{order['stock_code']} {order['order_type']} quantity {order['quantity']} Cancelled"""
                sayOutLoud(tts)
                ongoingLimitOrders.remove(order)


order1 = "notExecuted"


def on_ticks(ticks):
    global order1
    openPrice = ticks["open"]
    closePrice = ticks["close"]
    timeNow = datetime.now()
    if timeNow.hour >= 12:
        openTime = datetime(timeNow.year, timeNow.month, timeNow.day, 23, 45, 5)
    else:
        openTime = datetime(timeNow.year, timeNow.month, timeNow.day - 1, 23, 45, 5)

    print(ticks)
    print(order1)

    if timeNow >= openTime:
        if order1 == "notExecuted":
            p = round(closePrice * 1.02) / 2
            print(
                breeze.place_order(
                    stock_code="TATMOT",
                    exchange_code="BSE",
                    product="margin",
                    action="sell",
                    order_type="limit",
                    stoploss="0",
                    quantity="100",
                    price=str(p),
                    validity="day",
                    validity_date="2022-08-11T010:00:00.000Z",
                    disclosed_quantity="0",
                    expiry_date="",
                    right="others",
                    strike_price="0",
                    user_remark="Test",
                )
            )
            order1 = "Executed"
            sayOutLoud(f"Tata Motors sell order quantity 100 ordered at rate: {p}")
        elif order1 == "Executed":
            if timeNow.minute == 00 and timeNow.second <= 10:
                sayOutLoud(f"Repeating Tata Motors sell order was placed")


breeze = BreezeConnect(api_key="3C8+53q6f5=8718A568z90Z9a5*0B879")

print(
    "https://api.icicidirect.com/apiuser/login?api_key="
    + urllib.parse.quote_plus("3C8+53q6f5=8718A568z90Z9a5*0B879")
)

breeze.generate_session(
    api_secret="u9+8J4j14A95(06367U661S4i22G613)", session_token="1536349"
)

# breeze.ws_connect()
""" tataMotors = breeze.subscribe_feeds(
    exchange_code="BSE",
    stock_code="TATMOT",
    product_type="",
    expiry_date="20-August-2022",
    get_exchange_quotes=True,
    get_market_depth=False,
) """
# breeze.on_ticks = on_ticks

now = datetime.now().replace(microsecond=0)
today = datetime.today()
today.replace(microsecond=0)
tomorrow = today + timedelta(days=1)
tomorrow.replace(microsecond=0)
yesterday = datetime.today() - timedelta(days=1)
yesterday.replace(microsecond=0)
open = today.replace(hour=23, minute=45, second=0, microsecond=0)
close = today.replace(day=today.day, hour=7, minute=45, second=0, microsecond=0)
todayTime = f"{today.date()}T{today.time()}.000Z"
tomorrowTime = f"{tomorrow.date()}T{tomorrow.time()}.000Z"
yesterdayTime = f"{yesterday.date()}T{yesterday.time()}.000Z"
marketOpeningTime = f"{open.date()}T{open.time()}.000Z"
marketClosingTime = f"{close.date()}T{close.time()}.000Z"


historicalData = breeze.get_historical_data(
    interval="1day",
    from_date="2022-01-01T00:00:00.000Z",
    to_date="2022-08-05T00:00:00.000Z",
    stock_code="TATMOT",
    exchange_code="NSE",
    product_type="margin",
)
df = pd.DataFrame(historicalData["Success"])
df.to_csv("TATMOT NSE HISTORICAL DATA.csv")

orderA = "NE"
orderB = "NE"
while orderA == "NE" or orderB == "NE":
    if now.time() >= open.time() and orderA == "NE":
        p = (round(511 * 0.97) / 2)*2
        A = breeze.place_order(
            stock_code="STABAN",
            exchange_code="BSE",
            product="margin",
            action="buy",
            order_type="limit",
            stoploss="0",
            quantity="100",
            price=str(p),
            validity="day",
            validity_date="",
            disclosed_quantity="0",
            expiry_date="",
            right="others",
            strike_price="0",
            user_remark="Test",
        )
        print(A)
        orderA = "E"

    if now.time() >= open.time() and orderB == "NE":
        p = (round(454.6 * 0.97) / 2)*2
        B = breeze.place_order(
            stock_code="TATMOT",
            exchange_code="BSE",
            product="margin",
            action="buy",
            order_type="limit",
            stoploss="0",
            quantity="100",
            price=str(p),
            validity="day",
            validity_date="",
            disclosed_quantity="0",
            expiry_date="",
            right="others",
            strike_price="0",
            user_remark="Test",
        )
        print(B)
        orderB = "E"
    

# ttsRunForever(marketOpeningTime, marketClosingTime)
# print(breeze.get_order_list(exchange_code="BSE", from_date="2022-08-1T06:00:00.000Z", to_date="2022-08-3T21:00:00.000Z"))

""" while(1):
    if(tatMotQuote["open"] >= float(tatMotQuote["ltp"])*1.04):
        x = breeze.place_order(
            stock_code="TATMOT",
            exchange_code="BSE",
            product="margin", 
            action="sell", 
            order_type = "market", 
            stoploss="0",
            quantity="100",
            price="", 
            validity="day", 
            validity_date="2022-08-26T010:00:00.000Z",
            disclosed_quantity="0",
            expiry_date="",
            right="others",
            strike_price="0",
            user_remark="Test")
        print(x)
        engine = pyttsx3.init()
        engine.say(f"Tata Motors buy order executed at market rate")
        engine.runAndWait()
        print(tabulate(breeze.get_portfolio_holdings(exchange_code = "BSE")["Success"],headers="keys"))
        break
 """

"""
#get yesterdays date at a specific time
x = datetime.today() - timedelta(days=1)
y = x.replace(hour=12, minute = 50, second= 5)
z = y.strftime('%Y/%h/%d %H:%M:%S')
print(z)
print(datetime.today())

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password = "737763", 
    database = "data1",
)

mycursor = db.cursor()

mycursor.execute("SELECT * FROM student")

for x in mycursor:
    print(x)
"""
