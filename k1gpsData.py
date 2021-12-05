from PIL import Image
from PIL.ExifTags import GPSTAGS
from PIL.ExifTags import TAGS


def get_exif_data(image_path):
    try:
        image = Image.open(image_path)
        exif_data = {}
        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_data[sub_decoded] = value[t]
                    exif_data[decoded] = gps_data
                else:
                    exif_data[decoded] = value
        return gps_data
    except:
        pass


def gps_data(image_path):
    try:
        exif_data = get_exif_data(image_path)

        GPSLatitude = (str(exif_data['GPSLatitude']).replace('(', '').replace(')', '').replace(' ', '')).split(',')
        GPSLongitude = (str(exif_data['GPSLongitude']).replace('(', '').replace(')', '').replace(' ', '')).split(',')

        lat_deg = float(GPSLatitude[0])
        lat_min = float(GPSLatitude[1])
        lat_sec = float(GPSLatitude[2])
        latitude = lat_deg + (lat_min / 60) + (lat_sec / 3600)

        lon_deg = float(GPSLongitude[0])
        lon_min = float(GPSLongitude[1])
        lon_sec = float(GPSLongitude[2])
        longitude = lon_deg + (lon_min / 60) + (lon_sec / 3600)

        return latitude, longitude
    except:
        pass


if __name__ == '__main__':
    gps_data()
