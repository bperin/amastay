from flask_restx import Namespace, Resource, fields

# Define the Namespace
ns_health = Namespace("health", description="Health check endpoint")

# Define the response model
health_model = ns_health.model(
    "Health",
    {
        "status": fields.String(required=True, description="The status of the service"),
        "message": fields.String(
            required=True, description="A message describing the status"
        ),
    },
)


@ns_health.route("/check")
class HealthCheck(Resource):

    @ns_health.doc("health_check")
    @ns_health.marshal_with(health_model)
    def get(self):
        """
        Health check endpoint that returns the status of the service.
        """
        return {"status": "healthy", "message": "Service is running"}, 200
