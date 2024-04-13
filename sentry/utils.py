from urllib.request import urlopen
import base64
import re
import json

# Get address string and returns latitude and longitude
def geocode(location, key):
    address = location.replace(" ", "%20")
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s" % (address, key)
    response = urlopen(url).read()
    data = json.loads(response)
    try:
        lat = data["results"][0]["geometry"]["location"]["lat"]
        lng = data["results"][0]["geometry"]["location"]["lng"]
        return {
            "lat": lat, 
            "lng": lng
        }
    except:
        raise Exception("Couldn't fetch location's latitude and longitude")

# Get base64 encoded image -> Create new file with binary data -> Return image format
def decode64ImgFile(encoded_file):
    # Split header and data from base64 encoded image 
    original = encoded_file.split(",", 1)
    header = re.split("/|;", original[0])

    try:
        base64_to_bytes = original[1].encode("utf-8")
    except IndexError:
        return {
            "img_format": None,
            "data": None  # Add 'data' key with a value of None if no image found
        }

    decoded_data = base64.decodebytes(base64_to_bytes)

    with open(f"img.{header[1]}", "wb") as new_file:
        new_file.write(decoded_data)

    return {
        "img_format": header[1],
        "data": decoded_data  # Include 'data' key with the decoded image data
    }


# Split time input
def formatTime(input):
    time = input.split("-", 2)
    return {
        "year": int(time[0]),
        "month": int(time[1]),
        "day": int(time[2])
    }