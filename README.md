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

## Remarks
* The tools only updates the _draft_ grades. After using it, make sure the grades are OK, then publish them using Google Classroom's grade book (just a couple more clicks to make sure nothing crazy happened)!
* Any non-existing assignments _will be created_.
* Avoid using _merged_ cells for the ranges accessed by the tool.
* _Last Row_ must be strictly greater than _First Row_.

## Usage

### Requirements
* Python 3
* OAuth client credentials, with Sheets and Classroom APIs enabled, stored as a file named `credentials.json` in the working directory (you can get the credentials from the [Google API Console](https://console.developers.google.com/))
* Python dependencies that can be installed by `pip` using `pip install --user --upgrade -r requirements.txt`

#### Command-line Interface

Run the command-line interface using the command `python cli.py` and it will prompt you for the needed fields.

#### Web-based Interface

A mini-sever is also available to give a more convenient way of using the tool. It can be used by running `python server.py`. This was mainly implemented to be hosted online (see next section).

## Hosted Version

For extra convenience, a version of the tool is [hosted on Heroku](https://gradesync.herokuapp.com/sync). It only requires a browser to use it, i.e., no Python, OAuth credentials or dependencies! However, since the tool is not verified by Google, the authentication consent page will contain a warning about it being unsafe. The deployed code is identical to the one in this repository. If you do not feel comfortable with the warning, feel free to download it and run it locally using the previous instructions instead!

### Security and Privacy

All communications between your browser, the server and Google's APIs use SSL encryption and an error should occur in case of any insecure communication. The access token granted from Google (with your consent) is stored in your browser cookie and it is not saved in any sort of database on the server. (However, it may be logged through the typical operational logs emitted by the specific server running it because it is sent as a part of the route.) When you send a request, the token (in the cookie) is sent by your browser and it is used to communicate with Google's APIs on your behalf to sync the grades. Whenever an error occurs (due to malformed requests, unforeseen bugs or changes in Google's APIs), the access token is revoked and you will be asked by Google for permission to grant another one.

## License and Guarantees

This is a free open-source tool and it is offered _as is_ with no guarantees whatsoever (see LICENSE for details). **Use it at your own risk!**
