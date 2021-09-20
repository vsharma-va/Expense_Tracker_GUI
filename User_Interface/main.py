from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, QEvent, Qt
from PyQt5 import uic
import sys
import Src.Expenses
from PyQt5.QtChart import *


cmbMainModeData = ['Yearly', 'Monthly', 'All Time']
cmbMainMonthData = ['None']
cmbMainYearData = ['None']


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

        # flags
        self.tblShowData.setWindowFlags(self.tblShowData.windowFlags() & Qt.ItemIsEditable)

        # calling functions
        self.loadData_tblShowData()
        self.loadData_cmbs()
        self.displayGraph()

        # signals
        self.btnAddExpense.clicked.connect(self.evt_btnAddExpense_clicked)
        self.btnRefreshFilters.clicked.connect(self.evt_btnRefreshFilters_clicked)
        self.cmbMode.currentIndexChanged.connect(self.updateGraphsAndTable)
        self.cmbYear.currentIndexChanged.connect(self.updateGraphsAndTable)
        self.cmbMonth.currentIndexChanged.connect(self.updateGraphsAndTable)
        self.tblShowData.cellChanged.connect(self.evt_tblShowData_cellChanged)
        self.tblShowData.cellChanged.connect(self.updateGraphsAndTable)

    # signal functions
    def evt_btnAddExpense_clicked(self):
        self.AddWindow = AddExpenseWindow()
        self.AddWindow.show()

    def evt_btnRefreshFilters_clicked(self):
        self.cmbMode.clear()
        self.cmbMonth.clear()
        self.cmbYear.clear()
        self.loadData_cmbs()

    def evt_tblShowData_cellChanged(self, row, column):
        self.tblShowData.blockSignals(True)
        requiredRecord = self.tblShowData.item(row, column)
        self.tblShowData.setItem(row, column, requiredRecord)
        self.tblShowData.blockSignals(False)
        obj = Src.Expenses.Expense()
        obj.ChangeRecords(row, column, requiredRecord.text())

    # Display Items
    def loadData_tblShowData(self):
        try:
            row1 = 0
            column1 = 0
            allData = Src.Expenses.Expense.ReturnData()
            self.tblShowData.blockSignals(True)
            self.tblShowData.setRowCount(len(allData))
            self.tblShowData.setColumnCount(3)
            self.tblShowData.setColumnWidth(2, 131)
            for li in allData:
                for element in li:
                    self.tblShowData.setItem(row1, column1, QTableWidgetItem(element))
                    column1 += 1
                column1 = 0
                row1 += 1
            self.tblShowData.blockSignals(False)
        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', 'No Expense records exist!')

    def loadData_cmbs(self):
        self.blockSignals(True)
        allData = Src.Expenses.Expense.ReturnData()
        counter = 0
        for li in allData:
            for element in li:
                counter += 1
                if counter == 1:
                    monthYear = element.split(' ')
                    if monthYear[0] not in cmbMainMonthData:
                        cmbMainMonthData.append(monthYear[0])
                    if monthYear[1] not in cmbMainYearData:
                        cmbMainYearData.append(monthYear[1])
            counter = 0
        self.cmbMode.addItems(cmbMainModeData)
        self.cmbMonth.addItems(cmbMainMonthData)
        self.cmbYear.addItems(cmbMainYearData)
        self.blockSignals(False)

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

            set0 = QBarSet("Expenses Yearly")

            data = Src.Expenses.Expense.ReturnData()
            dataToPlot = []
            expenseList = []
            tagsList = []
            tempList = []
            addToDataToPlot = False
            counter = 0
            for li in data:
                for element in li:
                    counter += 1
                    if counter == 1:
                        monthYear = element.split(' ')
                        if monthYear[1] == cmbMainYearData[self.cmbYear.currentIndex()]:
                            addToDataToPlot = True
                    if addToDataToPlot:
                        if counter != 1:
                            tempList.append(element)
                dataToPlot.append(tempList)
                tempList = []
                addToDataToPlot = False
                counter = 0

            anotherCounter = 0
            for li2 in dataToPlot:
                for element in li2:
                    anotherCounter += 1
                    if anotherCounter == 1:
                        expenseList.append(float(element))
                    elif anotherCounter == 2:
                        tagsList.append(element)
                anotherCounter = 0

            set0.append(expenseList)

            series = QBarSeries()
            series.append(set0)

            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("")
            chart.setAnimationOptions(QChart.AllAnimations)

            categories = tagsList
            xAxis = QBarCategoryAxis()
            xAxis.append(categories)

            chart.createDefaultAxes()
            chart.setAxisX(xAxis, series)

            self.wiChart.setChart(chart)

        elif cmbMainModeData[self.cmbMode.currentIndex()] == 'Monthly':
            lengthMonth = self.cmbMonth.count()
            lengthYear = self.cmbYear.count()
            for i in range(lengthMonth):
                self.cmbMonth.model().item(i).setEnabled(True)
            for z in range(lengthYear):
                self.cmbMonth.model().item(z).setEnabled(True)

            data = Src.Expenses.Expense.ReturnData()
            dataToPlot = []
            expenseList = []
            tagsList = []
            tempList = []
            addToDataToPlot = False
            counter = 0
            for li in data:
                for element in li:
                    counter += 1
                    if counter == 1:
                        monthYear = element.split(' ')
                        if monthYear[1] == cmbMainYearData[self.cmbYear.currentIndex()] and \
                                monthYear[0] == cmbMainMonthData[self.cmbMonth.currentIndex()]:
                            addToDataToPlot = True
                    if addToDataToPlot:
                        if counter != 1:
                            tempList.append(element)
                dataToPlot.append(tempList)
                tempList = []
                addToDataToPlot = False
                counter = 0

            anotherCounter = 0
            for li2 in dataToPlot:
                for element in li2:
                    anotherCounter += 1
                    if anotherCounter == 1:
                        expenseList.append(float(element))
                    elif anotherCounter == 2:
                        tagsList.append(element)
                anotherCounter = 0

            set1 = QBarSet("Expenses Monthly")
            set1.append(expenseList)

            series = QBarSeries()
            series.append(set1)

            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("")
            chart.setAnimationOptions(QChart.AllAnimations)

            categories = tagsList
            xAxis = QBarCategoryAxis()
            xAxis.append(categories)

            chart.createDefaultAxes()
            chart.setAxisX(xAxis, series)

            self.wiChart.setChart(chart)

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
