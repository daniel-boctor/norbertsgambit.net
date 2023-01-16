import pandas as pd
import numpy as np
from math import floor

def norbits_gambit_cost_calc(params, DLR_TO, DLR_U_TO, buy_FX, sell_FX, initial=10000, initial_fx="CAD", buy_side_ecn=False, sell_side_ecn=True):
    data = pd.DataFrame(columns=["USD_TO_CAD", "CAD_TO_USD", "DLR.TO", "DLR-U.TO"], index=["BUY_FX", "SELL_FX"])
    data.loc["BUY_FX"] = [buy_FX, 1/buy_FX, DLR_TO, DLR_U_TO]
    data.loc["SELL_FX"] = [sell_FX, 1/sell_FX, DLR_TO, DLR_U_TO]

    FROM = ["CAD", "DLR.TO", "USD_TO_CAD"] if initial_fx in ["CAD", "TO"] else ["USD", "DLR-U.TO", "CAD_TO_USD"]
    TO = ["CAD", "DLR.TO", "USD_TO_CAD"] if initial_fx not in ["CAD", "TO"] else ["USD", "DLR-U.TO", "CAD_TO_USD"]

    output_ECN = pd.DataFrame(columns=["Currency", "# Shares", "ECN / Share", "Total ECN Payed"],
                                index=["Buy Side", "Sell Side"])
    output_commissions = pd.DataFrame(columns=["Currency", "# Shares", "Commission / Share", "Total Commission Payed"],
                                index=["Buy Side", "Sell Side"])
    output_transactions = pd.DataFrame(columns=["Currency", "# Shares", "Amount Converted / Received", "Leftover"],
                                        index=["Buy Side", "Sell Side"])
    output_explicit_costs = pd.DataFrame(columns=(["CAD", "USD"]),
                                index=["Local Cost", "Combined Cost"])

    output_total = pd.DataFrame(columns=([""]),
                                index=["Effective FX Rate", "Explicit Costs Incurred", "Implicit Spread Earned / Payed", "TOTAL RETURN"])
    
    shares = floor(initial / data[FROM[1]][0]) if initial_fx in ["CAD", "USD"] else initial

    #ECN
    if buy_side_ecn:
        output_ECN.loc["Buy Side"] = [FROM[0], shares, params["buy_side_ecn"], round(params["buy_side_ecn"] * shares, 2)]
    else:
        output_ECN.loc["Buy Side"] = [FROM[0], shares % 100, params["buy_side_ecn"], round(params["buy_side_ecn"] * (shares % 100), 2)]

    if sell_side_ecn:
        output_ECN.loc["Sell Side"] = [TO[0], shares, params["sell_side_ecn"], round(params["sell_side_ecn"] * shares, 2)]
    else:
        output_ECN.loc["Sell Side"] = [TO[0], shares % 100, params["sell_side_ecn"], round(params["sell_side_ecn"] * (shares % 100), 2)]

    #Commissions
    output_commissions.loc["Buy Side"] = [FROM[0], shares, params["buy_side_comm"], round(min(max(params["buy_side_comm"] * shares, params["lower_bound"]), params["upper_bound"]), 2) if params["buy_side_comm"] else 0]
    output_commissions.loc["Sell Side"] = [TO[0], shares, params["sell_side_comm"], round(min(max(params["sell_side_comm"] * shares, params["lower_bound"]), params["upper_bound"]), 2) if params["sell_side_comm"] else 0]

    #Transactions
    output_transactions.loc["Buy Side"] = [FROM[0], shares, shares * data[FROM[1]][0], (initial - (shares * data[FROM[1]][0])) if initial_fx in ["CAD", "USD"] else "N/A"]
    output_transactions.loc["Sell Side"] = [TO[0], shares, shares * data[TO[1]][0], ""]

    #Explicit Costs
    output_explicit_costs[FROM[0]]["Local Cost"] = round(output_ECN["Total ECN Payed"]["Buy Side"] + output_commissions["Total Commission Payed"]["Buy Side"], 2)
    output_explicit_costs[TO[0]]["Local Cost"] = round(output_ECN["Total ECN Payed"]["Sell Side"] + output_commissions["Total Commission Payed"]["Sell Side"], 2)
    output_explicit_costs[FROM[0]]["Combined Cost"] = round(output_explicit_costs[FROM[0]]["Local Cost"] + (output_explicit_costs[TO[0]]["Local Cost"] * data[FROM[2]][-1]), 2)
    output_explicit_costs[TO[0]]["Combined Cost"] = round((output_explicit_costs[FROM[0]]["Local Cost"] * data[TO[2]][0]) + output_explicit_costs[TO[0]]["Local Cost"], 2)

    #Total
    output_total.loc["Effective FX Rate"] = round((output_transactions["Amount Converted / Received"]["Buy Side"] + output_explicit_costs[FROM[0]]["Local Cost"]) / (output_transactions["Amount Converted / Received"]["Sell Side"] - output_explicit_costs[TO[0]]["Local Cost"]), 4) \
    if initial_fx in ["CAD", "TO"] else round((output_transactions["Amount Converted / Received"]["Sell Side"] - output_explicit_costs[TO[0]]["Local Cost"]) / (output_transactions["Amount Converted / Received"]["Buy Side"] + output_explicit_costs[FROM[0]]["Local Cost"]), 4)
    output_total.loc["Explicit Costs Incurred"] = "-" + str(round((output_explicit_costs[FROM[0]]["Combined Cost"] / output_transactions["Amount Converted / Received"]["Buy Side"]) * 100, 4)) + "%"
    output_total.loc["Implicit Spread Earned / Payed"] = str(round((((output_transactions["Amount Converted / Received"]["Sell Side"] * data[FROM[2]][-1]) / output_transactions["Amount Converted / Received"]["Buy Side"]) - 1) * 100, 4)) + "%"
    #output_total.loc["TOTAL RETURN"] = round(((((output_transactions["Amount Converted / Received"]["Sell Side"] - output_explicit_costs[TO[0]]["Combined Cost"]) * data[FROM[2]][-1]) / (output_transactions["Amount Converted / Received"]["Buy Side"])) - 1) * 100, 15).astype(str) + "%"
    output_total.loc["TOTAL RETURN"] = str(round((((((output_transactions["Amount Converted / Received"]["Sell Side"] - output_explicit_costs[TO[0]]["Local Cost"]) * data[FROM[2]][-1]) - output_explicit_costs[FROM[0]]["Local Cost"]) / (output_transactions["Amount Converted / Received"]["Buy Side"])) - 1) * 100, 4)) + "%"
    #output_total.loc["TOTAL P&L"] = "$" + round(((output_transactions["Amount Converted / Received"]["Sell Side"] * data[FROM[2]][-1]) - output_transactions["Amount Converted / Received"]["Buy Side"] - output_explicit_costs[FROM[0]]["Combined Cost"]), 2).astype(str)
    output_total.loc[f"TOTAL P&L ({FROM[0]})"] = "$" + str(round((((output_transactions["Amount Converted / Received"]["Sell Side"] - output_explicit_costs[TO[0]]["Local Cost"]) * data[FROM[2]][-1]) - output_explicit_costs[FROM[0]]["Local Cost"] - output_transactions["Amount Converted / Received"]["Buy Side"]), 2))
    if "brokers_spread" in params or "dealers_rate" in params:
        output_total.columns = ["Norbert's Gambit"]
    if "brokers_spread" in params:
        output_total["Brokers Spread For Comparison"] = ["", "", "", "-" + str(params["brokers_spread"]) + "%", "$-" + str(round((params["brokers_spread"]/100) * output_transactions["Amount Converted / Received"]["Buy Side"], 2))]
        #output_total["financial mathematics"] = ["", "", "-" + str(params["brokers_spread"]) + "%", "$" + str((output_transactions["Amount Converted / Received"]["Buy Side"] * data[TO[2]][0] * (1/data[TO[2]][0])) - ((params["brokers_spread"]/100) * output_transactions["Amount Converted / Received"]["Buy Side"]) - (output_transactions["Amount Converted / Received"]["Buy Side"]))]
    if "dealers_rate" in params:
        output_total["Dealers Rate For Comparison"] = ["", "", "", str(round((((round(output_transactions["Amount Converted / Received"]["Buy Side"] * (1/params["dealers_rate"] if initial_fx in ["CAD", "TO"] else params["dealers_rate"]), 2) * data[FROM[2]][-1]) / output_transactions["Amount Converted / Received"]["Buy Side"]) - 1) * 100, 4)) + "%", 
        "$" + str(round((round(output_transactions["Amount Converted / Received"]["Buy Side"] * (1/params["dealers_rate"] if initial_fx in ["CAD", "TO"] else params["dealers_rate"]), 2) * data[FROM[2]][-1]) - output_transactions["Amount Converted / Received"]["Buy Side"], 2))]

    output_tax = pd.DataFrame(columns=["Proceeds", "ACB", "Outlays", "Capital Gain / Loss"], index=[""])

    CAD_TERMS_BUY_DATE = 1 if FROM[0] == "CAD" else data[TO[2]][0]
    CAD_TERMS_SELL_DATE = 1 if TO[0] == "CAD" else data[FROM[2]][-1]

    output_tax["Proceeds"][""] = round(output_transactions.loc["Sell Side"][2] * CAD_TERMS_SELL_DATE, 2)
    output_tax["ACB"][""] = round((output_transactions.loc["Buy Side"][2] + output_explicit_costs[FROM[0]]["Local Cost"]) * CAD_TERMS_BUY_DATE, 2)
    output_tax["Outlays"][""] = round(output_explicit_costs[TO[0]]["Local Cost"] * CAD_TERMS_SELL_DATE, 2)
    output_tax["Capital Gain / Loss"][""] = round(output_tax["Proceeds"][""] - output_tax["ACB"][""] - output_tax["Outlays"][""], 2)
    output_tax.loc[""] = "$" + output_tax.loc[""].astype(str)

    return output_transactions, output_total, output_explicit_costs, output_ECN, output_commissions, output_tax