<!--
Copyright 2024 by Jonas Lache <jonas.lache@hs-ruhrwest.de>
SPDX-License-Identifier: GPL-3.0-or-later
-->

# STACK Response File Processor

A Python tool to extract information from Moodle response files.

## Version v0.3

On 24th October 2024, version v0.3 of the *STACK Response File Processor* has been
released. The following changes have been made:

1. Fixed issue [#3](https://github.com/jonaslache/STACK-Response-File-Processor/issues/3).
1. For better clarity, a checkbox has been added that allows users to control the display of the text field for custom strings that the tool searches for (introduced in v0.2).
1. Added sample CSV files (English and German) with which the "Response File Processor" can be tested.
2. Updated the docs.

For changes in older versions, please see the [development history](Development_history.md).

## About

The *STACK Response File Processor* is a Python tool with a graphical user
interface. It is designed to streamline the extraction of information from
student responses to STACK questions within Moodle quizzes, including:

- Value and state (valid, invalid, score) of STACK input fields 
- The score of the potential response trees and whether the PRTs were active
- Information about whether user-specified strings are present in each row of the quiz data (True/False).
- The [random seed](https://en.wikipedia.org/wiki/Random_seed) used in the specific attempt
- STACKrate evaluation results (see
    <https://www.ruhr-uni-bochum.de/stackrate-maths/>)

The tool provides an automatic detection of input field and PRT names that are
available in the response file. Another convenient feature is the conversion of
the strings in the "Time spent" column (e.g. 14 mins 7 secs) to seconds
(e.g. 847) for better processing.

## Prerequisites

Before using the tool, ensure you have the following prerequisites:

1. Python installed on your system (version 3.6 or higher).
1. Required Python libraries: `tkinter`, `pandas`, `re` and `json`:
   - Instructions on how to install `tkinter` can be found [here](https://www.pythonguis.com/installation/install-tkinter-windows/) (Windows) and [here](https://www.pythonguis.com/installation/install-tkinter-mac/) (macOS).
   - Instructions on how to install `pandas` can be found [here](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html#installing-from-pypi).
   - `re` and `json` are likely to be pre-installed.

## Usage

For users who prefer standalone solutions, experimental standalone files for
macOS (app) and Windows (exe) are available (see [here](https://github.com/jonaslache/STACK-Response-File-Processor/releases)), but it is
recommended to use the tool via the command line as described below.

To use the Python tool, follow these steps:

1. Download the file `response-file-processor.py` from this repository.

2. Get your data: To get started, you can use a [sample file](sample_data) from
    this repository. To use your own data, export a "Responses" quiz report from
    Moodle as a CSV file:
    1. Log in to Moodle and click on the quiz you want to access the report for.
        Make sure you have the rights to access the students' responses!
    2. Click on "Results" and select "Responses".
    3. Choose the attempts that you want to export and choose the output format
        `.csv`.
    4. Click on the "Download" button.

3. Run the tool: Open the command line or terminal, navigate to the directory
    where the file `response-file-processor.py` is located. When you saved the
    file in your Downloads folder, the command is likely to be 

    ```
    cd Downloads
    ```

4. Run the tool with the following command:

    ```
    python3 response-file-processor.py
    ```

    When the GUI appears, follow the instructions.

## Citing

If you use the *STACK Response File Processor* for a scientific publication, I would be grateful if you would cite the following [paper](https://zenodo.org/records/12795092):

```bibtex
@InProceedings{lacheDataProcessionMade2024,
  title = {Data {{Procession Made Easy}}: {{A Python Tool}} for {{Extracting Information}} from {{Student Responses}} to {{STACK Questions}}},
  booktitle = {Proceedings of the {{International Meeting}} of the {{STACK Community}} 2024},
  author = {Lache, Jonas},
  editor = {Weinmann, Michael},
  year = {2024},
  pages = {26--32},
  publisher = {International Meeting of the STACK Community 2024 (STACK Conference 2024)},
  address = {Amberg},
  doi = {10.5281/zenodo.12755221}
}
```

## License

The *STACK Response File Processor* is released under the GPL-3.0-or-later
license.

By using the tool, you agree to comply with the terms of the GPL-3.0-or-later
license. For more information about the license or to obtain a copy of the full
license text, please visit
<https://github.com/jonaslache/STACK-Response-File-Processor?tab=GPL-3.0-1-ov-file>.
If you have any questions or concerns regarding the licensing terms, please
contact [jonas.lache@hs-ruhrwest.de](mailto:jonas.lache@hs-ruhrwest.de).