from math import pow, floor, log
import matplotlib.pyplot as plt
import numpy as np
import csv
import scipy.stats

gammaGrid = [x/2 for x in range(0, 30)]  # Possible risk aversion values
del gammaGrid[2]  # Skips case where gamma = 1 to avoid dividing by infinity and writing up special ln case
poverty = {1: 12490, 2: 16910, 3: 21330, 4: 25750, 5: 30170, 6: 34590, 7: 39010, 8: 43430}
# poverty line in 2019, see https://aspe.hhs.gov/poverty-guidelines
beta = pow(0.98, 1/12)
percentiles = [.05, .1, .25, .5, .75, .95]
costGrid = [x * 1000 for x in range(50)]  # Generates costs between 0 and 10,000


def collectBorrowers(incomes):
    excelBorrowerList = []

    loc = "scf_data/scf_individual.csv"
    with open(loc, newline='') as csvfile:
        sheet = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in sheet:
            excelBorrowerList.append(row)

    del excelBorrowerList[0]  # Remove labelling column

    borrowerList = []
    for borrower in excelBorrowerList:
        parseBorrower = borrower[0].split(',')
        newBorrower = Borrower(parseBorrower, incomes)
        borrowerList.append(newBorrower)
    return borrowerList


def discretIncome(income, familySize):
    return max(0, income - 1.5 * poverty[familySize])  # TODO Update for states


class Borrower:
    def __init__(self, excelBorrower, incomes):  # Converts excel elements to data
        self.age = int(excelBorrower[0])
        self.principle = int(excelBorrower[1])
        self.IDR = 1 if int(excelBorrower[2]) else 0
        self.remainingLoan = int(excelBorrower[3])
        self.occu = int(excelBorrower[4]) - 1  # For list entries
        self.educ = int(excelBorrower[6])
        # TODO Add family sizes
        # TODO Add States

        if 25 <= self.age <= 28:
            self.age_bin = 0
        elif 29 <= self.age <= 32:
            self.age_bin = 1
        elif 33 <= self.age <= 36:
            self.age_bin = 2
        elif 37 <= self.age <= 40:
            self.age_bin = 3
        else:
            self.age_bin = 4

        self.income = incomes[self.age_bin][self.occu - 1]


def calcIncomes():  # Calculates all combinations of age, occu, and perc income values
    # TODO Update to allow for on demand calls
    loc = "scf_data/acs_income.csv"

    incomeList = []
    with open(loc, newline='') as csvfile:
        sheet = csv.reader(csvfile, delimiter=' ', quotechar='|')

        for row in sheet:
            incomeList.append(row)

        del incomeList[0]

        percIncomes = []
        for age_bin in range(5):
            percIncomes.append([])  # 1st index finds the appropriate age bin

            for occu in range(6):
                percIncomes[age_bin].append([0 for _ in percentiles])  # 2nd index finds the occupation

                for state in range(20):  # Average income over all states
                    rowNumber = state * 30 + (occu - 1) * 5 + age_bin + 1
                    newIncomes = []

                    parseRow = incomeList[rowNumber][0].split(',')
                    for idx, perc in enumerate(percentiles):
                        newIncomes.append(int(parseRow[idx + 3]))

                    percIncomes[age_bin][occu] = [sum(x) for x in zip(percIncomes[age_bin][occu], newIncomes)]
                    # Adds up the old income with the current states values

                for idx, perc in enumerate(percentiles):
                    percIncomes[age_bin][occu][idx] /= 20  # TODO Change normalization when state number is updated
                    if percIncomes[age_bin][occu][idx] == 0:
                        percIncomes[age_bin][occu][idx] = 1  # TODO Change minimum income

    return percIncomes


def loanRepay(loanAmount, interestRate, numYears, maxYears=25):  # monthly repayment amount in the 10 year loan option
    n = 12 * numYears
    r = interestRate / 12

    payment = loanAmount * ((r * ((r + 1) ** n)) / (((r + 1) ** n) - 1))

    return [payment] * n + [0] * 12 * (maxYears - numYears)


def loanConsumption(incomes, principle, rate=0.06, default=1):
    # TODO check if correct default method (currently 0.1)
    # TODO Update num years for loan
    # TODO fix income recording for default
    consumption = []
    for idx, perc in enumerate(percentiles):
        paymentStream = [min(loanPayment, incomes[idx] / 12 - default) for loanPayment in loanRepay(principle, rate, 10)]
        percCons = []
        for monthsPayment in paymentStream:
            percCons.append(incomes[idx] / 12 - monthsPayment)

        consumption.append(percCons)
    return consumption


def ibrRepay(loanAmount, interestRate, income, alpha, familySize, maxYears=25):  # TODO loan forgiveness
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
            pmt = min(alpha * discretIncome(income, familySize) / 12, pmt_cap)
            intr_pmt = p * r  # payment to interest
            prin_pmt = pmt - intr_pmt  # payment to principal
            p = p - prin_pmt  # new principal amount
            pmt_list[i] = pmt

    return pmt_list


# TODO What is alpha
def IBRConsumption(incomes, principle, alpha=0.15, rate=0.06):
    consumption = []
    for idx, perc in enumerate(percentiles):
        # TODO fix family size
        paymentList = ibrRepay(principle, rate, incomes[idx], alpha, 1)

        percCons = []
        for payment in paymentList:
            percCons.append(incomes[idx] / 12 - payment)

        consumption.append(percCons)

    return consumption


