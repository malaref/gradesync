# Welcome to GradeSync!
GradeSync is an easy-to-use tool I created to sync grades from a Google spreadsheet to a Google Classroom for the lack of a better option!

## Grades Format
The grades should be laid out as _columns_ in _one sheet_. They should span a _continuous range_ of _rows_ with each row representing a student, as well as, two _extra_ rows representing the assignments' _names (the header)_ and _full marks_. Students are identified by their _email addresses_, so an extra column is needed with that information.

## Example
|      Field      |                                                 Value                                                |
| --------------- | ---------------------------------------------------------------------------------------------------- |
| Spreadsheet URL | https://docs.google.com/spreadsheets/d/1g-Hz3-L35ObFxk0idqFsRtH6jYg-h2WhA-FPt9p8Thc/edit?usp=sharing |
| Sheet Name      | Sheet1                                                                                               |
| Header Row      | 1                                                                                                    |
| Full Mark Row   | 7                                                                                                    |
| First Row       | 2                                                                                                    |
| Last Row        | 6                                                                                                    |
| Emails Column   | A                                                                                                    |
| Grades Columns  | B C D E                                                                                              |

## Usage Remarks
* The tools only updates the _draft_ grades. After using it, make sure the grades are OK, then publish them using Google Classroom's grade book (just a couple more clicks to make sure nothing crazy happened)!
* Any non-existing assignments _will be created_.
* Avoid using _merged_ cells for the ranges accessed by the tool.
* _Last Row_ must be strictly greater than _First Row_.

## Requirements
* Python 3
* OAuth client credentials, with Sheets and Classroom APIs enabled, stored as a file named `credentials.json` in the working directory (you can get the credentials from the [Google API Console](https://console.developers.google.com/))
* Python dependencies that can be installed by `pip` using `pip install --user --upgrade -r requirements.txt`

## Usage
Run it using the command `python cli.py` and it will prompt you for the needed fields.
