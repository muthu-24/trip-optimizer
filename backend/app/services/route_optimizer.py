import math
from typing import List, Dict, Any, Tuple
from itertools import permutations

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) using Haversine formula.
    Returns distance in kilometers.
    """
    if None in (lat1, lon1, lat2, lon2):
        return 0.0

    # Convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def estimate_transit_minutes(distance_km: float, avg_speed_kmh: float = 35.0) -> int:
    """Estimate road transit time in minutes.
    Uses 35 km/h average for Sri Lankan roads (mixed terrain, local roads).
    This is an application-level estimate, not live traffic data."""
    if distance_km <= 0:
        return 0
    minutes = int(round((distance_km / avg_speed_kmh) * 60))
    return max(3, minutes)

def optimize_route(activities: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], float, str]:
    """
    Optimize the route for a list of activities.
    Returns the ordered list of activities, total distance, and the optimization method used.
    Activities missing coordinates are kept at the end.
    """
    if not activities:
        return [], 0.0, "none"
        
    valid_coords = []
    missing_coords = []
    
    for activity in activities:
        lat = activity.get("latitude")
        lon = activity.get("longitude")
        if lat is not None and lon is not None:
            valid_coords.append(activity)
        else:
            missing_coords.append(activity)
            
    if not valid_coords:
        return activities, 0.0, "none"

    n_valid = len(valid_coords)
    ordered = []
    total_distance = 0.0
    method = "none"

    if n_valid <= 5:
        method = "exact"
        best_dist = float('inf')
        best_perm = None
        
        for p in permutations(valid_coords):
            d = 0.0
            for i in range(len(p) - 1):
                d += calculate_distance(
                    p[i]["latitude"], p[i]["longitude"],
                    p[i+1]["latitude"], p[i+1]["longitude"]
                )
            if d < best_dist:
                best_dist = d
                best_perm = p
                
        ordered = list(best_perm) # type: ignore
        total_distance = best_dist
    else:
        method = "heuristic"
        # Nearest neighbor
        ordered = [valid_coords.pop(0)]
        
        while valid_coords:
            current = ordered[-1]
            nearest_idx = 0
            min_distance = float('inf')
            
            for i, candidate in enumerate(valid_coords):
                dist = calculate_distance(
                    current["latitude"], current["longitude"],
                    candidate["latitude"], candidate["longitude"]
                )
                if dist < min_distance:
                    min_distance = dist
                    nearest_idx = i
                    
            next_activity = valid_coords.pop(nearest_idx)
            ordered.append(next_activity)
            
        # 2-opt local improvement
        improved = True
        while improved:
            improved = False
            for i in range(1, len(ordered) - 1):
                for j in range(i + 1, len(ordered)):
                    d1 = calculate_distance(ordered[i-1]["latitude"], ordered[i-1]["longitude"],
                                            ordered[i]["latitude"], ordered[i]["longitude"])
                    d2 = calculate_distance(ordered[j-1]["latitude"], ordered[j-1]["longitude"],
                                            ordered[j]["latitude"], ordered[j]["longitude"])
                    
                    d_new1 = calculate_distance(ordered[i-1]["latitude"], ordered[i-1]["longitude"],
                                                ordered[j-1]["latitude"], ordered[j-1]["longitude"])
                    d_new2 = calculate_distance(ordered[i]["latitude"], ordered[i]["longitude"],
                                                ordered[j]["latitude"], ordered[j]["longitude"])
                                                
                    if d_new1 + d_new2 < d1 + d2 - 1e-9:
                        ordered[i:j] = ordered[i:j][::-1]
                        improved = True
                        break
                if improved:
                    break
        
        # Calculate total distance after 2-opt
        total_distance = 0.0
        for i in range(len(ordered) - 1):
            total_distance += calculate_distance(
                ordered[i]["latitude"], ordered[i]["longitude"],
                ordered[i+1]["latitude"], ordered[i+1]["longitude"]
            )
            
    # Set distance_to_next for valid coordinates
    for i in range(len(ordered) - 1):
        dist = calculate_distance(
            ordered[i]["latitude"], ordered[i]["longitude"],
            ordered[i+1]["latitude"], ordered[i+1]["longitude"]
        )
        ordered[i]["distance_to_next"] = round(dist, 2)
        
    # Append remaining activities that have no coordinates
    if missing_coords:
        ordered.extend(missing_coords)
        
    return ordered, round(total_distance, 2), method
