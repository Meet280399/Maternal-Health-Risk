import os
import traceback
from dataclasses import dataclass
from pathlib import Path
from time import ctime
from typing import Any, List, Optional

import numpy as np
import optuna
import pandas as pd
from pandas import DataFrame
from sklearn.model_selection import ParameterGrid
from tqdm import tqdm

from src._types import CVMethod, Estimator, FeatureSelection
from src.analyses import full_estimator_analysis
from src.options import ProgramOptions, get_options
from src.utils import Debug

RESULTS_DIR = Path(__file__).parent / "results"


@dataclass
class LoopArgs(Debug):
    """Container. Arguments / attributes following `options` override the properties
    in ProgramOptions.
    """

    options: ProgramOptions
    estimator: Estimator
    feature_selection: Optional[FeatureSelection]
    # verbosity: int = optuna.logging.ERROR
    verbosity: int = optuna.logging.INFO


def listify(item: Any) -> List[Any]:
    if isinstance(item, list):
        return item
    if isinstance(item, tuple):
        return [i for i in item]
    return [item]


def pbar_desc(loop_args: LoopArgs) -> str:
    estimator = loop_args.estimator
    selection = loop_args.feature_selection
    n_feat = loop_args.options.selection_options.n_feat
    htune_val = loop_args.options.htune_val
    if isinstance(htune_val, int):
        hv = f"{htune_val}-fold"
    elif isinstance(htune_val, float):
        hv = f"{int(100*htune_val)}%-holdout"
    elif htune_val == "mc":
        hv = "mc"
    else:
        hv = "none"
    return f"{estimator}|{selection}|{n_feat} features|htune_val={hv}"


def try_save(df: DataFrame, outdir: Path, file_info: str) -> None:
    json = outdir / f"{file_info}.json"
    csv = outdir / f"{file_info}.csv"
    try:
        df.to_json(json)
        print(f"Saved interim result to {json}")
    except Exception:
        traceback.print_exc()
        print(f"Failed to save following results to {json}")
        df.to_markdown(tablefmt="simple", floatfmt="0.5f")
    try:
        df.to_csv(csv)
        print(f"Saved interim result to {csv}")
    except Exception:
        traceback.print_exc()
        print(f"Failed to save following results to {csv}")
        df.to_markdown(tablefmt="simple", floatfmt="0.5f")


def save_interim_result(args: LoopArgs, result: DataFrame) -> None:
    estimator = args.estimator
    outdir = args.options.outdir
    if outdir is None:
        return
    step = "step-up" == args.feature_selection

    timestamp = ctime().replace(":", "-").replace("  ", " ").replace(" ", "_")
    file_info = f"results__{estimator}{'_step-up' if step else ''}__{timestamp}"
    try_save(result, outdir, file_info)


def sort_df(df: DataFrame) -> None:
    """Auto-detect if classification or regression based on columns and sort"""
    cols = [c.lower() for c in df.columns]
    is_regression = False
    sort_col = None
    for col in cols:
        if ("mae" in col) and ("sd" not in col):
            is_regression = True
            sort_col = col
            break
    if sort_col is None:
        return df
    ascending = is_regression
    return df.sort_values(by=sort_col, ascending=ascending)


def print_sorted(df: DataFrame) -> None:
    """Auto-detect if classification or regression based on columns"""
    cols = [c.lower() for c in df.columns]
    is_regression = False
    sort_col = None
    for col in cols:
        if ("mae" in col) and ("sd" not in col):
            is_regression = True
            sort_col = col
            break
    if sort_col is None:
        print(df.to_markdown(tablefmt="simple", floatfmt="0.3f"))
        return
    ascending = is_regression
    table = df.sort_values(by=sort_col, ascending=ascending).to_markdown(
        tablefmt="simple", floatfmt="0.3f"
    )
    print(table)


def run_analysis(
    loop_args: List[LoopArgs], estimators: List[Estimator], is_stepup: bool = False
) -> DataFrame:
    """Perform full analysis and feature selection for the *single* classifier and *single*
    feature-selection method specified in `args`.

    Parameters
    ----------
    args: List[Dict]
        Arguments for `src.analyses.full_estimator_analysis`, e.g.

            options: ProgramOptions
            estimator: Estimator
            feature_selection: Optional[FeatureSelection]
            verbosity: int = optuna.logging.ERROR

    estimators: List[Estimator]
        The list of models to tune and analyze. Argument only used for creating
        final summary DataFrame filename.

    is_stepup: bool = False
        If True, let's the function know we are doing step-up feature selection.

    Returns
    -------
    df: DataFrame
        DataFrame of analysis results sorted

    """
    results_dir = loop_args[0].options.outdir
    if not results_dir.exists():
        os.makedirs(results_dir, exist_ok=True)

    results = []
    pbar = tqdm(total=len(loop_args))
    for arg in loop_args:
        pbar.set_description(pbar_desc(arg))
        result = full_estimator_analysis(**arg.__dict__)
        results.append(result)
        save_interim_result(arg, result)
        pbar.update()

    df = sort_df(pd.concat(results, axis=0, ignore_index=True))
    timestamp = ctime().replace(":", "-").replace("  ", " ").replace(" ", "_")
    models = str(estimators).replace(" ", "").replace(",", "_").replace("(", "").replace(")", "").replace("'", "")
    file_info = f"results__{models}{'__step-up' if is_stepup else ''}__{timestamp}"
    try_save(df, results_dir, file_info)
    print_sorted(df)
    return df


if __name__ == "__main__":
    # TODO:
    # get arguments
    # run analyses based on args
    options = get_options()
    estimators = options.classifiers if options.mode == "classify" else options.regressors
    feature_selection = options.selection_options.feat_select
    is_stepup = "step-up" in listify(feature_selection)

    arg_options = dict(
        options=listify(options),
        estimator=listify(estimators),
        feature_selection=listify(feature_selection),
    )
    loop_args = [LoopArgs(**params) for params in ParameterGrid(arg_options)]
    run_analysis(loop_args, estimators, is_stepup)
