import os

import typer
from jinja2 import Template
from openai import OpenAI

from .nation import Issue, Nation

template = Template(
    """The following text describes the nation of {{ name }}:

{{ bio }}

Scenario:
{{ issue.text }}{% for option in issue.options %}

Option {{ loop.index }}:
{{ option.text }}{% endfor %}"""
)


def address_issue(
    openai_client: OpenAI, nation: Nation, bio: str, issue: Issue
) -> None:
    prompt = template.render(name=nation.name, bio=bio, issue=issue)
    print(prompt)

    attempt = 0
    max_attempts = 5
    while True:
        response = openai_client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "developer",
                    "content": "You are the personification of a nation-state and are making policy decisions on its behalf. You will be given a description of the nation-state itself, a scenario and a numbered list of options to choose from. Reply only with a single integer: the number of the option you believe is most suitable for the nation-state to take in that scenario.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            max_output_tokens=16,
        )
        print(response)
        try:
            option_index = int(response.output_text) - 1
        except ValueError:
            # sometimes the AI gives us a non-integer answer, e.g. answering with "Option"
            # so we need to try again
            if attempt < max_attempts:
                attempt += 1
                continue
            else:
                raise
        try:
            chosen_option = issue.options[option_index]
        except IndexError:
            if attempt < max_attempts:
                attempt += 1
                continue
            else:
                raise
        break

    return nation.answer_issue(issue.id, chosen_option.id)


def main(nation_name: str, nation_bio: str):
    client = OpenAI()
    password = os.environ["NATIONSTATES_PASSWORD"]
    nation = Nation(nation_name, password, session_file="session.json")
    issues = nation.get_issues()
    if not issues:
        print("No issues to address")
    else:
        for issue in issues:
            print(address_issue(client, nation, nation_bio, issue))


typer.run(main)
