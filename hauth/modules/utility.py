"""HAuth utility functions."""
import typing

from ..models import ReqLogin, ReqMMTResult, ReqEmailVerification


__all__ = ["request_data_to_model"]


def request_data_to_model(data: typing.Union[None, dict]) -> typing.Union[None, ReqLogin, ReqMMTResult, ReqEmailVerification]:
    """Convert request data to model."""
    if data is None:
        return data
    elif "account" in data:
        return ReqLogin(**data)
    elif "mmt_result" in data:
        return ReqMMTResult(**data)
    elif "code" in data:
        return ReqEmailVerification(**data)
    else:
        raise ValueError("Invalid request data.")
