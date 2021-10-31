CMPE 365 Assignment 2 Submission

| Name        | Student Number | NetID  |
| ----------- | -------------- | ------ |
| Bryan Hoang | 20053722       | 16bch1 |
| Liam Cregg  | 20054881       | 16lbc1 |

Comments for TA:

- The code has been:
  - mainly tested on python 3.10
  - formatted with `black`
  - linted with:
    - `pydocstyle`
    - `flake8`
  - modified with some additional type hints
  - modified to detect 'p' key *releases* rather than *presses* due to a bug on
    WSL 2 where "ghost presses" cause the program to exit prematurely. The
    behaviour is practically identical to the unmodified variant.
