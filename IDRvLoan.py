# To determine where IDRs cost more than loans

import Consumption

poverty = {1: 12490, 2: 16910, 3: 21330, 4: 25750, 5: 30170, 6: 34590, 7: 39010, 8: 43430}
# poverty line in 2019, see https://aspe.hhs.gov/poverty-guidelines
principle = 100000
incomeGrid = [x * 20 for x in range(10001)]
rate = 0.06
alpha = 0.15
famSize = 1

loanBetter = []
for income in incomeGrid:

    incomes = [income for _ in range(25*12)]
    idrTotalPay = 0
    loanTotalPay = 0

    idrPay = Consumption.ibrRepay(principle, rate, income, alpha, famSize, poverty)
    loanPay = Consumption.loanRepay(principle, rate, 10)

    if sum(idrPay) > sum(loanPay):
        loanBetter.append(1)
    else:
        loanBetter.append(0)

currentBest = 1
for idx, choice in enumerate(loanBetter):
    if choice != currentBest:
        print("At an income of " + str(incomeGrid[idx]) + " the choice switches to " + str(choice))
        currentBest = choice

print("Final income is " + str(incomeGrid[-1]))
