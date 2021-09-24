import csv
import os
import pandas as pd


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
        self.expenseList = [dateStr, float(expense), tag]
        return self.expenseList

    def WriteToCsv(self):
        doesntExists = False
        if os.path.isfile("../Resources/Expense.csv"):
            data = pd.read_csv("../Resources/Expense.csv")
            df = pd.DataFrame(data)
            if df.isin([self.expenseList[2]]).any().any() and df.isin([self.expenseList[0]]).any().any():
                tempDf = df.loc[df['Tags'] == self.expenseList[2], ['Date']]
                lenDf = len(tempDf)
                matchFound = False

                for i in range(lenDf):
                    if tempDf.iat[i, 0].strip() == self.expenseList[0].strip():
                        matchFound = True
                        break
                    else:
                        matchFound = False

                if matchFound:
                    df.loc[df['Tags'] == self.expenseList[2], ['Amount']] += float(self.expenseList[1])

                else:
                    doesntExists = True

            else:
                dfLength = len(df)
                df.loc[dfLength] = self.expenseList

            if doesntExists:
                dfLength = len(df)
                df.loc[dfLength] = self.expenseList

            df.to_csv("../Resources/Expense.csv", index=False)
        else:
            with open("../Resources/Expense.csv", 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                fields = ["Date", "Amount", "Tags"]
                writer.writerow(fields)
                writer.writerow(self.expenseList)
            file.close()

    def ChangeRecords(self, row: int, column: int, changedRecord: str) -> None:
        if os.path.isfile("../Resources/Expense.csv"):
            data = pd.read_csv("../Resources/Expense.csv")
            df = pd.DataFrame(data)
            df.iloc[row, column] = changedRecord
            df.to_csv("../Resources/Expense.csv", index=False)

    @staticmethod
    def AddTag(tagName: str) -> bool:
        with open("../Resources/Tags.txt", 'a', encoding='utf-8') as file:
            file.write('\n')
            file.write(tagName)
        file.close()
        return True

            

    @staticmethod
    def ReturnTags() -> list[list]:
        tagList = []
        with open("../Resources/Tags.txt", 'r', encoding='utf-8') as file:
            tempList = file.readlines()
            for i in tempList:
                tagList.append(i.strip('\n'))
        file.close()
        return tagList
        
            

    @staticmethod
    def ReturnData() -> list[list, bool]:
        data = []
        counter = 0
        if os.path.isfile("../Resources/Expense.csv"):
            with open("../Resources/Expense.csv", 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for line in reader:
                    counter += 1
                    if counter == 1:
                        continue
                    data.append(line)
            file.close()
            return [data, True]
        return [data, False]
            

    @staticmethod
    def ReturnPlotData() -> list[list, list]:
        if os.path.isfile("../Resources/Expense.csv"):
            data = pd.read_csv("../Resources/Expense.csv")
            df = pd.DataFrame(data)
            requiredDf = df.groupby(['Tags'])['Amount'].sum().reset_index()
            expenses = requiredDf.Amount.to_list()
            tags = requiredDf.Tags.to_list()
            print(requiredDf)
            return [expenses, tags]
        
            
            
        
            
