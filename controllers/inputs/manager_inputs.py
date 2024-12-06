from flask_restx import fields


def get_manager_input_models(ns_manager):
    """Define input models for manager endpoints"""

    manager_invite_model = ns_manager.model(
        "ManagerInvite",
        {
            "first_name": fields.String(required=True, description="Manager's first name"),
            "last_name": fields.String(required=True, description="Manager's last name"),
            "email": fields.String(required=True, description="Manager's email"),
            "phone": fields.String(required=True, description="Manager's phone number"),
            "team_id": fields.String(required=False, description="Team ID to invite manager to"),
        },
    )

    update_manager_model = ns_manager.model(
        "UpdateManager",
        {
            "id": fields.String(required=True, description="Manager ID"),
            "first_name": fields.String(required=False, description="Manager's first name"),
            "last_name": fields.String(required=False, description="Manager's last name"),
            "email": fields.String(required=False, description="Manager's email"),
            "phone": fields.String(required=False, description="Manager's phone number"),
        },
    )

    assign_manager_to_team_model = ns_manager.model(
        "AssignManagerToTeam",
        {"team_id": fields.String(required=True, description="Team ID"), "manager_id": fields.String(required=True, description="Manager ID")},
    )
    assign_manager_to_property = ns_manager.model(
        "AssignManagerToProperty",
        {"property_id": fields.String(required=True, description="Property ID"), "manager_id": fields.String(required=True, description="Manager ID")},
    )

    return {"manager_invite_model": manager_invite_model, "update_manager_model": update_manager_model, "assign_manager_to_team_model": assign_manager_to_team_model, "assign_manager_to_property_model": assign_manager_to_property}
