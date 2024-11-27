from flask_restx import Namespace, Resource, fields
from services.user_service import UserService
from auth_utils import jwt_required

ns_user = Namespace("users", description="User operations")

# Response Models
user_profile_model = ns_user.model("UserProfile", {"id": fields.String(description="User ID"), "email": fields.String(description="User email"), "phone": fields.String(description="User phone number", required=False), "metadata": fields.Raw(description="User metadata containing first and last name")})

# Request Models
profile_update_model = ns_user.model("ProfileUpdate", {"first_name": fields.String(required=True, description="User first name"), "last_name": fields.String(required=True, description="User last name")})

phone_update_model = ns_user.model("PhoneUpdate", {"phone_number": fields.String(required=True, description="User phone number")})


@ns_user.route("/profile")
class UserProfile(Resource):
    @ns_user.doc("get_profile")
    @ns_user.marshal_with(user_profile_model)
    @jwt_required
    def get(self, current_user):
        """Get user profile information"""
        return UserService.get_user_profile(current_user.id)

    @ns_user.doc("update_profile")
    @ns_user.expect(profile_update_model)
    @jwt_required
    def put(self, current_user):
        """Update user profile information"""
        return UserService.update_user_profile(current_user.id, ns_user.payload)


@ns_user.route("/phone")
class UserPhone(Resource):
    @ns_user.doc("add_phone")
    @ns_user.expect(phone_update_model)
    @jwt_required
    def post(self, current_user):
        """Add or update phone number"""
        if not ns_user.payload.get("phone_number"):
            return {"error": "Phone number is required"}, 400
        return UserService.add_phone_number(current_user.id, ns_user.payload["phone_number"])
