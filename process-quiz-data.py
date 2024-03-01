"""
Copyright 2024 by Jonas Lache <jonas.lache@hs-ruhrwest.de>
SPDX-License-Identifier: GPL-3.0-or-later
"""

# Import necessary libraries
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import pandas as pd
import re
import json

# Dictionaries for conversion of the time strings to seconds:
time_values_de = {
    "Sekunden":1, "Sekunde":1,
    "Minuten":60, "Minute":60,
    "Stunden":3600, "Stunde":3600,
    "Tage":86400, "Tag":86400
}
time_values_en = {
    "secs":1, "sec":1,
    "mins":60, "min":60,
    "hours":3600, "hour":3600,
    "days":86400, "day":86400
}

# Dictionary for matching the column name for the "time taken" column
# to the time_values dictionaries
time_languages = {
    "German":[time_values_de, "Verbrauchte Zeit"],
    "English":[time_values_en, "Time taken"]
}

# Function to extract STACKrate evaluation results
def get_survey_results(str):
    pattern = r'ans_survey:\s+"(.*?)"\s+\[score\]'
    match = re.search(pattern, str)
    if match:
        json_string = match.group(1)
        try:
            # Remove escape characters:
            survey_data = json.loads(json_string.replace('\\', ''))
            return survey_data
        except json.JSONDecodeError:
            return None
    return None

# Function to extract either ratings or comments from STACKrate evaluation dict
def extract_info(dictionary, key, attr=""):
    if dictionary and key in dictionary:
        if attr=="":
            return dictionary[key]
        else:
            return dictionary[key][attr]
    else:
        return None

# Function to convert information from the "time spent" column to seconds
def string_time_to_sec(time_str, time_values):
    total_seconds = 0
    time_parts = re.findall(r"(\d+)\s?(\w+)", time_str)
    for time_part in time_parts:
        value, unit = time_part
        total_seconds += int(value) * time_values[unit]
    return total_seconds

# Returns true if a given PRT has been active in an attempt
def is_prt_active(response_str, prt_name):
    return prt_name + ": # =" in response_str

# Returns the score of a given PRT in a an attempt
def get_prt_score(response_str, prt_name):
    pattern = r"{}: # = ([0-9]+(?:\.[0-9]+)?)".format(prt_name)
    match = re.search(pattern, response_str)
    if match:
        return float(match.group(1))
    else:
        return None

# Returns the value or the state of a given input field in an attempt
def get_input_value(response_str, input_name, mode=""):
    pattern = r"{}: (.*?) \[(score|valid|invalid)\]".format(input_name)
    match = re.search(pattern, response_str)
    if match:
        input_value = match.group(1)
        status = match.group(2)
        if mode=="value" or mode=="":
            return input_value
        if mode=="state":
            return status
        else:
            return None
    else:
        return None

# Makes the radio buttons for the language selection visible in the GUI
def show_language_radiobuttons():
    checkbox_seconds_row = checkbox_seconds.grid_info()["row"]
    radio_language_label.grid(row=checkbox_seconds_row+1)
    i=1
    for button in lang_radiobuttons:
        button.grid(row=checkbox_seconds_row+1+i)
        i+=1

# Makes the radio buttons for the language selection invisible in the GUI
def hide_language_radiobuttons():
    radio_language_label.grid_forget()
    for button in lang_radiobuttons:
        button.grid_forget()

# Shows/hides language selection in GUI when selecting/deselecting the option to
# convert string times to seconds
def toggle_seconds_options():
    if var_checkbox_seconds.get():
        show_language_radiobuttons()
    else:
        hide_language_radiobuttons()

# Stores input fields that are selected in the GUI
input_checkboxes_states = []
selected_input_checkboxes = []
def update_selected_inputs(checkbox_name, variable):
    index = next(i for i, name in enumerate(input_names) if name == checkbox_name)
    input_checkboxes_states[index] = variable.get()
    global selected_input_checkboxes
    selected_input_checkboxes = [name for name, state in zip(input_names, input_checkboxes_states) if state]

# Stores response trees that are selected in the GUI
prt_checkboxes_states = []
selected_prt_checkboxes = []
def update_selected_prts(prt_name, variable):
    index = next(i for i, name in enumerate(prts) if name == prt_name)
    prt_checkboxes_states[index] = variable.get()
    global selected_prt_checkboxes
    selected_prt_checkboxes = [name for name, state in zip(prts, prt_checkboxes_states) if state]

