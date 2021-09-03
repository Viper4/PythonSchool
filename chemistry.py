import time
import threading
import json
import re
import sys
from pynput.keyboard import Controller, Listener, KeyCode, Key


def tap(key, releaseDelay):
    controller.press(key)
    time.sleep(releaseDelay)
    controller.release(key)


class Input(threading.Thread):
    def __init__(self):
        super().__init__()
        self.program_running = True
        self.inputString = ""
        self.calcMode = ""
        self.lastResult = ""
        with open("settings.json", encoding='utf-8') as file:
            self.settings = json.load(file)
        with open("periodic_table.json", encoding='utf-8') as file:
            self.periodic_table = json.load(file)
        print("chemistry: Active")

    def calculate(self):
        self.inputString = str(input())
        if self.inputString == "get_molar_mass" or self.inputString == "gmm":
            print("get_molar_mass: Type formula Ex: 2NaHCO_3|")
            self.calcMode = "get_molar_mass"
        elif self.inputString == "get_element_info" or self.inputString == "gei":
            print("get_element_info: Type element")
            self.calcMode = "get_element_info"
        elif self.inputString == "moles_to_grams" or self.inputString == "mtg":
            print("moles_to_grams: Types moles and formula Ex: 1 mol NaCl")
            self.calcMode = "moles_to_grams"
        elif self.inputString == "get_sig_figs" or self.inputString == "gsf":
            print("get_sig_figs: Type number")
            self.calcMode = "get_sig_figs"
        elif self.calcMode == "get_molar_mass":
            molar_mass = str(self.get_molar_mass(self.inputString))
            print("get_molar_mass: " + self.inputString + ": " + molar_mass)
            self.lastResult = molar_mass
        elif self.calcMode == "get_element_info":
            for element in self.periodic_table["elements"]:
                if element["symbol"] == self.inputString or element["name"] == self.inputString:
                    print("get_element_info: " + element["symbol"] + " " + element["name"] + " (temp in Kelvin)")
                    for variable in element:
                        if variable != "symbol" and variable != "name" and variable != "color":
                            print(variable + ": " + str(element[str(variable)]))
            self.lastResult = self.inputString
        elif self.calcMode == "moles_to_grams":
            formula = re.sub("[0-9] mol ", "", self.inputString)
            moles = float(re.sub(" mol ", "", re.sub(formula, "", self.inputString)))
            grams = str(self.moles_to_grams(moles, formula))
            print("moles_to_grams: " + self.inputString + " = " + grams + "g")
            self.lastResult = grams
        elif self.calcMode == "get_sig_figs":
            value = self.inputString
            if self.inputString == "Last Result" or self.inputString == "LR":
                result = str(self.get_sig_figs(self.lastResult))
                value = self.lastResult
            else:
                result = str(self.get_sig_figs(self.inputString))

            print("get_sig_figs: " + value + " -> " + result)
            self.lastResult = result

    def get_molar_mass(self, formula):
        results = []
        total_molar_mass = 0.0
        element_list = re.findall("[0-9]?[0-9]?[A-Z][a-z]?[_]?[0-9]?[0-9]?[|]?", formula)
        print(formula + " molar mass:")
        for elementString in element_list:
            symbol = re.sub("[^A-Za-z]", "", elementString)
            coefficient = re.sub("[^0-9]", "", re.sub("[_][0-9]+[|]|[_][0-9]+", "", elementString))
            subscript = re.sub("[^0-9]", "", re.sub("[0-9][A-Z]|[0-9][0-9][A-Z]", "", elementString))
            if coefficient == "":
                coefficient = "1"
            if subscript == "":
                subscript = "1"
            for element in self.periodic_table["elements"]:
                if element["symbol"] == symbol:
                    atomic_mass = element["atomic_mass"]
                    molar_mass = float(coefficient) * atomic_mass * float(subscript)
                    results.append(molar_mass)
                    total_molar_mass += molar_mass
                    print(elementString + ": " + coefficient + "*" + str(atomic_mass) + "*" + subscript + " = " + str(
                        molar_mass))
        if len(results) > 1:
            print(str(results)[1:-1].replace(", ", "+") + " = " + str(total_molar_mass))
        return total_molar_mass

    def moles_to_grams(self, moles, formula):
        molar_mass = self.get_molar_mass(formula)
        print(str(moles) + " mol " + formula + " to grams:")
        grams = moles * molar_mass
        print(str(moles) + "*" + str(molar_mass) + " = " + str(grams))
        return grams

    def get_sig_figs(self, value):
        dotIndex = value.rfind(".")
        if dotIndex != -1:
            sigFig = re.search("[1-9][0-9]*[.]*[0-9]*", value)
        else:
            sigFig = re.search("[0-9]*[^0]", value)

        if sigFig != None:
            print(sigFig.group())
            return len(re.sub("[^0-9]", "", sigFig.group()))
        else:
            return 0

    def exit(self):
        print("chemistry: Exiting")
        self.program_running = False


controller = Controller()
inputThread = Input()
inputThread.start()


def on_press(key):
    global inputThread

    if key == KeyCode(char=inputThread.settings["settings"]["exitKey"]):
        inputThread.exit()
        listener.stop()
    elif key == Key.enter:
        inputThread.calculate()


with Listener(on_press=on_press) as listener:
    listener.join()
