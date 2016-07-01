import os
import csv
import requests

#####################################################
# JSS Asset Tag importer - v.3
# Import Asset tags from a csv into your Casper JSS
# Authored by Brad Schmidt @bradschm on 12/29/2015
#####################################################

#####################################################
# DISCLAIMER
# I am not providing any kind of warranty. This has been thoroughly tested in
# my environments but I cannot guarantee that this script is not without bugs.
# Thank you
#####################################################

#####################################################
# LICENSE
# The MIT License (MIT)
#
# Copyright (c) 2015 Brad Schmidt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#####################################################

#####################################################
# TODO
# Add more logging (Actual logging instead of print)
# Add gui? Prompt for values and file location
# Once bug in the API for large advanced searches is fixes, switch to advanced
# searches from smart groups.
#####################################################

#####################################################
# HOW TO USE
# 1. Make an API user and give it the rights specified BELOW
# 2. Save a csv file of your serial numbers and asset tags. Format is assettag,
# serialnumber. In other words, the first column is the asset tag and the
# second is the serialnumber.
# 3. Run the python script - be patient, this could take a while. Creating the
# groups can take a long time in large environments. Touching each record
# isn't blazing fast either but I did put in a progress counter ;)
# 4. Profit?
#####################################################

#####################################################
# HARD CODED VALUES

# JSS URL
JSS_HOST = "http://127.0.0.1"
JSS_PORT = "8080"
JSS_PATH = ""  # Example: "jss" for a JSS at https://www.company.com:8443/jss

# API User needs the following rights:
# 1. Create/Read Computer Smart Groups
# 2. Create/Read Mobile Device Smart Groups
# 3. Update Computer records
# 4. Update Mobile Device records

# JSS API Username and Password
JSS_USERNAME = "api_user"
JSS_PASSWORD = "potato"

# Place the csv in the same directory as the script.
CSV_FILE_NAME = 'filename.csv'

# Turn on or off device types False turns it off, True turns it on.
COMPUTERSMODE = True
# COMPUTERSMODE = False
MOBILEDEVICESMODE = True
# MOBILEDEVICESMODE = False

#####################################################
# You should not need to edit below this line #
#####################################################


def _mobile_devices():
    """Starts the mobile device process"""
    if MOBILEDEVICESMODE:
        print "---Starting the Mobile Device pass---"
        mobiledevices, status_code = get_mobile_devices()
        if mobiledevices is not None:
            if len(mobiledevices) != 0:
                if status_code == 200:
                    print "Got some mobile devices back!"

                mobiledevicestotal = len(mobiledevices)
                counter = 0
                for device in mobiledevices:
                    serialnumber = device.get("serial_number")
                    assettag = asset_lookup(serialnumber)
                    update_mobile_device_inventory(serialnumber, assettag)
                    counter += 1
                    print "Submitting %s of %s devices" % (counter, mobiledevicestotal)
                print "---Finished importing asset tags for Mobile Devices---"
            else:
                print "No Mobile Devices Found"
        else:
            print "Creating Mobile Device Group"
            create_mobiledevice_group()
    else:
        print "Mobile Device Mode: Off"


def _computers():
    """Start the computer process"""
    if COMPUTERSMODE:
        print "---Starting the Computer pass---"
        computers, status_code = get_computers()
        if computers is not None:
            if len(computers) != 0:
                if status_code == 200:
                    print "Got some computers back!"

                computerstotal = len(computers)
                counter = 0
                for computer in computers:
                    serialnumber = computer.get("serial_number")
                    assettag = asset_lookup(serialnumber)
                    update_computer_inventory(serialnumber, assettag)
                    counter += 1
                    print "Submitting %s of %s devices" % (counter, computerstotal)
                print "---Finished importing asset tags for Computers---"
            else:
                print "No Computers Found"
        else:
            print "Creating the Computer Group"
            create_computer_group()

    else:
        print "Computer Mode: off"


def create_computer_group():
    """Creates the computer group
    :rtype: object
    """
    print "Stand by, creating the Smart Group and this does take a while in larger environments..."
    body = ('<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
            '<computer_group><name>_API-Asset-Tag-Importer</name>'
            '<is_smart>true</is_smart><criteria><size>1</size><criterion>'
            '<name>Asset Tag</name><priority>0</priority><and_or>and</and_or>'
            '<search_type>is</search_type><value></value></criterion></criteria>'
            '<computers/></computer_group>')
    request = requests.post(JSS_HOST + ':' + str(JSS_PORT) + JSS_PATH +
                            '/JSSResource/computergroups/id/-1',
                            auth=(JSS_USERNAME, JSS_PASSWORD), data=body)
    if request.status_code == 201:
        print "Group created! Status code: %s " % request.status_code
        _computers()
    else:
        print "Something went wrong. Status code: %s " % request.status_code
        print request.text


