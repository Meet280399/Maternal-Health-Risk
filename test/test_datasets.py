from __future__ import annotations

# fmt: off
import sys  # isort: skip
from pathlib import Path  # isort: skip
ROOT = Path(__file__).resolve().parent.parent  # isort: skip
sys.path.append(str(ROOT))  # isort: skip
# fmt: on


import numpy as np

from df_analyze.testing.datasets import TestDataset, fast_ds, med_ds, slow_ds


@fast_ds
def test_loading(dataset: tuple[str, TestDataset]) -> None:
    dsname, ds = dataset
    df = ds.load()
    assert df.shape[0] > 0
    assert df.shape[1] > 0


@fast_ds
def test_categoricals(dataset: tuple[str, TestDataset]) -> None:
    dsname, ds = dataset
    assert isinstance(ds.categoricals, list)
    assert all(isinstance(c, str) for c in ds.categoricals)


def do_splitting(dataset: tuple[str, TestDataset]) -> None:
    dsname, ds = dataset
    X_tr, X_test, y_tr, y_test, num_classes = ds.train_test_split()

    if ds.is_classification:
        assert num_classes == len(np.unique(np.concatenate([y_tr, y_test])))
    assert np.isnan(np.ravel(X_tr)).sum() == 0
    assert np.isnan(np.ravel(X_test)).sum() == 0


@fast_ds
def test_splitting_fast(dataset: tuple[str, TestDataset]) -> None:
    do_splitting(dataset)


@med_ds
def test_splitting_med(dataset: tuple[str, TestDataset]) -> None:
    do_splitting(dataset)


@slow_ds
def test_splitting_slow(dataset: tuple[str, TestDataset]) -> None:
    do_splitting(dataset)
