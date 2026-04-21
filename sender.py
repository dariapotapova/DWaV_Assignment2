import csv
import time
import requests

CSV_FILE = 'ip_addresses.csv'  # input data file
URL = 'http://backend:5000/api/package'  # where to send


# send one package, return True if successful
def send_package(pkg):
    try:
        r = requests.post(URL, json=pkg, timeout=2)
        return r.status_code == 200
    except Exception as e:
        print(f'Error: {e}')
        return False


def main():
    print('Loading CSV...')

    # read csv file
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f'Found {len(rows)} packages')

    prev_ts = None

    for i, row in enumerate(rows):
        ts = int(row['Timestamp'])

        # wait according to timestamps in csv
        if prev_ts is not None:
            wait = ts - prev_ts
            if wait > 0:
                print(f'Waiting {wait} seconds...')
                time.sleep(wait)

        # build package from csv row
        pkg = {
            'ip': row['ip address'],
            'lat': float(row['Latitude']),
            'lon': float(row['Longitude']),
            'timestamp': ts,
            'suspicious': int(float(row['suspicious']))
        }

        print(f'[{i + 1}/{len(rows)}] Sending {pkg["ip"]}...', end=' ')

        if send_package(pkg):
            print('OK')
        else:
            print('FAIL')

        prev_ts = ts

    print('Done')


if __name__ == '__main__':
    main()