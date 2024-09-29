def pytest_sessionstart(session):
    """
    Called after the Session object has been created and before performing collection and entering the run test loop.

    For some reason imports break when using the container on Compute Canada, likely due to the strange filesystem
    and because passing in filesystem paths to apptainer is always strange and broken. So none of the test files
    can find the imports. So, we forcefully add a path so the container can find imports...
    """
    import sys
    from pathlib import Path

    # Stupid insane Python import garbage
    # https://github.com/huggingface/transformers/issues/5281#issuecomment-2365359156
    # https://github.com/huggingface/transformers/issues/5281#issuecomment-2365359156
    import torch

    ROOT = Path(__file__).resolve().parent
    SRC = ROOT / "src"
    sys.path.append(str(SRC))
