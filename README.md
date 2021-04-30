# Running the Script

To run the script do ...

# Data Notes

- the dataframe is divided into one for schizophrenia and one for normals in variables titled
  HealthyMeasurements and SchizophreniaMeasurements: you probably want to concatenate the two and
  create a corresponding label array
- Minimal hypertuning is needed so that I can say to the reviewer that we've 'optimized' the
  performance
- 5-fold validation is fine
- Basic feature analysis is fine.
- No deep learning is fine and expected. Off-the-shelf algorithms are great here.
- Saving the comparative performance and limited feature analysis in a spreadsheet is great.
- Simple python script is great.

The first version should implement:

  - SVM
  - RF
  - decision tree
  - "least squares bagging"
  - basic ANN
  - no deep learning, but it would be great if you could run a basic MLP with hypertuning

I also need some off-the-shelf feature selection including stepwise regression. The
first round of effort included some basic feature selection:
  - running PCA and selecting the leading components to inform prediction
    - this didn't work very well on this dataset
  - ranking all the features by a basic univariate statistic (like cohen's d or AUC) and selecting the leading
    features
    - these were very basic feature selection baselines to compare against and didn't work that
      well and weren't very interesting
  - stepwise regression got the best results so I would need that included

We do need to provide a few (let's say 3 minimum) off-the-shelf feature selection techniques applied
to each of the 5 classifiers. If there is a problem with any of that, please let me know and I'm
open to suggestions for modification (I don't mind explaining to reviewers that we redid the
experiment, though it is generally best for us to have the next version be similar to previous). We
can probably strengthen the paper with some well selected off-the-shelf feature selection
algorithms.

Please report OA (??? - Overall Accuracy?) and AUC mean and std deviation. The manuscript is due in ~9 days.