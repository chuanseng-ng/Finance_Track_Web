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
  - Plot monthly/yearly expense graph
  - Plot expense graph for custom time period
- To-Do
  - Legacy database import
  - Web app UI overhaul
- Quality of Life (QoL) items
  - (Done) Add support to skip currency conversion if API key does not exists in user_config.yaml

## Version Control

Note:  Only keep latest 5 version histories

| Version | Description | Changes |
| :-----: | :---------: | :-----: |
| V1.2 | Custom time period expenses graph plot | Add support for custom time period expense plot |
| V1.1 | Monthly/yearly expenses graph plot | Add support for current month/year expense plot |
| V1.0 | Update README for version_control | Add version_control info into README |
| V0.9 | month_salary calculation update | Add extra-cases in month_salary calculation to cover corner cases |
| V0.8 | Add salary support | Add salary_input support in web app + Add current month's balance calculation |

## References

- NIL
