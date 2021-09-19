import csv
import os


class Expense:
    def __init__(self):
        self.expenseList = []

    def CreateExpense(self, date: str, expense: str, tag: str) -> list:
        dateLi = date.split(' ')
        dateLi.pop(0)
        dateLi.pop(1)
        dateStr = ''
        for i in dateLi:
            dateStr += i + ' '
        self.expenseList = [dateStr, expense, tag]
        return self.expenseList

    def WriteToCsv(self):
        if os.path.isfile("../Resources/Expense.csv"):
            with open("../Resources/Expense.csv", 'a', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.expenseList)
        else:
            with open("../Resources/Expense.csv", 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                fields = ["Date", "Amount", "Tags"]
                writer.writerow(fields)
                writer.writerow(self.expenseList)
            file.close()

    @staticmethod
    def AddTag(tagName: str):
        with open("../Resources/Tags.txt", 'a', encoding='utf-8') as file:
            file.write('\n')
            file.write(tagName)
        file.close()

    @staticmethod
    def ReturnTags() -> list:
        tagList = []
        with open("../Resources/Tags.txt", 'r', encoding='utf-8') as file:
            tempList = file.readlines()
            for i in tempList:
                tagList.append(i.strip('\n'))
        file.close()
        return tagList

    @staticmethod
    def ReturnData() -> list:
        data = []
        counter = 0
        with open("../Resources/Expense.csv", 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for line in reader:
                counter += 1
                if counter == 1:
                    continue
                data.append(line)
        file.close()
        return data

