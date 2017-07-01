import time

from oandapyV20 import API
import OATools as oat
import OAUp as oau
import OADown as oad

account_id = 
token = 
instrument = "AUD_USD"

api = API(access_token=token, environment='live')

nUp = 3  # liczba zleceń w górę od aktualnej ceny
nDw = 3  # liczba zleceń w dół od aktualnej ceny
step = 1  # krok zlecenia w pipsach
levar = 0.01
position = 0.005
init_position = 0.5  # jeżeli rynek jest "equal" otwieramy tyle% dosepnych środków w obie strony
threshold = 25
lowPrice = 18.68

new_balance = oat.getBalance(account_id, api)
p = time.time()
print("Beginning balance: ", new_balance)


def printState():
    print("Current balance:", balance)
    print("Today I earn:", round(balance - lowPrice, 2), "USD - ", round(100 * (1 - (lowPrice / balance)), 2), "%")
    print("(", marketMode, accountMode, ") mode")
    print("Distances:", oat.getDistance(account_id, api), "pips... (", disttomin, disttomax, ")")
    print("MinMax:", "(", minimax[5], minimax[3], minimax[1], ":", minimax[4], minimax[2], minimax[0], ")")
    print("Closeout:", marginCloseoutPercent, "%", currentPrice)
    print("Available:", ava, units, "-", distance, int(3 * spread), "-", maava)
    print("Max drawdown trade:", maxdr)
    print("")


while True:
    marketMode = "manual"
    marketMode = oat.getMarketMode(account_id, api, instrument)
    balance = oat.getBalance(account_id, api)
    marginCloseoutPercent = oat.getMarginCloseoutPercent(account_id, api)
    currentPrice = oat.getCurrentPrice(account_id, api, instrument)
    units = int(position * (balance / levar / currentPrice[0]))
    accountMode = oat.getAccountMode(account_id, api, threshold)
    #maxdr = oat.getMaxDrID(account_id, api)
    net = oat.getNetUnits(account_id, api)
    ava = oat.getAva(account_id, api, instrument)
    maava = oat.getAvailableMargin(account_id, api)
    grow = (100.0 - marginCloseoutPercent) / 100.0
    spread = oat.currentSpread(account_id, api, instrument)

    if balance != new_balance:
        diff = balance - new_balance
        if diff > 0:
            if marketMode == "down":
                trade_id = maxdr[0]
            elif marketMode == "up":
                trade_id = maxdr[4]
            oat.maintainBalance(account_id, api, diff, trade_id)
            new_balance = balance

    minimax = oat.getMinMax(account_id, api)
    disttomin = int(10000 * abs(currentPrice[0] - minimax[5]))
    disttomax = int(10000 * abs(currentPrice[1] - minimax[4]))
    if disttomin > spread:
        print("short", currentPrice[0], minimax[5], disttomin, spread)
        oat.maintainPosition(account_id, api, instrument, -units, step, currentPrice[0])
    if disttomax > spread:
        print("long", currentPrice[1], minimax[4], disttomax, spread)
        oat.maintainPosition(account_id, api, instrument, units, step, currentPrice[1])

    distance = int(abs(10000 * (minimax[4] - minimax[5])))
    """
    if distance > int(3 * spread):
        if units < min(ava[0], ava[1]):
            if marketMode == "down":
                oat.maintainPosition(account_id, api, instrument, -units, step, currentPrice[1])
                oat.maintainPosition(account_id, api, instrument, units, step, currentPrice[0])
                # oat.maintainOrders(account_id, api, instrument, units, step, currentPrice[0])
            elif marketMode == "up":
                oat.maintainPosition(account_id, api, instrument, units, step, currentPrice[0])
                # oat.maintainOrders(account_id, api, instrument, units, step, currentPrice[1])

    if units > min(ava[0], ava[1]):
        pass
        # oat.maintainBalance(account_id, api, 0.1, maxdr[0])
        # oat.maintainBalance(account_id, api, 0.1, maxdr[4])

    if net != 0:
        if net < 0 and abs(net) <= ava[1]:
            oat.maintainPosition(account_id, api, instrument, net, step, currentPrice[1])
        if net > 0 and abs(net) <= ava[0]:
            oat.maintainPosition(account_id, api, instrument, net, step, currentPrice[0])
    """
    if (time.time() - p) > 60:
        printState()
        p = time.time()

    time.sleep(1)
