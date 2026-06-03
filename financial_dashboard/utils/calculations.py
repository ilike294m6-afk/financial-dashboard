"""
財務核心計算邏輯
"""
import pandas as pd


def calc_retirement_plan(
    principal, years, safe_rate,
    invest_rate, cash_fund_ratio, dist_rate,
):
    safe_factor = (1 + safe_rate) ** (years - 2)
    safe_amount = round(principal / safe_factor, 2)
    invest_amount = round(principal - safe_amount, 2)
    cash_invest = invest_amount * cash_fund_ratio
    monthly_income = round(cash_invest * dist_rate / 12, 1)
    annual_income = round(monthly_income * 12, 1)

    rows = []
    account_value = invest_amount
    cumulative_income = 0.0
    for y in range(1, years + 1):
        account_value = account_value * (1 + invest_rate / 100)
        cumulative_income += annual_income
        rows.append({
            "年度": y,
            "帳戶價值(萬)": round(account_value, 2),
            "累積配息(萬)": round(cumulative_income, 2),
            "總資產(萬)": round(account_value + cumulative_income, 2),
        })

    df = pd.DataFrame(rows)
    final_account = df.iloc[-1]["帳戶價值(萬)"]
    final_income = df.iloc[-1]["累積配息(萬)"]
    total_value = round(final_account + final_income, 2)
    annual_return = round((total_value - principal) / principal / years * 100, 2)

    return {
        "safe_amount": safe_amount,
        "invest_amount": invest_amount,
        "monthly_income": monthly_income,
        "annual_income": annual_income,
        "safe_factor": round(safe_factor, 4),
        "final_account": final_account,
        "final_income": final_income,
        "total_value": total_value,
        "annual_return": annual_return,
        "df": df,
    }


def calc_mortgage(price, down_ratio, rate, years):
    down = round(price * down_ratio, 2)
    loan = price - down
    n = years * 12
    r = rate / 12

    if r == 0:
        monthly = loan * 10000 / n
    else:
        monthly = loan * 10000 * r * (1 + r) ** n / ((1 + r) ** n - 1)
    monthly = round(monthly, 0)

    rows = []
    balance = loan * 10000
    for m in range(1, n + 1):
        interest_paid = round(balance * r, 0)
        principal_paid = monthly - interest_paid
        balance = max(balance - principal_paid, 0)
        rows.append({
            "月份": m,
            "年度": (m - 1) // 12 + 1,
            "還款金額": monthly,
            "本金": principal_paid,
            "利息": interest_paid,
            "剩餘本金": round(balance, 0),
        })

    df = pd.DataFrame(rows)
    total_paid = monthly * n
    total_interest = round(total_paid - loan * 10000, 0)

    return {
        "down": down, "loan": loan, "monthly": monthly,
        "total_paid": round(total_paid, 0),
        "total_interest": total_interest, "df": df,
    }


def calc_loan(amount, rate, years, method):
    n = years * 12
    r = rate / 12
    principal = amount * 10000
    rows = []

    if method == "等額本利":
        monthly = principal * r * (1 + r) ** n / ((1 + r) ** n - 1) if r > 0 else principal / n
        balance = principal
        for m in range(1, n + 1):
            interest_paid = round(balance * r, 0)
            principal_paid = round(monthly - interest_paid, 0)
            balance = max(balance - principal_paid, 0)
            rows.append({"月份": m, "年度": (m-1)//12+1,
                         "還款金額": round(monthly, 0),
                         "本金": principal_paid, "利息": interest_paid,
                         "剩餘本金": round(balance, 0)})
        monthly_display = round(monthly, 0)
    else:
        principal_per_month = principal / n
        balance = principal
        for m in range(1, n + 1):
            interest_paid = round(balance * r, 0)
            payment = round(principal_per_month + interest_paid, 0)
            balance = max(balance - principal_per_month, 0)
            rows.append({"月份": m, "年度": (m-1)//12+1,
                         "還款金額": payment,
                         "本金": round(principal_per_month, 0),
                         "利息": interest_paid,
                         "剩餘本金": round(balance, 0)})
        monthly_display = rows[0]["還款金額"]

    df = pd.DataFrame(rows)
    total_paid = df["還款金額"].sum()
    total_interest = round(total_paid - principal, 0)

    return {
        "monthly_first": monthly_display,
        "total_paid": round(total_paid, 0),
        "total_interest": total_interest, "df": df,
    }


INSURANCE_RATES = {
    20: 0.04, 25: 0.05, 30: 0.07, 35: 0.10,
    40: 0.15, 45: 0.23, 50: 0.38, 55: 0.62,
    60: 1.02, 65: 1.68,
}

def get_rate_for_age(age):
    for a in sorted(INSURANCE_RATES.keys()):
        if age <= a:
            return INSURANCE_RATES[a]
    return INSURANCE_RATES[65]

def calc_insurance(age, coverage, years, monthly_budget):
    rows = []
    total_premium = 0.0
    for y in range(years):
        cur_age = age + y
        rate = get_rate_for_age(cur_age)
        annual = round(coverage * rate * 12, 0)
        monthly = round(annual / 12, 0)
        total_premium += annual
        rows.append({
            "年度": y + 1, "年齡": cur_age,
            "月費率(‰)": rate, "月保費": monthly,
            "年保費": annual, "保額(萬)": coverage,
        })

    df = pd.DataFrame(rows)
    return {
        "total_premium": round(total_premium, 0),
        "avg_monthly": round(total_premium / (years * 12), 0),
        "df": df,
    }