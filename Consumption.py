from math import floor


def discretIncome(monthlyIncome, familySize, poverty):
    return max(0, monthlyIncome * 12 - 1.5 * poverty[familySize])


def loanRepayFixed(loanAmount, interestRate, numYears, maxYears=25):  # monthly repayment amount in the 10 year loan option
    n = 12 * numYears
    r = interestRate / 12

    payment = loanAmount * ((r * ((r + 1) ** n)) / (((r + 1) ** n) - 1))

    return [payment] * n + [0] * 12 * (maxYears - numYears)


def loanRepay(loanAmount, interestRate, incomes, numYears, default, maxYears=25):
    n = 12 * numYears
    r = interestRate / 12
    p = loanAmount
    fixed_pmt = loanAmount * ((r * ((r + 1) ** n)) / (((r + 1) ** n) - 1))

    pmt_list = [0] * (12 * maxYears)

    for i in range(n):
        if p <= 0:
            break
        else:
            pmt = min(incomes[i] - default, fixed_pmt)   # min of monthly income and fixed payment amount
            intr_pmt = p * r  # payment to interest
            prin_pmt = pmt - intr_pmt  # payment to principal
            p = p - prin_pmt  # new principal amount
            pmt_list[i] = pmt

    return pmt_list


def loanConsumption(incomes, principle, percentiles, numYears=10, rate=0.06, default=.1):
    # TODO check if correct default method (currently 0.1)
    consumption = []
    for idx, perc in enumerate(percentiles):
        percIncome = [monthlyIncomes[idx] for monthlyIncomes in incomes]  # Takes income stream for a perc of individual
        paymentStream = loanRepay(principle, rate, percIncome, numYears, default)

        percCons = []
        for month, monthsPayment in enumerate(paymentStream):
            percCons.append(incomes[month][idx] - monthsPayment)

        consumption.append(percCons)
    return consumption


def ibrRepay(loanAmount, interestRate, incomes, alpha, famSize, poverty, maxYears=25):
    n = 12 * maxYears  # number of repayment periods
    r = interestRate / 12  # monthly interest rate
    p = loanAmount  # principal amount
    pmt_cap = loanRepayFixed(loanAmount, interestRate, 10)[0]  # payment cap, first months repayment

    pmt_list = [0] * n

    # deduct from principal until either forgiveness or principal is repaid
    for i in range(n):
        if p <= 0:
            break
        else:
            pmt = min(alpha * discretIncome(incomes[i], famSize, poverty) / 12, pmt_cap)
            intr_pmt = p * r  # payment to interest
            prin_pmt = pmt - intr_pmt  # payment to principal
            p = p - prin_pmt  # new principal amount
            pmt_list[i] = pmt

    return pmt_list


def IBRConsumption(incomes, principle, percentiles, poverty, famSize, alpha=0.15, rate=0.06):
    consumption = []
    for idx, perc in enumerate(percentiles):
        percIncome = [monthlyIncome[idx] for monthlyIncome in incomes]
        paymentList = ibrRepay(principle, rate, percIncome, alpha, famSize, poverty)

        percCons = []
        for month, payment in enumerate(paymentList):
            percCons.append(percIncome[month] - payment)

        consumption.append(percCons)

    return consumption
