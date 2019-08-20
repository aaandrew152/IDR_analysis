from math import pow
import matplotlib.pyplot as plt
import Consumption
from Estimation import estimateCost
import IncomeCollection

poverty = {1: 12490, 2: 16910, 3: 21330, 4: 25750, 5: 30170, 6: 34590, 7: 39010, 8: 43430}
# poverty line in 2019, see https://aspe.hhs.gov/poverty-guidelines
beta = pow(0.98, 1/12)
percentiles = [.05, .1, .25, .5, .75, .95]
costGrid = [x * 1000 for x in range(50)]  # Generates costs between 0 and 10,000
globGamma = 2


def totalUtility(gamma, consumption):  # Returns utility from taking a loan
    utility = 0
    percZero = [0]
    percZero.extend(percentiles)  # Add zero to front to allow cumulative probabilities

    for idx, perc in enumerate(percentiles):
        for period, c in enumerate(consumption[idx]):  # Iterate over every month's consumption
            utility += (perc - percZero[idx]) * \
                       pow(beta, period - 1) * pow(c, 1 - gamma) / (1 - gamma)
    return utility


# TODO is the utility unbalanced in the income? Might skew results towards high earners
def borrowerUtilityDiff(borrower, gamma):  # Finds the respective difference in the utility between an ISA and a loan
    lConsumption = Consumption.loanConsumption(borrower.income, borrower.principle, percentiles)
    iConsumption = Consumption.IBRConsumption(borrower.income, borrower.principle, percentiles, poverty)

    lUtility = totalUtility(gamma, lConsumption)
    iUtility = totalUtility(gamma, iConsumption)

    return lUtility - iUtility


def costDiffToIncome(cost):  # Takes IDR costs and translates to an income level
    return 0


def main():
    incomes = IncomeCollection.calcIncomes(percentiles)
    borrowerList = IncomeCollection.collectBorrowers(incomes)

    utilityDiffs = []
    for borrower in borrowerList:
        utilityDiffs.append(borrowerUtilityDiff(borrower, globGamma))

    loanChoices = [1 - borrower.IDR for borrower in borrowerList]  # List of which borrowers chose loans
    IDRCost = estimateCost(utilityDiffs, loanChoices, costGrid)

    print("The estimated IDRCost is: " + str(IDRCost))


main()
