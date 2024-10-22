"""
Copyright 2024 by Jonas Lache <jonas.lache@hs-ruhrwest.de>
SPDX-License-Identifier: GPL-3.0-or-later
"""

# Import necessary libraries
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk, Text
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
def extract_survey_info(dictionary, key, attr=""):
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

# Returns the random seed in a given attempt
def get_random_seed(response_str):
    pattern = r"Seed:\s*(\d+)"
    match = re.search(pattern, response_str)
    if match:
        input_value = match.group(1)
        return input_value
    else:
        return None

# Returns True when `search_item` is included in `response_str` string
def is_present(response_str, search_item):
    result = search_item in response_str
    return result

# Makes the radio buttons for the language selection visible in the GUI
def show_language_radiobuttons():
    checkbox_seconds_row = checkbox_seconds.grid_info()["row"]
    radio_language_label.grid(row=checkbox_seconds_row+1, padx=20, pady=5)
    i=1
    for button in lang_radiobuttons:
        button.grid(row=checkbox_seconds_row+1+i, padx=20, pady=5)
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
        spalten_label.grid(row=1, padx=20, pady=5)
        # Create radiobutton for each column in csv file:
        global selected_col
        selected_col = tk.StringVar()
        i=1
        for option in options:
            radiobutton = tk.Radiobutton(
                inner_frame,
                text=option,
                value=option,
                variable=selected_col,
                tristatevalue=0
            )
            col_radiobuttons.append(radiobutton)
            radiobutton.grid(row=i+1, padx=20, pady=5)
            i+=1
        submit_button_cols.grid(row=len(col_radiobuttons)+2, padx=20, pady=5)
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
    # Add temporary column with identified prt and input names as entries:
    df[f"{selected_col.get()}: identified_placeholders"] = df[selected_col.get()].apply(identify_prts_inputs)
    # Create lists with input and prt names:
    for result in df[f"{selected_col.get()}: identified_placeholders"]:
        if result:
            input_names.update(result["inputs"])
            prts.update(result["prts"])
    i=1
    input_checkboxes_label.grid(row=i, padx=20, pady=5)
    i+=1
    # Create checkbox for each input name:
    global input_checkboxes
    input_checkboxes = []
    for input in input_names:
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(
            inner_frame,
            variable=var,
            text=input,
            command=lambda input=input, var=var: update_selected_inputs(input, var),
            tristatevalue=0
        )
        input_checkboxes.append(checkbox)
        checkbox.grid(row=i, padx=20, pady=5)
        input_checkboxes_states.append(False)
        i+=1
    sep1.grid(row=i, padx=20, ipadx=300, pady=10)
    i+=1
    prt_checkboxes_label.grid(row=i, padx=20, pady=5)
    i+=1
    # Create checkbox for each prt name:
    global prt_checkboxes
    prt_checkboxes = []
    for prt in prts:
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(
            inner_frame,
            variable=var,
            text=prt,
            command=lambda prt=prt, var=var: update_selected_prts(prt, var),
            tristatevalue=0
        )
        prt_checkboxes.append(checkbox)
        checkbox.grid(row=i, padx=20, pady=5)
        prt_checkboxes_states.append(False)
        i+=1
    sep2.grid(row=i, padx=20, ipadx=300, pady=10)
    i+=1
    additional_options_label.grid(row=i, padx=20, pady=5)
    i+=1
    textarea_label.grid(row=i, padx=20, pady=5)
    i+=1
    textarea.grid(row=i, padx=20, pady=5)
    i+=1
    checkbox_seconds.grid(row=i, padx=20, pady=5)
    i=i+2+len(time_languages)
    checkbox_stackrate.grid(row=i, padx=20, pady=5)
    i+=1
    checkbox_randseed.grid(row=i, padx=20, pady=5)
    i+=1
    process_button.grid(row=i, padx=20, pady=5)
    # Delete temporary column:
    del df[f"{selected_col.get()}: identified_placeholders"]

