use gh cli to open a new repo, call it cf-advanced-evals and clone it inside the /Code directory

create a good .gitignore for a python project

we use uv for everything in this project, make a reminder of that in an AGENTS.md file. This must be for installs via uv add or execution via uv run.

i want a custom data viewer for grading llm traces. this is for a class, i actually don't have an llm trace file (generate one small one with good cases and bad cases). use python streamlit for it and polars for the data processing if you need. we need a button for pass and a button for fail. assume this is an e ink reader sales assistant and that we sometimes have discounts. the agent should be very kind since it's a customer facing (include traces of bad behaviour). we also need an optional comment section. storing all state in a separate csv is ok (add a save button or autosave)

next step is to showcase pytest vs deepeval, so first give me a simple pytest of this project. very simple, just to showcase.


we need basic deepevals over the traces (you can reuse the traces we already have), use GEvals first instead of specialized evals. evaluate kindness of answer, maybe also product accuracy, and anything else you can consider. 


we're facing ModuleNotFoundError: No module named 'openai._types'