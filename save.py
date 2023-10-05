import csv
import queue
from datetime import datetime, timedelta


#TAX HARVESTING !
# Action,Time,ISIN,Ticker,Name,No. of shares,Price / share,Currency (Price / share),Exchange rate,Result,Currency (Result),Total,Currency (Total),Withholding tax,Currency (Withholding tax),Charge amount,Currency (Charge amount),Notes,ID,Currency conversion fee,Currency (Currency conversion fee)
# Market buy,2022-01-03 14:30:29,US5949181045,MSFT,"Microsoft",1.3471614000,335.77,USD,1.13254,,"EUR",400.00,"EUR",,,,,,EOF1731067165,0.60,"EUR"
# Market sell,2023-06-26 13:30:41,US5949181045,MSFT,"Microsoft",0.3264715000,333.80,USD,1.09139,3.06,"EUR",99.70,"EUR",,,,,,EOF3122300512,0.15,"EUR"


def processCSV():
    dict_of_queues = {}
    with open('merge.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            # Check if "No. of shares" is not empty
            if row["No. of shares"]:
                if "Market buy" in row["Action"]:
                    if row["Ticker"] in dict_of_queues:
                        if "qBuy" in dict_of_queues[row["Ticker"]]:
                            dict_of_queues[row["Ticker"]]["qBuy"].put(
                                {"No. of shares": float(row["No. of shares"]), "Time": row["Time"]})
                        else:
                            dict_of_queues[row["Ticker"]]["qBuy"] = queue.Queue()
                            dict_of_queues[row["Ticker"]]["qBuy"].put(
                                {"No. of shares": float(row["No. of shares"]), "Time": row["Time"]})
                    else:
                        qBuy = queue.Queue()
                        qBuy.put({"No. of shares": float(row["No. of shares"]), "Time": row["Time"]})
                        dict_of_queues[row["Ticker"]] = {"qBuy": qBuy}
                if "Market sell" in row["Action"]:
                    if row["Ticker"] in dict_of_queues:
                        if "qSell" in dict_of_queues[row["Ticker"]]:
                            dict_of_queues[row["Ticker"]]["qSell"].put(
                                {"No. of shares": float(row["No. of shares"]), "Time": row["Time"]})
                        else:
                            dict_of_queues[row["Ticker"]]["qSell"] = queue.Queue()
                            dict_of_queues[row["Ticker"]]["qSell"].put(
                                {"No. of shares": float(row["No. of shares"]), "Time": row["Time"]})
                    else:
                        qSell = queue.Queue()
                        qSell.put({"No. of shares": float(row["No. of shares"]), "Time": row["Time"]})
                        dict_of_queues[row["Ticker"]] = {"qSell": qSell}

    for ticker, data in dict_of_queues.items():
        if "qSell" not in data:
            continue  # Skip tickers with no 'qSell' queue

        temp = 0
        while not data["qSell"].empty():
            temp = data["qSell"].get()
            if "qBuy" not in data:
                break  # Skip if there is no 'qBuy' queue
            first_bought = data["qBuy"].get()
            new = first_bought["No. of shares"] - temp["No. of shares"]

            # Calculate the tax-free date based on the purchase date
            purchase_date = datetime.strptime(first_bought["Time"], '%Y-%m-%d %H:%M:%S')
            tax_free_date = purchase_date + timedelta(days=3*365)  # Assuming 1 year = 365 days

            temp_queue = queue.Queue()
            temp_queue.put({"No. of shares": new, "Time": tax_free_date.strftime('%Y-%m-%d %H:%M:%S')})
            while not data["qBuy"].empty():
                temp_queue.put(data["qBuy"].get())
            data["qBuy"] = temp_queue

            print("Action:", "Market buy" if "qBuy" in data else "Market sell")
            print("Ticker:", ticker)
            print("No. of shares (Bought):", first_bought["No. of shares"])
            print("Time (Bought):", first_bought["Time"])
            print("No. of shares (Sold):", temp["No. of shares"])
            print("Time (Sold):", temp["Time"])
            print("Result:", new)
            print("Tax-Free Date:", tax_free_date.strftime('%Y-%m-%d %H:%M:%S'))
            print()  # Add a line break for readability


processCSV()
