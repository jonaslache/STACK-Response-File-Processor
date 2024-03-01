<!--
Copyright 2024 by Jonas Lache <jonas.lache@hs-ruhrwest.de>
SPDX-License-Identifier: GPL-3.0-or-later
-->

# STACK Response File Processor

A Python tool to extract information from Moodle response files.

## About

The *STACK Response File Processor* is a Python tool with a graphical user
interface. It is designed to streamline the extraction of information from
student responses to STACK questions within Moodle quizzes.


## Prerequisites

Before using the tool, ensure you have the following prerequisites:

1. Python installed on your system (version 3.6 or higher).
1. Required Python libraries: `tkinter`, `pandas`, `re` and `json`

## Usage

To use the Python tool, follow these steps:

1. Download the file `response-file-processor.py` from this repository.

1. Get your data: Export a "Responses" quiz report from Moodle as a CSV file:
    1. Log in to Moodle and click on the quiz you want to access the report for.
        Make sure you have the rights to access the student's responses!
    1. Click on "Results" and select "Responses".
    1. Choose the attempts that you want to export and choose the output format
        `.csv`.
    1. Click on the "Download" button.

1. Run the Tool: Open the command line or terminal, navigate to the directory
    where the file `response-file-processor.py` is located, and run the tool
    with the following command:

    ```
    python3 response-file-processor.py
    ```

    When the GUI appears, follow the instructions.

## License

The *STACK Response File Processor* is released under the GPL-3.0-or-later
license.

By using the tool, you agree to comply with the terms of the GPL-3.0-or-later
license. For more information about the license or to obtain a copy of the full
license text, please visit \<add link to GPL-3.0-or-later.txt file \>.
If you have any questions or concerns regarding the licensing terms, please
contact [jonas.lache@hs-ruhrwest.de](mailto:jonas.lache@hs-ruhrwest.de).