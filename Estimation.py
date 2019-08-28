import numpy as np
import scipy.stats
from math import log


def estimateCost(utilityDiffs, choices, costGrid):  # Runs MLE to find best cost value
    maxLikelihood = -100000
    closeCost = 0
    for cost in costGrid:
        likelihood = calcLikelihood(utilityDiffs, choices, cost)
        if likelihood > maxLikelihood:
            closeCost = cost
            maxLikelihood = likelihood

    return closeCost


def normProb(newDiff):  # Calculates the normal prob of a loan
    return scipy.stats.norm(0, 100000).cdf(newDiff)  # TODO Determine if std dev is fine


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
