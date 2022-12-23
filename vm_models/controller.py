""" Module contains list of models (cache). Provides getting model,
    fitting, predicting and other functions to work with models
        Functions:
            _get_model - for getting model
            fit - for fitting model
            predict - for predicting data with model
            initialize - for initializing new model

"""

from typing import Any, Callable
from functools import wraps

from vm_models.models import base_model, get_model_class
from vm_models.models import get_additional_actions as model_get_actions
from vm_logging.exceptions import ModelException, ParameterNotFoundException
from vm_background_jobs.decorators import execute_in_background
from .model_filters import get_fitting_filter_class


__all__ = ['fit', 'predict', 'initialize', 'drop', 'get_info', 'drop_fitting', 'get_additional_actions']


def _check_input_parameters(func: Callable) -> Callable:
    """
    Decorator for checking input parameters
    :param func: function to decorate
    :return: decorated function
    """
    @wraps(func)
    def wrapper(parameters: dict[str, Any]):

        if not parameters.get('model'):
            raise ParameterNotFoundException('Parameter "model" is not found in request parameters')

        result = func(parameters)
        return result

    return wrapper


def _transform_model_parameters_for_fitting(func: Callable):
    """
    Decorator to transform model parameters
    :param func: function to decorate
    :return: decorated function
    """
    @wraps(func)
    def wrapper(parameters: dict[str, Any]):

        if 'fitting_parameters' not in parameters['model']:
            raise ParameterNotFoundException('Parameter "fitting_parameters" not found in model parameters')

        if 'filter' in parameters['model']['fitting_parameters']:

            input_filter = parameters['model']['fitting_parameters']['filter']
            filter_obj = get_fitting_filter_class()(input_filter)
            parameters['model']['fitting_parameters']['filter'] = filter_obj.get_value_as_model_parameter()

        if 'job_id' in parameters:
            parameters['model']['fitting_parameters']['job_id'] = parameters['job_id']

        result = func(parameters)
        return result

    return wrapper


@_check_input_parameters
@_transform_model_parameters_for_fitting
@execute_in_background
def fit(parameters: dict[str, Any]) -> dict[str, Any]:
    """ For fitting model
    :param parameters: request parameters
    :return: result of fitting
    """
    model = _get_model(parameters['model'])

    if 'fitting_parameters' not in parameters['model']:
        raise ModelException('Can not find fitting parameters in model parameters')

    result = model.fit(parameters['model']['fitting_parameters'])

    return result


@_check_input_parameters
def predict(parameters: dict[str, Any]) -> dict[str, Any]:
    """
    For predicting data using model
    :param parameters: request parameters
    :return: predicted data with description
    """
    if 'inputs' not in parameters:
        raise ParameterNotFoundException('Parameter "inputs" is not in request parameters')

    model = _get_model(parameters['model'])

    result = model.predict(parameters['inputs'])

    return result


@_check_input_parameters
def initialize(parameters: dict[str, Any]) -> dict[str, Any]:
    """ For initializing new model
    :param parameters: request parameters
    :return: result of initializing
    """
    if not parameters.get('model'):
        raise ParameterNotFoundException('Parameter "model" is not found in request parameters')

    if not parameters.get('db'):
        raise ParameterNotFoundException('Parameter "db" is not found in request parameters')

    model = _get_model(parameters['model'])

    result = model.initialize(parameters['model'])

    return result


@_check_input_parameters
def drop(parameters: dict[str, Any]) -> str:
    """ For deleting model from db
    :param parameters: request parameters
    :return: result of dropping
    """

    if not parameters.get('model'):
        raise ParameterNotFoundException('Parameter "model" is not found in request parameters')

    if not parameters.get('db'):
        raise ParameterNotFoundException('Parameter "db" is not found in request parameters')

    model = _get_model(parameters['model'])

    result = model.drop()

    return result


@_check_input_parameters
def get_info(parameters: dict[str, Any]) -> dict[str, Any]:
    """ For getting model info
    :param parameters: request parameters
    :return: model info
    """

    model = _get_model(parameters['model'])

    result = model.get_info()

    return result


def drop_fitting(parameters: dict[str, Any]) -> str:
    """ For deleting fit data from model
    :param parameters: request parameters
    :return: result of dropping
    """
    model = _get_model(parameters['model'])

    result = model.drop_fitting()

    return result


def get_additional_actions() -> dict[str|Callable]:
    """
    Forms dict of additional action from model package
    :return: dict of actions (functions)
    """
    return model_get_actions()


def _get_model(input_model: dict[str, Any]) -> base_model.Model:
    """
    Gets model object from parameters
    :param input_model: model parameters
    :return: required model object
    """
    if not input_model.get('id'):
        raise ModelException('Parameter "id" is not found in model parameters')

    model = get_model_class()(input_model['id'])

    return model