# Function which is called when user clicks the "Save CSV file" button in GUI.
# Opens file dialog for output file, exports file, shows "Close" button
def export_csv_file():
    export_filename = filedialog.asksaveasfilename(filetypes=[("CSV text files", "*.csv")])
    if ".csv" not in export_filename:
        export_filename+=".csv"
    df.to_csv(export_filename, index=False)
    success_text.grid(row=1, padx=20, pady=5)
    close_button.grid(row=2, padx=20, pady=5)
    export_button_info.grid_forget()
    export_button.grid_forget()

# Function where most of the "magic" happens. Called when clicking on "Submit".
# Depending on user's wishes, all columns are created
def process_input_strings():
    # Create "Seconds taken" column depending on user's choices:
    if var_checkbox_seconds.get():
        time_values = time_languages[selected_lang.get()][0]
        df_key = time_languages[selected_lang.get()][1]
        try:
             df["Seconds taken"] = df[df_key].apply(lambda x: string_time_to_sec(x,time_values))
        except:
            print("There is an error finding the column that contains the time information. Please make sure you selected the correct language.")
    # Create columns for selected input fields:
    for input_field in selected_input_checkboxes:
        df[f"{selected_col.get()}: {input_field} value"] = df[selected_col.get()].apply(lambda x: get_input_value(x, input_field, mode="value"))
        df[f"{selected_col.get()}: {input_field} state"] = df[selected_col.get()].apply(lambda x: get_input_value(x, input_field, mode="state"))
    # Create columns for selected prts:
    for prt in selected_prt_checkboxes:
        df[f"{selected_col.get()}: {prt} active"] = df[selected_col.get()].apply(lambda x: is_prt_active(x, prt))
        df[f"{selected_col.get()}: {prt} score"] = df[selected_col.get()].apply(lambda x: get_prt_score(x, prt))
    # Create columns for strings specified in text area
    textarea_content = textarea.get('1.0','end').strip()
    if textarea_content!="":
        for string in textarea_content.split(","):
            item = string.strip()
            df[f"{item} present"] = df[selected_col.get()].apply(lambda x: is_present(x, item))
    # Create STACKrate survey columns depending on user's choices:
    if var_checkbox_stackrate.get():
        df[f"{selected_col.get()}: Survey_Results"] = df[selected_col.get()].apply(get_survey_results)
        # Extract all STACKrate IDs:
        all_stackrate_keys = set()
        for survey_result in df[f"{selected_col.get()}: Survey_Results"]:
            if survey_result:
                all_stackrate_keys.update(survey_result.keys())
        # Create columns for all IDs:
        for key in all_stackrate_keys:
            df[f"{selected_col.get()}: STACKrate ratings to ID {key}"] = df[f"{selected_col.get()}: Survey_Results"].apply(lambda x: extract_survey_info(x, key, attr="ratings"))
            df[f"{selected_col.get()}: STACKrate comments to ID {key}"] = df[f"{selected_col.get()}: Survey_Results"].apply(lambda x: extract_survey_info(x, key, attr="comment"))
        df.drop(f"{selected_col.get()}: Survey_Results", axis=1, inplace=True)
    # Create colum with random seeds depending on user's choices:
    if var_checkbox_randseed.get():
        df["Random seed"] = df[selected_col.get()].apply(get_random_seed)
    input_checkboxes_label.grid_forget()
    for box in input_checkboxes:
        box.grid_forget()
    sep1.grid_forget()
    prt_checkboxes_label.grid_forget()
    for box in prt_checkboxes:
        box.grid_forget()
    sep2.grid_forget()
    additional_options_label.grid_forget()
    textarea_label.grid_forget()
    textarea.grid_forget()
    checkbox_seconds.grid_forget()
    hide_language_radiobuttons()
    checkbox_stackrate.grid_forget()
    checkbox_randseed.grid_forget()
    process_button.grid_forget()
    export_button_info.grid(row=1, padx=20, pady=5)
    export_button.grid(row=2, padx=20, pady=5)

# Closes GUI window:
def close_window():
    root.destroy()

# GUI setup:
root = tk.Tk()
root.title("STACK Response File Processor")

# Set the width and height for the main window
window_width = 650
window_height = 800
root.geometry(f"{window_width}x{window_height}")

# Create a Frame for the Canvas and Scrollbar
frame = tk.Frame(root)
frame.grid(row=0, column=0, sticky='nsew')

