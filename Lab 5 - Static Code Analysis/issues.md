# Lab 5: Static Code Analysis — Issue Report

## Tools Used
- Pylint
- Bandit
- Flake8

## Issue Table

| Issue | Type | Line(s) Before Fix | Description | Fix Approach |
|---|---|---|---|---|
| Shell command execution (B605) | Security - High | 63 | `os.system()` constructed a shell command using a variable. | Replaced shell execution with an HTTP connection and validated the IP address. |
| Unsafe XML parsing (B314) | Security - Medium | 18 | Standard ElementTree parsing can be unsafe for untrusted XML. | Used `defusedxml.ElementTree`. |
| XML parser import (B405) | Security - Low | 3 | Bandit flagged the standard XML ElementTree import. | Replaced it with `defusedxml.ElementTree` to use a hardened XML parser. |
| Hardcoded password (B105) | Security - Low | 13 | A password was embedded in the source code. | Removed the unused hardcoded password. |
| Mutable default argument | Code quality | 42 | `extras={}` could share mutable state between calls. | Changed the default to `None` and initialized a new dictionary when needed. |
| Non-standard function names | Code quality | Multiple | Function names used camelCase instead of snake_case. | Renamed functions and updated their calls. |
| Unused currency argument | Code quality | 50 | `averageBill` accepted an unused currency argument. | Removed the unused argument. |
| Missing docstrings | Code quality | Multiple | The module and functions lacked docstrings. | Added module and function docstrings. |
| Missing file encoding | Code quality | 57 | `open()` did not explicitly specify an encoding. | Added `encoding="utf-8"`. |
| Formatting violations | Style | Multiple | Flake8 reported blank-line, whitespace and line-length issues. | Corrected the formatting and spacing. |

## Verification

- Pylint before fixes: 5.44/10
- Pylint after fixes: 10.00/10
- Bandit after fixes: No issues identified.
- Flake8 after fixes: No violations displayed.
- The electricity bill demonstration produced the expected results after the changes.