# Identifies the PRT and input names out of a STACK response string
def identify_prts_inputs(response_str):
    list = response_str.split("; ")
    dict = {}
    for element in list:
        new_el = element.split(": ")
        if len(new_el)==2:
            dict[new_el[0]] = new_el[1]
    keys = [*dict]
    keys = [item for item in keys if item != "Seed" ]
    inputs = []
    prts = []
    newdict = {}
    pattern = r'\[[a-z]+\]$'
    for key in keys:
        value = dict[key]
        match = re.search(pattern, value) 
        if match is not None:
            inputs.append(key)
            # FIXME
            # It may be that someone names their answer note `[prt1-1-T]` etc.
            # This would result in the corresponding response tree would be
            # recognised as an input field.
        else:
            prts.append(key)
    newdict["prts"] = prts
    newdict["inputs"] = inputs
    return newdict

# Function which is called when submitting an input CSV file via GUI. Opens a
# file dialog and prepares GUI for next step
def open_csv_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        global df
        df = pd.read_csv(file_path)
        global options
        options = list(df.keys())
        global col_radiobuttons
        col_radiobuttons = []
        spalten_label.grid(row=1)
        # Create radiobutton for each column in csv file:
        global selected_col
        selected_col = tk.StringVar()
        i=1
        for option in options:
            radiobutton = tk.Radiobutton(
                root,
                text=option,
                value=option,
                variable=selected_col,
                tristatevalue=0
            )
            col_radiobuttons.append(radiobutton)
            radiobutton.grid(row=i+1)
            i+=1
        submit_button_cols.grid(row=len(col_radiobuttons)+2)
        open_button.grid_forget()
        open_button_info.grid_forget()

# Function which is called when user subits the answer column via GUI
def submit_columns():
    for button in col_radiobuttons:
        button.grid_forget()
    spalten_label.grid_forget()
    submit_button_cols.grid_forget()
    global input_names
    input_names = set()
    global prts
    prts = set()
    df[f"{selected_col.get()}: identified_placeholders"] = df[selected_col.get()].apply(identify_prts_inputs)
    for result in df[f"{selected_col.get()}: identified_placeholders"]:
        if result:
            input_names.update(result["inputs"])
            prts.update(result["prts"])
    i=1
    input_checkboxes_label.grid(row=i)
    i+=1
    global input_checkboxes
    input_checkboxes = []
    for input in input_names:
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(
            root,
            variable=var,
            text=input,
            command=lambda input=input, var=var: update_selected_inputs(input, var),
            tristatevalue=0
        )
        input_checkboxes.append(checkbox)
        checkbox.grid(row=i)
        input_checkboxes_states.append(False)
        i+=1
    sep1.grid(row=i, ipadx=300, pady=10)
    i+=1
    prt_checkboxes_label.grid(row=i)
    i+=1
    global prt_checkboxes
    prt_checkboxes = []
    for prt in prts:
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(
            root,
            variable=var,
            text=prt,
            command=lambda prt=prt, var=var: update_selected_prts(prt, var),
            tristatevalue=0
        )
        prt_checkboxes.append(checkbox)
        checkbox.grid(row=i)
        prt_checkboxes_states.append(False)
        i+=1
    sep2.grid(row=i, ipadx=300, pady=10)
    i+=1
    additional_options_label.grid(row=i)
    i+=1
    checkbox_seconds.grid(row=i)
    i=i+2+len(time_languages)
    checkbox_stackrate.grid(row=i)
    i+=1
    process_button.grid(row=i)
    del df[f"{selected_col.get()}: identified_placeholders"]

# Function which is called when the clicks the "Save CSV file" button in GUI.
# Opens file dialog for output file, exports file, shows "Close" button
def export_csv_file():
    export_filename = filedialog.asksaveasfilename(filetypes=[("CSV text files", "*.csv")])
    if ".csv" not in export_filename:
        export_filename+=".csv"
    df.to_csv(export_filename, index=False)
    success_text.grid(row=1)
    close_button.grid(row=2)
    export_button_info.grid_forget()
    export_button.grid_forget()

