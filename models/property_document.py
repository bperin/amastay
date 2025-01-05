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
            photo_dict["gc_uri"] = photo_data["gs_uri"]  # Note: using gc_uri to match existing format
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

    def to_text(self) -> str:
        """
        Convert the document into a human-readable text format.
        """
        sections = []

        # Property Header
        sections.append(f"Property ID: {self._id}")
        sections.append(f"\nProperty Name: {self._name}")
        sections.append(f"\nFull Address: {self._address}")
        sections.append(f"\nCoordinates: {self._latitude}, {self._longitude}")
        sections.append(f"\nLatitude: {self._latitude}")
        sections.append(f"\nLongitude: {self._longitude}")

        # Property Information
        if self._property_information:
            sections.append("\nProperty Description")
            sections.append("-" * 19)
            sections.append(f"{self._property_information}\n")

        # Amenities
        if self._amenities:
            sections.append("Amenities")
            sections.append("-" * 9)
            sections.append("\n".join(f"{amenity}" for amenity in self._amenities))
            sections.append("")

        # Reviews
        if self._reviews:
            sections.append("Guest Reviews")
            sections.append("-" * 12)
            sections.append("\n\n".join(f'"{review}"' for review in self._reviews))
            sections.append("")

        # Photos
        if self._photos:
            sections.append("Photos")
            sections.append("-" * 6)
            for photo in self._photos:
                if "description" in photo and "gs_uri" in photo:
                    sections.append(f"• {photo['description']}\nGS URI: {photo['gs_uri']}")

        return "\n".join(sections)
