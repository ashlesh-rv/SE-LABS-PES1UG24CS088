# Lab 5: Static Code Analysis — Reflection

## 1. What is static code analysis?

Static code analysis examines source code without executing it to identify potential bugs, security vulnerabilities, code quality problems and style violations.

## 2. What did Pylint, Bandit and Flake8 help identify?

Pylint identified code quality issues such as missing docstrings, naming conventions, mutable default arguments and unused arguments. Bandit identified security risks related to unsafe XML parsing (B314), the XML parser import (B405), a hardcoded password (B105) and shell command execution (B605). Flake8 identified formatting, whitespace and line-length problems.

## 3. How did fixing the issues improve the program?

The fixes improved readability, maintainability and security. The code now uses clearer function names, safer handling of default arguments, a hardened XML parser and an HTTP connection instead of shell command execution. The program continued to calculate and display the electricity bills correctly. Rerunning the tools verified that the reported issues had been addressed.

## 4. What did you learn from this lab?

I learned that a program can run correctly and still contain quality and security problems. Using multiple static analysis tools helps identify different types of issues. I also learned to rerun the tools after making changes to verify that the reported issues have been addressed.