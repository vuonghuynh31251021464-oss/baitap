!pip install scikit-fuzzy
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
from geopy.distance import geodesic
import folium
import random
from IPython.display import display

# Install scikit-fuzzy if not already installed
!pip install scikit-fuzzy

# ===== INPUT =====
friendliness = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'friendliness')
privacy = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'privacy')
distance = ctrl.Antecedent(np.arange(0, 20.1, 0.1), 'distance')
base_cost = ctrl.Antecedent(np.arange(0, 100.1, 0.1), 'base_cost')

# ===== OUTPUT =====
vehicle_type = ctrl.Consequent(np.arange(0, 10.1, 0.1), 'vehicle_type')
cost_total = ctrl.Consequent(np.arange(0, 200.1, 0.1), 'cost_total')

# ===== MEMBERSHIP =====
friendliness['low'] = fuzz.trimf(friendliness.universe, [0,0,5])
friendliness['high'] = fuzz.trimf(friendliness.universe, [5,10,10])

privacy['low'] = fuzz.trimf(privacy.universe, [0,0,5])
privacy['high'] = fuzz.trimf(privacy.universe, [5,10,10])

distance['near'] = fuzz.trimf(distance.universe, [0,0,5])
distance['medium'] = fuzz.trimf(distance.universe, [3,10,15])
distance['far'] = fuzz.trimf(distance.universe, [10,20,20])

base_cost['low'] = fuzz.trimf(base_cost.universe, [0,0,50])
base_cost['medium'] = fuzz.trimf(base_cost.universe, [30,60,90])
base_cost['high'] = fuzz.trimf(base_cost.universe, [70,100,100])

vehicle_type['bike'] = fuzz.trimf(vehicle_type.universe, [0,0,4])
vehicle_type['car'] = fuzz.trimf(vehicle_type.universe, [3,5,7])
vehicle_type['premium'] = fuzz.trimf(vehicle_type.universe, [6,10,10])

cost_total['cheap'] = fuzz.trimf(cost_total.universe, [0,0,80])
cost_total['normal'] = fuzz.trimf(cost_total.universe, [60,120,160])
cost_total['expensive'] = fuzz.trimf(cost_total.universe, [140,200,200])

# ===== RULES =====
rules = [
    ctrl.Rule(distance['near'] & base_cost['low'], vehicle_type['bike']),
    ctrl.Rule(distance['far'] & privacy['high'], vehicle_type['car']),
    ctrl.Rule(privacy['high'] & base_cost['high'], vehicle_type['premium']),
    ctrl.Rule(friendliness['high'] & distance['medium'], vehicle_type['car']),
    ctrl.Rule(distance['far'] & base_cost['low'], vehicle_type['car']),

    ctrl.Rule(distance['near'] & base_cost['low'], cost_total['cheap']),
    ctrl.Rule(distance['medium'] & base_cost['medium'], cost_total['normal']),
    ctrl.Rule(distance['far'] | base_cost['high'], cost_total['expensive']),
    ctrl.Rule(privacy['high'] & base_cost['high'], cost_total['expensive']),
    ctrl.Rule(friendliness['high'] & base_cost['medium'], cost_total['normal'])
]

system = ctrl.ControlSystem(rules)

# ===== USER =====
user_location = (10.7769, 106.7009)

# ===== CALCULATE =====

# STEP 1: chọn xe phù hợp với user (fuzzy)
sim_user = ctrl.ControlSystemSimulation(system)

sim_user.input['friendliness'] = random.uniform(3,10)
sim_user.input['privacy'] = random.uniform(3,10)
sim_user.input['distance'] = random.uniform(1,10)
sim_user.input['base_cost'] = random.uniform(20,100)

sim_user.compute()

v_score_user = sim_user.output.get('vehicle_type', 0)

if v_score_user < 4:
    best_vehicle_type = "BIKE 🛵"
elif v_score_user < 7:
    best_vehicle_type = "CAR 🚗"
else:
    best_vehicle_type = "PREMIUM 🚘"

# STEP 2: random driver + random xe
vehicle_list = ["BIKE 🛵", "CAR 🚗", "PREMIUM 🚘"]

results = []

for _ in range(6):
    d = (user_location[0] + random.uniform(-0.01, 0.01),
         user_location[1] + random.uniform(-0.01, 0.01))

    vehicle = random.choice(vehicle_list)

    dist_km = geodesic(user_location, d).km

    results.append((d, vehicle, dist_km))

# ===== BEST =====
filtered = [r for r in results if r[1] == best_vehicle_type]

if not filtered:
    filtered = results
    print("⚠️ Không có đúng loại xe → lấy gần nhất bất kỳ")

best_choice = min(filtered, key=lambda x: x[2])

best_location, best_vehicle, best_distance = best_choice

print("===== KẾT QUẢ =====")
print("Xe phù hợp:", best_vehicle_type)
print("Tài xế gần nhất:", round(best_distance,2), "km")

# ===== MAP =====
m = folium.Map(location=user_location, zoom_start=14)

folium.Marker(user_location, popup="YOU", icon=folium.Icon(color='blue')).add_to(m)

for d, vehicle, dist in results:
    color = "green" if vehicle == best_vehicle_type else "gray"

    folium.Marker(
        d,
        popup=f"{vehicle} | Dist:{round(dist,2)} km",
        icon=folium.Icon(color=color)
    ).add_to(m)

    folium.PolyLine([user_location, d], color=color).add_to(m)

# highlight best
folium.Marker(
    best_location,
    popup=f"⭐ BEST\n{best_vehicle}\nDist:{round(best_distance,2)} km",
    icon=folium.Icon(color='red', icon='star')
).add_to(m)

folium.PolyLine([user_location, best_location], color="red", weight=6).add_to(m)

display(m)
