# %% IMPORTS

from regression_model_template.core import schemas
from regression_model_template.utils import splitters

# %% SPLITTERS


def test_train_test_splitter(inputs: schemas.Inputs, targets: schemas.Targets) -> None:
    # given
    shuffle = False
    test_size = 50
    random_state = 0
    splitter = splitters.TrainTestSplitter(shuffle=shuffle, test_size=test_size, random_state=random_state)
    # when
    n_splits = splitter.get_n_splits(inputs=inputs, targets=targets)
    splits = list(splitter.split(inputs=inputs, targets=targets))
    train_index, test_index = splits[0]  # train/test indexes
    # then
    assert n_splits == len(splits) == 1, "Splitter should return 1 split!"
    assert len(test_index) == test_size, "Test index should have the given size!"
    assert len(train_index) == len(targets) - test_size, "Train index should have the remaining size!"
    assert not inputs.iloc[test_index].empty, "Test index should be a subset of the inputs!"
    assert not targets.iloc[train_index].empty, "Train index should be a subset of the targets!"


def test_time_series_splitter(inputs: schemas.Inputs, targets: schemas.Targets) -> None:
    # given
    gap = 0
    n_splits = 3
    test_size = 50
    splitter = splitters.TimeSeriesSplitter(gap=gap, n_splits=n_splits, test_size=test_size)
    # when
    n_splits = splitter.get_n_splits(inputs=inputs, targets=targets)
    splits = list(splitter.split(inputs=inputs, targets=targets))
    # then
    assert n_splits == len(splits), "Splitter should return the given n splits!"
    for i, (train_index, test_index) in enumerate(splits):
        assert len(test_index) == test_size, "Test index should have the given test size!"
        assert len(train_index) == (
            len(inputs) - test_size * (n_splits - i)
        ), "Train index should have the cumulative remaining size!"
        assert train_index.max() < test_index.min(), "Train index should always be lower than test index!"
        assert not inputs.iloc[train_index].empty, "Train index should be a subset of the inputs!"
        assert not inputs.iloc[test_index].empty, "Test index should be a subset of the inputs!"
