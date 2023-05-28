# flake8: noqa
FORMAT_INSTRUCTIONS = """RESPONSE FORMAT INSTRUCTIONS
----------------------------
When responding, format response as a markdown code snippet formatted in the following schema:

```json
{{{{{{{{
    {extra_thoughts}"action": string [The action to take. Must be one of [{tool_names}]]
    "action_input": string [The input to the action]
}}}}}}}}
```"""
