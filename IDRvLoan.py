import Consumption
import matplotlib.pyplot as plt
import numpy as np

poverty = {1: 12490, 2: 16910, 3: 21330, 4: 25750, 5: 30170, 6: 34590, 7: 39010, 8: 43430}
# poverty line in 2019, see https://aspe.hhs.gov/poverty-guidelines
principle = 40000
incomeGrid = [x * 20 for x in range(5001)]
rate = 0.06
alpha = 0.15
famSize = 1
beta = pow(.98, 1/12)

loanBetter = []
idrCost = []
loanCost = []

discountIdrCost = []
discountLoanCost = []

for idx, income in enumerate(incomeGrid):

    incomes = [income / 12 for _ in range(25*12)]
    idrTotalPay = 0
    loanTotalPay = 0

    idrPay = Consumption.ibrRepay(principle, rate, incomes, alpha, famSize, poverty)
    loanPay = Consumption.loanRepay(principle, rate, incomes, 10, 0.1)

    if sum(idrPay) > sum(loanPay):
        loanBetter.append(1)
    else:
        loanBetter.append(0)

    idrCost.append(sum(idrPay))
    loanCost.append(sum(loanPay))

currentBest = 1
for idx, choice in enumerate(loanBetter):
    if choice != currentBest:
        print("At an income of " + str(incomeGrid[idx]) + " the choice switches to " + str(choice))
        currentBest = choice

print("Maximum income is " + str(incomeGrid[-1]))


plt.xlabel('Income', fontsize='18')
plt.ylabel('Total Payment', fontsize='18')
plt.title('Cost Comparison: Loan V. IDR', fontsize='18')
plt.tick_params(labelsize='18')

idrLine, = plt.plot(incomeGrid, idrCost, 'g--', label='IDR Cost')
loanLine, = plt.plot(incomeGrid, loanCost, 'b-', label='Loan Cost')
plt.legend(handles=[idrLine, loanLine])
plt.show()


def calculateDiscounted(idrPay, loanPay):
    discountIdrCost.append(0)
    discountLoanCost.append(0)

    for period, payment in enumerate(idrPay):
        discountIdrCost[idx] += payment * pow(beta, period)

    for period, payment in enumerate(loanPay):
        discountLoanCost[idx] += payment * pow(beta, period)

    plt.plot(incomeGrid, discountIdrCost, 'g--')
    plt.plot(incomeGrid, discountLoanCost, 'b-')
    plt.show()