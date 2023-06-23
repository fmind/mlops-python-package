"""Test the splitters module."""
# pylint: disable=missing-docstring

# %% IMPORTS

from wines import schemas, splitters

# %% SPLITTERS


def test_train_test_splitter(inputs: schemas.Inputs):
    # given
    ratio = 0.6
    # when
    splitter = splitters.TrainTestSplitter(ratio=ratio)
    train, test = splitter.split(data=inputs)
    # then
    assert len(train) > len(test), "Train set should be larger than the test set!"
    assert len(train) + len(test) == len(inputs), "Train + test should have the same lenght as data!"
