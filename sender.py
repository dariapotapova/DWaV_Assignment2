import csv
import time
import requests

CSV_FILE = 'ip_addresses.csv'              # input data file
URL = 'http://backend:5000/api/package'    # where to send (backend service name in docker)


def send_package(pkg):
    # send one package to backend, return True if successful
    try:
        r = requests.post(URL, json=pkg, timeout=2)
        return r.status_code == 200
    except Exception as e:
        print(f'Error: {e}')
        return False


def main():
    print('Loading CSV...')

    # read all rows from csv file
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f'Found {len(rows)} packages')

    prev_ts = None

    # loop through each package
    for i, row in enumerate(rows):
        ts = int(row['Timestamp'])

        # wait based on timestamp difference from previous package
        if prev_ts is not None:
            wait = ts - prev_ts
            if wait > 0:
                print(f'Waiting {wait} seconds...')
                time.sleep(wait)

        # build package dictionary from csv row
        pkg = {
            'ip': row['ip address'],
            'lat': float(row['Latitude']),
            'lon': float(row['Longitude']),
            'timestamp': ts,
            'suspicious': int(float(row['suspicious']))
        }

        print(f'[{i + 1}/{len(rows)}] Sending {pkg["ip"]}...', end=' ')

        # send and show result
        if send_package(pkg):
            print('OK')
        else:
            print('FAIL (frontend not ready yet)')

        prev_ts = ts

    print('Done')


if __name__ == '__main__':
    main()