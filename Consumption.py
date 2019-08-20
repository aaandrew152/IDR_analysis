def discretIncome(income, familySize, poverty):
    return max(0, income - 1.5 * poverty[familySize])  # TODO Update for states
    # 08/15/2019 (DN): all states except Alaska seem to have same standards


def loanRepay(loanAmount, interestRate, numYears, maxYears=25):  # monthly repayment amount in the 10 year loan option
    n = 12 * numYears
    r = interestRate / 12

    payment = loanAmount * ((r * ((r + 1) ** n)) / (((r + 1) ** n) - 1))

    return [payment] * n + [0] * 12 * (maxYears - numYears)
 # Todo principle shouldn't decrease if no payment made


def loanConsumption(incomes, principle, percentiles, rate=0.06, default=1):
    # TODO check if correct default method (currently 0.1)
    # TODO Update num years for loan
    # TODO fix income recording for default
    # TODO fix the interest rate later
    consumption = []
    for idx, perc in enumerate(percentiles):
        paymentStream = [min(loanPayment, incomes[idx] / 12 - default) for loanPayment in loanRepay(principle, rate, 10)]
        percCons = []
        for monthsPayment in paymentStream:
            percCons.append(incomes[idx] / 12 - monthsPayment)

        consumption.append(percCons)
    return consumption


def ibrRepay(loanAmount, interestRate, income, alpha, familySize, poverty, maxYears=25):  # TODO loan forgiveness
    n = 12 * maxYears  # number of repayment periods
    r = interestRate / 12  # monthly interest rate
    p = loanAmount  # principal amount
    pmt_cap = loanRepay(loanAmount, interestRate, 10)[0]  # payment cap, first months repayment

    pmt_list = [0] * n

    # deduct from principal until either forgiveness or principal is repaid
    for i in range(n):
        if p <= 0:
            break
        else:  # TODO Allow income to change over years
            pmt = min(alpha * discretIncome(income, familySize, poverty) / 12, pmt_cap)
            intr_pmt = p * r  # payment to interest
            prin_pmt = pmt - intr_pmt  # payment to principal
            p = p - prin_pmt  # new principal amount
            pmt_list[i] = pmt

    return pmt_list


# TODO What is alpha
def IBRConsumption(incomes, principle, percentiles, poverty, alpha=0.15, rate=0.06):
    consumption = []
    for idx, perc in enumerate(percentiles):
        # TODO fix family size
        paymentList = ibrRepay(principle, rate, incomes[idx], alpha, 1, poverty)

        percCons = []
        for payment in paymentList:
            percCons.append(incomes[idx] / 12 - payment)

        consumption.append(percCons)

    return consumption
