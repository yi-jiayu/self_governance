import os

import httpx
import openai
import typer
from jinja2 import Template

from .nation import Issue, Nation

openai.api_key = os.getenv("OPENAI_API_KEY")

template = Template(
    """The following text describes the nation of {{ name }}:

{{ bio }}

Given the following scenario and options, which option is most suitable for the nation of {{ name }}?

Scenario:
{{ issue.text }}{% for option in issue.options %}

Option {{ loop.index }}:
{{ option.text }}{% endfor %}

Answer: Option"""
)


def address_issue(nation: Nation, bio: str, issue: Issue) -> None:
    prompt = template.render(name=nation.name, bio=bio, issue=issue)
    print(prompt)

    response = openai.Completion.create(
        model="text-davinci-001",
        prompt=prompt,
        max_tokens=1,
        temperature=0.4,
        best_of=5,
        frequency_penalty=0,
        presence_penalty=0,
    )
    option_index = int(response["choices"][0]["text"].strip()) - 1
    chosen_option = issue.options[option_index]

    return nation.answer_issue(issue.id, chosen_option.id)


def main(nation_name: str, nation_bio: str):
    password = os.environ["NATIONSTATES_PASSWORD"]
    nation = Nation(nation_name, password, session_file="session.json")
    issues = nation.get_issues()
    for issue in issues:
        print(address_issue(nation, nation_bio, issue))
    else:
        print("No issues to address")


typer.run(main)
