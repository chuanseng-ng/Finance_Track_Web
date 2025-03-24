# Personal Web Finance Track

## Introduction

- Simple WebUI-based finance tracker
  - Tracks daily expenses
  - Tracks monthly recurring expenses
  - Utilizes salary to calculate remaining spending power
  - Plot monthly/yearly expense graph
  - Plot expense graph for custom time period

## Features

- Implemented
  - Tracks daily expenses
  - Auto currency conversion (XXX to SGD)
  - Tracks monthly recurring expenses (Included in current month's total expense if valid)
  - Utilizes salary to calculate remaining spending power
- To-Do
  - Plot monthly/yearly expense graph
  - Plot expense graph for custom time period
  - Legacy database import
  - Web app UI overhaul
- Quality of Life (QoL) items
  - (Done) Add support to skip currency conversion if API key does not exists in user_config.yaml

## Version Control

Note:  Only keep latest 5 version histories

| Version | Description | Changes |
| :-----: | :---------: | :-----: |
| V0.9 | month_salary calculation update | Add extra-cases in month_salary calculation to cover corner cases |
| V0.8 | Add salary support | Add salary_input support in web app + Add current month's balance calculation |
| V0.7 | Update current month's total | Add recurring_expenses in current month's total if valid + Add NULL end_date support |
| V0.6 | Add bypass for error_case | Add error_bypass option + code refactoring |
| V0.5 | Add recurring_expenses to current month's total | Add valid recurring expenses into current month's total expenses |

## References

- NIL
