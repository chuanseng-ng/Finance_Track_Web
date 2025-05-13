# Personal Web Finance Track

## Status

[![Python Linting](https://github.com/chuanseng-ng/Finance_Track_Web/actions/workflows/pylint.yml/badge.svg?branch=main&event=push)](https://github.com/chuanseng-ng/Finance_Track_Web/actions/workflows/pylint.yml/badge.svg)
[![CodeQL](https://github.com/chuanseng-ng/Finance_Track_Web/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/chuanseng-ng/Finance_Track_Web/actions/workflows/github-code-scanning/codeql)
[![Codacy Code Quality](https://app.codacy.com/project/badge/Grade/4ae04aa0ae404916b1c52a7d53557f07)](https://app.codacy.com/gh/chuanseng-ng/Finance_Track_Web/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codacy Coverage](https://app.codacy.com/project/badge/Coverage/4ae04aa0ae404916b1c52a7d53557f07)](https://app.codacy.com/gh/chuanseng-ng/Finance_Track_Web/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

## Code Coverage
<!-- markdownlint-disable MD033 -->
<!-- Pytest Coverage Comment:Begin -->
<a href="https://github.com/chuanseng-ng/Finance_Track_Web/blob/code/pre_release/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-100%25-brightgreen.svg" /></a><details><summary>Coverage Report </summary><table><tr><th>File</th><th>Stmts</th><th>Miss</th><th>Cover</th></tr><tbody><tr><td><b>TOTAL</b></td><td><b>892</b></td><td><b>0</b></td><td><b>100%</b></td></tr></tbody></table></details>
<!-- Pytest Coverage Comment:End -->

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
  - Plot monthly/yearly expense graph (Using plotly)
  - Plot expense graph for custom time period (Using plotly)
  - Web app UI overhaul
- To-Do
  - NA
- Quality of Life (QoL) items
  - (Done) Add support to skip currency conversion if API key does not exists in user_config.yaml
  - (Done) Legacy database import (Specific format in Excel)
  - (Done) Admin page for direct database modification
    - With pre-filters based on database year + date range

## Version Control

Note:  Only keep latest 5 version histories

| Version | Description | Changes |
| :-----: | :---------: | :-----: |
| V3.3 | Improved web-app UI | Overhaul web-app UI using bootstrap CSS |
| V3.2 | Admin table modification | Allow admin to modify database as needed |
| V3.1 | Admin page addition | Add admin login page for database modification |
| V3.0 | Legacy excel database import support | Add support for legacy database import merge with current |
| V2.1 | Custom time period expenses graph plot | Add support for custom time period expense plot |

## References

- NIL
