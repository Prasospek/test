import csv
from datetime import datetime, timedelta
from collections import defaultdict

# Function to calculate taxes based on capital gains and tax rate
def calculate_tax(capital_gains, tax_rate):
    return capital_gains * tax_rate

def processCSV():
    purchase_queues = defaultdict(list)  # Dictionary to store FIFO queues of purchased shares by Ticker

    with open('merge.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row["No. of shares"]:
                if "Market buy" in row["Action"]:
                    purchase_date = datetime.strptime(row["Time"], '%Y-%m-%d %H:%M:%S')
                    purchase_queues[row["Ticker"]].append(
                        {"shares": float(row["No. of shares"]), "price": float(row["Price / share"]), "date": purchase_date}
                    )

                if "Market sell" in row["Action"]:
                    sale_date = datetime.strptime(row["Time"], '%Y-%m-%d %H:%M:%S')
                    ticker = row["Ticker"]

                    if ticker in purchase_queues and purchase_queues[ticker]:
                        # Find the oldest eligible purchase based on the 3-year holding period
                        eligible_purchase = None
                        for purchase in purchase_queues[ticker]:
                            if sale_date - purchase["date"] >= timedelta(days=3 * 365):
                                eligible_purchase = purchase
                                break

                        if eligible_purchase:
                            # Calculate and print taxes for tax-free shares
                            print("Action: Market sell")
                            print("Ticker:", ticker)
                            print("No. of shares (Bought):", eligible_purchase["shares"])
                            print("Time (Bought):", eligible_purchase["date"].strftime('%Y-%m-%d %H:%M:%S'))
                            print("No. of shares (Sold):", row["No. of shares"])
                            print("Time (Sold):", sale_date.strftime('%Y-%m-%d %H:%M:%S'))
                            print("Result: Tax-Free")
                            print("Tax-Free Date:", (eligible_purchase["date"] + timedelta(days=3 * 365)).strftime('%Y-%m-%d %H:%M:%S'))
                            print()
                            # Remove the purchased shares from the queue
                            purchase_queues[ticker].remove(eligible_purchase)
                        else:
                            # Calculate and print taxes for non-tax-free shares
                            purchase = purchase_queues[ticker].pop(0)  # FIFO
                            buying_price = purchase["price"]
                            selling_price = float(row["Price / share"])
                            capital_gains = (selling_price - buying_price) * float(row["No. of shares"])
                            # Set your local tax rate here (e.g., 0.23 for 23%)
                            tax_rate = 0.23
                            tax_amount = calculate_tax(capital_gains, tax_rate)

                            print("Action: Market sell")
                            print("Ticker:", ticker)
                            print("No. of shares (Bought):", purchase["shares"])
                            print("Time (Bought):", purchase["date"].strftime('%Y-%m-%d %H:%M:%S'))
                            print("No. of shares (Sold):", row["No. of shares"])
                            print("Time (Sold):", sale_date.strftime('%Y-%m-%d %H:%M:%S'))
                            print("Result: Taxable")
                            print("Capital Gains:", capital_gains)
                            print("Tax Amount:", tax_amount)
                            print()

# Call the function to process the CSV file
processCSV()
