---
trigger: glob
description: "Defines the custom Hexa-Script language. See ADR-0004 for implementation choice."
globs: src/hexa_core/engine/script_runner.py, tests/spec/test_script_runner.py
---

# Rule: Bot Scripting Language ("Hexa-Script")

## 3.1 Language Design

* **Style:** A simple, case-insensitive, BASIC-like interpreted language.
* **Implementation:** Use the `sly` library ([https://github.com/dabeaz/sly](https://github.com/dabeaz/sly)) to build a lexer and parser.
* **Error Handling:** For the MVP, script execution MUST halt immediately on any runtime error (e.g., invalid command, insufficient tokens).

## 3.2 Syntax

* **Variables:**  `SET "varName" <value|expression>`
* **Flow Control:**  `LABEL "name"`, `GOTO "name"`
* **Conditionals:**  `IF <condition> THEN <command>` or `IF <condition> GOTO "label"`
* **Expressions:**  `( <operand> <operator> <operand> )`

## 3.3 Bot API

* **Context (Free):**  `SELF` (dict) and `ENEMIES` (list) are globally available.
* **Helpers (1 Token):**  `find_path(start, end)`
* **Actions (Variable Cost):**  `move(path)`, `attack(target_id)`
