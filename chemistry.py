import json
import re
import time
import urllib.request
import scipy.constants


class Program:
    def __init__(self):
        super().__init__()
        with open("settings.json", encoding='utf-8') as file:
            self.settings = json.load(file)
        self.calcMode = ""
        self.lastResult = ""
        self.show_work = self.settings["load_settings"]["show_work"]
        self.load_locally = self.settings["load_settings"]["load_locally"]

        self.inputPrompt = "Type command: "
        valid_response = True
        if self.load_locally is None:
            valid_response = False
            local_prompt = input("Load files locally? Y/N: ")
        while not valid_response:
            if local_prompt.lower() == "y":
                self.load_locally = True
                valid_response = True
            elif local_prompt.lower() == "n":
                self.load_locally = False
                valid_response = True
            else:
                local_prompt = input("Invalid response, type Y or N: ")
            time.sleep(0.1)
        if self.load_locally:
            with open("periodic_table.json", encoding='utf-8') as file:
                self.periodic_table = json.load(file)
            with open("polyatomic_ions.json", encoding='utf-8') as file:
                self.polyatomic_ions = json.load(file)
            with open("prefixes_suffixes.json", encoding='utf-8') as file:
                self.prefixes_suffixes = json.load(file)
            with open("settings.json", encoding='utf-8') as file:
                self.settings = json.load(file)
        else:
            periodic_table_url = urllib.request.urlopen(
                'https://raw.githubusercontent.com/Viper4/PythonSchool/master/periodic_table.json')
            self.periodic_table = json.load(periodic_table_url)

            polyatomic_ions_url = urllib.request.urlopen(
                'https://raw.githubusercontent.com/Viper4/PythonSchool/master/polyatomic_ions.json')
            self.polyatomic_ions = json.load(polyatomic_ions_url)

            prefixes_suffixes_url = urllib.request.urlopen(
                'https://raw.githubusercontent.com/Viper4/PythonSchool/master/prefixes_suffixes.json')
            self.prefixes_suffixes = json.load(prefixes_suffixes_url)

            settings_url = urllib.request.urlopen(
                'https://raw.githubusercontent.com/Viper4/PythonSchool/master/settings.json')
            self.settings = json.load(settings_url)
        print("chemistry: Active, " + str(self.settings["commands"]["exit"]["command"])[1:-1].replace(", ",
                                                                                                      " or ") + " to exit")

    def calculate(self, inputString):
        if inputString.lower() in self.settings["commands"]["toggle_work"]["command"]:
            self.show_work = not self.show_work
            print("Show work: " + str(self.show_work))
            re.sub("show work|/sw", "", inputString)
        if inputString != "/sw" and inputString != "show work":
            switch_cmd = False
            for cmd in self.settings["commands"]:
                if inputString.lower() in self.settings["commands"][cmd]["command"]:
                    print(self.settings["commands"][cmd]["example"])
                    self.inputPrompt = cmd + ": "
                    self.calcMode = cmd
                    switch_cmd = True
                    break
                else:
                    switch_cmd = False
            if not switch_cmd:
                try:
                    if self.calcMode == "get_molar_mass":
                        molar_mass = str(self.get_molar_mass(inputString, True, self.show_work))
                        print("get_molar_mass: " + self.translate_text(inputString,
                                                                       "f_subscript") + " = " + molar_mass + "g/mol")
                        self.lastResult = molar_mass
                    elif self.calcMode == "get_element_info":
                        split_string = inputString.split(" ", 1)
                        element_string = split_string[0]
                        try:
                            variable = split_string[1]
                        except IndexError:
                            variable = ""
                        for element in self.periodic_table["elements"]:
                            if element["symbol"] == element_string or element["name"].lower() == element_string.lower():
                                print("get_element_info: " + element["symbol"] + " " + element[
                                    "name"] + " (temp in Kelvin)")
                                if variable == "" or variable.lower() == "all":
                                    for var in element:
                                        if var != "symbol" and var != "name":
                                            print(" " + var + ": " + str(element[str(var)]))
                                else:
                                    if variable.lower() in element:
                                        print(" " + variable.lower() + ": " + str(element[variable.lower()]))
                                    else:
                                        print(" '" + variable + "' does not exist")
                                break
                        self.lastResult = inputString
                    elif self.calcMode == "get_polyatomic_info":
                        split_string = inputString.split(" ", 1)
                        poly_string = split_string[0]
                        try:
                            variable = split_string[1]
                        except IndexError:
                            variable = ""
                        for polyatomic in self.polyatomic_ions["ions"]:
                            if polyatomic["symbol"] == poly_string or polyatomic["name"].lower() == poly_string.lower():
                                print("get_polyatomic_info: " + polyatomic["symbol"] + " " + polyatomic["name"])
                                if variable == "" or variable.lower() == "all":
                                    for var in polyatomic:
                                        if var != "symbol" and var != "name":
                                            print(" " + var + ": " + str(polyatomic[str(var)]))
                                else:
                                    if variable.lower() in polyatomic:
                                        print(" " + variable.lower() + ": " + str(polyatomic[variable.lower()]))
                                    else:
                                        print(" '" + variable + "' does not exist")
                                break
                        self.lastResult = inputString
                    elif self.calcMode == "unit_conversion":
                        split_string = re.split("[ ]", inputString, 2)
                        value = float(re.sub("[A-Za-z]", "", split_string[0]))
                        unit = re.sub("[0-9]*[.]*[0-9]*", "", split_string[0])
                        formula = split_string[1]
                        desired_unit = re.sub("[->][to]?[ ]*", "", split_string[2])

                        output = self.unit_conversion(value, unit, desired_unit, formula, True, self.show_work)
                        print("unit_conversion: " + str(value) + unit + " " + self.translate_text(formula,
                                                                                                  "f_subscript") + " = " + output)
                        self.lastResult = output
                    elif self.calcMode == "get_sig_figs":
                        if inputString == "Last Result" or inputString == "LR":
                            result = str(self.get_sig_figs(self.lastResult))
                            print("get_sig_figs: " + self.lastResult + " -> " + result)
                        else:
                            result = str(self.get_sig_figs(inputString))
                            print("get_sig_figs: " + inputString + " -> " + result)
                        self.lastResult = result
                    elif self.calcMode == "get_systematic_name":
                        name = self.get_systematic_name(inputString, self.show_work)
                        print("get_systematic_name: " + self.translate_text(inputString, "f_subscript") + " -> " + name)
                        self.lastResult = name
                    elif self.calcMode == "get_acid_name":
                        name = self.get_acid_name(inputString, self.show_work)
                        print("get_acid_name: " + self.translate_text(inputString, "f_subscript") + " -> " + name)
                        self.lastResult = name
                    elif self.calcMode == "get_chemical_formula":
                        formula = self.get_chemical_formula(inputString, self.show_work)
                        print("get_chemical_formula: " + formula)
                        self.lastResult = formula
                    elif self.calcMode == "get_mass_percent":
                        split_string = inputString.split("in", 1)
                        try:
                            elements = re.findall("[(].*?[)][0-9]*|[A-Z][a-z]?[0-9]*", split_string[0])
                            compound = re.sub("[ ]", "", split_string[1])
                        except IndexError:
                            elements = []
                            compound = inputString
                        if len(elements) == 0:
                            elements = re.findall("[(].*?[)][0-9]*|[A-Z][a-z]?[0-9]*", compound)
                        self.get_mass_percent(elements, compound, True, self.show_work)
                        self.lastResult = inputString
                    elif self.calcMode == "balance_equation":
                        equation = self.balance_equation(inputString, self.show_work)
                        print("balance_equation: " + equation)
                        self.lastResult = equation
                except AttributeError:
                    print(self.calcMode + ": '" + inputString + "' is invalid")

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
                p_subscript = re.sub("[^0-9]", "", re.search("[)][0-9]*", string).group())
                if p_subscript == "":
                    p_subscript = "1"
                p_atomic_mass = self.get_molar_mass(re.sub("[()][0-9]*", "", string), False, False)

                if len(split_compound) == 1:
                    p_molar_mass = int(coefficient) * p_atomic_mass * int(p_subscript)
                    results.append(p_molar_mass)
                    total_molar_mass += p_molar_mass
                else:
                    p_molar_mass = p_atomic_mass * int(p_subscript)
                    results.append(p_molar_mass)
                    total_molar_mass += p_molar_mass
                if show_work:
                    print(" " + formatted_polyatomic + ": " + str(p_atomic_mass) + "*" + p_subscript + " = " + str(
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
                                print(" " + self.translate_text(element_string, "f_subscript") + ": " + str(
                                    atomic_mass) + "*" + str(subscript) + " = " + str(molar_mass))
        if len(results) > 1:
            total_molar_mass *= int(coefficient)
            if show_work:
                print(" " + formatted_compound + ": " + str(coefficient) + "(" + str(results)[1:-1].replace(", ",
                                                                                                            "+") + ") = " + str(
                    total_molar_mass))
            if round_sig_figs:
                total_molar_mass = self.round_sig_figs(total_molar_mass, results, "+-", show_work)
        return total_molar_mass

    def unit_conversion(self, value, unit, desired_unit, formula, round_sig_figs, show_work):
        output_val = 0
        molar_mass = 0
        if formula.lower() != "none":
            molar_mass = self.get_molar_mass(formula, False, show_work)
            if show_work:
                print(str(value) + unit + " " + self.translate_text(formula,
                                                                    "f_subscript") + " to " + desired_unit + ": ")

        if unit == "g" or unit == "grams":
            if desired_unit == "mol" or desired_unit == "moles":
                output_val = value / molar_mass
                if show_work:
                    print(" " + str(value) + "/" + str(molar_mass) + " = " + str(output_val))
                if round_sig_figs:
                    output_val = self.round_sig_figs(output_val, [value, molar_mass], "*/", show_work)
        elif unit == "mol" or unit == "moles":
            if desired_unit == "g" or desired_unit == "grams":
                output_val = value * molar_mass
                if show_work:
                    print(" " + str(value) + "*" + str(molar_mass) + " = " + str(output_val))
                if round_sig_figs:
                    output_val = self.round_sig_figs(output_val, [value, molar_mass], "*/", show_work)
            elif desired_unit == "atoms" or desired_unit == "molecules":
                output_val = value * scipy.constants.N_A
                if show_work:
                    print(" " + str(value) + "*" + str(scipy.constants.N_A) + " = " + str(output_val))
                if round_sig_figs:
                    output_val = self.round_sig_figs(output_val, [value, scipy.constants.N_A], "*/", show_work)
        elif unit == "atoms" or unit == "molecules":
            if desired_unit == "mol" or desired_unit == "moles":
                output_val = value / scipy.constants.N_A
                if show_work:
                    print(" " + str(value) + "/" + str(scipy.constants.N_A) + " = " + str(output_val))
                if round_sig_figs:
                    output_val = self.round_sig_figs(output_val, [value, scipy.constants.N_A], "*/", show_work)
        return str(output_val) + desired_unit

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

    def get_systematic_name(self, formula, show_work):
        formatted_compound = self.translate_text(formula, "f_subscript")
        if show_work:
            print(formatted_compound + " systematic name:")
        systematic_name = ""
        atomic_list = self.process_compound(formula)

        not_metal = 0
        metal = 0
        for item in atomic_list:
            if "nonmetal" in item["category"] or "metalloid" in item["category"] or "noble gas" in \
                    item["category"] or "polyatomic ion" in item["category"]:
                not_metal += 1
            elif "metal" in item["category"]:
                metal += 1
            if show_work:
                print(" " + item["symbol"] + " is a " + item["category"])
        if metal == 0:
            if show_work:
                print(" " + formatted_compound + " is covalent")
            for item in atomic_list:
                syllables = self.syllables(item["name"].lower())
                item["prefix"] = self.prefixes_suffixes["prefixes"][item["subscript"] - 1]

                if atomic_list.index(item) != 0:
                    item["name"] = syllables[0] + "ide"
                    if item["name"][0] == "o" and item["prefix"] == "mono":
                        item["prefix"] = "mon"
                else:
                    if item["prefix"] == "mono":
                        item["prefix"] = ""

                systematic_name = str(systematic_name) + (item["prefix"] + item["name"]).capitalize() + " "
        elif metal >= 1 and not_metal >= 1:
            if show_work:
                print(" " + formatted_compound + " is ionic")
            for element in atomic_list:
                if "transition metal" in element["category"]:
                    charge = 0
                    charges = []
                    for i in range(1, len(atomic_list)):
                        charge += int(-(atomic_list[i]["charge"] * atomic_list[i]["subscript"]))
                        charges.append(
                            "(" + str(atomic_list[i]["charge"]) + "*" + str(atomic_list[i]["subscript"]) + ")")
                    charge = int(charge / element["subscript"])
                    if show_work:
                        text = self.translate_text(element["symbol"] + str(element["subscript"]), "f_subscript") + \
                               " charge: " + "-(" + re.sub(", ", "+", str(charges)[1:-1].replace("'", "")) + ")/" + str(
                            element["subscript"]) + " = " + str(charge)
                        print(" " + text)
                    systematic_name = element["name"] + "(" + self.int_to_roman(charge) + ") " + str(systematic_name)
                else:
                    if element["category"] != "polyatomic ion" and atomic_list.index(element) != 0:
                        syllables = self.syllables(element["name"].lower())
                        element["name"] = syllables[0] + "ide"
                    systematic_name += element["name"].capitalize() + " "
        return systematic_name

    def get_acid_name(self, formula, show_work):
        formatted_compound = self.translate_text(formula, "f_subscript")
        if show_work:
            print(formatted_compound + " acid name:")
        acid_name = ""
        atomic_list = self.process_compound(formula)
        for item in atomic_list:
            syllables = self.syllables(item["name"].lower())
            if atomic_list.index(item) == 0:
                acid_name = re.sub(syllables[len(syllables) - 1], "", item["name"].lower())[:-1]
            else:
                if item["category"] == "polyatomic_ion":
                    extra_ending = item["ending"]
                    if "ate" in syllables[len(syllables) - 1].lower():
                        if show_work:
                            print(" " + item["symbol"] + " ends in ate")

                        acid_name = syllables[0] + str(extra_ending) + "ic"
                    elif "ite" in syllables[len(syllables) - 1].lower():
                        if show_work:
                            print(" " + item["symbol"] + " ends in ite")
                        acid_name = syllables[0] + str(extra_ending) + "ous"
                else:
                    if show_work:
                        print(" " + item["symbol"] + " ends in ide")
                    acid_name += syllables[0] + "ic"

        return acid_name.capitalize() + " acid"

    def get_chemical_formula(self, systematic_name, show_work):
        formula = ""
        if show_work:
            print(systematic_name + " chemical formula:")
        atomic_list = self.process_sys_name(systematic_name)

        not_metal = 0
        metal = 0
        acid = False
        for element in atomic_list:
            if element["symbol"] == "H":
                acid = True
                metal += 1
            else:
                if "nonmetal" in element["category"] or "metalloid" in element["category"] or "noble gas" in element[
                    "category"] or "polyatomic_ion" in element["category"]:
                    not_metal += 1
                elif "metal" in element["category"]:
                    metal += 1
            if show_work:
                print(" " + element["symbol"] + " is a " + element["category"])
        if metal == 0:
            if show_work:
                print(" " + systematic_name + " is covalent")
            for item in atomic_list:
                if item["category"] == "polyatomic_ion" and item["subscript"] != 1:
                    formula += "(" + item["symbol"] + ")" + str(item["subscript"])
                else:
                    formula += item["symbol"] + str(item["subscript"])
        elif metal >= 1 and not_metal >= 1:
            if show_work:
                if acid:
                    print(" " + systematic_name + " is an acid")
                else:
                    print(" " + systematic_name + " is ionic")
            for dictionary in atomic_list:
                subscript = 0
                if dictionary["charge"] is not None:
                    index = atomic_list.index(dictionary)
                    other_dictionary = atomic_list[(len(atomic_list) - 1) - index]
                    subscript = abs(other_dictionary["charge"])
                    maxCharge = max(dictionary["charge"], other_dictionary["charge"])
                    minCharge = min(dictionary["charge"], other_dictionary["charge"])
                    remainder = maxCharge % minCharge
                    divisible = remainder == 0

                    if show_work:
                        other_charge = other_dictionary["charge"]
                        if other_dictionary["charge"] > 0:
                            other_charge = "+" + str(other_dictionary["charge"])
                        print(" Flip and drop: " +
                              self.translate_text(self.translate_text(other_dictionary["symbol"], "f_subscript") + str(other_charge)[::-1], "f_superscript")
                              + " -> " + self.translate_text(dictionary["symbol"] + str(subscript), "f_subscript"))
                    if divisible:
                        if dictionary["charge"] == maxCharge:
                            dictionary["charge"] = -int(maxCharge / minCharge)
                            other_dictionary["charge"] = -int(minCharge / minCharge)
                        else:
                            dictionary["charge"] = -int(minCharge / minCharge)
                            other_dictionary["charge"] = -int(maxCharge / minCharge)
                if dictionary["category"] == "polyatomic_ion" and subscript != 1:
                    formula += "(" + dictionary["symbol"] + ")" + str(subscript)
                else:
                    formula += dictionary["symbol"] + str(subscript)

        return self.translate_text(formula, "f_subscript")

    def get_mass_percent(self, elements, compound, round_sig_figs, show_work):
        total_molar_mass = self.get_molar_mass(compound, False, show_work)
        if show_work:
            print("mass percent of " + self.translate_text(inputString, "f_subscript") + ":")
        for element in elements:
            if element not in compound:
                print(element + " is not in " + compound)
            else:
                molar_mass = self.get_molar_mass(element, False, False)
                mass_percent = (molar_mass / total_molar_mass) * 100
                if round_sig_figs:
                    mass_percent = self.round_sig_figs(mass_percent, [molar_mass, total_molar_mass], "*/", show_work)
                if show_work:
                    print(" " + self.translate_text(element, "f_subscript") + ": (" + str(molar_mass) + "/" + str(
                        total_molar_mass) + ")*100 = " + str(mass_percent) + "%")
                else:
                    print(" " + self.translate_text(element, "f_subscript") + ": " + str(mass_percent) + "%")

    def balance_equation(self, equation, show_work):
        split_equation = str(equation).split("->", 1)
        reactants = split_equation[0].replace(" ", "").split("+")
        products = split_equation[1].replace(" ", "").split("+")
        reactant_text = []
        product_text = []

        reactant_compounds = {}
        reactant_amounts = {}
        product_compounds = {}
        product_amounts = {}
        for reactant in reactants:
            try:
                coefficient = re.match("^.*?[0-9]*", reactant).group()
            except AttributeError:
                coefficient = "1"
            if coefficient == "":
                coefficient = "1"
            atomic_list = self.process_compound(reactant)
            amounts = {}
            for item in atomic_list:
                amounts[item["symbol"]] = float(coefficient) * item["subscript"]
                try:
                    reactant_amounts[item["symbol"]] += float(coefficient) * item["subscript"]
                except KeyError:
                    reactant_amounts[item["symbol"]] = float(coefficient) * item["subscript"]
                reactant_compounds[reactant] = {"coefficient": float(coefficient), "elements": amounts}
        for product in products:
            try:
                coefficient = re.match("^.*?[0-9]*", product).group()
            except AttributeError:
                coefficient = "1"
            if coefficient == "":
                coefficient = "1"
            atomic_list = self.process_compound(product)
            amounts = {}
            for item in atomic_list:
                amounts[item["symbol"]] = float(coefficient) * item["subscript"]
                try:
                    product_amounts[item["symbol"]] += float(coefficient) * item["subscript"]
                except KeyError:
                    product_amounts[item["symbol"]] = float(coefficient) * item["subscript"]
                product_compounds[product] = {"coefficient": float(coefficient), "elements": amounts}

        balanced = False
        i = 0

        while not balanced:
            reactant_text = []
            product_text = []
            if show_work:
                print(" Reactants | Products")
            for element in reactant_amounts:
                if show_work:
                    print(" " + element + ": " + str(reactant_amounts[element]) + " | " + element + ": " + str(product_amounts[element]))
                balanced = reactant_amounts[element] == product_amounts[element]

            # Calculating new coefficients
            temp_pr_amounts = {}
            for product in products:
                for element in product_compounds[product]["elements"]:
                    if product_amounts[element] < reactant_amounts[element]:
                        remainder = reactant_amounts[element] % product_amounts[element]
                        divisible = remainder == 0
                        if divisible:
                            coefficient = product_compounds[product]["coefficient"] * (reactant_amounts[element] / product_amounts[element])
                            if show_work:
                                print(" New coefficient for " + product + ": " + str(coefficient) + " = " + str(product_compounds[product]["coefficient"]) + " * " + str(reactant_amounts[element]) + " / " + str(product_amounts[element]))
                            product_compounds[product]["coefficient"] = coefficient
                atomic_list = self.process_compound(product)
                for item in atomic_list:
                    try:
                        temp_pr_amounts[item["symbol"]] += product_compounds[product]["coefficient"] * item["subscript"]
                    except KeyError:
                        temp_pr_amounts[item["symbol"]] = product_compounds[product]["coefficient"] * item["subscript"]
                    product_amounts[item["symbol"]] = temp_pr_amounts[item["symbol"]]

                coefficient_string = str(int(product_compounds[product]["coefficient"]))
                if len(coefficient_string) == 1 and coefficient_string == "1":
                    coefficient_string = ""
                product_text.append(coefficient_string + self.translate_text(re.sub(re.match("^.*?[0-9]*", product).group(), "", product), "f_subscript"))

            temp_re_amounts = {}
            for reactant in reactants:
                for element in reactant_compounds[reactant]["elements"]:
                    if reactant_amounts[element] < product_amounts[element]:
                        remainder = product_amounts[element] % reactant_amounts[element]
                        divisible = remainder == 0
                        if divisible:
                            coefficient = reactant_compounds[reactant]["coefficient"] * (product_amounts[element] / reactant_amounts[element])
                            if show_work:
                                print(" New coefficient for " + reactant + ": " + str(coefficient) + " = " + str(reactant_compounds[reactant]["coefficient"]) + " * " + str(product_amounts[element]) + " / " + str(reactant_amounts[element]))
                            reactant_compounds[reactant]["coefficient"] = coefficient
                atomic_list = self.process_compound(reactant)
                for item in atomic_list:
                    try:
                        temp_re_amounts[item["symbol"]] += reactant_compounds[reactant]["coefficient"] * item["subscript"]
                    except KeyError:
                        temp_re_amounts[item["symbol"]] = reactant_compounds[reactant]["coefficient"] * item["subscript"]
                    reactant_amounts[item["symbol"]] = temp_re_amounts[item["symbol"]]

                coefficient_string = str(int(reactant_compounds[reactant]["coefficient"]))
                if len(coefficient_string) == 1 and coefficient_string == "1":
                    coefficient_string = ""
                reactant_text.append(coefficient_string + self.translate_text(re.sub(re.match("^.*?[0-9]*", reactant).group(), "", reactant), "f_subscript"))

            i += 1
            if i > 9:
                balanced = True
        return (str(reactant_text)[1:-1].replace(", ", " + ") + " -> " + str(product_text)[1:-1].replace(", ", " + ")).replace("'", "")

    def process_compound(self, compound):
        atomic_list = []

        split_compound = re.findall("[(].*?[)][0-9]*|[A-Z][a-z]?[0-9]*", compound)
        for string in split_compound:
            element_string_list = re.findall("[A-Z][a-z]?[0-9]*", string)
            if len(element_string_list) > 1:
                p_subscript = re.sub("[(].*?[)]", "", re.search("[(].*?[)][0-9]*", string).group())
                if p_subscript == "":
                    p_subscript = "1"
                for polyatomic_ion in self.polyatomic_ions["ions"]:
                    if polyatomic_ion["symbol"] in string:
                        append = False
                        if len(polyatomic_ion["symbol"]) == len(
                                re.sub("[()]", "", re.search("[(].*?[)]", string).group())):
                            append = True
                        if append:
                            atomic_list.append({"raw_string": string, "symbol": polyatomic_ion["symbol"],
                                                "name": polyatomic_ion["name"],
                                                "subscript": int(p_subscript),
                                                "charge": polyatomic_ion["charge"],
                                                "category": "polyatomic ion",
                                                "ending": polyatomic_ion["ending"]})
            else:
                for element_string in element_string_list:
                    symbol = re.sub("[^A-Za-z]", "", element_string)
                    subscript = re.sub("[^0-9]", "", element_string)
                    if subscript == "":
                        subscript = "1"

                    for element in self.periodic_table["elements"]:
                        if element["symbol"] == symbol:
                            atomic_list.append(
                                {"raw_string": element_string, "symbol": symbol, "name": element["name"],
                                 "prefix": "", "suffix": "",
                                 "subscript": int(subscript),
                                 "charge": element["charge"],
                                 "category": element["category"]})
        return atomic_list

    def process_sys_name(self, systematic_name):
        names = str(systematic_name).split(" ")
        atomic_list = []
        for name in names:
            index = names.index(name)
            formatted_name = re.sub("[(].*?[)]", "", name).capitalize()
            prefix = ""
            subscript = 1
            for pre in self.prefixes_suffixes["prefixes"]:
                if pre.capitalize() in formatted_name:
                    prefix = pre
                    subscript = self.prefixes_suffixes["prefixes"].index(pre) + 1
                    formatted_name = (re.sub(pre, "", formatted_name.lower())).capitalize()

            for polyatomic_ion in self.polyatomic_ions["ions"]:
                if polyatomic_ion["name"] in formatted_name:
                    atomic_list.append(
                        {"sys_name": name, "symbol": "(" + polyatomic_ion["symbol"] + ")", "prefix": prefix, "subscript": subscript,
                         "category": "polyatomic_ion",
                         "charge": polyatomic_ion["charge"]})
                    break
            else:
                for element in self.periodic_table["elements"]:
                    syllables = self.syllables(element["name"].lower())
                    if index == 0:
                        match = formatted_name == element["name"].capitalize()
                    else:
                        match = syllables[0].capitalize() in formatted_name
                    if match:
                        charge = element["charge"]

                        if "(" in name:
                            charge = self.roman_to_int(re.sub("[()]", "", re.search("[(].*?[)]", name).group()))
                        atomic_list.append(
                            {"sys_name": name, "symbol": element["symbol"], "prefix": prefix, "subscript": subscript,
                             "category": element["category"],
                             "charge": charge})
                        break
        return atomic_list

    def translate_text(self, text, translation):
        normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
        numbers = "0123456789"
        sup = "0123456789+-"

        subscript = str.maketrans(normal, "ₐ₈CDₑբGₕᵢⱼₖₗₘₙₒₚQᵣₛₜᵤᵥwₓᵧZₐ♭꜀ᑯₑբ₉ₕᵢⱼₖₗₘₙₒₚ૧ᵣₛₜᵤᵥwₓᵧ₂₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎")
        f_subscript = str.maketrans(numbers, "₀₁₂₃₄₅₆₇₈₉")
        superscript = str.maketrans(normal, "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖ۹ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾")
        f_superscript = str.maketrans(sup, "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")

        if translation == "subscript":
            return text.translate(subscript)
        elif translation == "f_subscript":
            coefficient = re.match("^.*?[0-9]*", text).group()
            if coefficient == "1":
                coefficient = ""
            compound = re.search("[(]*[A-Z](.*)+", text).group()
            return coefficient + re.sub("(?<=\D)[1]{1}(?=\D)|(?<=\D)[1]{1}(?=$)", "", compound).translate(f_subscript)
        elif translation == "superscript":
            return text.translate(superscript)
        elif translation == "f_superscript":
            coefficient = re.match("^.*?[0-9]*", text).group()
            if coefficient == "1":
                coefficient = ""
            compound = re.search("[(]*[A-Z](.*)+", text).group()
            return coefficient + re.sub("(?<=\D)[1]{1}(?=\D)|(?<=\D)[1]{1}(?=$)", "", compound).translate(f_superscript)

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

    def roman_to_int(self, roman_num):
        roman = {"M": 1000, "CM": 900, "D": 500, "CD": 400,
                 "C": 100, "XC": 90, "L": 50, "XL": 40,
                 "X": 10, "IX": 9, "V": 5, "IV": 4,
                 "I": 1}
        i = 0
        number = 0
        while i < len(roman_num):
            if i + 1 < len(roman_num) and roman_num[i:i + 2] in roman:
                number += roman[roman_num[i:i + 2]]
                i += 2
            else:
                number += roman[roman_num[i]]
                i += 1
        return number

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
        try:
            decimal_places = len(str(number).split(".", 1)[1])
        except IndexError:
            decimal_places = 0
        return decimal_places


running = True
program = Program()

while running:
    inputString = input(program.inputPrompt)
    if inputString.lower() in program.settings["commands"]["exit"]["command"]:
        print("chemistry: Exiting")
        running = False
    elif inputString.lower() in program.settings["commands"]["command_list"]["command"]:
        print("command_list: All commands")
        for cmd in program.settings["commands"]:
            print(
                " " + cmd + ": " + str(program.settings["commands"][cmd]["command"])[1:-1].replace(", ", " or ") + " " +
                program.settings["commands"][cmd]["info"])
    else:
        program.calculate(inputString)
    time.sleep(0.1)