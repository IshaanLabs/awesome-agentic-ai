QUESTIONS = {
    "task_type": {
        "type": "choice",
        "instructions": "What kind of help is the user asking for in `prompt`?",
        "criteria": {
            "simple_chat": "Greetings, small talk, a well-known fact, a definition, a short rewrite or translation",
            "general": "An everyday task: explaining a concept, summarizing, drafting text, giving advice",
            "coding": "Writing, fixing, explaining or reviewing code, shell commands, SQL or regex",
            "reasoning": "Multi-step math, logic puzzles, planning, or weighing options to make a decision",
            "agentic": "A large goal that needs many steps, tools, files or actions to complete, like building a whole project or running a workflow",
        },
    },
    "complexity": {
        "type": "score",
        "instructions": "How much work does a good answer to `prompt` take?",
        "criteria": [
            "A one-line answer or a well-known fact",
            "A short explanation or a small task done in one step",
            "Several steps, careful checking, or a long detailed answer",
        ],
    },
    "needs_fresh_info": {
        "type": "noul",
        "instructions": "Does answering `prompt` correctly require information from the last few weeks?",
    },
}
