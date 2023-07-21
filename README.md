# Project for the SingleStore Summer Hackathon 2023

[SingleStore](https://www.singlestore.com/) hosts two internal hackathons every year, where
employees are free to work on whatever they want - doesn't have to be useful in any way.

The theme of this hackathon was AI/ML, so we decided to try to do something with the vector
database stuff *SingleStore* provides us and also mix in some *OpenAI* shenanigans.

The goal of the project is still not very clear at the moment but we want to make something along
the lines of "There are multiple AI agents living in a Pokemon-like world, which must collaborate
to achieve tasks given by the user".

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
