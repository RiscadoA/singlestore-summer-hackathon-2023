# Fases

1. Show goal, current plan, context and ask to reevaluate plan
2. Ask to execute the first step in the plan

## First prompt
```
You are a character in a world.
Your final goal is '{goal}'.
Taking into account the information below about the world, reevaluate your current plan, if necessary, so that you can later perform it by calling the functions walk and interact.

Your current plan is:
1. X
2. Y
3. Z

Information about the world (ordered from most relevant to least relevant):
"""
{newline.join(context)}
You have an inventory, which contains the following items: {", ".join(inventory)}.
"""
```

## Second prompt

```
Now, call the function which gets you closer to completing the first task.
Instead of answering with text, you should call only one of the functions walk and interact exposed to you by the API to achieve your goal.
```

1. Tasks succeeds, but its not the last one
2. Task succeeds, but its the last one
3. Task fails

## Third prompt

If the task succeeded, and there are still more tasks, ask if the task was really finished and if it should be removed from the task list.

# Fases

# Tasks succeeds, but its not the last one

System: You have 