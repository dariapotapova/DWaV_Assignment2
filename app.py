from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)

packages = []  # store received packages here
is_active = True  # whether server still accepts new packages
start_time = None  # timestamp of first package


# stop accepting packages 10 seconds after first one arrives
def stop_after_10_seconds():
    global is_active
    time.sleep(10)
    is_active = False
    print('10 seconds passed. No longer accepting new packages.')


# endpoint where sender posts packages
@app.route('/api/package', methods=['POST'])
def add_package():
    global is_active, start_time

    # start the 10 second timer on first package
    if start_time is None:
        start_time = datetime.now()
        thread = threading.Thread(target=stop_after_10_seconds)
        thread.daemon = True
        thread.start()
        print('Started accepting packages. Will stop after 10 seconds.')

    # reject packages after time limit
    if not is_active:
        print('Rejected: Server is no longer accepting packages (10 seconds passed)')
        return {'status': 'rejected', 'reason': 'time limit exceeded'}, 403

    data = request.get_json()

    pkg = {
        'ip': data['ip'],
        'lat': float(data['lat']),
        'lon': float(data['lon']),
        'timestamp': data['timestamp'],
        'suspicious': bool(data['suspicious'])
    }
    packages.append(pkg)

    print(f'Added: {pkg["ip"]} at ({pkg["lat"]}, {pkg["lon"]}) suspicious={pkg["suspicious"]}')
    print(f'Total packages: {len(packages)}')
    return {'status': 'ok'}, 200


# frontend fetches points from here
@app.route('/api/points', methods=['GET'])
def get_points():
    points = []
    for p in packages:
        points.append({
            'lat': p['lat'],
            'lng': p['lon'],
            'ip': p['ip'],
            'suspicious': p['suspicious']
        })
    return {'points': points}, 200


# stats for dashboard
@app.route('/api/stats', methods=['GET'])
def get_stats():
    normal = 0
    suspicious = 0
    ip_counts = {}

    for p in packages:
        if p['suspicious']:
            suspicious += 1
        else:
            normal += 1
        ip_counts[p['ip']] = ip_counts.get(p['ip'], 0) + 1

    top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        'normal': normal,
        'suspicious': suspicious,
        'total': len(packages),
        'active_ips': len(ip_counts),
        'top_ips': [{'ip': ip, 'count': c} for ip, c in top_ips],
        'is_active': is_active
    }, 200


# health check endpoint
@app.route('/api/status', methods=['GET'])
def get_status():
    return {
        'is_active': is_active,
        'packages_received': len(packages),
        'time_elapsed': (datetime.now() - start_time).seconds if start_time else 0
    }, 200


if __name__ == '__main__':
    print('Server on http://localhost:5000')
    print('Will accept packages for 10 seconds only')
    app.run(host='0.0.0.0', port=5000, debug=True)