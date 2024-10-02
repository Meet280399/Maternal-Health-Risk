from __future__ import annotations

# fmt: off
import sys  # isort: skip
from pathlib import Path  # isort: skip
ROOT = Path(__file__).resolve().parent.parent # isort: skip
sys.path.append(str(ROOT))  # isort: skip
# fmt: on

from enum import EnumMeta
from tempfile import TemporaryDirectory
from typing import Type, Union

import pytest
from pytest import CaptureFixture
from cli_test_helpers import ArgvContext

from df_analyze.analysis.univariate.associate import (
    CatClsStats,
    CatRegStats,
    ContClsStats,
    ContRegStats,
)
from df_analyze.cli.cli import ProgramOptions, Verbosity, get_options, random_cli_args
from df_analyze.enumerables import (
    ClsScore,
    DfAnalyzeClassifier,
    DfAnalyzeRegressor,
    EmbedSelectionModel,
    FeatureSelection,
    NanHandling,
    Normalization,
    RegScore,
    WrapperSelection,
    WrapperSelectionModel,
)
from df_analyze.testing.datasets import ALL_DATASETS, TEST_DATASETS, TestDataset, all_ds

PATH = list(TEST_DATASETS.values())[0].datapath


@pytest.mark.fast
def test_classifiers() -> None:
    with ArgvContext(
        "df-analyze.py",
        "--df",
        f"{PATH}",
        "--categoricals",
        "one,two,three",  # spaces are allowed but count in names; commas separate
    ):
        # opts = get_options(f"--df {PATH} --categoricals one two three")
        opts = get_options()
        assert opts.categoricals == sorted(["one", "two", "three"])


@pytest.mark.fast
def test_quoted_classifiers() -> None:
    # NOTE: can also just confirm manually that this does work to allow
    # column names with spaces in them.
    with ArgvContext(
        "df-analyze.py",
        "--df",
        f"{PATH}",
        "--categoricals",
        "a one,a two",
        "--verbosity",
        "0",
    ):
        opts = get_options()
    assert opts.categoricals == ["a one", "a two"]


@all_ds
def test_random_types(dataset: tuple[str, TestDataset]) -> None:
    typings = {
        "datapath": (Path,),
        "target": (str,),
        "categoricals": (list, str),
        "ordinals": (list, str),
        "drops": (list, str),
        "nan_handling": (NanHandling,),
        "norm": (Normalization,),
        "wrapper_model": (WrapperSelectionModel,),
        "filter_assoc_cont_cls": (ContClsStats,),
        "filter_assoc_cat_cls": (CatClsStats,),
        "filter_assoc_cont_reg": (ContRegStats,),
        "filter_assoc_cat_reg": (CatRegStats,),
        "filter_pred_cls_score": (ClsScore,),
        "filter_pred_reg_score": (RegScore,),
        "is_classification": (bool,),
        "htune_trials": (int,),
        "outdir": (Path,),
        "is_spreadsheet": (bool,),
        "separator": (str,),
        "verbosity": (Verbosity,),
        "no_warn_explosion": (bool,),
        "no_preds": (bool,),
    }
    comparables: dict[str, tuple[Union[EnumMeta, Type[None]], ...]] = {
        "feat_select": (FeatureSelection,),
        "embed_select": (EmbedSelectionModel, type(None)),
        "classifiers": (DfAnalyzeClassifier,),
        "regressors": (DfAnalyzeRegressor,),
    }
    nullables = {
        "wrapper_select": (WrapperSelection,),
        "n_feat_wrapper": (int, float),
    }
    numerics = {
        "n_filter_cont": (int, float),
        "n_filter_cat": (int, float),
        "n_feat_filter": (int, float),
        "test_val_size": (int, float),
    }
    all_attrs = sorted(
        set([*typings.keys(), *comparables.keys(), *nullables.keys(), *numerics.keys()])
    )
    dsname, ds = dataset
    with TemporaryDirectory() as tempfile:
        for _ in range(50):
            opts = ProgramOptions.random(ds, outdir=Path(tempfile))
            for attr in all_attrs:
                if not hasattr(opts, attr):
                    raise ValueError(f"ProgramOptions missing attribute: {attr}")

                value = getattr(opts, attr)
                if attr in comparables:
                    if not isinstance(value, tuple):
                        raise TypeError(
                            f"Expected tuple for type of ProgramOptions.{attr}. "
                            f"Got '{type(value)}' instead."
                        )
                    expected = comparables[attr]
                    values = value
                    for val in values:
                        if not isinstance(val, expected):
                            raise TypeError(
                                f"Expected ProgramOptions.{attr} to be instance of "
                                f"{expected}. Got '{type(val)}' instead."
                            )

                elif attr in nullables:
                    expected = (type(None), *nullables[attr])
                    if not isinstance(value, expected):
                        raise TypeError(
                            f"Expected one of {expected} for type of ProgramOptions.{attr}. "
                            f"Got '{type(value)}' instead."
                        )

                elif attr in numerics:
                    expected = numerics[attr]
                    if not isinstance(value, expected):
                        raise TypeError(
                            f"Expected one of {expected} for type of ProgramOptions.{attr}. "
                            f"Got '{type(value)}' instead."
                        )
                elif attr in typings:
                    expected = typings[attr]
                    if not isinstance(value, expected):
                        raise TypeError(
                            f"Expected one of {expected} for type of ProgramOptions.{attr}. "
                            f"Got '{type(value)}' instead."
                        )
                else:
                    raise RuntimeError(
                        f"Impossible! (Attribute {attr} is missing on `ProgramOptions`."
                    )


if __name__ == "__main__":
    for dsname, ds in ALL_DATASETS:
        with TemporaryDirectory() as tempdir:
            args = random_cli_args(ds, Path(tempdir), spreadsheet=True)
            print(args)
            args = random_cli_args(ds, Path(tempdir), spreadsheet=False)
            print(args)
