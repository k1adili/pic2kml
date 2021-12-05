import easygui
import os
from k1gpsData import gps_data

folder_path = easygui.diropenbox()
list_all_file_inDir = os.listdir(folder_path)

for file in list_all_file_inDir:
    try:
        extention = file.split('.')[-1]
        if extention.lower() == 'jpg' or extention.lower() == 'png' or extention.lower() == 'jpeg':
            imagePath = folder_path + '\\' + file
            imagename = imagePath.split('\\')[-1]

            latitude_longitude = gps_data(imagePath)

            print(latitude_longitude)

            kml_name = imagename

            latitude = latitude_longitude[0]
            longitude = latitude_longitude[1]

            print('latitude= ', latitude)
            print('longitude= ', longitude)

            kml_text = f"""<?xml version="1.0" encoding="UTF-8"?>
                            <kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
                            <Document>
                                <name>{kml_name}.kml</name>
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
                                <Placemark>
                                    <name> </name>
                                    <description><![CDATA[<img style="max-width:500px;" src="{imagename}">{imagename}, Created by K1.Adili]]></description>
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
                            </Document>
                            </kml>
                            """

            f = open(folder_path + '\\' + kml_name + '.kml', 'w')
            f.write(kml_text)
            f.close()
            print(kml_name + '.kml created')
    except:
        print('-')
