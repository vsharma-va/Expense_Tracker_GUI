import sys
sys.path.insert(1, '../Src')
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, QEvent, Qt
from PyQt5.QtChart import QChart, QBarSet, QBarSeries, QBarCategoryAxis, QChartView
from PyQt5.QtGui import QColor
from PyQt5 import uic   
import Expenses

cmbMainModeData = ['None', 'Yearly', 'Monthly', 'All Time']
cmbMainMonthData = ['None']
cmbMainYearData = ['None']

cmbMainGraphMonthData = ['None']
cmbMainGraphYearData = ['None']


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
        self.allTags = Expenses.Expense.ReturnTags()
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
            obj = Expenses.Expense()
            obj.CreateExpense(QDate.currentDate().toString(), expense, self.allTags[tagIndex])
            obj.WriteToCsv()
            QMessageBox.information(self, 'Confirmation', 'Expense Successfully added')

    def evt_btnRefreshTags_clicked(self):
        self.allTags = Expenses.Expense.ReturnTags()
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
            Expenses.Expense.AddTag(newTagName)
            QMessageBox.information(self, 'Confirmation', "New Tag Name added")


class DlgMain(QMainWindow):
    def __init__(self):
        super(DlgMain, self).__init__()
        uic.loadUi("Main_Window.ui", self)
        self.setWindowTitle("Expense Tracker")
        # so that I can change the event when the window looses focus
        self.installEventFilter(self)
        print("Please")
        # widgets
        self.tblShowData = self.findChild(QTableWidget, "tblShowData")
        self.tblShowData.setToolTip("Double click on any cell to change it's value")

        self.cmbMode = self.findChild(QComboBox, "cmbMode")
        self.cmbMode.setToolTip("Filter")

        self.cmbMonth = self.findChild(QComboBox, "cmbMonth")
        self.cmbMonth.setToolTip("Select Month")

        self.cmbYear = self.findChild(QComboBox, "cmbYear")
        self.cmbYear.setToolTip("Select Year")

        self.cmbGraphMonth = self.findChild(QComboBox, "cmbGraphMonth")
        self.cmbGraphMonth.setToolTip("Select month to compare")

        self.cmbGraphYear = self.findChild(QComboBox, "cmbGraphYear")
        self.cmbGraphYear.setToolTip("Select which year to compare")

        self.btnAddExpense = self.findChild(QPushButton, "btnAddExpense")
        self.btnAddExpense.setToolTip("Click To Add a new expense")

        self.btnRefreshFilters = self.findChild(QPushButton, "btnRefreshFilters")
        self.btnRefreshFilters.setToolTip("Click if new months or years are not shown")

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
        self.cmbGraphYear.currentIndexChanged.connect(self.updateGraphsAndTable)
        self.cmbGraphMonth.currentIndexChanged.connect(self.updateGraphsAndTable)
        self.tblShowData.cellChanged.connect(self.evt_tblShowData_cellChanged)
        self.tblShowData.cellChanged.connect(self.updateGraphsAndTable)
        self.tblShowData.cellClicked.connect(self.evt_tblShowData_itemEntered)

    # signal functions
    def evt_btnAddExpense_clicked(self):
        self.AddWindow = AddExpenseWindow()
        self.AddWindow.show()

    def evt_btnRefreshFilters_clicked(self):
        self.cmbMode.clear()
        self.cmbMonth.clear()
        self.cmbYear.clear()
        self.cmbGraphMonth.clear()
        self.cmbGraphYear.clear()
        self.loadData_cmbs()

    def evt_tblShowData_cellChanged(self, row, column):
        self.tblShowData.blockSignals(True)
        requiredRecord = self.tblShowData.item(row, column)
        if column == 1:
            self.tblShowData.setItem(row, column, requiredRecord)
            self.tblShowData.blockSignals(False)
            obj = Expenses.Expense()
            obj.ChangeRecords(row, column, requiredRecord.text())
        else:
            self.tblShowData.blockSignals(False)
            
    def evt_tblShowData_itemEntered(self, row, column):
        self.displayGraph(row)

    # Display Items
    def loadData_tblShowData(self):
        try:
            if cmbMainModeData[self.cmbMode.currentIndex()] == 'All Time':
                row1 = 0
                column1 = 0
                allData = Expenses.Expense.ReturnData()
                self.tblShowData.blockSignals(True)
                self.tblShowData.setRowCount(0)
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

            elif cmbMainModeData[self.cmbMode.currentIndex()] == 'Yearly':
                row = 0
                column = 0
                findDateCounter = 0
                allData = Expenses.Expense.ReturnData()
                addToRequiredData = False
                requiredData = []
                for li in allData:
                    for element in li:
                        findDateCounter += 1
                        if findDateCounter == 1:
                            monthYear = element.split(' ')
                            if monthYear[1] == cmbMainYearData[self.cmbYear.currentIndex()]:
                                addToRequiredData = True
                        if addToRequiredData:
                            requiredData.append(element)
                    addToRequiredData = False
                    findDateCounter = 0
                self.tblShowData.blockSignals(True)
                self.tblShowData.setRowCount(0)
                # divide by three because the data will always be in multiple of 3.
                # and each row contain three cells
                self.tblShowData.setRowCount(len(requiredData) / 3)
                self.tblShowData.setColumnCount(3)
                for i in requiredData:
                    for records in requiredData:
                        self.tblShowData.setItem(row, column, QTableWidgetItem(records))
                        column += 1
                    column = 0
                    row = 0
                self.tblShowData.blockSignals(False)

            elif cmbMainModeData[self.cmbMode.currentIndex()] == 'Monthly':
                row = 0
                column = 0
                findDateCounter = 0
                allData = Expenses.Expense.ReturnData()
                addToRequiredData = False
                requiredData = []
                for li in allData:
                    for element in li:
                        findDateCounter += 1
                        if findDateCounter == 1:
                            monthYear = element.split(' ')
                            if monthYear[1] == cmbMainYearData[self.cmbYear.currentIndex()] and \
                                    monthYear[0] == cmbMainMonthData[self.cmbMonth.currentIndex()]:
                                addToRequiredData = True
                        if addToRequiredData:
                            requiredData.append(element)
                    addToRequiredData = False
                    findDateCounter = 0

                self.tblShowData.blockSignals(True)
                self.tblShowData.setRowCount(0)
                # divide by three because the data will always be in multiple of 3.
                # and each row contain three cells
                self.tblShowData.setRowCount(len(requiredData) / 3)
                self.tblShowData.setColumnCount(3)
                for i in requiredData:
                    for records in requiredData:
                        self.tblShowData.setItem(row, column, QTableWidgetItem(records))
                        column += 1
                    column = 0
                    row = 0
                self.tblShowData.blockSignals(False)

        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', 'No Expense records exist!')

    def loadData_cmbs(self):
        self.blockSignals(True)
        allData = Expenses.Expense.ReturnData()
        counter = 0
        for li in allData:
            for element in li:
                counter += 1
                if counter == 1:
                    monthYear = element.split(' ')
                    if monthYear[0] not in cmbMainMonthData:
                        cmbMainMonthData.append(monthYear[0])
                        cmbMainGraphMonthData.append(monthYear[0])
                    if monthYear[1] not in cmbMainYearData:
                        cmbMainYearData.append(monthYear[1])
                        cmbMainGraphYearData.append(monthYear[1])
            counter = 0
        self.cmbMode.addItems(cmbMainModeData)
        self.cmbMonth.addItems(cmbMainMonthData)
        self.cmbYear.addItems(cmbMainYearData)
        self.cmbGraphYear.addItems(cmbMainGraphYearData)
        self.cmbGraphMonth.addItems(cmbMainGraphMonthData)
        self.blockSignals(False)

    # Plots
    def displayGraph(self, row: int = 0):
        # all time graph. Includes all tags and dates
        if cmbMainModeData[self.cmbMode.currentIndex()] == 'All Time':
            indexMonth = self.cmbMonth.findData('None')
            indexYear = self.cmbYear.findData('None')
            lengthMonth = self.cmbMonth.count()
            lengthYear = self.cmbYear.count()
            lengthGraphMonth = self.cmbGraphMonth.count()
            lengthGraphYear = self.cmbGraphYear.count()
            for i in range(lengthMonth):
                if i != indexMonth:
                    self.cmbMonth.model().item(i).setEnabled(False)
            for z in range(lengthYear):
                if z != indexYear:
                    self.cmbYear.model().item(z).setEnabled(False)
            for k in range(lengthGraphMonth):
                self.cmbGraphMonth.model().item(k).setEnabled(False)
            for h in range(lengthGraphYear):
                self.cmbGraphYear.model().item(h).setEnabled(False)
            set0 = QBarSet("Expense")
            data = Expenses.Expense.ReturnPlotData()
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
            lengthGraphMonth = self.cmbGraphMonth.count()
            lengthGraphYear = self.cmbGraphYear.count()
            for i in range(lengthMonth):
                if i != indexMonth:
                    self.cmbMonth.model().item(i).setEnabled(False)
            for z in range(lengthYear):
                self.cmbYear.model().item(z).setEnabled(True)
            for k in range(lengthGraphMonth):
                self.cmbGraphMonth.model().item(k).setEnabled(False)
            for h in range(lengthGraphYear):
                self.cmbGraphYear.model().item(h).setEnabled(True)

            set0 = QBarSet("Expenses Yearly")

            data = Expenses.Expense.ReturnData()
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

            subPlot = self.displaySubplots(self.cmbGraphYear.currentIndex(), self.cmbGraphMonth.currentIndex(), tagsList, True, False)

            set0.append(expenseList)

            series = QBarSeries()
            series.append(set0)
            series.append(subPlot[0])

            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("")
            chart.setAnimationOptions(QChart.AllAnimations)

            categories = tagsList
            xAxis = QBarCategoryAxis()
            xAxis.append(categories)
            xAxis.append(subPlot[1])

            chart.createDefaultAxes()
            chart.setAxisX(xAxis, series)

            self.wiChart.setChart(chart)

        elif cmbMainModeData[self.cmbMode.currentIndex()] == 'Monthly':
            lengthMonth = self.cmbMonth.count()
            lengthYear = self.cmbYear.count()
            lengthGraphMonth = self.cmbGraphMonth.count()
            lengthGraphYear = self.cmbGraphYear.count()
            for i in range(lengthMonth):
                self.cmbMonth.model().item(i).setEnabled(True)
            for z in range(lengthYear):
                self.cmbMonth.model().item(z).setEnabled(True)
            for k in range(lengthGraphMonth):
                self.cmbGraphMonth.model().item(k).setEnabled(True)
            for h in range(lengthGraphYear):
                self.cmbGraphYear.model().item(h).setEnabled(True)

            data = Expenses.Expense.ReturnData()
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

            
            subPlot = self.displaySubplots(self.cmbGraphYear.currentIndex(), self.cmbGraphMonth.currentIndex(), tagsList, True, True)
            barToHighlight = self.highlightSelectedItem_graph(row, self.cmbYear.currentIndex(), self.cmbMonth.currentIndex(), True, True)
            
            try:
                if barToHighlight[0]:
                    set1 = QBarSet("Expenses Monthly")
                    set3 = QBarSet('Highlighted')
                    set3.setColor(QColor(255, 0, 0, 127))
                    set1.setColor(QColor(0, 255, 25, 255))
                    #[dataToHighlightList, tempExpenseList, tempTagsList, tag, row]
                    set3.append(barToHighlight[0])
                    expenseList.pop(barToHighlight[4])
                    expenseList.insert(barToHighlight[4], 0)
                    set1.append(expenseList)
                    
                    series = QBarSeries()
                    series.append(set3)
                    series.append(subPlot[0])
                    series.append(set1)
                    
                    chart = QChart()
                    chart.addSeries(series)
                    chart.setTitle("")

                    categories = tagsList
                    xAxis = QBarCategoryAxis()
                    xAxis.append(categories)
                    xAxis.append(subPlot[1])
                    
                    
                    chart.createDefaultAxes()
                    chart.setAxisX(xAxis, series)
                    self.wiChart.setChart(chart)
                    
                
                else:
                    
                    set1 = QBarSet("Expenses Monthly")
                    set1.append(expenseList)

                    series = QBarSeries()
                        
                    series.append(set1)
                    series.append(subPlot[0])

                    chart = QChart()
                    chart.addSeries(series)
                    chart.setTitle("")
                    chart.setAnimationOptions(QChart.AllAnimations)

                    categories = tagsList
                    xAxis = QBarCategoryAxis()
                    xAxis.append(categories)
                    xAxis.append(subPlot[1])

                    chart.createDefaultAxes()
                    chart.setAxisX(xAxis, series)
                
                    self.wiChart.setChart(chart)
            
            except TypeError:
                print("Caught")

    def displaySubplots(self, graphYearIndex: int, graphMonthIndex: int, xTicks: list, year: bool, month: bool) -> list:
        userData = Expenses.Expense.ReturnData()
        dataToPlot = []
        tempExpenseList = []
        expenseList = []
        tagsList = []
        tempList = []
        addToDataToPlot = False
        counter = 0
        for li in userData:
            for element in li:
                counter += 1
                if counter == 1:
                    monthYear = element.split(' ')
                    if year and month:
                        if monthYear[1] == cmbMainGraphYearData[graphYearIndex] and \
                                monthYear[0] == cmbMainMonthData[graphMonthIndex]:
                            addToDataToPlot = True
                    elif year and not month:
                        if monthYear[1] == cmbMainGraphYearData[graphYearIndex]:
                            addToDataToPlot = True
                    elif not year and month:
                        if monthYear[0] == cmbMainMonthData[graphMonthIndex]:
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
                    tempExpenseList.append(float(element))
                elif anotherCounter == 2:
                    tagsList.append(element)
            anotherCounter = 0

        counterToRemove = 0
        for i in range(len(xTicks)):
            try:
                if xTicks[i] == tagsList[i]:
                    expenseList.append(tempExpenseList[i - counterToRemove])
                    tempExpenseList.pop(i - counterToRemove)
                    counterToRemove += 1
                else:
                    expenseList.append(0)
            except IndexError:
                expenseList.append(0)

        if tempExpenseList:
            for i in tempExpenseList:
                expenseList.append(i)

        if year and month:
            set2 = QBarSet('{} {}'.format(cmbMainGraphYearData[graphYearIndex], cmbMainGraphMonthData[graphMonthIndex]))
        elif year and not month:
            set2 = QBarSet('{}'.format(cmbMainGraphYearData[graphYearIndex]))

        set2.append(expenseList)
        return [set2, tagsList]
    
    def highlightSelectedItem_graph(self, row: int, yearIndex: int, monthIndex:int, year: bool, month: bool) -> list[list, str, list, list]:
        userData = Expenses.Expense.ReturnData()
        dataToPlot = []
        tempExpenseList = []
        expenseList = []
        tempTagsList = []
        tempList = []
        dataToHighlightList = []
        addToDataToPlot = False
        counter = 0
        for li in userData:
            for element in li:
                counter += 1
                if counter == 1:
                    monthYear = element.split(' ')
                    if year and month:
                        if monthYear[1] == cmbMainYearData[yearIndex] and \
                                monthYear[0] == cmbMainMonthData[monthIndex]:
                            print('1')
                            addToDataToPlot = True
                    elif year and not month:
                        if monthYear[1] == cmbMainYearData[yearIndex]:
                            addToDataToPlot = True
                    elif not year and month:
                        if monthYear[0] == cmbMainMonthData[monthIndex]:
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
                    tempExpenseList.append(float(element))
                elif anotherCounter == 2:
                    tempTagsList.append(element)
            anotherCounter = 0
        try:  
            dataToHighlight = tempExpenseList.pop(row)
            tag = tempTagsList.pop(row)
            
            for i in range(len(tempExpenseList) + 1):
                if i == row:
                    dataToHighlightList.append(dataToHighlight)
                else:
                    dataToHighlightList.append(0)
                    
            return [dataToHighlightList, tempExpenseList, tempTagsList, tag, row]
        except IndexError:
            print('caught highlight')
        
        
        
    # update widget functions:

    def updateGraphsAndTable(self, row: int = 0):
        self.displayGraph(row)
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
