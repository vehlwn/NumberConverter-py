from PyQt5 import QtWidgets, QtCore, QtGui
import numberconverter
import ui_mainwindow


class MainWindow(QtWidgets.QMainWindow, ui_mainwindow.Ui_MainWindow):
    def __init__(self, parent: QtCore.QObject = None):
        super().__init__(parent)

        self._converter = numberconverter.NumberConverter()
        self._qInputNumber = ""
        self._qResult = ""
        self._base1 = 0
        self._base2 = 0
        self._precision = 0

        self.setupUi(self)

        self.clearFields()
        self.labelBaseRange.setText(
            f"({self._converter.min_base()}..{self._converter.max_base()})"
        )
        self.plainTextEditInput.installEventFilter(self)

    @QtCore.pyqtSlot()
    def on_pushButtonConvert_clicked(self):
        try:
            self.readFields()
            self._qResult = ""
            self._qResult = self._converter(
                self._qInputNumber, self._base1, self._base2, self._precision
            )
            self.plainTextEditOutput.setPlainText(self._qResult)
        except numberconverter.ParserException as ex:
            QtWidgets.QMessageBox.critical(self, "Error", str(ex))
            cursor = self.plainTextEditInput.textCursor()
            cursor.setPosition(ex.pos)
            cursor.setPosition(ex.pos + 1, QtGui.QTextCursor.KeepAnchor)
            self.plainTextEditInput.setTextCursor(cursor)
            self.plainTextEditInput.setFocus()
        except Exception as ex:
            QtWidgets.QMessageBox.critical(self, "Error", str(ex))

    def clearFields(self):
        self._qInputNumber = self._qResult = ""
        self._base1 = 10
        self._base2 = 2
        self._precision = 20
        self.plainTextEditInput.setPlainText(self._qInputNumber)
        self.plainTextEditOutput.setPlainText(self._qResult)
        self.lineEditBase1.setText(str(self._base1))
        self.lineEditBase2.setText(str(self._base2))
        self.lineEditPrecision.setText(str(self._precision))
        self.plainTextEditInput.setFocus()

    @QtCore.pyqtSlot()
    def on_pushButtonClear_clicked(self):
        self.clearFields()

    def readFields(self):
        try:
            self._qInputNumber = self.plainTextEditInput.toPlainText()
            self._base1 = max(
                self._converter.min_base(),
                min(int(self.lineEditBase1.text()), self._converter.max_base()),
            )
            self.lineEditBase1.setText(str(self._base1))
            self._base2 = max(
                self._converter.min_base(),
                min(int(self.lineEditBase2.text()), self._converter.max_base()),
            )
            self.lineEditBase2.setText(str(self._base2))
            self._precision = max(0, int(self.lineEditPrecision.text()))
            self.lineEditPrecision.setText(str(self._precision))
        except Exception as ex:
            QtWidgets.QMessageBox.critical(self, "Error", str(ex))

    @QtCore.pyqtSlot()
    def on_plainTextEditInput_textChanged(self):
        self.labelInputSize.setText(str(len(self.plainTextEditInput.toPlainText())))

    @QtCore.pyqtSlot()
    def on_plainTextEditOutput_textChanged(self):
        self.labelOutputSize.setText(str(len(self.plainTextEditOutput.toPlainText())))

    @QtCore.pyqtSlot()
    def on_actionSaveResult_triggered(self):
        try:
            # Save result to a file.
            if not self._qResult:
                raise RuntimeError("No computed result.")
            fileName = QtWidgets.QFileDialog.getSaveFileName(
                self, "Save result", ".", "Text files (*.txt);;All files (*.*)"
            )[0]
            if not fileName:
                return
            with open(fileName, "wt") as f:
                f.write(
                    f"{self._qInputNumber}_{{{self._base1}}} = {self._qResult}_{{{self._base2}}}"
                )
        except OSError as ex:
            QtWidgets.QMessageBox.critical(self, "Error", str(ex))
        except RuntimeError as ex:
            QtWidgets.QMessageBox.critical(self, "Error", str(ex))

    @QtCore.pyqtSlot()
    def on_actionExit_triggered(self):
        # Exit.
        self.close()

    @QtCore.pyqtSlot()
    def on_actionHelpGrammar_triggered(self):
        print("on_actionHelpGrammar_triggered")
        QtWidgets.QMessageBox.information(
            self,
            "Grammar",
            "Start <- [ \\t\\r\\n]* ("
            "\n    IntPart '{0}' FractPart"
            "\n    / IntPart '{0}'?"
            "\n    / '{0}' FractPart"
            "\n)"
            "\nIntPart <- Digit+"
            "\nFractPart <- Digit+"
            "\nDigit <- [0-9a-zA-Z]".format(
                numberconverter.NumberConverter.decimal_point()
            ),
        )

    @QtCore.pyqtSlot()
    def on_pushButtonSwap_clicked(self):
        inputStr = self._qInputNumber
        outStr = self._qResult
        inputStr, outStr = outStr, inputStr
        self.plainTextEditInput.setPlainText(inputStr)
        base1Str = str(self._base1)
        base2Str = str(self._base2)
        self.lineEditBase1.setText(base2Str)
        self.lineEditBase2.setText(base1Str)
        self.on_pushButtonConvert_clicked()

    def eventFilter(self, target: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if target == self.plainTextEditInput:
            if event.type() == QtCore.QEvent.KeyPress:
                if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                    self.on_pushButtonConvert_clicked()
                    return True
                elif event.key() == QtCore.Qt.Key_Escape:
                    self.on_pushButtonClear_clicked()
                    return True
        return super().eventFilter(target, event)
