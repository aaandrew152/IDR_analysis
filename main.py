from math import pow, log
import Consumption
import Estimation
import IncomeCollection
from matplotlib import pyplot as plt

poverty = {1: 12490, 2: 16910, 3: 21330, 4: 25750, 5: 30170, 6: 34590, 7: 39010, 8: 43430}
# poverty line in 2019, see https://aspe.hhs.gov/poverty-guidelines
beta = pow(0.98, 1/12)
percentiles = [x * 0.05 + 0.05 for x in range(19)]
costGrid = [pow(10, x) for x in range(6)] #[x * 0.05 for x in range(11)]  # 0.25?
thetaGrid = [pow(0.1, x) for x in range(8)]
globGamma = 2
maxYears = 25
minIncome = 0.01
estimType = 1  # 0 for logit, 1 for probit


def totalUtility(gamma, consumption, percs):  # Returns utility from taking a loan
    utility = 0
    percZero = [0]
    percZero.extend(percs)  # Add zero to front to allow cumulative probabilities

    for idx, perc in enumerate(percs):
        for period, c in enumerate(consumption[idx]):  # Iterate over every month's consumption
            utility += (perc - percZero[idx]) * \
                       pow(beta, period - 1) * pow(c, 1 - gamma) / (1 - gamma)

    return utility


def totalCons(consumption):
    cons = 0
    for percCons in consumption:
        cons += sum(percCons)
    return cons


# TODO is the utility unbalanced in the income? Might skew results towards high earners
def borrowerUtilityDiff(borrower, gamma):  # Finds the respective difference in the utility between an ISA and a loan
    lConsumption = Consumption.loanConsumption(borrower.incomes, borrower.principle, percentiles)
    iConsumption = Consumption.IBRConsumption(borrower.incomes, borrower.principle, percentiles, poverty, borrower.famSize)

    lUtility = totalUtility(gamma, lConsumption, percentiles)
    iUtility = totalUtility(gamma, iConsumption, percentiles)

    return iUtility - lUtility


def graphUDiff(uDiff, choices):
    plt.scatter(uDiff, choices)
    plt.xlabel('Utility Difference', fontsize='18')
    plt.ylabel('Loan Choice', fontsize='18')
    plt.title('Loan Costs and Choices', fontsize='18')
    plt.tick_params(labelsize='18')
    plt.show()


def costDiffToIncome(cost, gamma):  # Takes IDR costs and translates to an income level undoing risk aversion
    return 0


def main():
    incomes = IncomeCollection.calcIncomes(percentiles, minIncome)
    borrowerList = IncomeCollection.collectBorrowers(incomes)

    utilityDiffs = []
    for borrower in borrowerList:
        utilityDiffs.append(borrowerUtilityDiff(borrower, globGamma))

    loanChoices = [1 - borrower.IDR for borrower in borrowerList]  # List of which borrowers chose loans

    print(Estimation.statSig(utilityDiffs, loanChoices))

    graphUDiff(utilityDiffs, loanChoices)

    #cost, theta = Estimation.costMLE(utilityDiffs, loanChoices, costGrid, thetaGrid, estimType)

    #print("The estimated equations is: " + str(cost) + " - " + str(theta) + " * \\Delta U")


main()