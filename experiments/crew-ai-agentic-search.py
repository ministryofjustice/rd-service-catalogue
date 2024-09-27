"""Search for GitHub organisational synergies & trade-offs with CrewAI.

Currently only uses 3 fields from all repos across MoJ GitHub orgs:
html_url: the url of the githu repo
description: the free text field the user inputs on creating the repo
topics: Optional tags applied to the repo
TODO: Either scrape or have the agents use a tool to scrape the README
files, code content to validate whether a good relationship has been found.
TODO: We've found an hallucination - a repo that didn't exist. Another
agent with access to a tool that confirms whether identified repos actually
exist!
"""
import glob

from crewai import Agent, Crew, LLM, Task
import dotenv
import pandas as pd
from pyprojroot import here

secrets = dotenv.dotenv_values(here(".env"))
openai_key = secrets["OPENAI_KEY"]
parquet_dir = here("data/")

# grab all parquet files
parquet_files = glob.glob(f"{parquet_dir}/*.parquet")
df = pd.concat(
    [pd.read_parquet(file) for file in parquet_files], ignore_index=True)
# Build prompt using repo metadata name, description, topics
tab = df.loc[:, ["html_url", "description", "topics"]]

# Define LLMs -------------------------------------------------------------


# Define LLM with specified configuration (uses LiteLLM backend)
gpt_4o_mini = LLM(
    model="gpt-4o-mini", # this has a token limit of 200k per min. Prompt is currently c.50k.
    temperature=0.7,
    base_url="https://api.openai.com/v1",
    api_key=openai_key
)

gpt_4o_latest = LLM(
    model="chatgpt-4o-latest", # this has a token limit of 128k.
    temperature=0.7,
    base_url="https://api.openai.com/v1",
    api_key=openai_key
)

# Define agents -----------------------------------------------------------

agent1 = Agent(
    role="I.T. strategy consultant",
    goal="Communicate complex, technical language clearly and concisely.",
    backstory="An expert digital professional.",
    llm=gpt_4o_mini,
    verbose=True, # enable CoT reasoning logs
    allow_delegation=True, 
    max_iter=5, # how many iterations before providing its best answer, default is 25...
)
agent2 = Agent(
    role="Oppositional consultant",
    goal="Critique the work of an I.T. strategy consultant, ensuring value for money for the public body.",
    backstory="An expert digital professional with a broad experience in government bodies.",
    llm=gpt_4o_latest, # 128k token context window
    verbose=True, # enable CoT reasoning logs
    allow_delegation=True,
    max_iter=5, 
)
agent3 = Agent(
    role="Policy Analyst",
    goal="Compile a markdown report including an executive summary, the top 3 actions to take and a list of the identified relations",
    backstory="An expert in communicating technical language to executive decision makers.",
    llm=gpt_4o_latest, # 128k token context window
    verbose=True, # enable CoT reasoning logs
    allow_delegation=True,
    max_iter=5,
)


# config  -----------------------------------------------------------------


# crew configuration
agents = [agent1, agent2, agent3]
n_agents = len(agents)
process="sequential"

out_dirnm = f"agent-{n_agents}-process-{process}"


# Define tasks ------------------------------------------------------------
# agent 1: I.T. strategy consultant
prompt = f"""
You have been tasked with helping a government body improve its digital
strategy by identifying synergies and trade-offs within its current
software development portfolio.

You have been provided with choice metadata from the organisation's GitHub
code repositories in the table provided in the triple backtick delimiters
below:

```{"".join(tab.to_string(index=False).split())}```

With this metadata, you should identify projects with unseen, non-obvious
relations so that the development teams can ensure they coordinate to
optimise their efforts.
"""

ONE_SHOT = """
Format your reponse with the following entries:
Repo URLs: <insert related repository urls, 2 or more.> 
Relation: <Either synergy, trade-off or duplication>
Reason: <insert the reasons for the relation you identified>

Respond with an entry for each relation that you identify.
"""
# assign task to agent
task1 = Task(
    description=prompt,
    expected_output=ONE_SHOT,
    agent=agent1,
    output_file=f"outputs/{out_dirnm}/RELATIONSHIPS.md",
)

# agent 2: Oppositional consultant

TASK_2 = """
Ensure that non-obvious synergies have been identified. Backends /
frontends for the same product or tool are not of interest.
"""

OUTPUT_2 = """
"If trivial or obvious relations are identified (such as backend and
frontend for the same product), indicate that these are of no interest and
to remove them from the final report."
"""

task2 = Task(
    description=TASK_2,
    expected_output=OUTPUT_2,
    agent=agent2,
    output_file=f"outputs/{out_dirnm}/MODERATION.md",
)

# agent 3: Policy Analyst

TASK_3 = """
Format the findings as a markdown report for senior executives. Include
sections for an executive summary, top 3 actionable items and a section for
each identified relation entry.
"""

REPORT_FORMAT = """
# Related Repository Analysis

## Executive Summary

<Insert summary here>


## Top 3 Actionables

<Insert 3 priorities identified in the entries below>

## Software Relationships

<Insert identified entries here>

## Conclusion
<Insert summary of main findings.>
"""

task3 = Task(
    description=TASK_3,
    expected_output=REPORT_FORMAT,
    agent=agent3,
    output_file=f"outputs/{out_dirnm}/REPORT.md",
)


#  kick off the crew...
crew = Crew(
    agents=[agent1, agent2, agent3],
    tasks=[task1, task2, task3],
    verbose=True,
    output_log_file=f"logs/log.txt",
)
# let's go!
result = crew.kickoff()