def create_mobiledevice_group():
    """Create the mobile device group if it doesn't exist"""
    print ("Stand by, creating the Smart Group and this does take a "
           "while in larger environments...")
    body = ("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>"
            "<mobile_device_group><name>_API-Asset-Tag-Importer</name>"
            "<is_smart>true</is_smart><criteria><size>1</size><criterion>"
            "<name>Asset Tag</name><priority>0</priority><and_or>and</and_or>"
            "<search_type>is</search_type><value></value></criterion></criteria>"
            "<mobile_devices/></mobile_device_group>")
    request = requests.post('{0}:{1}{2}/JSSResource/mobiledevicegroups/id/-1'.format(
        JSS_HOST, str(JSS_PORT), JSS_PATH),
                            auth=(JSS_USERNAME, JSS_PASSWORD), data=body)
    if request.status_code == 201:
        print "Group created!. Status code: %s " % request.status_code
        # Jump back to the main program for mobile devices
        _mobile_devices()
    else:
        print "Something went wrong. Status code: %s " % request.status_code
        print request.text



def get_mobile_devices():
    """
    Attempts to get the mobile devices without asset tags
    :rtype: object
    """
    request = requests.get(
        JSS_HOST + ':' + str(JSS_PORT) + JSS_PATH
        + '/JSSResource/mobiledevicegroups/name/_API-Asset-Tag-Importer',
        headers={'Accept': 'application/json'}, auth=(JSS_USERNAME, JSS_PASSWORD))
    try:
        report_data = request.json()["mobile_device_group"]
        return report_data["mobile_devices"], request.status_code
    except:
        report_data = None
        return report_data, request.status_code


def get_computers():
    """Attempt to get the computers without asset tags"""
    request = requests.get(
        JSS_HOST + ':' + str(JSS_PORT) + JSS_PATH
        + '/JSSResource/computergroups/name/_API-Asset-Tag-Importer',
        headers={'Accept': 'application/json'}, auth=(JSS_USERNAME, JSS_PASSWORD))
    try:
        report_data = request.json()["computer_group"]
        return report_data["computers"], request.status_code
    except:
        report_data = None
        return report_data, request.status_code


def asset_lookup(serial):
    """Lookup and try to find the asset tag"""
    csv_file = os.path.join(os.path.dirname(__file__), CSV_FILE_NAME)
    filename = open(csv_file)
    filereader = csv.reader(filename)
    for row in filereader:
        try:
            if row[1] == serial:
                asset = row[0]
                # strip dashs for my environment
                asset_tag = (asset.translate(None, "-"))
                return asset_tag
        except:
            continue


def update_mobile_device_inventory(serialnumber, assettag):
    """Submits the new asset tag to the JSS"""
    if assettag is not None:

        print "\tSubmitting command to update device " + serialnumber + "..."
        try:
            body = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>" \
                   "<mobile_device><general><asset_tag>%s</asset_tag></general>" \
                   "</mobile_device>" % assettag
            requests.put(
                JSS_HOST + ':' + JSS_PORT + JSS_PATH +
                '/JSSResource/mobiledevices/serialnumber/' + serialnumber,
                auth=(JSS_USERNAME, JSS_PASSWORD), data=body)
            # print r.text
            print ""
        except requests.exceptions.HTTPError as error:
            print "\t%s" % error
    else:
        print "Skipping Serial Number: %s...Not found in csv" % serialnumber


def update_computer_inventory(serialnumber, assettag):
    """Submits the new asset tag to the JSS"""
    if assettag is not None:

        print "\tSubmitting command to update device " + serialnumber + "..."
        try:
            body = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>" \
                   "<computer><general><asset_tag>%s</asset_tag></general>" \
                   "</computer>" % assettag
            requests.put(
                JSS_HOST + ':' + JSS_PORT + JSS_PATH +
                '/JSSResource/computers/serialnumber/' + serialnumber,
                auth=(JSS_USERNAME, JSS_PASSWORD), data=body)

        except requests.exceptions.HTTPError as error:
            print "\t%s" % error
    else:
        print u'Skipping Serial Number: {0:s}...' \
              u'Not found in csv'.format(serialnumber)


if __name__ == '__main__':
    _computers()
    _mobile_devices()
