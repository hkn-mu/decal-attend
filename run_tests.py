import json
from utils import getUser, buildSections, parseResponses
from pathlib import Path
from git import Repo
from typing import TypedDict, Literal


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


if __name__ == "__main__":
    repo = Repo.init("/autograder/autograder_samples")
    last_updated = repo.head.commit.committed_datetime
    last_updated_str = last_updated.strftime("%B %-d, %Y at %-I:%M %p")

    user = getUser()
    sections = buildSections()
    responses = parseResponses(user["email"])

    autograder_result: AutograderResult = {
        "output": f"Attendance for {user['name']} ({user['email']}) as of {last_updated_str}. If something seems incorrect, please reach out to staff through Ed!",
        "output_format": "text",
        "test_output_format": "md",
        "test_name_format": "text",
        "tests": [],
    }

    for sectionName in sections.keys():
        section = sections[sectionName]

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

        comments = filtered_response[filtered_response["Comments"].notnull()]
        if len(filtered_response) != 0 and len(comments) == 0:
            test["output"] += "\n No feedback provided."
        elif len(comments) != 0:
            x = comments["Comments"].values
            test["output"] += "\n Your feedback: \n ```"

            for comment in x:
                test["output"] += f"{comment} \n"

            test["output"] += "```"

        autograder_result["tests"].append(test)

    with open("/autograder/results/results.json", "w") as f:
        f.write(json.dump(autograder_result))
