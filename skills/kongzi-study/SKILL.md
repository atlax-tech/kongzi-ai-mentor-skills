---
name: kongzi-study
description: Run source-backed Kongzi teaching sessions with active questions, recorded learner output, grading, correction, and transfer practice.
---

# Kongzi study

From the Kongzi skill root, read `operating-protocol.md` and `evidence-protocol.md` in the `references` directory.

Start a session for one node. If the command returns due cards, handle them first. State a small success criterion, ask a diagnostic question, and wait.

Record the learner's exact response with `session answer`. Only then grade it with `session grade`, citing relevant claim IDs. Use retrieval, accuracy, and transfer scores. Give a concise correction and, where needed, a fresh application/debug/create prompt.

If the learner asks a question at any point:

1. preserve the exact question with `session question`;
2. acknowledge the specific confusion and decide whether existing claims support an answer;
3. if evidence is missing, register a source and claim before teaching;
4. record the patient, source-backed answer with `session explain --claim ... --check-question ...`;
5. stop and wait for the learner to restate or apply the idea;
6. record that response with `session answer --explanation-id ...`, grade it, then resume the interrupted task.

Use a concrete example, contrast, analogy, or smaller prerequisite when the first explanation does not land. Never repeat the same wording louder or replace the learner's attempt with a polished answer.

Do not append broad caveats about other databases, tools, schools of thought, or domains unless the cited claims support them. Either register the extra source, narrow the sentence to the supported system, or label the comparison unresolved.

Do not finish a session with ungraded answers, unanswered learner questions, or unchecked explanations. Record time, confidence, and the learner's reflection. Capture durable synthesis as an Obsidian note with claim IDs. Update observed profile only from a session/answer/grade/review evidence ID.
