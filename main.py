import json
import requests
from geopy.geocoders import Nominatim
from neighborhood import Neighborhood
from shapely.geometry import Point, Polygon
from pyproj import Proj, Transformer, transform

neighborhoodList = []
address = "1300 SE Stark Street, Portland, OR 97214"

def load_neighborhood_set(api_url):
    response = requests.get(api_url)

    # Parse the JSON data
    json_data = response.json()

    # Extract names of the features
    feature_names = [feature['attributes']['NAME'] for feature in json_data['features']]
    feature_polygon = [feature['geometry']['rings'] for feature in json_data['features']]

    for feature in json_data['features']:
        neighborhoodName = feature['attributes']['NAME']
        neighborhoodPolygon = feature['geometry']['rings'][0]

        neighborhood = Neighborhood(neighborhoodName, neighborhoodPolygon)
        neighborhoodList.append(neighborhood)


def latlon_to_web_mercator(latitude, longitude):
    # Create a transformer from WGS84 (standard lat/long) to Web Mercator (EPSG:4326 to EPSG:3857)
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
    
    # Convert latitude and longitude to Web Mercator coordinates
    mercator_x, mercator_y = transformer.transform(longitude, latitude)

    return mercator_x, mercator_y  # Return Web Mercator coordinates


def get_neighborhood(location, neighborhoodList):
    for neighborhood in neighborhoodList:
        polygon = Polygon(neighborhood.polygon)
        point = Point(latlon_to_web_mercator(location.latitude, location.longitude))

        is_inside = point.within(polygon)

        if is_inside:
            return neighborhood.name

    return "Neighborhood not found"


def get_location(address):
    geolocator = Nominatim(user_agent="marteze2015@gmail.com")
    return geolocator.geocode(address)


def recursive_neighborhood_get(address, current_neighborhood):
    location = get_location(address)
    neighborhood = get_neighborhood(location, neighborhoodList)

    print(f"Address: {address}, Neighborhood: {neighborhood}")

    # Check if the neighborhood has changed
    if neighborhood == current_neighborhood:
        address_parts = address.split()
        address_number = int(address_parts[0])
        address_parts[0] = str(address_number + 100)
        new_address = ' '.join(address_parts)

        recursive_neighborhood_get(new_address, current_neighborhood)
    else:
        print(f"Address with a different neighborhood: {address}, Neighborhood: {neighborhood}")



#########

location = get_location(address)

print("Dirección: " + location.address)
print("Coordenadas: " + "(" + str(location.latitude) + ", " + str(location.longitude) + ")")

load_neighborhood_set("https://www.portlandmaps.com/arcgis/rest/services/Public/COP_OpenData/MapServer/125/query?where=1%3D1&text=&objectIds=&time=&timeRelation=esriTimeRelationOverlaps&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot&relationParam=&outFields=&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&havingClause=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset=&resultRecordCount=&returnExtentOnly=false&sqlFormat=none&datumTransformation=&parameterValues=&rangeValues=&quantizationParameters=&featureEncoding=esriDefault&f=pjson")

neighborhood = get_neighborhood(location, neighborhoodList)

print("la dirección se encuentra en el neighborhood de " + neighborhood)

print("")
print("Funcion recursiva...")

recursive_neighborhood_get(address, neighborhood)


