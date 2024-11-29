from flask_restx import fields
from pydantic import BaseModel
from typing import Type


def pydantic_to_swagger_model(ns, model_name: str, pydantic_model: Type[BaseModel]):
    """
    Converts a Pydantic model to a Flask-RESTx Swagger model without descriptions.

    Args:
        ns: The namespace instance from Flask-RESTx.
        model_name: The name for the Swagger model.
        pydantic_model: The Pydantic model to convert.

    Returns:
        A Swagger model compatible with Flask-RESTx.
    """
    swagger_fields = {}
    for field_name, field_type in pydantic_model.__annotations__.items():
        if field_type == str:
            swagger_fields[field_name] = fields.String
        elif field_type == bool:
            swagger_fields[field_name] = fields.Boolean
        elif field_type == int:
            swagger_fields[field_name] = fields.Integer
        elif field_type == float:
            swagger_fields[field_name] = fields.Float
        elif field_type == dict:
            swagger_fields[field_name] = fields.Raw
        elif "datetime" in str(field_type):
            swagger_fields[field_name] = fields.String
        else:
            swagger_fields[field_name] = fields.String  # Fallback for unknown types

    return ns.model(model_name, swagger_fields)
