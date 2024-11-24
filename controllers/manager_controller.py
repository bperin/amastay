import logging
from typing import List
from flask import g, request
from flask_restx import Namespace, Resource, fields
from uuid import UUID

from services.manager_service import ManagerService
from auth_utils import jwt_required

# Create namespace for manager-related routes
ns_manager = Namespace("managers", description="Manager management")

# Define model for manager operations
create_manager_model = ns_manager.model(
    "CreateManager",
    {
        "property_id": fields.String(required=True, description="Property ID"),
        "first_name": fields.String(required=True, description="Manager's first name"),
        "last_name": fields.String(required=True, description="Manager's last name"),
        "email": fields.String(required=True, description="Manager's email"),
        "phone": fields.String(required=False, description="Manager's phone number"),
    },
)


@ns_manager.route("")
class ManagerList(Resource):
    @ns_manager.doc("create_manager")
    @ns_manager.expect(create_manager_model)
    @jwt_required
    def post(self):
        """Create a new manager"""
        try:
            data = request.get_json()
            owner_id = g.user_id

            manager = ManagerService.create_manager(owner_id=owner_id, property_id=UUID(data["property_id"]), first_name=data["first_name"], last_name=data["last_name"], email=data["email"], phone=data.get("phone"))
            return manager.model_dump(), 201
        except Exception as e:
            logging.error(f"Error creating manager: {e}")
            return {"error": str(e)}, 500

    @ns_manager.doc("list_managers")
    def get(self):
        """List all managers for the owner"""
        try:
            owner_id = g.user_id
            managers = ManagerService.get_managers_by_owner(owner_id)
            return [manager.model_dump() for manager in managers], 200
        except Exception as e:
            logging.error(f"Error listing managers: {e}")
            return {"error": str(e)}, 500


@ns_manager.route("/<uuid:manager_id>")
class ManagerResource(Resource):
    @ns_manager.doc("get_manager")
    @jwt_required
    def get(self, manager_id: UUID):
        """Get a specific manager"""
        try:
            manager = ManagerService.get_manager(manager_id)
            if manager:
                return manager.model_dump(), 200
            return {"error": "Manager not found"}, 404
        except Exception as e:
            logging.error(f"Error getting manager: {e}")
            return {"error": str(e)}, 500

    @ns_manager.doc("update_manager")
    @ns_manager.expect(create_manager_model)
    @jwt_required
    def put(self, manager_id: UUID):
        """Update a manager"""
        try:
            data = request.get_json()
            manager = ManagerService.update_manager(manager_id, first_name=data.get("first_name"), last_name=data.get("last_name"), email=data.get("email"), phone=data.get("phone"))
            if manager:
                return manager.model_dump(), 200
            return {"error": "Manager not found"}, 404
        except Exception as e:
            logging.error(f"Error updating manager: {e}")
            return {"error": str(e)}, 500

    @ns_manager.doc("delete_manager")
    @jwt_required
    def delete(self, manager_id: UUID):
        """Delete a manager"""
        try:
            if ManagerService.delete_manager(manager_id):
                return {"message": "Manager deleted successfully"}, 200
            return {"error": "Manager not found"}, 404
        except Exception as e:
            logging.error(f"Error deleting manager: {e}")
            return {"error": str(e)}, 500
