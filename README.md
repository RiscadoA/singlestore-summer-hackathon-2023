# Project for the SingleStore Summer Hackathon 2023

[SingleStore](https://www.singlestore.com/) hosts two internal hackathons every year, where
employees are free to work on whatever they want - doesn't have to be useful in any way.

The theme of this hackathon was AI/ML, so we decided to try to do something with the vector
database stuff *SingleStore* provides us and also mix in some *OpenAI* shenanigans.

## Goal

The goal of the project was to make something along the lines of "There are multiple AI agents
living in a Pokemon-like world, which must collaborate to achieve tasks given by the user".

Unfortunately, due to time constraints, we ended up only implementing AI support for a single
agent. Turns out prompt engineering is not easy - the agents are quite dumb and sometimes end up
repeating tasks they have already done, like opening a door they've already opened.

## How

Agents can perform two actions: `walk(target)` and `interact(item, target)`.
Walking to a target just moves the character next to the given object or character.
Interact can be used, for example, to open a door using a key.

Agents get feedback from the result of their actions: for example, `walk(goal)` can result in
`Cannot walk to 'goal' because 'door' is blocking the path`.
Decisions are performed by querying world information from a vector database (`SingleStore` in this
case) and including it in prompts.

World information includes rules and state. For example:
```
You can open 'door's by interacting with them using 'key'.
There is a 'door' named 'door 1'.
```

Agents are controlled with 3 different prompt types:
- **Planning**: we give it a goal, queried data, current inventory, and ask it to generate a plan to achieve it.
- **Execute**: we give it the first task from its plan and ask it to execute the right action (walk/interact).
- **Reevaluate**: when an action fails or the task list is exhausted before the goal is fulfilled, we ask it to generate a new plan considering the previous result and plan.

## Instructions

1. Clone the repo
2. `cp .env{.example,}`
3. Edit the `.env` file and populate it (needs creating a SingleStore database)
4. To run: `LEVEL=<level_name> DATABASE=[dumb|s2] python3
scripts/main.py`

*Note:* `level_name` is the name of a file of your choosing inside the
`scripts/levels` folder.

## Assets

- [ArMM1998's Zelda-like tilesets and sprites](https://opengameart.org/content/zelda-like-tilesets-and-sprites)

## Authors

- [Filipe Silva](https://github.com/filipelsilva)
- [Ricardo Antunes](https://github.com/riscadoa)
