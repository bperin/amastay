from flask_restx import fields
from pydantic import BaseModel
from typing import Type, Dict, Any, get_args, get_origin, Union, List


def pydantic_to_swagger_model(ns, model_name: str, pydantic_model: Type[BaseModel]) -> fields.Raw:
    """
    Converts a Pydantic model to a Flask-RESTx Swagger model
    """

    def convert_field(field_info, field_name):
        # Handle Union types (like Union[List[UserIdentity], None])
        if field_info.get("anyOf") or field_info.get("oneOf"):
            # Get the non-null type
            for type_option in field_info.get("anyOf", []) + field_info.get("oneOf", []):
                if type_option.get("type") != "null":
                    return convert_field(type_option, field_name)

        field_type = field_info.get("type")

        if field_type == "array":
            # Handle arrays (like List[UserIdentity])
            items = field_info["items"]
            if items.get("$ref"):
                # Get the model name from the reference
                ref_model_name = items["$ref"].split("/")[-1]
                # Find the referenced model in definitions
                ref_model = definitions[ref_model_name]
                # Convert the referenced model
                item_model = ns.model(f"{field_name}_item", {k: convert_field(v, k) for k, v in ref_model["properties"].items()})
                return fields.List(fields.Nested(item_model))
            return fields.List(fields.String)

        elif field_type == "object":
            nested_props = field_info.get("properties", {})
            nested_fields = {k: convert_field(v, k) for k, v in nested_props.items()}
            return fields.Nested(ns.model(f"{field_name}_model", nested_fields))

        elif field_type == "string":
            return fields.String
        elif field_type == "boolean":
            return fields.Boolean
        elif field_type == "integer":
            return fields.Integer
        elif field_type == "number":
            return fields.Float

        return fields.String

    # Get the full schema with definitions
    schema = pydantic_model.model_json_schema()
    definitions = schema.get("$defs", {})

    # Convert the main model's properties
    swagger_fields = {field_name: convert_field(field_info, field_name) for field_name, field_info in schema.get("properties", {}).items()}

    return ns.model(model_name, swagger_fields)
