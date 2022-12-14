""" Module for defining actions of background jobs package

    functions:
        get_actions() returning dict of actions {request_type, action_object}

"""

from typing import Callable, Any
from . import controller
__all__ = ['get_actions']


def get_actions() -> dict[str, Callable]:
    return {'jobs_get_info': _get_jobs_info, 'jobs_delete': _delete_background_job}


def _get_jobs_info(parameters: dict[str, Any]) -> dict[str, Any]:
    """ Returning background jobs info (id, status, start_date, end_date, pid) according to filter """
    return controller.get_jobs_info(parameters)


def _delete_background_job(parameters: dict[str, Any]) -> str:
    """ Removing job line from db"""
    result = controller.delete_background_job(parameters)
    return result
