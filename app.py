from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

packages = []  # store all received packages
is_active = False  # backend starts disabled, enabled when frontend connects


# endpoint where sender posts packages
@app.route('/api/package', methods=['POST'])
def add_package():
    global is_active

    # only accept packages if frontend has connected
    if not is_active:
        print('Rejected: frontend not connected yet')
        return {'status': 'rejected', 'reason': 'frontend not ready'}, 403

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
    print(f'Total packages in storage: {len(packages)}')
    return {'status': 'ok'}, 200


# frontend fetches points from here
@app.route('/api/points', methods=['GET'])
def get_points():
    global is_active

    # enable backend when frontend first requests data
    if not is_active:
        is_active = True
        print('Frontend connected. Backend now accepting packages.')

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
        'packages_received': len(packages),
        'is_active': is_active
    }, 200


if __name__ == '__main__':
    print('Server on http://localhost:5000')
    print('Backend disabled. Waiting for frontend to connect...')
    app.run(host='0.0.0.0', port=5000, debug=True)