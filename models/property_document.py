class PropertyDocument:
    """
    A single class that can hold and build all parts of a document
    (including ID, content, property info, reviews, photos, and amenities).
    """

    def __init__(self):
        # Internal fields
        self._id = None
        self._name = None
        self._latitude = None
        self._longitude = None
        self._address = None
        self._property_information = None
        self._reviews = []
        self._photos = []
        self._amenities = []

    def set_id(self, doc_id):
        """Set the unique ID for this document."""
        self._id = doc_id
        return self  # return self to allow chaining

    def set_name(self, name):
        """Set the property name."""
        self._name = name
        return self

    def set_location(self, latitude, longitude):
        """Set the property location coordinates."""
        self._latitude = latitude
        self._longitude = longitude
        return self

    def set_address(self, address):
        """Set the property address."""
        self._address = address
        return self

    def set_content(self, content):
        """Set the primary textual content for this document."""
        self._content = content
        return self

    def set_property_information(self, property_info):
        """Set the property-specific information (e.g., address, description, etc.)."""
        self._property_information = property_info
        return self

    def push_review(self, review_text):
        """Add a single review (string) to the list of reviews."""
        self._reviews.append(review_text)
        return self

    def push_amenity(self, amenity):
        """Add a single amenity to the list of amenities."""
        self._amenities.append(amenity)
        return self

    def push_photo(self, photo_data):
        """
        Add a photo using a dictionary containing photo information.
        Expected keys: 'url', 'gs_uri', 'description' (optional)
        """
        photo_dict = {}
        if "url" in photo_data:
            photo_dict["url"] = photo_data["url"]
        if "gs_uri" in photo_data:
            photo_dict["gs_uri"] = photo_data["gs_uri"]  # Fixed: use gs_uri consistently
        if "description" in photo_data:
            photo_dict["description"] = photo_data["description"]

        self._photos.append(photo_dict)
        return self

    def to_dict(self):
        """
        Convert the final document into a dictionary,
        maintaining the order of fields as they are added in the scraper.
        """
        # Order matches the sequence of operations in scraper_service.py
        return {
            "id": self._id,
            "name": self._name,
            "latitude": self._latitude,
            "longitude": self._longitude,
            "address": self._address,
            "property_information": self._property_information,
            "reviews": self._reviews,
            "amenities": self._amenities,
            "photos": self._photos,
        }

    def to_text(self):
        """
        Convert the document into a searchable text format,
        including all relevant information including photos.
        """
        sections = []

        # Add property name and basic info
        sections.append(f"Property: {self._name}")
        sections.append(f"Location: {self._address}")
        sections.append(f"Coordinates: {self._latitude}, {self._longitude}")

        # Add main property information
        if self._property_information:
            sections.append("\nProperty Information:")
            sections.append(self._property_information)

        # Add amenities
        if self._amenities:
            sections.append("\nAmenities:")
            sections.extend(self._amenities)

        # Add reviews
        if self._reviews:
            sections.append("\nReviews:")
            sections.extend(self._reviews)

        # Add photo descriptions
        if self._photos:
            sections.append("\nPhoto Descriptions:")
            for photo in self._photos:
                if "description" in photo:
                    sections.append(photo["description"])

        # Join all sections with newlines
        return "\n".join(filter(None, sections))
