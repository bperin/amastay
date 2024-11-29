from flask_restx import fields


def get_team_input_models(ns_team):
    """Define input models for team endpoints"""

    create_team_model = ns_team.model(
        "CreateTeam",
        {
            "name": fields.String(required=True, description="Team name"),
            "description": fields.String(required=True, description="Team description"),
        },
    )

    assign_team_to_property_model = ns_team.model(
        "AssignTeamToProperty",
        {
            "team_id": fields.String(required=True, description="Team ID"),
            "property_id": fields.String(required=True, description="Property ID"),
        },
    )

    assign_manager_to_team_model = ns_team.model(
        "AssignManagerToTeam",
        {"team_id": fields.String(required=True, description="Team ID"), "manager_id": fields.String(required=True, description="Manager ID")},
    )

    return {"create_team_model": create_team_model, "assign_team_to_property_model": assign_team_to_property_model, "assign_manager_to_team_model": assign_manager_to_team_model}
