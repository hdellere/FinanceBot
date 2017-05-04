"""minty.py.

This script will pull from a Mint API and aggregate financial data
for use in a Finances CSV file. Target data is account balances, recent
transactions, transaction categories, upcoming payments (maybe), etc.
Target output of the function is initially data frames and eventually
will be used as function calls in a MintyFinance python script that will
push current finance data to the CSV file.
"""
import mintapi
import datetime
from creds import email, myPass, ius_session, thx_guid


def MintyBalance():
    """MintyBalance.

    Function will return the current balance of all Mint accounts in a dict
    """
    mint = mintapi.Mint(email=email, password=myPass,
                        ius_session=ius_session, thx_guid=thx_guid)
    mintyBalances = mint.get_accounts()
    accounts = []
    balances = []
    mintyList = []
    for index in mintyBalances:
        for key, value in index.items():
            mintyList.append(index)
    for transaction in mintyList:
        for key, value in transaction.items():
            if key == 'accountName':
                accounts.append(value)
            if key == 'value':
                balances.append(value)
    totalBalances = dict((el, 0) for el in accounts)
    for i in range(0, len(balances)):
            totalBalances[accounts[i]] = balances[i]
    return totalBalances


def Timestamp():
    """Timestamp.

    Funtion will return date for MintAPI search as well as sheet name for
    csv file manipulation.
    """
    today = datetime.datetime.now()
    day = today.strftime("%d")
    year = today.strftime("%Y")
    month = today.strftime("%b")
    today = month + ' ' + str(int(today.strftime("%d")))
    sheet = month + ' ' + year
    return today, sheet, day


def MintyScrape(today):
    """MintyScrape.

    This function scrapes the mint API and will return dictionaries with
    account totals for the day and also category totals for the day.
    """
    mint = mintapi.Mint(email=email, password=myPass,
                        ius_session=ius_session, thx_guid=thx_guid)
    mintyJSON = mint.get_transactions_json(include_investment=False,
                                           skip_duplicates=True)
    # print(mintyJSON)
    mintyList = []
    for index in mintyJSON:
        for key, value in index.items():
            if value == today:
                mintyList.append(index)
    accounts = []
    amounts = []
    isDebit = []  # True False Boolean for debit status
    transID = []  # Individual transaction ID number used to id duplicates
    categories = []  # Spending Category
    for transaction in mintyList:
        for key, value in transaction.items():
            if key == 'account':
                accounts.append(value)
            if key == 'amount':
                amounts.append(value[1:])
            if key == 'isDebit':
                isDebit.append(value)
            if key == 'id':
                transID.append(value)
            if key == 'mcategory':
                categories.append(value)

    ###########################################################################
    # Remove duplicate entries from the JSON data
    # seen = []
    for index, i in enumerate(transID):
        if transID[index] == transID[index-1]:
            del accounts[index]
            del amounts[index]
            del isDebit[index]
            del transID[index]
            del categories[index]

    ###########################################################################
    # Generate dictionary of accounts and sum up their value for the day
    totals = dict((el, 0) for el in accounts)
    for i in range(0, len(amounts)):
        try:
            if str(isDebit[i]) == "False":
                totals[accounts[i]] = (totals[accounts[i]] +
                                       float(amounts[i].replace(",", "")))
            else:
                totals[accounts[i]] = (totals[accounts[i]] -
                                       float(amounts[i].replace(",", "")))
        except ValueError:
            break

    ###########################################################################
    # Generate dictionary of categories and sum up their value for the day
    catTotals = dict((el, 0) for el in categories)
    for i in range(0, len(amounts)):
        try:
            if str(isDebit[i]) == "True":
                catTotals[categories[i]] = (catTotals[categories[i]] +
                                            float(amounts[i].replace(",", "")))
            else:
                catTotals[categories[i]] = (catTotals[categories[i]] -
                                            float(amounts[i].replace(",", "")))

        except ValueError:
            break
    return totals, catTotals


###############################################################################
# Excel File formatting input, get format for sheet in input file
