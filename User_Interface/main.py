from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate
from PyQt5 import uic
import sys
import Src.Expenses


class AddExpenseWindow(QWidget):
    def __init__(self):
        super(AddExpenseWindow, self).__init__()
        uic.loadUi("CreateExpense_Window.ui", self)
        self.setWindowTitle("Add Expense")
        # widgets
        self.leditExpense = self.findChild(QLineEdit, "leditExpense")
        self.cmbTag = self.findChild(QComboBox, "cmbTag")
        self.btnAdd = self.findChild(QPushButton, "btnAdd")
        self.btnConfirm = self.findChild(QPushButton, "btnConfirm")
        self.btnRefreshTags = self.findChild(QPushButton, "btnRefreshTags")

        # Display Items
        self.allTags = Src.Expenses.Expense.ReturnTags()
        self.cmbTag.addItems(self.allTags)

        # signals
        self.btnAdd.clicked.connect(self.evt_btnAdd_clicked)
        self.btnConfirm.clicked.connect(self.evt_btnConfirm_clicked)
        self.btnRefreshTags.clicked.connect(self.evt_btnRefreshTags_clicked)

    def evt_btnAdd_clicked(self):
        self.AddWindow = AddTagWindow()
        self.AddWindow.show()

    def evt_btnConfirm_clicked(self):
        expense = self.leditExpense.text()
        if len(expense) == 0:
            QMessageBox.critical(self, 'Error', 'Expense field can not be empty!')
        else:
            tagIndex = self.cmbTag.currentIndex()
            obj = Src.Expenses.Expense()
            obj.CreateExpense(QDate.currentDate().toString(), expense, self.allTags[tagIndex])
            obj.WriteToCsv()
            QMessageBox.information(self, 'Confirmation', 'Expense Successfully added')

    def evt_btnRefreshTags_clicked(self):
        self.allTags = Src.Expenses.Expense.ReturnTags()
        self.cmbTag.clear()
        self.cmbTag.addItems(self.allTags)


class AddTagWindow(QWidget):
    def __init__(self):
        super(AddTagWindow, self).__init__()
        uic.loadUi("NewTag_Window.ui", self)

        # widgets
        self.leditNewTag = self.findChild(QLineEdit, "leditNewTag")
        self.btnConfirm = self.findChild(QPushButton, "btnConfirm")

        # signals
        self.btnConfirm.clicked.connect(self.evt_btnConfirm_clicked)

    def evt_btnConfirm_clicked(self):
        newTagName = self.leditNewTag.text()
        if len(newTagName) == 0:
            QMessageBox.critical(self, 'Error', 'Tag name field can not be empty')
        else:
            Src.Expenses.Expense.AddTag(newTagName)
            QMessageBox.information(self, 'Confirmation', "New Tag Name added")


class DlgMain(QMainWindow):
    def __init__(self):
        super(DlgMain, self).__init__()
        uic.loadUi("Main_Window.ui", self)
        self.setWindowTitle("Expense Tracker")

        # widgets
        self.tblShowData = self.findChild(QTableWidget, "tblShowData")
        self.cmbShowDataType = self.findChild(QComboBox, "cmbShowDataType")
        self.btnAddExpense = self.findChild(QPushButton, "btnAddExpense")

        self.loadData_tblShowData()

        # signals
        self.btnAddExpense.clicked.connect(self.evt_btnAddExpense_clicked)

    def evt_btnAddExpense_clicked(self):
        self.AddWindow = AddExpenseWindow()
        self.AddWindow.show()

    # Display Items
    def loadData_tblShowData(self):
        try:
            row = 0
            column = 0
            allData = Src.Expenses.Expense.ReturnData()
            self.tblShowData.setRowCount(len(allData))
            self.tblShowData.setColumnCount(3)
            self.tblShowData.setColumnWidth(2, 131)
            for li in allData:
                for element in li:
                    print(element)
                    print(column)
                    print(row)
                    self.tblShowData.setItem(row, column, QTableWidgetItem(element))
                    column += 1
                column = 0
                row += 1
        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', 'No Expense records exist!')


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlgMain = DlgMain()
    dlgMain.show()
    sys.exit(app.exec_())