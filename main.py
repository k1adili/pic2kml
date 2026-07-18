"""
Pic2KML
=======
Scans a folder of photos, reads the GPS coordinates embedded in each
photo's EXIF data, and generates:

  1. One .kml placemark file per geotagged photo (same behaviour as the
     original version), so each photo can be dragged into Google Earth
     on its own.
  2. One combined "all_photos.kml" file containing every geotagged
     photo as a single placemark collection, so the whole folder can be
     opened in Google Earth at once.

Works on Windows, macOS and Linux.

Author: Keyvan Adili (K1)
"""

import argparse
import os
import sys

from k1gpsData import gps_data

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png")

PLACEMARK_STYLES = """\
    <Style id="sh_blu-blank">
      <IconStyle>
        <scale>1.3</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/paddle/P.png</href>
        </Icon>
        <hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>
      </IconStyle>
      <ListStyle>
        <ItemIcon>
          <href>http://maps.google.com/mapfiles/kml/paddle/P-lv.png</href>
        </ItemIcon>
      </ListStyle>
    </Style>
    <Style id="sn_blu-blank">
      <IconStyle>
        <scale>1.1</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/paddle/P.png</href>
        </Icon>
        <hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>
      </IconStyle>
      <ListStyle>
        <ItemIcon>
          <href>http://maps.google.com/mapfiles/kml/paddle/P-lv.png</href>
        </ItemIcon>
      </ListStyle>
    </Style>
    <StyleMap id="msn_blu-blank">
      <Pair>
        <key>normal</key>
        <styleUrl>#sn_blu-blank</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#sh_blu-blank</styleUrl>
      </Pair>
    </StyleMap>
"""


def build_placemark(image_name, latitude, longitude):
    """Return the <Placemark> XML block for a single photo."""
    return f"""    <Placemark>
      <name>{image_name}</name>
      <description><![CDATA[<img style="max-width:500px;" src="{image_name}">{image_name}, Created by K1.Adili]]></description>
      <LookAt>
        <longitude>{longitude}</longitude>
        <latitude>{latitude}</latitude>
        <altitude>0</altitude>
        <heading>7.217522438579517</heading>
        <tilt>0</tilt>
        <range>1000</range>
        <gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>
      </LookAt>
      <styleUrl>#msn_blu-blank</styleUrl>
      <Point>
        <gx:drawOrder>1</gx:drawOrder>
        <coordinates>{longitude},{latitude},0</coordinates>
      </Point>
    </Placemark>
"""


def build_kml(document_name, placemarks_xml):
    """Wrap one or more placemarks in a full KML document."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
  <Document>
    <name>{document_name}</name>
{PLACEMARK_STYLES}{placemarks_xml}  </Document>
</kml>
"""


def choose_folder(cli_folder):
    """Return the folder to scan: from --folder if given, otherwise via
    a GUI folder picker (easygui)."""
    if cli_folder:
        if not os.path.isdir(cli_folder):
            sys.exit(f"Folder not found: {cli_folder}")
        return cli_folder

    try:
        import easygui
    except ImportError:
        sys.exit(
            "No --folder given and easygui is not installed.\n"
            "Install it with: pip install easygui\n"
            "or run again with: python main.py --folder /path/to/photos"
        )

    folder = easygui.diropenbox(title="Select the folder containing your photos")
    if not folder:
        sys.exit("No folder selected. Exiting.")
    return folder


def main():
    parser = argparse.ArgumentParser(
        description="Generate KML placemarks from geotagged photos."
    )
    parser.add_argument(
        "--folder",
        help="Path to the folder containing photos. "
        "If omitted, a folder-picker window will open.",
    )
    parser.add_argument(
        "--no-individual",
        action="store_true",
        help="Skip creating a separate .kml file for each photo; "
        "only create the combined all_photos.kml.",
    )
    args = parser.parse_args()

    folder_path = choose_folder(args.folder)

    image_files = sorted(
        f
        for f in os.listdir(folder_path)
        if f.lower().endswith(SUPPORTED_EXTENSIONS)
    )

    if not image_files:
        sys.exit(f"No .jpg/.jpeg/.png files found in: {folder_path}")

    combined_placemarks = []
    created_count = 0
    skipped_count = 0

    for image_name in image_files:
        image_path = os.path.join(folder_path, image_name)

        try:
            coordinates = gps_data(image_path)
        except Exception as error:  # corrupted/unsupported file, etc.
            print(f"[skip] {image_name}: could not read EXIF data ({error})")
            skipped_count += 1
            continue

        if coordinates is None:
            print(f"[skip] {image_name}: no GPS data in EXIF")
            skipped_count += 1
            continue

        latitude, longitude = coordinates
        print(f"[ok]   {image_name}: latitude={latitude}, longitude={longitude}")

        placemark_xml = build_placemark(image_name, latitude, longitude)
        combined_placemarks.append(placemark_xml)

        if not args.no_individual:
            kml_name = os.path.splitext(image_name)[0] + ".kml"
            kml_path = os.path.join(folder_path, kml_name)
            with open(kml_path, "w", encoding="utf-8") as kml_file:
                kml_file.write(build_kml(kml_name, placemark_xml))
            created_count += 1

    if combined_placemarks:
        combined_kml_path = os.path.join(folder_path, "all_photos.kml")
        with open(combined_kml_path, "w", encoding="utf-8") as kml_file:
            kml_file.write(build_kml("all_photos.kml", "".join(combined_placemarks)))
        print(f"\nCombined file created: {combined_kml_path}")

    print(
        f"\nDone. {len(combined_placemarks)} photo(s) geotagged, "
        f"{skipped_count} skipped"
        + (f", {created_count} individual .kml file(s) created." if created_count else ".")
    )


if __name__ == "__main__":
    main()
