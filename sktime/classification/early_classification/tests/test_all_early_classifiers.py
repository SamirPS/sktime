# -*- coding: utf-8 -*-
"""Unit tests for early classifier input output."""

__author__ = ["mloning", "TonyBagnall", "fkiraly", "MatthewMiddlehurst"]

import numpy as np

from sktime.classification.tests.test_all_classifiers import (
    TestAllClassifiers as _TestAllClassifiers,
)
from sktime.tests.test_all_estimators import BaseFixtureGenerator, QuickTester


class EarlyClassifierFixtureGenerator(BaseFixtureGenerator):
    """Fixture generator for early classifier tests.

    Fixtures parameterized
    ----------------------
    estimator_class: estimator inheriting from BaseObject
        ranges over estimator classes not excluded by EXCLUDE_ESTIMATORS, EXCLUDED_TESTS
    estimator_instance: instance of estimator inheriting from BaseObject
        ranges over estimator classes not excluded by EXCLUDE_ESTIMATORS, EXCLUDED_TESTS
        instances are generated by create_test_instance class method
    scenario: instance of TestScenario
        ranges over all scenarios returned by retrieve_scenarios
    """

    # note: this should be separate from TestAllEarlyClassifiers
    #   additional fixtures, parameters, etc should be added here
    #   TestAllEarlyClassifiers should contain the tests only

    estimator_type_filter = "early_classifier"


class TestAllEarlyClassifiers(EarlyClassifierFixtureGenerator, QuickTester):
    """Module level tests for all sktime classifiers."""

    def test_multivariate_input_exception(self, estimator_instance):
        """Test univariate early classifiers raise exception on multivariate X."""
        test = _TestAllClassifiers.test_multivariate_input_exception
        test(self, estimator_instance)

    def test_classifier_output(self, estimator_instance, scenario):
        """Test classifier outputs the correct data types and values.

        Test predict produces a np.array or pd.Series with only values seen in the train
        data, and that predict_proba probability estimates add up to one.
        """
        n_classes = scenario.get_tag("n_classes")
        X_new = scenario.args["predict"]["X"]
        y_train = scenario.args["fit"]["y"]
        y_pred, decisions, state_info = scenario.run(
            estimator_instance, method_sequence=["fit", "predict"]
        )

        # check predict
        assert isinstance(y_pred, np.ndarray)
        assert y_pred.shape == (X_new.shape[0],)
        assert np.all(np.isin(np.unique(y_pred), np.unique(y_train)))
        assert isinstance(decisions, np.ndarray)
        assert decisions.shape == (X_new.shape[0],)
        assert decisions.dtype == bool

        # predict and update methods should update the state info as an array
        assert isinstance(estimator_instance.get_state_info(), np.ndarray)

        # check predict proba (all classifiers have predict_proba by default)
        y_proba, decisions, state_info = scenario.run(
            estimator_instance, method_sequence=["predict_proba"]
        )
        assert isinstance(y_proba, np.ndarray)
        assert y_proba.shape == (X_new.shape[0], n_classes)
        np.testing.assert_allclose(y_proba.sum(axis=1), 1)
        assert isinstance(decisions, np.ndarray)
        assert decisions.shape == (X_new.shape[0],)
        assert decisions.dtype == bool
