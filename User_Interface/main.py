from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, QEvent
from PyQt5 import uic
import sys
import Src.Expenses
from PyQt5.QtChart import *


cmbMainModeData = ['Yearly', 'Monthly', 'All Time']
cmbMainMonthData = {'None'}
cmbMainYearData = {'None'}


class AddExpenseWindow(QWidget):
    def __init__(self):
        super(AddExpenseWindow, self).__init__()
        uic.loadUi("CreateExpense_Window.ui", self)
        self.setWindowTitle("Add Expense")
        self.setFocus()

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
        self.setFocus()

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
        # so that I can change the event when the window looses focus
        self.installEventFilter(self)

        # widgets
        self.tblShowData = self.findChild(QTableWidget, "tblShowData")
        self.cmbMode = self.findChild(QComboBox, "cmbMode")
        self.cmbMonth = self.findChild(QComboBox, "cmbMonth")
        self.cmbYear = self.findChild(QComboBox, "cmbYear")
        self.btnAddExpense = self.findChild(QPushButton, "btnAddExpense")
        self.btnRefreshFilters = self.findChild(QPushButton, "btnRefreshFilters")
        self.wiChart = self.findChild(QChartView, 'wiChart')

        # calling functions
        self.loadData_tblShowData()
        self.loadData_cmbs()
        self.displayGraph()

        # signals
        self.btnAddExpense.clicked.connect(self.evt_btnAddExpense_clicked)
        self.btnRefreshFilters.clicked.connect(self.evt_btnRefreshFilters_clicked)
        self.cmbMode.currentIndexChanged.connect(self.updateGraphsAndTable)

    # signal functions
    def evt_btnAddExpense_clicked(self):
        self.AddWindow = AddExpenseWindow()
        self.AddWindow.show()

    def evt_btnRefreshFilters_clicked(self):
        self.cmbMode.clear()
        self.cmbMonth.clear()
        self.cmbYear.clear()
        self.loadData_cmbs()

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
                    self.tblShowData.setItem(row, column, QTableWidgetItem(element))
                    column += 1
                column = 0
                row += 1
        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', 'No Expense records exist!')

    def loadData_cmbs(self):
        allData = Src.Expenses.Expense.ReturnData()
        counter = 0
        for li in allData:
            for element in li:
                counter += 1
                if counter == 1:
                    monthYear = element.split(' ')
                    cmbMainMonthData.add(monthYear[0])
                    cmbMainYearData.add(monthYear[1])
            counter = 0
        self.cmbMode.addItems(cmbMainModeData)
        self.cmbMonth.addItems(cmbMainMonthData)
        self.cmbYear.addItems(cmbMainYearData)

    # Plots
    def displayGraph(self):
        # all time graph. Includes all tags and dates
        if cmbMainModeData[self.cmbMode.currentIndex()] == 'All Time':
            indexMonth = self.cmbMonth.findData('None')
            indexYear = self.cmbYear.findData('None')
            lengthMonth = self.cmbMonth.count()
            lengthYear = self.cmbYear.count()
            for i in range(lengthMonth):
                if i != indexMonth:
                    self.cmbMonth.model().item(i).setEnabled(False)
            for z in range(lengthYear):
                if z != indexYear:
                    self.cmbYear.model().item(z).setEnabled(False)
            set0 = QBarSet("Expense")
            data = Src.Expenses.Expense.ReturnPlotData()
            set0.append(data[0])

            series = QBarSeries()
            series.append(set0)

            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("")
            chart.setAnimationOptions(QChart.AllAnimations)

            categories = data[1]
            xAxis = QBarCategoryAxis()
            xAxis.append(categories)

            chart.createDefaultAxes()
            chart.setAxisX(xAxis, series)

            self.wiChart.setChart(chart)
        elif cmbMainModeData[self.cmbMode.currentIndex()] == 'Yearly':
            indexMonth = self.cmbMonth.findData('None')
            lengthMonth = self.cmbMonth.count()
            lengthYear = self.cmbYear.count()
            for i in range(lengthMonth):
                if i != indexMonth:
                    self.cmbMonth.model().item(i).setEnabled(False)
            for z in range(lengthYear):
                self.cmbYear.model().item(z).setEnabled(True)

        elif cmbMainModeData[self.cmbMode.currentIndex()] == 'Monthly':
            lengthMonth = self.cmbMonth.count()
            lengthYear = self.cmbYear.count()
            for i in range(lengthMonth):
                self.cmbMonth.model().item(i).setEnabled(True)
            for z in range(lengthYear):
                self.cmbMonth.model().item(z).setEnabled(True)


    # update widget functions:
    def updateGraphsAndTable(self):
        self.displayGraph()
        self.loadData_tblShowData()

    # event filter for change in focus:
    def eventFilter(self, object, event):
        if event.type() == QEvent.WindowActivate:
            self.updateGraphsAndTable()
        elif event.type() == QEvent.WindowDeactivate:
            self.updateGraphsAndTable()
        return False



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
