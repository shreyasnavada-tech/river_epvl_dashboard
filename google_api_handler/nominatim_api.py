"""This file for accessing Nominatim APIs using py"""

from typing import Optional

from geopy.distance import geodesic
from httpx import Client, Response

# DOC: https://nominatim.org/release-docs/develop/api/Overview/

# Sample structured query. Not yet supported.
struct_query = {
    "amenity": "name",
    "street": "housenumber and streetname",
    "city": "city",
    "county": "county",
    "state": "state",
    "country": "country",
    "postalcode": "postal code",
}


class NominatimAPI:
    """
    This is class to access Nominatim APIs by initializing a http client and Nominatim endpoint.
    """

    def __init__(self, client: Client, endpoint: str, mail_id: Optional[str] = None):
        self.endpoint = endpoint
        self.client = client
        self.mail_id = mail_id or "nagendrar@rideriver.com"

    def fetch__data_from_coords(
        self,
        lattitude: float | int,
        longitude: float | int,
        format: str = "json",
    ) -> Response:
        """
        This method is used to fetch the full address for a given lat lon pair.
        Sample response - {'place_id': 8304876, 'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright', 'osm_type': 'way', 'osm_id': 737164080, 'lat': '12.980659264392552', 'lon': '77.71456402495784', 'class': 'highway', 'type': 'residential', 'place_rank': 26, 'importance': 0.0533433333333333, 'addresstype': 'road', 'name': '', 'display_name': 'Sitaramapalya, EPIP Zone, Bengaluru East City Corporation, Bengaluru, Bangalore East, Bengaluru Urban, Karnataka, 560048, India', 'address': {'quarter': 'Sitaramapalya', 'suburb': 'EPIP Zone', 'city_district': 'Bengaluru East City Corporation', 'city': 'Bengaluru', 'county': 'Bangalore East', 'state_district': 'Bengaluru Urban', 'state': 'Karnataka', 'ISO3166-2-lvl4': 'IN-KA', 'postcode': '560048', 'country': 'India', 'country_code': 'in'}, 'boundingbox': ['12.9801772', '12.9814141', '77.7144566', '77.7147196']}
        """
        request = (
            self.endpoint
            + "/reverse?lat="
            + str(lattitude)
            + "&lon="
            + str(longitude)
            + "&format="
            + format
            + "&email="
            + self.mail_id
        )
        return self.client.get(request)

    def fetch_nominatim_status(self, format: str = "json") -> Response:
        """
        This method is used to fetch the status of Nominatim server. A status of 0 and messgae of `OK` signifies that the server is up and running.
        Sample response - {'status': 0, 'message': 'OK', 'data_updated': '2025-09-11T20:15:16+00:00', 'software_version': '5.1.0', 'database_version': '5.1.0-0'}
        """
        request = self.endpoint + "/status?format=" + format + "&email=" + self.mail_id
        return self.client.get(request)

    def fetch_description_for_given_location(
        self, query_type: str, query: str, format: str = "json"
    ) -> Response:
        """
        This methods supports freeform of query. Query type is "freeform" or "structured"
        Sample response - [{'place_id': 8201269, 'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright', 'osm_type': 'node', 'osm_id': 1384732673, 'lat': '12.9829217', 'lon': '77.7617553', 'class': 'highway', 'type': 'bus_stop', 'place_rank': 30, 'importance': 9.99999999995449e-06, 'addresstype': 'highway', 'name': 'MVJ College', 'display_name': 'MVJ College, Channasandra Main Road, AKG Colony, Bengaluru East City Corporation, Bengaluru, Bangalore East, Bengaluru Urban, Karnataka, 560067, India', 'boundingbox': ['12.9828717', '12.9829717', '77.7617053', '77.7618053']}]
        """
        if query_type == "freeform":
            request = (
                self.endpoint
                + "/search?q="
                + query
                + "&format="
                + format
                + "&email="
                + self.mail_id
            )
            return self.client.get(request)
        return NotImplementedError("Structured queries is not supported")


def calc_dist_between_coords(src_coords: tuple, dest_coords: tuple) -> float:
    """This method returns the displacement between 2 sets of coordinates"""
    return geodesic(src_coords, dest_coords).km


if __name__ == "__main__":
    endpoint = "http://192.168.10.17:8080"
    client = Client()
    na = NominatimAPI(client, endpoint)
    print(na.fetch__data_from_coords(12.980682, 77.714462).json())
    print(na.fetch_nominatim_status().json())
    print(
        na.fetch_description_for_given_location(
            "freeform", "channasandra+college"
        ).json()
    )
    print(calc_dist_between_coords((1, 2), (2, 4)))
