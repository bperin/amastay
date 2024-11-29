import logging
from typing import List
from flask import g, request
from flask_restx import Namespace, Resource, fields
from uuid import UUID

from services.manager_service import ManagerService
from auth_utils import jwt_required
from models.manager import Manager
from .inputs.manager_inputs import get_manager_input_models

# Create namespace for manager-related routes
ns_manager = Namespace("managers", description="Manager operations")

# Get input models
manager_input_models = get_manager_input_models(ns_manager)
manager_invite_model = manager_input_models["manager_invite_model"]
update_manager_model = manager_input_models["update_manager_model"]
assign_manager_to_team_model = manager_input_models["assign_manager_to_team_model"]

# Response models
manager_model = ns_manager.model(
    "Manager",
    {
        "id": fields.String(description="Manager ID"),
        "owner_id": fields.String(description="Owner ID"),
        "first_name": fields.String(description="Manager's first name"),
        "last_name": fields.String(description="Manager's last name"),
        "email": fields.String(description="Manager's email"),
        "phone": fields.String(description="Manager's phone number"),
        "created_at": fields.DateTime(description="Creation timestamp"),
        "updated_at": fields.DateTime(description="Last update timestamp"),
    },
)


@ns_manager.route("/invite")
class ManagerInvite(Resource):
    @ns_manager.doc("invite_manager")
    @ns_manager.expect(manager_invite_model)
    @ns_manager.response(200, "Manager invited successfully")
    @ns_manager.response(400, "Invalid request")
    @ns_manager.response(500, "Internal server error")
    @jwt_required
    def post(self):
        """Send invitation to a new manager"""
        try:
            data = request.get_json()
            owner_id = g.user_id

            team_id = data.get("team_id", None)  # Use get() to handle optional team_id
            result = ManagerService.create_manager_invitation(first_name=data["first_name"], last_name=data["last_name"], phone=data["phone"], owner_id=owner_id, email=data["email"], team_id=team_id)
            return result, 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            logging.error(f"Error inviting manager: {e}")
            return {"error": "Internal server error"}, 500


@ns_manager.route("/list")
class ListManagers(Resource):
    @ns_manager.doc("list_managers")
    @ns_manager.response(200, "Success", [manager_model])
    @ns_manager.response(500, "Internal server error")
    @jwt_required
    def get(self):
        """List all managers for the owner"""
        try:
            owner_id = g.user_id
            managers = ManagerService.get_managers_by_owner(owner_id)
            return [manager.model_dump() for manager in managers], 200
        except Exception as e:
            logging.error(f"Error listing managers: {e}")
            return {"error": "Internal server error"}, 500


@ns_manager.route("/<uuid:manager_id>")
@ns_manager.param("manager_id", "Manager identifier")
class ManagerResource(Resource):
    @ns_manager.doc("get_manager")
    @ns_manager.response(200, "Success", manager_model)
    @ns_manager.response(404, "Manager not found")
    @jwt_required
    def get(self, manager_id: UUID):
        """Get a specific manager"""
        try:
            manager = ManagerService.get_manager(manager_id)
            if not manager:
                return {"error": "Manager not found"}, 404
            return manager.model_dump(), 200
        except Exception as e:
            logging.error(f"Error getting manager: {e}")
            return {"error": "Internal server error"}, 500

    @ns_manager.doc("update_manager")
    @ns_manager.expect(update_manager_model)
    @ns_manager.response(200, "Manager updated", manager_model)
    @ns_manager.response(404, "Manager not found")
    @jwt_required
    def put(self):
        """Update a manager"""
        try:
            data = request.get_json()
            manager = ManagerService.update_manager(data)
            if not manager:
                return {"error": "Manager not found"}, 404
            return manager.model_dump(), 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            logging.error(f"Error updating manager: {e}")
            return {"error": "Internal server error"}, 500

    @ns_manager.doc("delete_manager")
    @ns_manager.response(200, "Manager deleted")
    @ns_manager.response(404, "Manager not found")
    @jwt_required
    def delete(self, manager_id: UUID):
        """Delete a manager"""
        try:
            if ManagerService.delete_manager(manager_id):
                return {"message": "Manager deleted successfully"}, 200
            return {"error": "Manager not found"}, 404
        except Exception as e:
            logging.error(f"Error deleting manager: {e}")
            return {"error": "Internal server error"}, 500
