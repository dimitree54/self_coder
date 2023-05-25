# flake8: noqa
FORMAT_INSTRUCTIONS = """RESPONSE FORMAT INSTRUCTIONS
----------------------------
When responding, format response as a markdown code snippet formatted in the following schema:

```json
{{{{
    "first_thought": string [What is the best way to solve the task? What action to take with what action_input?]"
    "criticism": string [Constructive criticism of the first_thought, considering an alternative options.]
    "final_thought": string  [Final reasoning, what action and action_input to choose and why]
    "action": string [The action to take. Must be one of [{tool_names}]]
    "action_input": string [The input to the action]
}}}}
```"""
