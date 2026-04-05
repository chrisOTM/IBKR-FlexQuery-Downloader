#!/usr/bin/env python

import argparse
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

REQUEST_VERSION = '3'
XML_VERSION = '3'
INITIAL_WAIT = 5  # Waiting time for first attempt
RETRY = 7  # number of retry before aborting
RETRY_INCREMENT = 10  # amount of wait time increase for each failed attempt


def download_xml(token, report_number, filename='statement.xml'):
    """Request, poll, and download an IBKR Flex Query XML statement."""
    print("Downloading FlexQuery XML-Data...")

    url_values = urllib.parse.urlencode({'t': token, 'q': report_number, 'v': REQUEST_VERSION})
    base_url = 'https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest'
    full_url = base_url + '?' + url_values

    with urllib.request.urlopen(full_url) as xml_request_response:
        xml_reply = ET.fromstring(xml_request_response.read())

    status = xml_reply.findtext('Status')
    print('XML request is {}'.format(status))
    if status != 'Success':
        print('ERROR: XML request is rejected.')
        raise SystemExit(1)

    xml_base_url = xml_reply.findtext('Url')
    reference_code = xml_reply.findtext('ReferenceCode')
    if not xml_base_url or not reference_code:
        print('ERROR: XML request response is missing download details.')
        raise SystemExit(1)

    xml_url_values = urllib.parse.urlencode({'q': reference_code, 't': token, 'v': XML_VERSION})
    xml_full_url = xml_base_url + '?' + xml_url_values

    retry = 0
    while retry < RETRY:
        timer = retry * RETRY_INCREMENT + INITIAL_WAIT
        print('Waiting {} seconds before fetching XML'.format(timer))
        time.sleep(timer)
        with urllib.request.urlopen(xml_full_url) as xml_data:
            xml_result = ET.fromstring(xml_data.read())

        if len(xml_result) > 0 and xml_result[0].tag == 'FlexStatements':
            print('XML download is successful.')
            break

        error_code = xml_result.findtext('ErrorCode')
        error_message = xml_result.findtext('ErrorMessage')
        if error_code == '1019':  # statement generation in process, retry later
            print('XML is not yet ready.')
            retry += 1
            continue

        print('Error Code: {}'.format(error_code))
        print('Error Message: {}'.format(error_message))
        raise SystemExit(1)
    else:
        print('ERROR: XML request retry all failed.')
        raise SystemExit(1)

    tree = ET.ElementTree(xml_result)
    # the response is actually an xml file that you can write directly to a file
    with open(filename, 'wb') as f:
        tree.write(f)
    print("Flexquery XML Download completed!")


def main():
    parser = argparse.ArgumentParser(description='Download an IBKR Flex Query XML statement.')
    parser.add_argument('token', help='IBKR Flex Web Service token')
    parser.add_argument('report_number', help='IBKR Flex Query report number')
    parser.add_argument('filename', nargs='?', default='statement.xml', help='Output XML filename')
    args = parser.parse_args()
    download_xml(args.token, args.report_number, args.filename)


if __name__ == '__main__':
    main()
