import csv
from math import floor


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
    def __init__(self, excelBorrower, incomes, maxYears=25):  # Converts excel elements to data
        self.age = int(excelBorrower[8])  # Age upon graduating
        self.principle = int(excelBorrower[1])
        self.IDR = 1 if int(excelBorrower[2]) else 0
        self.remainingLoan = int(excelBorrower[3])
        self.occu = int(excelBorrower[4]) - 1  # For list entries
        self.educ = int(excelBorrower[6])
        self.famSize = int(excelBorrower[7])
        self.determineAgeBin()

        self.incomes = []
        for month in range(maxYears*12):  # Updates the age bin over time
            if month % 12 == 11:  # New year
                self.age += 1
                self.determineAgeBin()

            self.incomes.append([income/12 for income in incomes[self.age_bin][self.occu]])
            # Each element of self.incomes is a list of percentile based levels of income

    def determineAgeBin(self):
        if 24 < self.age < 65:
            self.age_bin = floor((self.age - 25) / 2)
        elif self.age >= 65:
            self.age_bin = 19
        else:
            self.age_bin = 0


def calcIncomes(percentiles, minIncome):  # Calculates all combinations of age, occu, and perc income values
    loc = "data/acs_income.csv"

    incomeList = []
    with open(loc, newline='') as csvfile:
        sheet = csv.reader(csvfile, delimiter=' ', quotechar='|')

        for row in sheet:
            incomeList.append(row)

        del incomeList[0]  # Delete the headings row

        percIncomes = []
        for age_bin in range(20):
            percIncomes.append([])  # 1st index finds the appropriate age bin

            for occu in range(6):
                percIncomes[age_bin].append([0 for _ in percentiles])  # 2nd index finds the occupation

                rowNumber = occu * 20 + age_bin
                percIncomes[age_bin][occu] = []

                parseRow = incomeList[rowNumber][0].split(',')

                for idx, perc in enumerate(percentiles):
                    income = float(parseRow[idx + 2])
                    if income == 0:
                        percIncomes[age_bin][occu].append(minIncome)
                    else:
                        percIncomes[age_bin][occu].append(income)

    return percIncomes
