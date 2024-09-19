import datetime
import json
import pandas
from pathlib import Path
from typing import TypedDict, Callable
from pytz import timezone


class Section(TypedDict):
    name: str
    date: datetime.datetime
    code: str


class User(TypedDict):
    name: str
    email: str
    id: int


def buildSections(keywords: pandas.DataFrame) -> dict[str, Section]:
    sections: dict[str, Section] = {}

    # Iterating usually bad but keywords small and we need to touch every value
    year = datetime.datetime.now().year
    for _, row in keywords.iterrows():
        try:
            month = int(str(row["Lecture"]).split("(")[1].split("/")[0])
            day = int(str(row["Lecture"]).split("(")[1].split("/")[1].split(")")[0])

            sections[row["Lecture"]] = {
                "name": str(row["Lecture"]).split("(")[0].strip(),
                "date": timezone("US/Pacific").localize(
                    datetime.datetime(year, month, day, 20, 00, 00, 00)
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


def parseResponses(responses: pandas.DataFrame, email: str) -> pandas.DataFrame:
    filter_function: Callable[[str], bool] = (
        lambda elem: elem.lower().strip() == email.lower()
    )

    filter = responses["Email Address"].astype("string").apply(filter_function, 1)
    return responses.filter(axis=0, items=filter[filter].index)


def getUser() -> User:
    p = Path(".")
    q = p / "submission_metadata.json"
    metadata = {}
    with q.open() as f:
        metadata = json.load(f)

    if "users" in metadata and len(metadata["users"]) == 1:
        return metadata["users"][0]
    return {}