# Set fixed width for the canvas
canvas_width = window_width-50
canvas_height = window_height-50
canvas = tk.Canvas(frame, width=canvas_width, height=canvas_height)
canvas.grid(row=0, column=0, sticky='nsew')

# Add a vertical Scrollbar to the Canvas
scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
scrollbar.grid(row=0, column=1, sticky='ns')

# Create another Frame inside the Canvas
inner_frame = tk.Frame(canvas)

# Create a window in the canvas
canvas.create_window((canvas_width/2, 0), window=inner_frame, anchor='n')

# Configure the scrollbar and canvas
inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.configure(yscrollcommand=scrollbar.set)

# GUI elements for opening the input csv file:
open_button_info = tk.Label(inner_frame,
        text="Click on the following button to select a CSV file:",
        wraplength=canvas_width-40)
open_button_info.grid(row=1, padx=20, pady=5)
open_button = tk.Button(inner_frame, text="Open CSV file", command=open_csv_file)
open_button.grid(row=2, padx=20, pady=5)

# GUI elements for selecting the columns:
spalten_label = tk.Label(inner_frame,
        text="Your CSV file contains the following columns. \nPlease select the one that relates to a STACK task and from which you wish to extract information about student responses.",
        wraplength=canvas_width-40)
submit_button_cols = tk.Button(inner_frame, text="Submit", command=submit_columns)

# GUI elements for selecting the desired input and prt names:
input_checkboxes_label = tk.Label(inner_frame,
        text="The following input names have been found in your column. Please select those that you want to get a report for.",
        wraplength=canvas_width-40)
sep1 = ttk.Separator(inner_frame,orient='horizontal')
prt_checkboxes_label = tk.Label(inner_frame,
        text="The following PRT names have been found in your column. Please select those that you want to get a report for.",
        wraplength=canvas_width-40)
additional_options_label = tk.Label(inner_frame,
        text="In addition, you can choose the following options (optional):",
        wraplength=canvas_width-40)
sep2 = ttk.Separator(inner_frame,orient='horizontal')

# GUI elements for text area:
textarea_label = tk.Label(inner_frame,
        text="Comma-separated list of strings for which the quiz data will be searched (e.g. PRT answer notes such as prt1-1-F).\nFor each string specified, a column will be created that contains True or False, depending on whether the string is present in the respective row.",
        wraplength=canvas_width-40)
textarea = tk.Text(inner_frame, height=3, width=50)

# GUI elements for "Time to seconds" feature:
var_checkbox_seconds = tk.BooleanVar()
checkbox_seconds = tk.Checkbutton(inner_frame, text="Insert column for time spent in seconds (only English and German response files)",
    variable=var_checkbox_seconds, command=toggle_seconds_options)
radio_language_label = tk.Label(inner_frame,
        text="Please select the language of your input file:",
        wraplength=canvas_width-40)
lang_radiobuttons = []
selected_lang = tk.StringVar()
# Create radiobutton for each language:
for language in list(time_languages.keys()):
    radiobutton = tk.Radiobutton(
        inner_frame,
        text=language,
        value=language,
        variable=selected_lang,
        tristatevalue=0
    )
    lang_radiobuttons.append(radiobutton)

# GUI elements for STACKrate feature:
var_checkbox_stackrate = tk.BooleanVar()
checkbox_stackrate = tk.Checkbutton(inner_frame, text="Insert columns for STACKrate evaluation results",
    variable=var_checkbox_stackrate)

# GUI elements for random seed feature:
var_checkbox_randseed = tk.BooleanVar()
checkbox_randseed = tk.Checkbutton(inner_frame, text="Insert column for random seeds",
    variable=var_checkbox_randseed)
process_button = tk.Button(inner_frame, text="Submit", command=process_input_strings)

# GUI elements for export:
export_button_info = tk.Label(inner_frame,
        text="Click on the following button to select a storage location for the output file and start the export:",
        wraplength=canvas_width-40)
export_button = tk.Button(inner_frame, text="Save CSV file", command=export_csv_file)

# GUI elements for the close page:
success_text = tk.Label(inner_frame,
        text="The file has been saved successfully!",
        wraplength=canvas_width-40)
close_button = tk.Button(inner_frame, text="Close", command=close_window)

root.mainloop()