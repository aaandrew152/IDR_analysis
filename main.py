from math import pow
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import xlrd


gammaGrid = [x/10 for x in range(0, 150)]  # Possible risk aversion values
poverty = {1: 12490, 2: 16910, 3: 21330, 4: 25750, 5: 30170, 6: 34590, 7: 39010, 8: 43430}
# poverty line in 2019, see https://aspe.hhs.gov/poverty-guidelines
beta = 0.98


def collectBorrowers():
    excelBorrowerList = []

    loc = ("scf_data/scf_individual.csv")
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)

    for row_i in range(sheet.nrows):
        excelBorrowerList.append(sheet.row_values(row_i))

    del excelBorrowerList[0]  # Remove labelling column

    borrowerList = []
    for borrower in excelBorrowerList:
        newBorrower = Borrower(borrower)
    return borrowerList


def loanRepay(loanAmount, interestRate, numYears):  # monthly repayment amount in the 10 year loan option
    n = 12 * numYears
    r = interestRate / 12

    pmt = loanAmount * ((r * ((r + 1) ** n)) / (((r + 1) ** n) - 1))

    return pmt


def ibrRepay(loanAmount, income, alpha, familySize):  # monthly repayment amount in the IBR option
    pmt = min(alpha * discretIncome(income, familySize) / 12, loanRepay(loanAmount, 0.039, 10))
    return pmt


def discretIncome(income, familySize):
    return income - 1.5 * poverty[familySize]  # TODO Update for states


class Borrower:
    def __init__(self, excelBorrower):  # Converts excel elements to data
        self.age = excelBorrower[0]
        self.occu = excelBorrower[4]
        self.principle = excelBorrower[1]
        self.remainingLoan = excelBorrower[3]
        self.educ = excelBorrower[6]
        self.income = calcIncomePerc(self.age, self.occu)
        # TODO Add family sizes
        # TODO Add States


def calcIncomePerc(age, occu):
    loc = ("scf_data/acs_income.csv")
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)

    if 10 <= age <= 18:
        age_bin = 1
    elif 18 <= age <= 25:
        age_bin = 2
    else:
        age_bin = 3
    # TODO update age bins

    percIncomes = [0 for x in range(6)]
    for state in range(56):  # Average income over all states
        rowNumber = state * 30 + (occu - 1) * 5 + age_bin + 1
        percIncomes = [sum(percIncomes) for x in zip(percIncomes, sheet.row_values(rowNumber)[3:9])]  # Adds up the old income with the current states values

    for idx, perc in enumerate(percIncomes):
        percIncomes[idx] /= 56  # Normalize

    return percIncomes


def loanConsumption(income, principle, rate):  # TODO Incorrect loan payments currently, update
    payments = []
    currentTotal = principle

    # TODO allow for loan defaults
    for year in range(10):  # each year part of the principle is paid off, and the remainder has interest
        payment = principle / 10
        currentTotal -= payment
        interest = currentTotal * (1 + rate)
        currentTotal += interest
        principle += interest
        payments.append(payment)

    consumption = [income[period] - payments[period] for period in range(10)]

    return consumption


def IBRConsumption(principle, income, rate):  # TODO Incorrect payments, fix
    payments = []
    currentTotal = principle

    for year in range(10):
        payment = max(min(principle/10, discretIncome(income)), 0)  # Cannot pay more than initial loan or less than 0
        currentTotal -= payment
        interest = currentTotal * (1 + rate)
        currentTotal += interest
        principle += interest
        payments.append(payment)

    consumption = [income[period] - payments[period] for period in range(10)]

    return consumption


def totalUtility(gamma, consumption):  # Returns utility from taking a loan
    utility = 0
    for period in range(10):
        utility += pow(beta, period - 1) * pow(consumption[period], 1 - gamma) / (1 - gamma)

    return utility


def plotIndividualGammas(loanBetter):  # Graphs the gammas for which loans > IBR
    plt.plot(gammaGrid, loanBetter)
    plt.xlabel("Gamma", fontsize='20')
    plt.ylabel("Are Loans better", fontsize='20')
    plt.show()


def borrowCalc(borrower):
    loanBetter = []

    for gamma in gammaGrid:
        lConsumption = loanConsumption(borrower.principle, borrower.interest, borrower.rate)
        iConsumption = IBRConsumption(borrower.principle, borrower.interest, borrower.rate)

        lUtility = totalUtility(gamma, lConsumption)
        iUtility = totalUtility(gamma, iConsumption)

        if lUtility > iUtility:
            loanBetter.append(1)
        else:
            loanBetter.append(0)

    # plotIndividualGammas(loanBetter)

    for gIndex, gamma in enumerate(gammaGrid):
        if loanBetter[gIndex] == 0:
            return gamma, loanBetter


def graphGammas(gammaList):
    num_bins = 20
    # the histogram of the data
    n, bins, patches = plt.hist(gammaList, num_bins, normed=1, facecolor='blue', alpha=0.5)

    plt.xlabel('Gamma')
    plt.ylabel('Occurrences')
    plt.title('Histogram of Gammas')

    # Tweak spacing to prevent clipping of ylabel
    plt.subplots_adjust(left=0.15)
    plt.show()


def main():
    borrowerList = collectBorrowers()

    gammaLess = []
    gammaGreater = []

    for borrower in borrowerList:
        borrowerGamma = borrowCalc(borrower)

        if borrower.loan:
            gammaLess.append(borrowerGamma)
        else:
            gammaGreater.append(borrowerGamma)

    graphGammas(gammaLess)
    graphGammas(gammaGreater)


