import csv


def collectBorrowers(incomes):
    excelBorrowerList = []

    loc = "data/scf_individual.csv"
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


def calcIncomes(percentiles):  # Calculates all combinations of age, occu, and perc income values
    # TODO Update to allow for on demand calls
    loc = "data/acs_income.csv"

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
