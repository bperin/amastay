from flask_restx import Namespace, Resource, fields
from flask import g, request
from models.property_information import PropertyInformation
from models.team import Team
from models.manager import Manager
from models.to_swagger import pydantic_to_swagger_model
from services.team_service import TeamService
from auth_utils import jwt_required
import logging
from uuid import UUID
from .inputs.team_inputs import get_team_input_models


# Create namespace
ns_team = Namespace("teams", description="Team management operations")

# Get input models
team_input_models = get_team_input_models(ns_team)
create_team_model = team_input_models["create_team_model"]
assign_team_to_property_model = team_input_models["assign_team_to_property_model"]
assign_manager_to_team_model = team_input_models["assign_manager_to_team_model"]

team_response_model = pydantic_to_swagger_model(ns_team, "Team", Team)
manager_response_model = pydantic_to_swagger_model(ns_team, "Manager", Manager)


@ns_team.route("/create")
class CreateTeam(Resource):
    @ns_team.doc("create_team")
    @ns_team.expect(create_team_model)
    @ns_team.response(201, "Success", team_response_model)
    @jwt_required
    def post(self):
        """Create a new team"""
        try:
            data = request.get_json()
            data["owner_id"] = g.user.id

            result = TeamService.create_team(data)
            return result.model_dump(), 201

        except Exception as e:
            logging.error(f"Error in create_team: {e}")
            return {"error": str(e)}, 500


@ns_team.route("/list")
class ListTeams(Resource):
    @ns_team.doc("list_teams")
    @ns_team.response(200, "Success", [team_response_model])
    @jwt_required
    def get(self):
        """Get all teams owned by the current user"""
        try:
            owner_id = g.user.id
            teams = TeamService.get_owner_teams(owner_id)
            return [team.model_dump() for team in teams], 200

        except Exception as e:
            logging.error(f"Error in get_owner_teams: {e}")
            return {"error": str(e)}, 500


@ns_team.route("/assign_property")
class TeamProperty(Resource):

    @ns_team.doc("assign_team_to_property")
    @ns_team.expect(assign_team_to_property_model)
    @ns_team.response(200, "Success")
    @jwt_required
    def post(self):
        """Assign a team to manage a property"""
        try:
            data = request.get_json()
            data["owner_id"] = g.user.id
            result = TeamService.assign_team_to_property(data)
            return result, 200

        except Exception as e:
            logging.error(f"Error in assign_team_to_property: {e}")
            return {"error": str(e)}, 500


@ns_team.route("/<uuid:team_id>/managers")
class TeamManagers(Resource):
    @ns_team.doc("get_team_managers")
    @ns_team.response(200, "Success", [manager_response_model])
    @jwt_required
    def get(self, team_id: UUID):
        """Get all managers of a team"""
        try:
            managers = TeamService.get_team_managers(str(team_id))
            return [manager.model_dump() for manager in managers], 200
        except Exception as e:
            logging.error(f"Error in get_team_managers: {e}")
            return {"error": str(e)}, 500


@ns_team.route("/<uuid:team_id>/properties")
class TeamManagers(Resource):
    @ns_team.doc("get_team_properties")
    @ns_team.response(200, "Success", [manager_response_model])
    @jwt_required
    def get(self, team_id: UUID):
        """Get all properties of a team"""
        try:
            properties = TeamService.get_team_properties(str(team_id))
            return [properties.model_dump() for properties in properties], 200
        except Exception as e:
            logging.error(f"Error in get_team_properties: {e}")
            return {"error": str(e)}, 500


@ns_team.route("/assign_manager")
class AssignManagerToTeam(Resource):
    @ns_team.doc("assign_manager_to_team")
    @ns_team.expect(assign_manager_to_team_model)
    @ns_team.response(200, "Success")
    @jwt_required
    def post(self):
        """Assign a manager to a team"""
        try:
            data = request.get_json()
            data["owner_id"] = g.user.id
            result = TeamService.assign_manager_to_team(data)
            return result, 200
        except Exception as e:
            logging.error(f"Error in assign_manager_to_team: {e}")
            return {"error": str(e)}, 500


@ns_team.route("/<uuid:team_id>/managers/<uuid:manager_id>")
class TeamManager(Resource):
    @ns_team.doc("remove_manager_from_team")
    @ns_team.response(200, "Manager removed successfully")
    @jwt_required
    def delete(self, team_id: UUID, manager_id: UUID):
        """Remove a manager from a team"""
        try:
            data = {"team_id": str(team_id), "manager_id": str(manager_id), "owner_id": g.user.id}
            result = TeamService.remove_manager_from_team(data)
            return result, 200
        except Exception as e:
            logging.error(f"Error in remove_manager_from_team: {e}")
            return {"error": str(e)}, 500
