# Personal Web Finance Track

## Status

[![Python Linting](https://github.com/chuanseng-ng/Finance_Track_Web/actions/workflows/pylint.yml/badge.svg?branch=main&event=push)](https://github.com/chuanseng-ng/Finance_Track_Web/actions/workflows/pylint.yml/badge.svg)
[![CodeQL](https://github.com/chuanseng-ng/Finance_Track_Web/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/chuanseng-ng/Finance_Track_Web/actions/workflows/github-code-scanning/codeql)

## Code Coverage
<!-- markdownlint-disable MD033 -->
<!-- Pytest Coverage Comment:Begin -->
<a href="https://github.com/chuanseng-ng/Finance_Track_Web/blob/code/pre_release/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-97%25-brightgreen.svg" /></a><details><summary>Coverage Report </summary><table><tr><th>File</th><th>Stmts</th><th>Miss</th><th>Cover</th><th>Missing</th></tr><tbody><tr><td colspan="5"><b>routes</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/chuanseng-ng/Finance_Track_Web/blob/code/pre_release/routes/admin_routes.py">admin_routes.py</a></td><td>37</td><td>19</td><td>49%</td><td><a href="https://github.com/chuanseng-ng/Finance_Track_Web/blob/code/pre_release/routes/admin_routes.py#L20-L22">20&ndash;22</a>, <a href="https://github.com/chuanseng-ng/Finance_Track_Web/blob/code/pre_release/routes/admin_routes.py#L31-L45">31&ndash;45</a>, <a href="https://github.com/chuanseng-ng/Finance_Track_Web/blob/code/pre_release/routes/admin_routes.py#L51-L53">51&ndash;53</a>, <a href="https://github.com/chuanseng-ng/Finance_Track_Web/blob/code/pre_release/routes/admin_routes.py#L59-L63">59&ndash;63</a></td></tr><tr><td colspan="5"><b>tests/routes</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/chuanseng-ng/Finance_Track_Web/blob/code/pre_release/tests/routes/test_index_routes.py">test_index_routes.py</a></td><td>52</td><td>4</td><td>92%</td><td><a href="https://github.com/chuanseng-ng/Finance_Track_Web/blob/code/pre_release/tests/routes/test_index_routes.py#L41-L45">41&ndash;45</a>, <a href="https://github.com/chuanseng-ng/Finance_Track_Web/blob/code/pre_release/tests/routes/test_index_routes.py#L88">88</a></td></tr><tr><td><b>TOTAL</b></td><td><b>716</b></td><td><b>23</b></td><td><b>97%</b></td><td>&nbsp;</td></tr></tbody></table></details>
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
- To-Do
  - Web app UI overhaul
- Quality of Life (QoL) items
  - (Done) Add support to skip currency conversion if API key does not exists in user_config.yaml
  - (Done) Legacy database import (Specific format in Excel)

## Version Control

Note:  Only keep latest 5 version histories

| Version | Description | Changes |
| :-----: | :---------: | :-----: |
| V3.0 | Legacy excel database import support | Add support for legacy database import merge with current |
| V2.1 | Custom time period expenses graph plot | Add support for custom time period expense plot |
| V2.0 | Monthly/yearly expenses graph plot | Add support for current month/year expense plot |
| V1.0 | Update README for version_control | Add version_control info into README |
| V0.9 | month_salary calculation update | Add extra-cases in month_salary calculation to cover corner cases |
| V0.8 | Add salary support | Add salary_input support in web app + Add current month's balance calculation |

## References

- NIL
