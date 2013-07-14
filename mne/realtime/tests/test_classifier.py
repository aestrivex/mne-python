# Author: Mainak Jas <mainak@neuro.hut.fi>
#
# License: BSD (3-clause)

import os.path as op
from nose.tools import assert_true, assert_raises
from numpy.testing import assert_array_equal

from mne import fiff, read_events, Epochs
from mne.realtime import Scaler, FilterEstimator, PSDEstimator, ConcatenateChannels

tmin, tmax = -0.2, 0.5
event_id = dict(aud_l=1, vis_l=3)
start, stop = 0, 8

data_dir = op.join(op.dirname(__file__), '..', '..', 'fiff', 'tests', 'data')
raw_fname = op.join(data_dir, 'test_raw.fif')
event_name = op.join(data_dir, 'test-eve.fif')

raw = fiff.Raw(raw_fname, preload=True)
events = read_events(event_name)

picks = fiff.pick_types(raw.info, meg=True, stim=False, ecg=False, eog=False,
                        exclude='bads')
picks = picks[1:13:3]

epochs = Epochs(raw, events, event_id, tmin, tmax, picks=picks,
                baseline=(None, 0), preload=True)


def test_scaler():
    """Test methods of Scaler
    """
    epochs_data = epochs.get_data()
    scaler = Scaler(epochs.info)
    y = epochs.events[:, -1]
    X = scaler.fit_transform(epochs_data, y)

    assert_true(X.shape == epochs_data.shape)
    assert_array_equal(scaler.fit(epochs_data, y).transform(epochs_data), X)

    # Test init exception
    assert_raises(ValueError, scaler.fit, epochs, y)
    assert_raises(ValueError, scaler.fit, epochs, y)


def test_filterestimator():
    """Test methods of FilterEstimator
    """
    epochs_data = epochs.get_data()
    filt = FilterEstimator(epochs.info, 1, 40)
    y = epochs.events[:, -1]
    X = filt.fit_transform(epochs_data, y)

    assert_true(X.shape == epochs_data.shape)
    assert_array_equal(filt.fit(epochs_data, y).transform(epochs_data), X)

    # Test init exception
    assert_raises(ValueError, filt.fit, epochs, y)
    assert_raises(ValueError, filt.fit, epochs, y)


def test_psdstimator():
    """Test methods of PSDEstimator
    """
    epochs_data = epochs.get_data()
    psd = PSDEstimator(epochs.info)
    y = epochs.events[:, -1]
    X = psd.fit_transform(epochs_data, y)

    assert_true(X.shape[0] == epochs_data.shape[0])
    assert_array_equal(psd.fit(epochs_data, y).transform(epochs_data), X)

    # Test init exception
    assert_raises(ValueError, psd.fit, epochs, y)
    assert_raises(ValueError, psd.fit, epochs, y)


def test_concatenatechannels():
    """Test methods of ConcatenateChannels
    """
    epochs_data = epochs.get_data()
    concat = ConcatenateChannels(epochs.info)
    y = epochs.events[:, -1]
    X = concat.fit_transform(epochs_data, y)

    # Check data dimensions
    assert_true(X.shape[0] == epochs_data.shape[0])
    assert_true(X.shape[1] == epochs_data.shape[1] * epochs_data.shape[2])

    assert_array_equal(concat.fit(epochs_data, y).transform(epochs_data), X)

    # Check if data is preserved
    n_times = epochs_data.shape[2]
    assert_array_equal(epochs_data[0, 0, 0:n_times], X[0, 0:n_times])

    # Test init exception
    assert_raises(ValueError, concat.fit, epochs, y)
    assert_raises(ValueError, concat.fit, epochs, y)