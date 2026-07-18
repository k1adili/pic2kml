"""
k1gpsData.py

Utility functions for extracting GPS coordinates from an image's EXIF
metadata using Pillow. Works with any Pillow-supported format that can
carry EXIF data (JPEG, PNG with EXIF, TIFF, ...).

Author: Keyvan Adili (K1)
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def _get_exif_data(image_path):
    """Return a dict of decoded EXIF tags for an image, or None if the
    image has no EXIF data at all."""
    with Image.open(image_path) as image:
        exif_raw = image.getexif()

    if not exif_raw:
        return None

    exif_data = {}
    for tag_id, value in exif_raw.items():
        tag_name = TAGS.get(tag_id, tag_id)

        if tag_name == "GPSInfo":
            gps_data_raw = exif_raw.get_ifd(tag_id)
            gps_data_decoded = {}
            for gps_tag_id, gps_value in gps_data_raw.items():
                gps_tag_name = GPSTAGS.get(gps_tag_id, gps_tag_id)
                gps_data_decoded[gps_tag_name] = gps_value
            exif_data[tag_name] = gps_data_decoded
        else:
            exif_data[tag_name] = value

    return exif_data


def _dms_to_decimal(dms, reference):
    """Convert an EXIF (degrees, minutes, seconds) tuple into decimal
    degrees. `reference` is one of 'N', 'S', 'E', 'W'."""
    degrees, minutes, seconds = dms
    decimal = float(degrees) + float(minutes) / 60.0 + float(seconds) / 3600.0

    if reference in ("S", "W"):
        decimal = -decimal

    return decimal


def gps_data(image_path):
    """
    Extract (latitude, longitude) in decimal degrees from an image's
    EXIF GPS metadata.

    Returns:
        tuple(float, float): (latitude, longitude) if GPS data is present.
        None: if the image has no usable GPS metadata.

    Raises:
        Any exception Pillow raises while opening a corrupted/unsupported
        file is propagated to the caller.
    """
    exif = _get_exif_data(image_path)
    if not exif or "GPSInfo" not in exif:
        return None

    gps_info = exif["GPSInfo"]
    required_keys = (
        "GPSLatitude",
        "GPSLatitudeRef",
        "GPSLongitude",
        "GPSLongitudeRef",
    )
    if not all(key in gps_info for key in required_keys):
        return None

    latitude = _dms_to_decimal(gps_info["GPSLatitude"], gps_info["GPSLatitudeRef"])
    longitude = _dms_to_decimal(gps_info["GPSLongitude"], gps_info["GPSLongitudeRef"])

    return latitude, longitude
