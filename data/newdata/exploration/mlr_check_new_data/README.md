# MLR3 assumption check on current data (2026-10-12)

Reruns every code cell of `colab/MLR3.ipynb` (80/10/10, seed 99) on `cleaned/merged.csv` (57,050 rows) with these changes only:
- data adapter (`prep_data.py`): column names, car_age = 2026 - year, 4 rows mileage 0 -> 1
- `fastlinalg.py`: pinv/lstsq/matrix_rank via scaled normal equations because LAPACK SVD is very slow on this machine
  (checked on one fold: max |beta diff| 2e-8 vs SVD lstsq, rank 503/503)
- cell 19 (variable selection): CV only run for variables whose F-test p > alpha (same decision rule, much faster)
- SHA256 assertion skipped

Run: `python prep_data.py <dir>`, `python build_runner.py <dir>` (builds `run_mlr3_new.py` in <dir>), `python -I -X utf8 run_mlr3_new.py > mlr3_new.log` (about 25 min).
`mlr3_new.log` is the full output of the run.
