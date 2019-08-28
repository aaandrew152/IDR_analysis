import Consumption
import matplotlib.pyplot as plt
import numpy as np

gammaGrid = [x/2 for x in range(0, 30)]  # Possible risk aversion values
del gammaGrid[2]  # Skips case where gamma = 1 to avoid dividing by infinity and writing up special ln case


def findBorrowerGamma(borrower):
    lConsumption = Consumption.loanConsumption(borrower.income, borrower.principle, borrower.percentiles)
    iConsumption = Consumption.IBRConsumption(borrower.income, borrower.principle, borrower.percentiles)

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

