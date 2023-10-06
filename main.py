import csv
import queue
from datetime import datetime, timedelta  # Import timedelta for date calculations

# Načte to CSV, proloopuje řádky a pro každej Buy/Sell to vytvoří do dict_of_queues nový klíč pro daného tickera a nastaví mu 2 queue.
# Pokud již existuje, tak to do queues jen přidá.
# Následně projíždí queues a porovnává (obě FIFO), je potřeba pořešit kontrolu data
def processCSV():
    dict_of_queues = {}
    with open('merge.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
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

            print(first_bought["No. of shares"], temp["No. of shares"], new)
            

            print("Action:", "Market buy" if "qBuy" in data else "Market sell")
            print("Ticker:", ticker)
            print("No. of shares (Bought):", first_bought["No. of shares"])
            print("Time (Bought):", first_bought["Time"])
            print("No. of shares (Sold):", temp["No. of shares"])
            print("Time (Sold):", temp["Time"])
            print("Result:", new)
            print("Tax-Free Date:", tax_free_date.strftime('%Y-%m-%d %H:%M:%S'))
            print()  # Add a line break for readability

#if __name__ == "__main__":
#    processCSV()

processCSV()