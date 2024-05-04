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


def address_issue(openai_client, nation: Nation, bio: str, issue: Issue):
    prompt = template.render(name=nation.name, bio=bio, issue=issue)
    print(prompt)

    attempt = 0
    max_attempts = 5
    while True:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are the personification of a nation-state and are making policy decisions on its behalf. You will be given a description of the nation-state itself, a scenario  and a numbered list of options to choose from. Reply only with a single integer: the number of the option you believe is most suitable for the nation-state to take in that scenario.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=1,
            max_tokens=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        print(response)
        try:
            option_index = int(response.choices[0].message.content) - 1
        except ValueError:
            # sometimes the AI gives us a non-integer answer, e.g. answering with "Option"
            # so we need to try again
            if attempt < max_attempts:
                attempt += 1
                continue
            else:
                raise
        chosen_option = issue.options[option_index]
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