def totalUtility(gamma, consumption):  # Returns utility from taking a loan
    utility = 0
    percZero = [0]
    percZero.extend(percentiles)  # Add zero to front to allow cumulative probabilities

    for idx, perc in enumerate(percentiles):
        for period, c in enumerate(consumption[idx]):  # Iterate over every month's consumption
            utility += (perc - percZero[idx]) * \
                       pow(beta, period - 1) * pow(c, 1 - gamma) / (1 - gamma)
    return utility


def findBorrowerGamma(borrower):
    lConsumption = loanConsumption(borrower.income, borrower.principle)
    iConsumption = IBRConsumption(borrower.income, borrower.principle)

    for gamma in gammaGrid:
        lUtility = totalUtility(gamma, lConsumption)
        iUtility = totalUtility(gamma, iConsumption)

        if lUtility < iUtility:
            return gamma  # Returns first gamma for which IDR is better

    return gammaGrid[-1]  # Returns last gamma if IDR is never better


def graphGammas(gammaList, title):
    if gammaList is None:
        return 0

    num_bins = 20

    plt.hist(np.asarray(gammaList), num_bins, density=1, facecolor='blue', alpha=0.5)  # n, bins, patches =

    plt.xlabel('Gamma')
    plt.ylabel('Occurrences')
    plt.title(title)

    # Tweak spacing to prevent clipping of y label
    plt.subplots_adjust(left=0.15)
    plt.show()


def determineGammas(borrowerList):
    gammaLess = []
    gammaGreater = []

    for borrower in borrowerList:
        borrowerGamma = findBorrowerGamma(borrower)

        if borrower.IDR:
            gammaGreater.append(borrowerGamma)
        else:
            gammaLess.append(borrowerGamma)

    graphGammas(gammaLess, "Loan Gammas")
    graphGammas(gammaGreater, "IDR Gammas")


# TODO is the utility unbalanced in the income? Might skew results towards high earners
def borrowerUtilityDiff(borrower, gamma):  # Finds the respective difference in the utility between an ISA and a loan
    lConsumption = loanConsumption(borrower.income, borrower.principle)
    iConsumption = IBRConsumption(borrower.income, borrower.principle)
    # totalConsDiff = 0
    # for idx, perc in enumerate(percentiles):
    #     totalConsDiff += sum(lConsumption[idx]) - sum(iConsumption[idx])
    # print(totalConsDiff)
    lUtility = totalUtility(gamma, lConsumption)
    iUtility = totalUtility(gamma, iConsumption)

    return lUtility - iUtility


def estimateCost(utilityDiffs, choices):  # Runs MLE to find best cost value
    maxLikelihood = -100000
    closeCost = 0
    for cost in costGrid:
        likelihood = calcLikelihood(utilityDiffs, choices, cost)
        if likelihood > maxLikelihood:
            closeCost = cost
            maxLikelihood = likelihood

    return closeCost


def normProb(newDiff):  # Calculates the normal prob of a loan
    return scipy.stats.norm(0, 20000).cdf(newDiff)  # TODO Determine if std dev is fine


def calcLikelihood(utilityDiffs, loanChoices, IDRCost):  # Calculates log likelihood value
    logLikelihood = 0
    for idx, diff in enumerate(utilityDiffs):
        loanLikelihood = normProb(diff + IDRCost)

        if loanChoices[idx]:  # If the borrower took a loan
            likelihood = loanLikelihood
        else:
            likelihood = 1 - loanLikelihood

        if likelihood == 0:  # TODO determine if necessary
            return -10000000  # To avoid taking the log of 0 for extreme values of cost
        else:
            logLikelihood += log(likelihood)

    return logLikelihood


def newton_raphson(model, tol=1e-3, max_iter=1000, display=True):
    i = 0
    error = 100  # Initial error value

    # Print header of output
    if display:
        header = f'{"Iteration_k":<13}{"Log-likelihood":<16}{"θ":<60}'
        print(header)
        print("-" * len(header))

    # While loop runs while any value in error is greater
    # than the tolerance until max iterations are reached
    while np.any(error > tol) and i < max_iter:
        H, G = model.H(), model.G()
        newBeta = model.beta - (np.linalg.inv(H) @ G)
        error = newBeta - model.beta
        model.beta = newBeta

        # Print iterations
        if display:
            betaList = [f'{t:.3}' for t in list(model.beta.flatten())]
            update = f'{i:<13}{model.logL():<16.8}{betaList}'
            print(update)

        i += 1

    print(f'Number of iterations: {i}')
    print(f'β_hat = {model.beta.flatten()}')

    return model.beta.flatten()        # Return a flat array for β (instead of a k_by_1 column vector)


def costDiffToIncome(cost):  # Takes IDR costs and translates to an income level
    return 0


def main():
    incomes = calcIncomes()
    borrowerList = collectBorrowers(incomes)

    gamma = 2  # TODO update value
    utilityDiffs = []
    for borrower in borrowerList:
        utilityDiffs.append(borrowerUtilityDiff(borrower, gamma))

    loanChoices = [1 - borrower.IDR for borrower in borrowerList]  # List of which borrowers chose loans
    IDRCost = estimateCost(utilityDiffs, loanChoices)

    print("The estimated IDRCost is: " + str(IDRCost))


main()


