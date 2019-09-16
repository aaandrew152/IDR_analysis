import numpy as np
import scipy.stats
from math import log, exp
from scipy.stats import ttest_ind


def costMLE(utilityDiffs, choices, costGrid, thetaGrid, estimType):  # Runs MLE to find best cost value
    maxLikelihood = -100000
    closestParams = (0, 0)
    for cost in costGrid:
        for theta in thetaGrid:
            likelihood = calcLikelihood(utilityDiffs, choices, cost, theta, estimType)

            if likelihood > maxLikelihood:
                closestParams = cost, theta
                maxLikelihood = likelihood

    return closestParams


def normProb(c, uDiff, theta, stdDev=10000):  # Calculates the normal prob of a loan
    return scipy.stats.norm(0, stdDev).cdf(c - theta * uDiff)


def logit(c, uDiff, theta):  # Estimate ln p/(1-p) = C_I - \theta \Delta U
    try:
        prob = 1 / (1 + exp(c - theta * uDiff))
    except OverflowError:  # Occurs when the value of newDiff is so large so as to make the power function explode
        prob = 0
    return prob


def calcLikelihood(utilityDiffs, loanChoices, IDRCost, theta, estimType=0):  # Calculates log likelihood value
    logLikelihood = 0
    for idx, diff in enumerate(utilityDiffs):
        if estimType:
            loanLikelihood = normProb(IDRCost, diff, theta)
        else:
            loanLikelihood = logit(IDRCost, diff, theta)

        if loanChoices[idx]:  # If the borrower took a loan
            likelihood = loanLikelihood
        else:
            likelihood = 1 - loanLikelihood

        if likelihood == 0:  # TODO determine if necessary
            return -10000000  # To avoid taking the log of 0 for extreme values of cost
        else:
            logLikelihood += log(likelihood)

    return logLikelihood


def newton_raphson(model, tol=1e-3, max_iter=1000, display=True):  # TODO Unused, replace current estimation method
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


def statSig(uDiffs, choices):  # Separates the sample into those who choose IDR or not and tests for significance in uDiff
    loans = []
    idrs = []

    for idx, diff in enumerate(uDiffs):
        if choices[idx] == 1:
            loans.append(diff)
        else:
            idrs.append(diff)

    return ttest_ind(loans, idrs)
