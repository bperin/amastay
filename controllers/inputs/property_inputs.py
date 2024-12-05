from flask_restx import fields


def get_property_input_models(ns_property):
    """Define input models for property endpoints"""

    create_property_model = ns_property.model(
        "CreateProperty",
        {
            "name": fields.String(required=True, description="The property name"),
            "address": fields.String(required=True, description="The property address"),
            "description": fields.String(required=False, description="The property description"),
            "property_url": fields.String(required=True, description="The property Url"),
        },
    )

    update_property_model = ns_property.model(
        "UpdateProperty",
        {
            "id": fields.String(required=True, description="The property id"),
            "name": fields.String(required=False, description="The property name"),
            "address": fields.String(required=False, description="The property address"),
            "description": fields.String(required=False, description="The property description"),
            "property_url": fields.String(required=False, description="The property Url"),
            "manager_id": fields.String(required=False, description="The property Url"),
        },
    )

    add_property_info_model = ns_property.model(
        "AddPropertyInformation",
        {
            "property_id": fields.String(required=True, description="Property id"),
            "name": fields.String(required=True, description="Information name"),
            "detail": fields.String(required=True, description="Information detail"),
            "is_recommendation": fields.Boolean(required=True, description="Recommendation"),
            "metadata_url": fields.String(required=False, description="Information metadata url"),
            "category_id": fields.String(required=False, description="Information category_id"),
        },
    )

    update_property_info_model = ns_property.model(
        "UpdatePropertyInformation",
        {
            "id": fields.String(required=True, description="Property information id"),
            "name": fields.String(required=False, description="Information name"),
            "detail": fields.String(required=False, description="Information detail"),
            "is_recommendation": fields.Boolean(required=False, description="Recommendation"),
        },
    )

    return {"create_property_model": create_property_model, "update_property_model": update_property_model, "add_property_info_model": add_property_info_model, "update_property_info_model": update_property_info_model}
