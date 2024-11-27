import logging
from typing import List
from flask import g, request
from flask_restx import Namespace, Resource, fields
from uuid import UUID

from services.manager_service import ManagerService
from auth_utils import jwt_required
from models.manager import Manager

# Create namespace for manager-related routes
ns_manager = Namespace("managers", description="Manager operations")

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

# Input models
create_manager_model = ns_manager.model(
    "CreateManager",
    {
        "first_name": fields.String(required=True, description="Manager's first name"),
        "last_name": fields.String(required=True, description="Manager's last name"),
        "email": fields.String(required=True, description="Manager's email"),
        "phone": fields.String(required=False, description="Manager's phone number"),
    },
)

update_manager_model = ns_manager.model(
    "UpdateManager",
    {
        "id": fields.String(required=True, description="Manager ID"),
        "first_name": fields.String(description="Manager's first name"),
        "last_name": fields.String(description="Manager's last name"),
        "email": fields.String(description="Manager's email"),
        "phone": fields.String(description="Manager's phone number"),
    },
)


@ns_manager.route("")
class ManagerList(Resource):
    @ns_manager.doc("create_manager")
    @ns_manager.expect(create_manager_model)
    @ns_manager.response(201, "Manager created", manager_model)
    @ns_manager.response(400, "Validation error")
    @ns_manager.response(500, "Internal server error")
    @jwt_required
    def post(self):
        """Create a new manager"""
        try:
            data = request.get_json()

            data["owner_id"] = g.user_id

            manager = ManagerService.create_manager(data)
            return manager.model_dump(), 201
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            logging.error(f"Error creating manager: {e}")
            return {"error": "Internal server error"}, 500

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
