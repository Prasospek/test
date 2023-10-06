import csv
import queue
from datetime import datetime, timedelta


#TAX HARVESTING !
# Action,Time,ISIN,Ticker,Name,No. of shares,Price / share,Currency (Price / share),Exchange rate,Result,Currency (Result),Total,Currency (Total),Withholding tax,Currency (Withholding tax),Charge amount,Currency (Charge amount),Notes,ID,Currency conversion fee,Currency (Currency conversion fee)
# Market buy,2022-01-03 14:30:29,US5949181045,MSFT,"Microsoft",1.3471614000,335.77,USD,1.13254,,"EUR",400.00,"EUR",,,,,,EOF1731067165,0.60,"EUR"
# Market sell,2023-06-26 13:30:41,US5949181045,MSFT,"Microsoft",0.3264715000,333.80,USD,1.09139,3.06,"EUR",99.70,"EUR",,,,,,EOF3122300512,0.15,"EUR"

#Capital Gains = (Selling Price - Buying Price) * Number of Shares Sold


# Function to calculate taxes based on capital gains and tax rate
def calculate_tax(capital_gains, tax_rate):
    return capital_gains * tax_rate



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
                                {"No. of shares": float(row["No. of shares"]), "Time": row["Time"],
                                 "Price": float(row["Price / share"])})
                        else:
                            dict_of_queues[row["Ticker"]]["qBuy"] = queue.Queue()
                            dict_of_queues[row["Ticker"]]["qBuy"].put(
                                {"No. of shares": float(row["No. of shares"]), "Time": row["Time"],
                                 "Price": float(row["Price / share"])})
                    else:
                        qBuy = queue.Queue()
                        qBuy.put({"No. of shares": float(row["No. of shares"]), "Time": row["Time"],
                                   "Price": float(row["Price / share"])})
                        dict_of_queues[row["Ticker"]] = {"qBuy": qBuy}
                if "Market sell" in row["Action"]:
                    if row["Ticker"] in dict_of_queues:
                        if "qSell" in dict_of_queues[row["Ticker"]]:
                            dict_of_queues[row["Ticker"]]["qSell"].put(
                                {"No. of shares": float(row["No. of shares"]), "Time": row["Time"],
                                 "Price": float(row["Price / share"])})
                        else:
                            dict_of_queues[row["Ticker"]]["qSell"] = queue.Queue()
                            dict_of_queues[row["Ticker"]]["qSell"].put(
                                {"No. of shares": float(row["No. of shares"]), "Time": row["Time"],
                                 "Price": float(row["Price / share"])})
                    else:
                        qSell = queue.Queue()
                        qSell.put({"No. of shares": float(row["No. of shares"]), "Time": row["Time"],
                                   "Price": float(row["Price / share"])})
                        dict_of_queues[row["Ticker"]] = {"qSell": qSell}

    for ticker, data in dict_of_queues.items():
        if "qSell" not in data:
            continue  # Skip tickers with no 'qSell' queue

        temp = 0
        while not data["qSell"].empty():
            temp = data["qSell"].get()
            if "qBuy" not in data:
                break  # Skip if there is no 'qBuy' queue

            # Calculate the tax-free date based on the purchase date
            purchase_date = datetime.strptime(data["qBuy"].queue[0]["Time"], '%Y-%m-%d %H:%M:%S')
            tax_free_date = purchase_date + timedelta(days=3 * 365)  # Assuming 1 year = 365 days

            # Check if the sale date is earlier than the tax-free date
            sale_date = datetime.strptime(temp["Time"], '%Y-%m-%d %H:%M:%S')
            if sale_date < tax_free_date:
                # Calculate capital gains and taxes for these shares
                buying_price = data["qBuy"].queue[0]["Price"]
                selling_price = temp["Price"]
                capital_gains = (selling_price - buying_price) * temp["No. of shares"]
                # Calculate taxes based on capital gains and your local tax rate
                tax_rate = 0.23                        
                tax_amount = calculate_tax(capital_gains, tax_rate)

                print("Action: Market buy" if "qBuy" in data else "Market sell")
                print("Ticker:", ticker)
                print("No. of shares (Bought):", data["qBuy"].queue[0]["No. of shares"])
                print("Time (Bought):", data["qBuy"].queue[0]["Time"])
                print("No. of shares (Sold):", temp["No. of shares"])
                print("Time (Sold):", temp["Time"])
                print("Result:", capital_gains)
                print("Tax-Free Date:", tax_free_date.strftime('%Y-%m-%d %H:%M:%S'))
                print("Capital Gains:", capital_gains)
                print("Tax Amount:", tax_amount)
                print()  # Add a line break for readability
                
                #test
                print("Purchase Date:", purchase_date.strftime('%Y-%m-%d %H:%M:%S'))
                print("Sale Date:", sale_date.strftime('%Y-%m-%d %H:%M:%S'))

processCSV()