# Function where most of the "magic" happens. Called when clicking on "Submit".
# Depending on user's wishes, all columns are created
def process_input_strings():
    if var_checkbox_seconds.get():
        time_values = time_languages[selected_lang.get()][0]
        df_key = time_languages[selected_lang.get()][1]
        try:
             df["Seconds taken"] = df[df_key].apply(lambda x: string_time_to_sec(x,time_values))
        except:
            print("There is an error finding the column that contains the time information. Please make sure you selected the correct language.")
    for input_field in selected_input_checkboxes:
        df[f"{selected_col.get()}: {input_field} value"] = df[selected_col.get()].apply(lambda x: get_input_value(x, input_field, mode="value"))
        df[f"{selected_col.get()}: {input_field} state"] = df[selected_col.get()].apply(lambda x: get_input_value(x, input_field, mode="state"))
    for prt in selected_prt_checkboxes:
        df[f"{selected_col.get()}: {prt} active"] = df[selected_col.get()].apply(lambda x: is_prt_active(x, prt))
        df[f"{selected_col.get()}: {prt} score"] = df[selected_col.get()].apply(lambda x: get_prt_score(x, prt))
    if var_checkbox_stackrate.get():
        df[f"{selected_col.get()}: Survey_Results"] = df[selected_col.get()].apply(get_survey_results)
        # Extract all STACKrate IDs:
        all_stackrate_keys = set()
        for survey_result in df[f"{selected_col.get()}: Survey_Results"]:
            if survey_result:
                all_stackrate_keys.update(survey_result.keys())
        # Create columns for all IDs:
        for key in all_stackrate_keys:
            df[f"{selected_col.get()}: STACKrate ratings to ID {key}"] = df[f"{selected_col.get()}: Survey_Results"].apply(lambda x: extract_info(x, key, attr="ratings"))
            df[f"{selected_col.get()}: STACKrate comments to ID {key}"] = df[f"{selected_col.get()}: Survey_Results"].apply(lambda x: extract_info(x, key, attr="comment"))
        df.drop(f"{selected_col.get()}: Survey_Results", axis=1, inplace=True)
    input_checkboxes_label.grid_forget()
    for box in input_checkboxes:
        box.grid_forget()
    sep1.grid_forget()
    prt_checkboxes_label.grid_forget()
    for box in prt_checkboxes:
        box.grid_forget()
    sep2.grid_forget()
    additional_options_label.grid_forget()
    checkbox_seconds.grid_forget()
    hide_language_radiobuttons()
    checkbox_stackrate.grid_forget()
    process_button.grid_forget()
    export_button_info.grid(row=1)
    export_button.grid(row=2)

# Closes GUI window
def close_window():
    root.destroy()

# GUI setup
root = tk.Tk()
root.title("STACK Response File Processor")

# GUI elements for opening the input csv file
open_button_info = tk.Label(root, text="Click on the following button to select a CSV file:")
open_button_info.grid(row=1)
open_button = tk.Button(root, text="Open CSV file", command=open_csv_file)
open_button.grid(row=2)

# GUI elements for selecting the columns
spalten_label = tk.Label(root, text="Your CSV file contains the following columns. \nPlease select the one that relate to a STACK task and from which you wish to extract information about student responses.")
submit_button_cols = tk.Button(root, text="Submit", command=submit_columns)

# GUI elements for selecting the desired input and prt names
input_checkboxes_label = tk.Label(root,
        text="The following input names have been found in your column. Please select those that you want to get a report for.")
sep1 = ttk.Separator(root,orient='horizontal')
prt_checkboxes_label = tk.Label(root,
        text="The following PRT names have been found in your column. Please select those that you want to get a report for.")
additional_options_label = tk.Label(root,
        text="In addition, you can choose the following options (optional):")
sep2 = ttk.Separator(root,orient='horizontal')

# GUI elements for "Time to seconds" feature:
var_checkbox_seconds = tk.BooleanVar()
checkbox_seconds = tk.Checkbutton(root, text="Insert column for time spent in seconds (only English and German response files)",
    variable=var_checkbox_seconds, command=toggle_seconds_options)
radio_language_label = tk.Label(root, text="Please select the language of your input file:")
lang_radiobuttons = []
selected_lang = tk.StringVar()
for language in list(time_languages.keys()):
    # Create radiobutton for each langaue:
    radiobutton = tk.Radiobutton(
        root,
        text=language,
        value=language,
        variable=selected_lang,
        tristatevalue=0
    )
    lang_radiobuttons.append(radiobutton)

# GUI elements for STACKrate feature:
var_checkbox_stackrate = tk.BooleanVar()
checkbox_stackrate = tk.Checkbutton(root, text="Insert columns for STACKrate evaluation results",
    variable=var_checkbox_stackrate)
process_button = tk.Button(root, text="Submit", command=process_input_strings)

# GUI elements for export
export_button_info = tk.Label(root, text="Click on the following button to select a storage location for the output file and start the export:")
export_button = tk.Button(root, text="Save CSV file", command=export_csv_file)

# GUI elements for the close page
success_text = tk.Label(root, text="The file has been saved successfully!")
close_button = tk.Button(root, text="Close", command=close_window)

root.mainloop()