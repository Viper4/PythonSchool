import json
import re
import urllib.request
from pynput.keyboard import Controller, Listener, KeyCode, Key


class Input:
    def __init__(self):
        super().__init__()
        self.inputString = ""
        self.calcMode = ""
        self.lastResult = ""
        self.showWork = True
        settings_url = urllib.request.urlopen(
            'https://raw.githubusercontent.com/Viper4/PythonSchool/master/settings.json')
        self.settings = json.load(settings_url)

        periodic_table_url = urllib.request.urlopen(
            'https://raw.githubusercontent.com/Viper4/PythonSchool/master/periodic_table.json')
        self.periodic_table = json.load(periodic_table_url)

        prefixes_suffixes_url = urllib.request.urlopen(
            'https://raw.githubusercontent.com/Viper4/PythonSchool/master/prefixes_suffixes.json')
        self.prefixes_suffixes = json.load(prefixes_suffixes_url)

        polyatomic_ions_url = urllib.request.urlopen(
            'https://raw.githubusercontent.com/Viper4/PythonSchool/master/polyatomic_ions.json')
        self.polyatomic_ions = json.load(polyatomic_ions_url)

        print("chemistry: Active")

    def calculate(self):
        self.inputString = str(input())
        if "show work" in self.inputString or "sw" in self.inputString:
            self.showWork = not self.showWork
            print("Show work: " + str(self.showWork))
            re.sub("show work|sw", "", self.inputString)
        if self.inputString != "sw" and self.inputString != "show work":
            if "get_molar_mass" in self.inputString or "gmm" in self.inputString:
                print("get_molar_mass: Type compound Ex: 2NaHCO3")
                self.calcMode = "get_molar_mass"
            elif "get_element_info" in self.inputString or "gei" in self.inputString:
                print("get_element_info: Type element")
                self.calcMode = "get_element_info"
            elif "moles_to_grams" in self.inputString or "mtg" in self.inputString:
                print("moles_to_grams: Types moles and formula Ex: 1.3 mol NaCl")
                self.calcMode = "moles_to_grams"
            elif "get_sig_figs" in self.inputString or "gsf" in self.inputString:
                print("get_sig_figs: Type number")
                self.calcMode = "get_sig_figs"
            elif "get_systematic_name" in self.inputString or "gsn" in self.inputString:
                print("get_systematic_name: Type formula Ex: Fe2O3")
                self.calcMode = "get_systematic_name"
            elif "get_mass_percent" in self.inputString or "gmp" in self.inputString:
                print("get_mass_percent: Type elements/molecules in compound Ex: H2 O in H2O")
                self.calcMode = "get_mass_percent"
            else:
                if self.calcMode == "get_molar_mass":
                    molar_mass = str(self.get_molar_mass(self.inputString, False, self.showWork))
                    print("get_molar_mass: " + self.translate_text(self.inputString, "f_subscript") + ": " + molar_mass)
                    self.lastResult = molar_mass
                elif self.calcMode == "get_element_info":
                    for element in self.periodic_table["elements"]:
                        if element["symbol"] == self.inputString or element["name"] == self.inputString:
                            print(
                                "get_element_info: " + element["symbol"] + " " + element["name"] + " (temp in Kelvin)")
                            for variable in element:
                                if variable != "symbol" and variable != "name" and variable != "color":
                                    print(variable + ": " + str(element[str(variable)]))
                    self.lastResult = self.inputString
                elif self.calcMode == "moles_to_grams":
                    formula = re.sub("[0-9]*[.]*[0-9]* mol ", "", self.inputString)
                    moles = re.sub(" mol ", "", re.sub(formula, "", self.inputString))
                    grams = self.moles_to_grams(moles, formula, True, self.showWork)
                    print("moles_to_grams: " + self.translate_text(formula, "f_subscript") + " = " + grams + "g")
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
                    name = self.get_systematic_name(self.inputString, self.showWork)
                    print(
                        "get_systematic_name: " + self.translate_text(self.inputString, "f_subscript") + " -> " + name)
                    self.lastResult = self.inputString
                elif self.calcMode == "get_mass_percent":
                    split_string = self.inputString.split("in", 1)
                    try:
                        elements = re.findall("[(].*?[)][0-9]*|[A-Z][a-z]?[0-9]*", split_string[0])
                        compound = re.sub("[ ]", "", split_string[1])
                    except IndexError:
                        elements = []
                        compound = self.inputString
                    if len(elements) == 0:
                        elements = re.findall("[(].*?[)][0-9]*|[A-Z][a-z]?[0-9]*", compound)
                    print("get_mass_percent: " + self.translate_text(self.inputString, "f_subscript"))
                    self.get_mass_percent(elements, compound, True, self.showWork)
                    self.lastResult = self.inputString

    def get_molar_mass(self, formula, round_sig_figs, show_work):
        try:
            coefficient = re.match("^.*?[0-9]*", formula).group()
        except AttributeError:
            coefficient = "1"
        if coefficient == "":
            coefficient = "1"
        total_molar_mass = 0.0
        results = []
        formatted_compound = self.translate_text(formula, "f_subscript")
        if show_work:
            print(formatted_compound + " molar mass:")

        split_compound = re.findall("[(].*?[)][0-9]*|[A-Z][a-z]?[0-9]*", formula)
        for string in split_compound:
            element_string_list = re.findall("[A-Z][a-z]?[0-9]*", string)
            if len(element_string_list) > 1:
                formatted_polyatomic = self.translate_text(string, "f_subscript")
                p_subscript = re.sub("[^0-9]", "", re.search("[(].*?[)][0-9]*", string).group())
                if p_subscript == "":
                    p_subscript = "1"
                p_atomic_mass = self.get_molar_mass(re.sub("[()0-9]", "", string), False, False)

                if len(split_compound) == 1:
                    p_molar_mass = int(coefficient) * p_atomic_mass * int(p_subscript)
                    results.append(p_molar_mass)
                    total_molar_mass += p_molar_mass
                else:
                    p_molar_mass = p_atomic_mass * int(p_subscript)
                    results.append(p_molar_mass)
                    total_molar_mass += p_molar_mass
                if show_work:
                    print(formatted_polyatomic + ": " + str(p_atomic_mass) + "*" + p_subscript + " = " + str(
                        p_molar_mass))
            else:
                for element_string in element_string_list:
                    symbol = re.sub("[^A-Za-z]", "", element_string)
                    subscript = re.sub("[^0-9]", "", element_string)
                    if subscript == "":
                        subscript = "1"

                    for element in self.periodic_table["elements"]:
                        if element["symbol"] == symbol:
                            atomic_mass = element["atomic_mass"]
                            molar_mass = atomic_mass * int(subscript)
                            results.append(molar_mass)
                            total_molar_mass += molar_mass
                            if show_work:
                                print(self.translate_text(element_string, "f_subscript") + ": " + str(
                                    atomic_mass) + "*" + str(subscript) + " = " + str(molar_mass))
        if len(results) > 1:
            total_molar_mass *= int(coefficient)
            if show_work:
                print(formatted_compound + ": " + str(coefficient) + "(" + str(results)[1:-1].replace(", ", "+") + ") = " + str(total_molar_mass))
            if round_sig_figs:
                total_molar_mass = self.round_sig_figs(total_molar_mass, results, "+-", show_work)
        return total_molar_mass

    def moles_to_grams(self, moles, formula, round_sig_figs, show_work):
        molar_mass = self.get_molar_mass(formula, False, True)
        grams = float(moles) * molar_mass
        if show_work:
            print(moles + " mol " + formula + " to grams:")
            print(moles + "*" + str(molar_mass) + " = " + str(grams))
        if round_sig_figs:
            grams = self.round_sig_figs(grams, [moles, molar_mass], "*/", show_work)

        return str(grams)

    def get_sig_figs(self, value):
        dot_index = str(value).rfind(".")
        if dot_index != -1:
            sig_figs_string = re.search("[1-9][0-9]*[.]*[0-9]*", str(value))
        else:
            sig_figs_string = re.search("[0-9]*[^0]", str(value))

        if sig_figs_string is not None:
            sig_figs = len(re.sub("[^0-9]", "", sig_figs_string.group()))
        else:
            sig_figs = 0
        return sig_figs

    def round_sig_figs(self, output, values, operation, show_work):
        lowest_sig_figs = 999999999
        sig_figs = 999999999
        for value in values:
            if operation == "*/":
                sig_figs = self.get_sig_figs(value)
            elif operation == "+-":
                sig_figs = self.get_decimal_places(value)

            if sig_figs < lowest_sig_figs:
                lowest_sig_figs = sig_figs

        if operation == "*/":
            out_sig_figs = self.get_sig_figs(output)
            decimal_places = self.get_decimal_places(output)
            if decimal_places != 0:
                output = round(self.shift_decimal_place(output, decimal_places, False), lowest_sig_figs - out_sig_figs)
                output = self.shift_decimal_place(output, decimal_places, True)
            else:
                output = round(output, lowest_sig_figs - out_sig_figs)

            # Remove sig figs
            while self.get_sig_figs(output) - lowest_sig_figs > 0:
                if str(output).rfind(".") != -1:
                    output = str(output)[:-1]
                else:
                    output = str(output)[:-1] + "0"
            # Add sig figs
            while self.get_sig_figs(output) - lowest_sig_figs < 0:
                if str(output).rfind(".") != -1:
                    output = str(output) + "0"
                else:
                    output = str(output) + "."
        elif operation == "+-":
            output = round(output, lowest_sig_figs)

            # Remove decimals
            while self.get_decimal_places(output) - lowest_sig_figs > 0:
                output = str(output)[:-1]
            # Add decimals
            while self.get_decimal_places(output) - lowest_sig_figs < 0:
                if str(output).rfind(".") != -1:
                    output = str(output) + "0"
                else:
                    output = str(output) + ".0"
        if show_work:
            print("round_sig_figs (" + operation + "): " + str(values)[1:-1].replace("'", "") + " -> " + str(
                lowest_sig_figs) + " sig figs")

        return output

    def get_systematic_name(self, compound, show_work):
        formatted_compound = self.translate_text(compound, "f_subscript")
        print(formatted_compound + " systematic name:")
        systematic_name = ""
        atomic_list = self.process_compound(compound)

        not_metal = 0
        metal = 0
        for element in atomic_list:
            if "nonmetal" in element["category"] or "metalloid" in element["category"] or "noble gas" in \
                    element["category"] or "polyatomic ion" in element["category"]:
                not_metal += 1
            elif "metal" in element["category"]:
                metal += 1
            if show_work:
                print(element["symbol"] + " is a " + element["category"])
        if metal == 0:
            if show_work:
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
            if show_work:
                print(formatted_compound + " is ionic")
            for element in atomic_list:
                if element["category"] == "transition metal":
                    charge = 0
                    charges = []
                    for i in range(1, len(atomic_list)):
                        charge += int(-(atomic_list[i]["charge"] * atomic_list[i]["subscript"]))
                        charges.append(
                            "(" + str(atomic_list[i]["charge"]) + "*" + str(atomic_list[i]["subscript"]) + ")")

                    if show_work:
                        text = self.translate_text(element["symbol"] + str(element["subscript"]), "f_subscript") + \
                               " charge: " + "-(" + re.sub(", ", "+", str(charges)[1:-1].replace("'", "")) + ")/" + str(
                            element["subscript"]) + " = " + str(charge)
                        print(text)
                    systematic_name = element["name"] + "(" + self.int_to_roman(charge) + ") " + str(systematic_name)
                else:
                    if element["category"] != "polyatomic ion" and atomic_list.index(element) != 0:
                        syllables = self.syllables(element["name"])
                        element["name"] = syllables[0] + "ide"
                    systematic_name = str(systematic_name) + element["name"] + " "
        return systematic_name

    def get_mass_percent(self, elements, compound, round_sig_figs, show_work):
        total_molar_mass = self.get_molar_mass(compound, False, show_work)
        for element in elements:
            if element not in compound:
                print(element + " is not in " + compound)
            else:
                molar_mass = self.get_molar_mass(element, False, False)
                mass_percent = (molar_mass / total_molar_mass) * 100
                if round_sig_figs:
                    mass_percent = self.round_sig_figs(mass_percent, [molar_mass, total_molar_mass], "*/", show_work)
                if show_work:
                    print(self.translate_text(element, "f_subscript") + "%: (" + str(molar_mass) + "/" + str(
                        total_molar_mass) + ")*100 = " + str(mass_percent) + "%")
                else:
                    print(self.translate_text(element, "f_subscript") + "%: " + str(mass_percent) + "%")

    def process_compound(self, compound):
        atomic_list = []

        split_compound = re.findall("[(].*?[)][0-9]*|[A-Z][a-z]?[0-9]*", compound)
        for string in split_compound:
            element_string_list = re.findall("[A-Z][a-z]?[0-9]*", string)
            if len(element_string_list) > 1:
                p_subscript = re.sub("[^0-9]", "", re.search("[(].*?[)][0-9]*", string).group())
                if p_subscript == "":
                    p_subscript = "1"
                for polyatomic_ion in self.polyatomic_ions["ions"]:
                    if polyatomic_ion["symbol"] in string:
                        atomic_list.append({"raw_string": string, "symbol": polyatomic_ion["symbol"],
                                            "name": polyatomic_ion["name"].lower(),
                                            "subscript": int(p_subscript), "charge": polyatomic_ion["charge"],
                                            "category": "polyatomic ion"})
            else:
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
                            atomic_list.append(
                                {"raw_string": element_string, "symbol": symbol, "name": element["name"].lower(),
                                 "prefix": "", "suffix": "",
                                 "subscript": int(subscript), "charge": int(charge),
                                 "category": element["category"]})
        return atomic_list

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
            coefficient = re.match("^.*?[0-9]*", text).group()
            compound = re.search("[A-Z](.*)+", text).group()
            return coefficient + (compound.translate(f_subscript)).replace("₁", "")
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

    def get_decimal_places(self, number):
        split_string = str(number).split(".", 1)
        try:
            decimal_places = len(split_string[1])
        except IndexError:
            decimal_places = 0
        return decimal_places


controller = Controller()
inputClass = Input()


def on_press(key):
    if key == KeyCode(char=inputClass.settings["settings"]["exitKey"]):
        print("chemistry: Exiting")
        listener.stop()
    elif key == Key.enter:
        inputClass.calculate()


with Listener(on_press=on_press) as listener:
    listener.join()
