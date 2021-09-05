import time
import threading
import json
import re
import decimal
from pynput.keyboard import Controller, Listener, KeyCode, Key


def tap(key, release_delay):
    controller.press(key)
    time.sleep(release_delay)
    controller.release(key)


class Input(threading.Thread):
    def __init__(self):
        super().__init__()
        self.inputString = ""
        self.calcMode = ""
        self.lastResult = ""
        with open("settings.json", encoding='utf-8') as file:
            self.settings = json.load(file)
        with open("periodic_table.json", encoding='utf-8') as file:
            self.periodic_table = json.load(file)
        with open("prefixes_suffixes.json", encoding='utf-8') as file:
            self.prefixes_suffixes = json.load(file)
        with open("polyatomic_ions.json", encoding='utf-8') as file:
            self.polyatomic_ions = json.load(file)
        print("chemistry: Active")

    def calculate(self):
        self.inputString = str(input())
        if self.inputString == "get_molar_mass" or self.inputString == "gmm":
            print("get_molar_mass: Type compound Ex: 2NaHCO3")
            self.calcMode = "get_molar_mass"
        elif self.inputString == "get_element_info" or self.inputString == "gei":
            print("get_element_info: Type element")
            self.calcMode = "get_element_info"
        elif self.inputString == "moles_to_grams" or self.inputString == "mtg":
            print("moles_to_grams: Types moles and formula Ex: 1.3 mol NaCl")
            self.calcMode = "moles_to_grams"
        elif self.inputString == "get_sig_figs" or self.inputString == "gsf":
            print("get_sig_figs: Type number")
            self.calcMode = "get_sig_figs"
        elif self.inputString == "get_systematic_name" or self.inputString == "gsn":
            print("get_systematic_name: Type formula Ex: Fe2O3")
            self.calcMode = "get_systematic_name"
        else:
            if self.calcMode == "get_molar_mass":
                molar_mass = str(self.get_molar_mass(self.inputString, True))
                print("get_molar_mass: " + self.format_compound(self.inputString) + ": " + molar_mass)
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
                formula = re.sub("[0-9]*[.]*[0-9]* mol ", "", self.inputString)
                moles = re.sub(" mol ", "", re.sub(formula, "", self.inputString))
                grams = self.moles_to_grams(moles, formula, True)
                print("moles_to_grams: " + self.format_compound(formula) + " = " + grams + "g")
                self.lastResult = grams
            elif self.calcMode == "get_sig_figs":
                if self.inputString == "Last Result" or self.inputString == "LR":
                    result = str(self.get_sig_figs(self.lastResult))
                    print("get_sig_figs: " + self.lastResult + " -> " + result)
                else:
                    result = str(self.get_sig_figs(self.inputString))
                    print("get_sig_figs: " + self.inputString + " -> " + result)
                self.lastResult = result
            elif self.calcMode == "get_systematic_name":
                name = self.get_systematic_name(self.inputString)
                print("get_systematic_name: " + self.format_compound(self.inputString) + " -> " + name)
                self.lastResult = self.inputString

    def get_molar_mass(self, formula, round_sig_figs):
        results = []
        element_string_list = re.findall("[A-Z][a-z]?[0-9]*", formula)
        try:
            coefficient = re.sub("[^0-9]", "", re.match("[0-9]*[A-Z]", formula).group())
        except AttributeError:
            coefficient = "1"
        if coefficient == "":
            coefficient = 1
        total_molar_mass = 0.0
        print(self.format_compound(formula) + " molar mass:")
        for element_string in element_string_list:
            for element in self.periodic_table["elements"]:
                symbol = re.sub("[^A-Za-z]", "", element_string)
                subscript = re.sub("[^0-9]", "", element_string)
                if subscript == "":
                    subscript = "1"
                if element["symbol"] == symbol:
                    atomic_mass = element["atomic_mass"]
                    molar_mass = atomic_mass * float(subscript)
                    results.append(molar_mass)
                    total_molar_mass += molar_mass
                    print(self.translate_text(element_string, "f_subscript") + ": " + str(atomic_mass) + "*" + subscript + " = " + str(
                        molar_mass))
        total_molar_mass *= float(coefficient)
        if len(results) > 1:
            print(str(coefficient) + "(" + str(results)[1:-1].replace(", ", "+") + ") = " + str(total_molar_mass))
            if round_sig_figs:
                total_molar_mass = self.round_sig_figs(total_molar_mass, results, "+-")
        return total_molar_mass

    def moles_to_grams(self, moles, formula, round_sig_figs):
        molar_mass = self.get_molar_mass(formula, False)
        print(moles + " mol " + formula + " to grams:")
        grams = float(moles) * molar_mass
        print(moles + "*" + str(molar_mass) + " = " + str(grams))
        if round_sig_figs:
            grams = self.round_sig_figs(grams, [moles, molar_mass], "*/")

        return str(grams)

    def get_sig_figs(self, value):
        dot_index = str(value).rfind(".")

        if dot_index != -1:
            sig_figs_string = re.search("[1-9][0-9]*[.]*[0-9]*", str(value))
        else:
            sig_figs_string = re.search("[0-9]*[^0]", str(value))

        if sig_figs_string != None:
            sig_figs = len(re.sub("[^0-9]", "", sig_figs_string.group()))
        else:
            sig_figs = 0
        return sig_figs

    def round_sig_figs(self, output, values, operation):
        lowest_sig_figs = 999999999
        sig_figs = 999999999
        for value in values:
            if operation == "*/":
                sig_figs = self.get_sig_figs(value)
            elif operation == "+-":
                d = decimal.Decimal(str(value))
                sig_figs = -d.as_tuple().exponent

            if sig_figs < lowest_sig_figs:
                lowest_sig_figs = sig_figs

        if operation == "*/":
            d = decimal.Decimal(str(output))
            decimal_places = -d.as_tuple().exponent
            out_sig_figs = self.get_sig_figs(output)
            if decimal_places != 0:
                output = round(self.shift_decimal_place(output, decimal_places, False), lowest_sig_figs - out_sig_figs)
                output = self.shift_decimal_place(output, decimal_places, True)
            else:
                output = round(output, lowest_sig_figs - out_sig_figs)
        elif operation == "+-":
            output = round(output, lowest_sig_figs)

        print("round_sig_figs (" + operation + "): " + str(values)[1:-1].replace("'", "") + " -> " + str(lowest_sig_figs) + "")

        sig_fig_difference = self.get_sig_figs(output) - lowest_sig_figs

        # Remove sig figs
        if sig_fig_difference > 0:
            output = str(output)[:lowest_sig_figs + 1]
        # Add sig figs
        elif sig_fig_difference < 0:
            output = str(output) + "."
            for i in range(-sig_fig_difference):
                output = str(output) + "0"

        return output

    def get_systematic_name(self, compound):
        formatted_compound = self.format_compound(compound)
        print(formatted_compound + " systematic name:")
        systematic_name = ""
        atomic_list = []
        order = []
        for polyatomic_ion in self.polyatomic_ions["ions"]:
            if polyatomic_ion["symbol"] in compound:
                subscript = re.sub("[^0-9]", "", re.search("[(]*" + polyatomic_ion["symbol"] + "[)]*[0-9]*", compound).group())
                if subscript == "":
                    subscript = "1"
                index = re.sub("[^A-Z]", "", compound).index(re.sub("[^A-Z]", "", polyatomic_ion["symbol"]))
                atomic_list.append({"symbol": polyatomic_ion["symbol"], "name": polyatomic_ion["name"].lower(),
                                    "subscript": int(subscript), "charge": polyatomic_ion["charge"],
                                    "category": "polyatomic ion", "index": index})
                compound = compound.replace(polyatomic_ion["symbol"], "")
                order.append(index)
        element_string_list = re.findall("[A-Z][a-z]?[0-9]*", compound)
        for element_string in element_string_list:
            symbol = re.sub("[^A-Za-z]", "", element_string)
            subscript = re.sub("[^0-9]", "", element_string)
            if subscript == "":
                subscript = "1"
            for element in self.periodic_table["elements"]:
                if element["symbol"] == symbol:
                    charge = 0
                    if element["xpos"] >= 15:
                        charge = element["xpos"] - 18
                    elif element["xpos"] <= 2:
                        charge = element["xpos"]
                    index = re.sub("[^A-Z]", "", compound).index(re.sub("[^A-Z]", "", symbol))
                    atomic_list.append({"symbol": symbol, "name": element["name"].lower(), "prefix": "", "suffix": "", "subscript": int(subscript), "charge": int(charge), "category": element["category"], "index": index})
                    order.append(index)
        atomic_list = [atomic_list[i] for i in order]

        not_metal = 0
        metal = 0
        for element in atomic_list:
            if "nonmetal" in element["category"] or "metalloid" in element["category"] or "noble gas" in element["category"] or "polyatomic ion" in element["category"]:
                not_metal += 1
            elif "metal" in element["category"]:
                metal += 1
            print(element["symbol"] + " is a " + element["category"])
        if metal == 0:
            print(formatted_compound + " is covalent")
            for element in atomic_list:
                if atomic_list.index(element) != 0:
                    syllables = self.syllables(element["name"])
                    element["name"] = syllables[0] + "ide"
                    element["prefix"] = self.prefixes_suffixes["prefixes"][element["f_subscript"] - 1]
                    if element["prefix"] == "mono" and element["name"][0] == "o":
                        element["prefix"] = "mon"
                systematic_name = str(systematic_name) + element["prefix"] + element["name"] + " "
        elif metal >= 1 and not_metal >= 1:
            print(formatted_compound + " is ionic")
            for element in atomic_list:
                if element["category"] == "transition metal":
                    charge = int(-(atomic_list[1]["charge"] * atomic_list[1]["subscript"]) / element["subscript"])
                    print(self.translate_text(element["symbol"] + str(element["subscript"]), "f_subscript") + " charge: " + "-(" + str(atomic_list[1]["charge"]) + "*" + str(atomic_list[1]["subscript"]) + ")/" + str(element["subscript"]) + " = " + str(charge))
                    systematic_name = element["name"] + "(" + self.int_to_roman(charge) + ") " + str(systematic_name)
                else:
                    if element["category"] != "polyatomic ion" and atomic_list.index(element) != 0:
                        syllables = self.syllables(element["name"])
                        element["name"] = syllables[0] + "ide"
                    systematic_name = str(systematic_name) + element["name"] + " "
        return systematic_name

    def format_compound(self, compound):
        element_string_list = re.findall("[(]*[A-Z][a-z]?[0-9]*[)]*[0-9]*", compound)
        print(element_string_list)
        formatted_compound = re.sub("[^0-9]", "", re.match("[0-9]*[A-Z]", compound).group())
        for element_string in element_string_list:
            formatted_compound = formatted_compound + self.translate_text(element_string, "f_subscript")
        return formatted_compound

    def translate_text(self, text, translation):
        normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
        numbers = "0123456789"

        subscript = str.maketrans(normal, "ₐ₈CDₑբGₕᵢⱼₖₗₘₙₒₚQᵣₛₜᵤᵥwₓᵧZₐ♭꜀ᑯₑբ₉ₕᵢⱼₖₗₘₙₒₚ૧ᵣₛₜᵤᵥwₓᵧ₂₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎")
        f_subscript = str.maketrans(numbers, "₀₁₂₃₄₅₆₇₈₉")
        superscript = str.maketrans(normal, "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖ۹ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾")
        f_superscript = str.maketrans(numbers, "⁰¹²³⁴⁵⁶⁷⁸⁹")

        if translation == "subscript":
            return text.translate(subscript)
        elif translation == "f_subscript":
            subscript_number = re.sub("[^0-9]", "", text)
            if len(subscript_number) == 1:
                return re.sub("[0-9]", "", text) + (subscript_number.translate(f_subscript)).replace("₁", "")
            return re.sub("[0-9]", "", text) + subscript_number.translate(f_subscript)

        elif translation == "superscript":
            return text.translate(superscript)
        elif translation == "f_superscript":
            return (text.translate(f_superscript)).replace("1", "")

    def int_to_roman(self, number):
        val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
        ]
        syb = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV",
            "I"
        ]
        roman_num = ""
        i = 0
        while number > 0:
            for _ in range(number // val[i]):
                roman_num += syb[i]
                number -= val[i]
            i += 1
        return roman_num

    def syllables(self, word):
        count = 0
        vowels = "aeiouy"
        syllables = [word[0]]
        if word[0] in vowels:
            count += 1
        for i in range(1, len(word)):
            if word[i] in vowels and word[i - 1] not in vowels:
                count += 1
                if word.endswith("e") and word[i] == "e":
                    count -= 1
            try:
                syllables[count - 1] = syllables[count - 1] + word[i]
            except IndexError:
                syllables.append(word[i])
        if count == 0:
            count += 1
        return syllables

    def shift_decimal_place(self, number, times, left):
        for i in range(times):
            if left:
                number /= 10
            else:
                number *= 10
        return number

    def exit(self):
        print("chemistry: Exiting")


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
