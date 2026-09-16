from typing import Generic, TypeVar

TResponse = TypeVar("TResponse")
TError = TypeVar("TError")


class Result(Generic[TResponse, TError]):
    response: TResponse
    error: TError
