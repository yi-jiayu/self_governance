import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Literal, Self, TypedDict
from xml.etree.ElementTree import Element

import httpx
import structlog

from .__version__ import __version__

logger = structlog.get_logger(__name__)


@dataclass
class IssueOption:
    id: int
    text: str

    @classmethod
    def from_xml(cls, element: Element) -> Self:
        return cls(
            id=element.get("id"),
            text=element.text,
        )


@dataclass
class Issue:
    id: int
    title: str
    text: str
    options: list[IssueOption]

    @classmethod
    def from_xml(cls, element: Element) -> Self:
        return cls(
            id=element.get("id"),
            title=element.find("TITLE").text,
            text=element.find("TEXT").text,
            options=[
                IssueOption.from_xml(option) for option in element.findall("OPTION")
            ],
        )


class Nation:
    def __init__(
        self,
        name: str,
        password: str | None = None,
        session_file: str | None = None,
    ) -> None:
        self.name = name
        self.password = password
        self.pin = None
        self.autologin = None
        self.user_agent = f"self_governance@{__version__}"
        self.http = httpx.Client(
            base_url="https://www.nationstates.net/cgi-bin/api.cgi",
            headers={"user-agent": self.user_agent},
        )
        self.session = {}
        self.session_file = session_file

    def load_session(self) -> None:
        if not self.session_file:
            return

        with open(self.session_file) as f:
            self.session = json.load(f)

        self.pin = self.session.get("pin")
        self.autologin = self.session.get("autologin")

    def save_session(self) -> None:
        if not self.session_file:
            return

        if self.pin == self.session.get("pin") and self.autologin == self.session.get(
            "autologin"
        ):
            return

        self.session = {"pin": self.pin, "autologin": self.autologin}

        with open(self.session_file, "w") as f:
            json.dump(self.session, f)

    def _make_request(self, args: dict, method: Literal["GET", "POST"] = "GET"):
        headers = {}
        if self.pin is not None:
            headers["x-pin"] = str(self.pin)
        if self.autologin is not None:
            headers["x-autologin"] = self.autologin
        elif self.password is not None:
            headers["x-password"] = self.password

        args = args | {"nation": self.name}

        if method == "POST":
            response = self.http.post("", data=args, headers=headers)
        else:
            response = self.http.get("", params=args, headers=headers)

        if pin := response.headers.get("x-pin"):
            self.pin = pin

        if autologin := response.headers.get("x-autologin"):
            self.autologin = autologin

        self.save_session()

        return response

    def get_issues(self):
        response = self._make_request({"q": "issues"})
        response.raise_for_status()

        root = ET.fromstring(response.text)
        return [Issue.from_xml(elem) for elem in root.find("ISSUES").findall("ISSUE")]

    def answer_issue(self, issue_id: int, option_id: int) -> str:
        response = self._make_request(
            {"c": "issue", "issue": issue_id, "option": option_id}
        )
        response.raise_for_status()
        return response.text
