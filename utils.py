import datetime
import json
import pandas
from pathlib import Path
from typing import TypedDict
from pytz import timezone


class Section(TypedDict):
    name: str
    date: datetime.datetime
    code: str


class User(TypedDict):
    name: str
    email: str
    id: int


def buildSections() -> dict[str, Section]:
    sections: dict[str, Section] = {}
    p = Path(".") / "studentdata" / "keywords.csv"
    keywords = pandas.read_csv(
        p.resolve(), header=0, usecols=["Lecture", "Secret Word"]
    )

    # Iterating usually bad but keywords small and we need to touch every value
    year = datetime.datetime.now().year
    for _, row in keywords.iterrows():
        try:
            month = int(str(row["Lecture"]).split("(")[1].split("/")[0])
            day = int(str(row["Lecture"]).split("(")[1].split("/")[1].split(")")[0])

            sections[row["Lecture"]] = {
                "name": str(row["Lecture"]).split("(")[0].strip(),
                "date": datetime.datetime(
                    year, month, day, 22, 00, 00, 00, timezone("US/Pacific")
                ),
                "code": str(row["Secret Word"]).lower().strip(),
            }
        except:
            sections[row["Lecture"]] = {
                "name": str(row["Lecture"]).split("(")[0].strip(),
                "date": None,
                "code": str(row["Secret Word"]).lower().strip(),
            }

    return sections


def parseResponses(email: str) -> pandas.DataFrame:
    p = Path(".") / "studentdata" / "responses.csv"
    responses = pandas.read_csv(
        p.resolve(),
        header=0,
        usecols=["Email Address", "Lecture", "Secret Word", "Comments"],
    )
    return responses[responses["Email Address"] == email]


def getUser() -> User:
    p = Path(".")
    q = p / "studentdata" / "submission_metadata.json"
    metadata = {}
    with q.open() as f:
        metadata = json.load(f)

    if "users" in metadata and len(metadata["users"]) == 1:
        return metadata["users"][0]
    return {}
