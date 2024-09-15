import json
from utils import getUser, buildSections, parseResponses
from pathlib import Path
from typing import TypedDict, Literal
import datetime
from pytz import timezone
import gspread
import pandas
import time


class Test(TypedDict):
    score: float
    max_score: float
    name: str
    visibility: Literal["visible", "hidden", "after_due_date", "after_published"]
    output: str


class AutograderResult(TypedDict):
    output: str
    output_format: str
    test_output_format: str
    test_name_format: str
    tests: list[Test]


SEMESTER_CONFIG = {
    "sheet_id": "1NZFt_ZgkvujTZaKIsiY_mNkP-ixJUOkRPyUBogQZaRY",
    "responses_gid": 1457747331,
    "keywords_gid": 277060732,
}


def run_autograder() -> AutograderResult:
    # Connect to Google Sheets API
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    gc = gspread.service_account("secret.json", SCOPES)
    sheet = gc.open_by_key(SEMESTER_CONFIG["sheet_id"])
    responses_sheet = sheet.get_worksheet_by_id(SEMESTER_CONFIG["responses_gid"])
    keywords_sheet = sheet.get_worksheet_by_id(SEMESTER_CONFIG["keywords_gid"])

    # Get the latest version of our two relevant sheets

    responses = pandas.DataFrame(
        responses_sheet.get_all_records(),
    )

    keywords = pandas.DataFrame(
        keywords_sheet.get_all_records(),
    )

    user = getUser()
    sections = buildSections(keywords)
    responses = parseResponses(responses, user["email"])

    autograder_result: AutograderResult = {
        "output": f"Attendance for {user['name']} ({user['email']}) as of {last_updated_str}. If something seems incorrect, please reach out to staff through Ed!",
        "output_format": "md",
        "test_output_format": "md",
        "test_name_format": "text",
        "tests": [],
    }

    current_max = 0
    for sectionName, section in sections.items():

        test: Test = {
            "score": 0.0,
            "max_score": 1.0,
            "name": f"{section['name']}",
            "visibility": "hidden",
            "output": "",
        }

        if section["date"] != None:
            test["name"] += f" ({section['date'].strftime('%B %-d, %Y')})"

        if section["date"] == None or section["date"] < last_updated:
            test["visibility"] = "visible"
            current_max += 1

        response = responses[responses["Lecture"] == sectionName]
        filter = response["Secret Word"].apply(
            lambda a: str(a).lower().strip() == section["code"], 1
        )

        filtered_response = response.filter(axis=0, items=filter[filter].index)

        if len(filtered_response) != 0:
            test["score"] = 1.0
            test["output"] = "Thanks for coming to class!"

        elif len(response) != 0:
            test["output"] = "Incorrect secret word provided."
        else:
            test["output"] = "No submission found."

        comments = filtered_response[filtered_response["Comments"] != ""]
        if len(filtered_response) != 0 and len(comments) == 0:
            test["output"] += "\nNo feedback provided."
        elif len(comments) != 0:
            x = comments["Comments"].values
            test["output"] += "\nYour feedback:\n"

            for comment in x:
                test["output"] += f"> {comment} \n"

        autograder_result["tests"].append(test)

    autograder_result[
        "output"
    ] += f"\n**The current max score for this assignment is: {current_max}/{len(autograder_result['tests'])}**"
    return autograder_result


def attempt_run(attempts: int) -> AutograderResult:
    try:
        autograder_result = run_autograder()
    except:
        if attempts == 0:
            autograder_result = {
                "output": f"The autograder was rate limited. Please ask someone on staff to re-run it.",
                "score": 0,
                "output_format": "text",
                "test_output_format": "md",
                "test_name_format": "text",
                "tests": [],
            }
        else:
            time.sleep(20)
            return attempt_run(attempts - 1)

    return autograder_result


if __name__ == "__main__":
    # Pick the time that we'll use to represent the "last ran" time
    last_updated = datetime.datetime.now(timezone("US/Pacific"))
    last_updated_str = last_updated.strftime("%B %-d, %Y at %-I:%M %p")

    autograder_result = attempt_run(2)

    with open("/autograder/results/results.json", "w") as f:
        f.write(json.dumps(autograder_result))
