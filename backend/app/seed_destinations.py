"""
Seed file for Sri Lankan Destinations and Activities.

Provides curated, realistic travel data for 18 popular destinations in Sri Lanka
with separated cost categories (Accommodation, Food, Transportation) and realistic
attraction/activity ticket fees based on official tourism, DWC, CCF, and local operator rates.
"""

from sqlalchemy import text
from app.database import SessionLocal, engine
from app.models.destination import Destination
from app.models.activity import Activity


def run_database_migrations():
    """Ensure all required columns exist in PostgreSQL tables."""
    with engine.connect() as conn:
        # Migration for destinations table
        conn.execute(
            text(
                """
            ALTER TABLE destinations ADD COLUMN IF NOT EXISTS region VARCHAR(100);
            ALTER TABLE destinations ADD COLUMN IF NOT EXISTS description VARCHAR(600);
            ALTER TABLE destinations ADD COLUMN IF NOT EXISTS accommodation_cost FLOAT DEFAULT 0.0;
            ALTER TABLE destinations ADD COLUMN IF NOT EXISTS food_cost FLOAT DEFAULT 0.0;
            ALTER TABLE destinations ADD COLUMN IF NOT EXISTS transport_cost FLOAT DEFAULT 0.0;
            ALTER TABLE destinations ADD COLUMN IF NOT EXISTS recommended_duration INTEGER DEFAULT 3;
            """
            )
        )

        # Migration for activities table
        conn.execute(
            text(
                """
            ALTER TABLE activities ADD COLUMN IF NOT EXISTS description VARCHAR(300);
            """
            )
        )
    print("[OK] Schema migrations checked successfully.")


DESTINATIONS_DATA = [
    {
        "name": "Ella",
        "country": "Sri Lanka",
        "region": "Uva Province",
        "category": "Nature",
        "budget_level": "Medium",
        "description": "Picturesque hill country haven renowned for misty mountain vistas, the iconic Nine Arch Bridge, lush Ceylon tea estates, and scenic hiking treks.",
        "accommodation_cost": 6000.0,
        "food_cost": 3500.0,
        "transport_cost": 2500.0,
        "average_daily_cost": 12000.0,
        "best_season": "December-April",
        "activities": "Hiking,Nature,Scenic",
        "rating": 4.8,
        "recommended_duration": 3,
        "activities_list": [
            {"name": "Little Adam's Peak Hike", "category": "Hiking", "cost": 0.0, "duration": 2.0, "rating": 4.8},
            {"name": "Nine Arch Bridge Viewpoint & Walk", "category": "Sightseeing", "cost": 0.0, "duration": 1.5, "rating": 4.9},
            {"name": "Ella Rock Summit Trek", "category": "Hiking", "cost": 0.0, "duration": 4.0, "rating": 4.7},
            {"name": "Ravana Falls & Cave Viewpoint", "category": "Nature", "cost": 0.0, "duration": 1.0, "rating": 4.5},
            {"name": "Halpewatte Tea Factory Guided Tour", "category": "Culture", "cost": 1500.0, "duration": 2.0, "rating": 4.6},
            {"name": "Flying Ravana Adventure Zipline", "category": "Adventure", "cost": 8500.0, "duration": 1.5, "rating": 4.7},
        ],
    },
    {
        "name": "Nuwara Eliya",
        "country": "Sri Lanka",
        "region": "Central Province",
        "category": "Nature",
        "budget_level": "Medium",
        "description": "Cool-climate colonial highland retreat known as 'Little England', featuring sprawling Ceylon tea estates, serene Gregory Lake, and misty mountain air.",
        "accommodation_cost": 7500.0,
        "food_cost": 3500.0,
        "transport_cost": 2000.0,
        "average_daily_cost": 13000.0,
        "best_season": "January-April",
        "activities": "Nature,Scenic,Hiking",
        "rating": 4.6,
        "recommended_duration": 3,
        "activities_list": [
            {"name": "Gregory Lake Boating & Leisure Park", "category": "Relaxation", "cost": 1000.0, "duration": 2.0, "rating": 4.5},
            {"name": "Victoria Park Botanic Gardens", "category": "Nature", "cost": 500.0, "duration": 1.5, "rating": 4.4},
            {"name": "Pedro Tea Estate & Factory Guided Tour", "category": "Culture", "cost": 1200.0, "duration": 2.0, "rating": 4.6},
            {"name": "Lover's Leap Waterfall Hike", "category": "Hiking", "cost": 0.0, "duration": 2.0, "rating": 4.4},
            {"name": "Horton Plains & World's End Trek", "category": "Hiking", "cost": 11500.0, "duration": 5.0, "rating": 4.9},
            {"name": "Hakgala Subtropical Botanic Gardens", "category": "Nature", "cost": 3000.0, "duration": 2.5, "rating": 4.6},
        ],
    },
    {
        "name": "Kandy",
        "country": "Sri Lanka",
        "region": "Central Province",
        "category": "Culture",
        "budget_level": "Medium",
        "description": "Spiritual and cultural capital nestled in the central hills, home to the Sacred Temple of the Tooth Relic, royal botanical gardens, and historic traditions.",
        "accommodation_cost": 6500.0,
        "food_cost": 3000.0,
        "transport_cost": 2000.0,
        "average_daily_cost": 11500.0,
        "best_season": "January-April",
        "activities": "Culture,History,Nature",
        "rating": 4.7,
        "recommended_duration": 2,
        "activities_list": [
            {"name": "Sacred Temple of the Tooth Relic (Sri Dalada Maligawa)", "category": "Culture", "cost": 2000.0, "duration": 2.5, "rating": 4.9},
            {"name": "Royal Botanic Gardens Peradeniya", "category": "Nature", "cost": 3000.0, "duration": 3.0, "rating": 4.8},
            {"name": "Kandy Lake Scenic Promenade", "category": "Relaxation", "cost": 0.0, "duration": 1.5, "rating": 4.5},
            {"name": "Kandyan Cultural Dance & Drum Performance", "category": "Culture", "cost": 2500.0, "duration": 1.5, "rating": 4.6},
            {"name": "Bahirawakanda Vihara Buddha Statue Viewpoint", "category": "Sightseeing", "cost": 300.0, "duration": 1.0, "rating": 4.4},
            {"name": "Udawatta Kele Sanctuary Forest Walk", "category": "Nature", "cost": 1000.0, "duration": 2.5, "rating": 4.5},
        ],
    },
    {
        "name": "Galle",
        "country": "Sri Lanka",
        "region": "Southern Province",
        "category": "Culture",
        "budget_level": "Medium",
        "description": "UNESCO World Heritage 17th-century fortified city combining Portuguese, Dutch, and British colonial ramparts with vibrant boutique cafes and ocean ramparts.",
        "accommodation_cost": 7000.0,
        "food_cost": 4000.0,
        "transport_cost": 2000.0,
        "average_daily_cost": 13000.0,
        "best_season": "December-April",
        "activities": "Beach,Culture,History",
        "rating": 4.7,
        "recommended_duration": 2,
        "activities_list": [
            {"name": "Galle Dutch Fort Ramparts & Lighthouse Walk", "category": "Culture", "cost": 0.0, "duration": 2.5, "rating": 4.9},
            {"name": "National Maritime Museum of Galle", "category": "Culture", "cost": 1500.0, "duration": 1.5, "rating": 4.4},
            {"name": "Unawatuna Bay Relaxation & Swim", "category": "Beach", "cost": 0.0, "duration": 3.0, "rating": 4.7},
            {"name": "Jungle Beach Snorkeling Cove", "category": "Swimming", "cost": 0.0, "duration": 2.5, "rating": 4.5},
            {"name": "Historical Mansion Museum & Craft Walk", "category": "Sightseeing", "cost": 0.0, "duration": 1.0, "rating": 4.3},
        ],
    },
    {
        "name": "Mirissa",
        "country": "Sri Lanka",
        "region": "Southern Province",
        "category": "Beach",
        "budget_level": "Medium",
        "description": "Tropical southern beach paradise popular for crescent-shaped golden shores, world-class whale watching excursions, and scenic coastal palms.",
        "accommodation_cost": 7000.0,
        "food_cost": 3500.0,
        "transport_cost": 2000.0,
        "average_daily_cost": 12500.0,
        "best_season": "December-March",
        "activities": "Beach,Surfing,Whale Watching",
        "rating": 4.6,
        "recommended_duration": 3,
        "activities_list": [
            {"name": "Mirissa Blue Whale Watching Cruise", "category": "Wildlife", "cost": 14000.0, "duration": 4.5, "rating": 4.7},
            {"name": "Coconut Tree Hill Sunset Viewpoint", "category": "Nature", "cost": 0.0, "duration": 1.5, "rating": 4.8},
            {"name": "Mirissa Main Beach Swimming & Lounging", "category": "Swimming", "cost": 0.0, "duration": 3.0, "rating": 4.7},
            {"name": "Secret Beach Hidden Bay & Tide Pools", "category": "Relaxation", "cost": 0.0, "duration": 2.5, "rating": 4.5},
            {"name": "Parrot Rock Island Scramble", "category": "Sightseeing", "cost": 0.0, "duration": 1.0, "rating": 4.4},
            {"name": "Mirissa Beginner Surfing Session", "category": "Surfing", "cost": 4000.0, "duration": 2.0, "rating": 4.6},
        ],
    },
    {
        "name": "Sigiriya",
        "country": "Sri Lanka",
        "region": "Central / Cultural Triangle",
        "category": "Adventure",
        "budget_level": "Medium",
        "description": "Ancient 5th-century rock citadel rising 200m above jungle plains, featuring majestic palace ruins, ancient frescoes, and world-renowned landscaped gardens.",
        "accommodation_cost": 6500.0,
        "food_cost": 3000.0,
        "transport_cost": 2500.0,
        "average_daily_cost": 12000.0,
        "best_season": "January-April",
        "activities": "Hiking,History,Culture",
        "rating": 4.9,
        "recommended_duration": 2,
        "activities_list": [
            {"name": "Sigiriya Lion Rock Fortress Climb & Frescoes", "category": "Culture", "cost": 11000.0, "duration": 3.5, "rating": 4.9},
            {"name": "Pidurangala Rock Sunrise Summit Trek", "category": "Hiking", "cost": 1000.0, "duration": 2.5, "rating": 4.8},
            {"name": "Sigiriya Archaeological Museum", "category": "Culture", "cost": 0.0, "duration": 1.5, "rating": 4.5},
            {"name": "Hiriwadunna Traditional Village Tour & Boat Ride", "category": "Culture", "cost": 3500.0, "duration": 2.5, "rating": 4.6},
            {"name": "Minneriya Wild Elephant Gathering Safari", "category": "Wildlife", "cost": 16500.0, "duration": 4.0, "rating": 4.8},
        ],
    },
    {
        "name": "Dambulla",
        "country": "Sri Lanka",
        "region": "Central / Cultural Triangle",
        "category": "Culture",
        "budget_level": "Low",
        "description": "Hub of the Cultural Triangle, home to the UNESCO World Heritage Royal Cave Temple complex with over 150 Buddha statues and vivid Buddhist ceiling murals.",
        "accommodation_cost": 4500.0,
        "food_cost": 2500.0,
        "transport_cost": 1500.0,
        "average_daily_cost": 8500.0,
        "best_season": "January-April",
        "activities": "Culture,History,Sightseeing",
        "rating": 4.7,
        "recommended_duration": 2,
        "activities_list": [
            {"name": "Dambulla Royal Rock Cave Temple", "category": "Culture", "cost": 2000.0, "duration": 2.5, "rating": 4.8},
            {"name": "Golden Temple & Buddhist Museum", "category": "Sightseeing", "cost": 500.0, "duration": 1.0, "rating": 4.3},
            {"name": "Ibbankatuwa Megalithic Prehistoric Tombs", "category": "Culture", "cost": 500.0, "duration": 1.5, "rating": 4.4},
            {"name": "Dambulla Agricultural Market Tour", "category": "Culture", "cost": 0.0, "duration": 1.5, "rating": 4.2},
            {"name": "Kandalama Lake Sunset Cycling", "category": "Nature", "cost": 1500.0, "duration": 2.0, "rating": 4.6},
        ],
    },
    {
        "name": "Yala",
        "country": "Sri Lanka",
        "region": "Southern / Uva Province",
        "category": "Wildlife",
        "budget_level": "High",
        "description": "Sri Lanka's premier national park boasting the highest leopard density in the world, wild Asian elephants, sloth bears, and diverse coastal ecosystems.",
        "accommodation_cost": 12000.0,
        "food_cost": 4000.0,
        "transport_cost": 4000.0,
        "average_daily_cost": 20000.0,
        "best_season": "February-June",
        "activities": "Wildlife,Safari,Nature",
        "rating": 4.8,
        "recommended_duration": 2,
        "activities_list": [
            {"name": "Yala National Park Morning Leopard Safari", "category": "Wildlife", "cost": 19500.0, "duration": 4.5, "rating": 4.8},
            {"name": "Yala Evening Wilderness Game Drive", "category": "Wildlife", "cost": 19500.0, "duration": 4.0, "rating": 4.7},
            {"name": "Sithulpawwa Ancient Rock Monastery", "category": "Culture", "cost": 0.0, "duration": 2.0, "rating": 4.6},
            {"name": "Kirinda Coastal Temple & Sand Dunes", "category": "Sightseeing", "cost": 0.0, "duration": 1.5, "rating": 4.5},
            {"name": "Palatupana Salt Pans Bird Watching", "category": "Nature", "cost": 0.0, "duration": 1.5, "rating": 4.4},
        ],
    },
    {
        "name": "Udawalawe",
        "country": "Sri Lanka",
        "region": "Sabaragamuwa Province",
        "category": "Wildlife",
        "budget_level": "Medium",
        "description": "Spectacular wildlife haven renowned for guaranteed sightings of wild elephant herds roaming open grasslands around the Udawalawe reservoir.",
        "accommodation_cost": 6500.0,
        "food_cost": 3000.0,
        "transport_cost": 2500.0,
        "average_daily_cost": 12000.0,
        "best_season": "October-April",
        "activities": "Wildlife,Safari,Nature",
        "rating": 4.7,
        "recommended_duration": 2,
        "activities_list": [
            {"name": "Udawalawe National Park Elephant Safari", "category": "Wildlife", "cost": 15000.0, "duration": 4.0, "rating": 4.8},
            {"name": "Elephant Transit Home Milk Feeding", "category": "Wildlife", "cost": 1000.0, "duration": 1.5, "rating": 4.7},
            {"name": "Udawalawe Reservoir Dam Scenic Walk", "category": "Relaxation", "cost": 0.0, "duration": 1.0, "rating": 4.3},
            {"name": "Sankapala Ancient Raja Maha Vihara", "category": "Culture", "cost": 0.0, "duration": 1.5, "rating": 4.4},
            {"name": "Maduwanwela Walawwa Heritage Manor", "category": "Culture", "cost": 500.0, "duration": 2.0, "rating": 4.2},
        ],
    },
    {
        "name": "Arugam Bay",
        "country": "Sri Lanka",
        "region": "Eastern Province",
        "category": "Beach",
        "budget_level": "Medium",
        "description": "World-renowned surf haven on the sun-soaked east coast with legendary point breaks, relaxed beachfront cafes, and rich wildlife lagoon excursions.",
        "accommodation_cost": 6500.0,
        "food_cost": 3500.0,
        "transport_cost": 2000.0,
        "average_daily_cost": 12000.0,
        "best_season": "May-September",
        "activities": "Surfing,Beach,Adventure",
        "rating": 4.7,
        "recommended_duration": 4,
        "activities_list": [
            {"name": "Main Point World-Class Surfing Session", "category": "Surfing", "cost": 3500.0, "duration": 3.0, "rating": 4.9},
            {"name": "Pottuvil Lagoon Mangrove Canoe Safari", "category": "Wildlife", "cost": 4500.0, "duration": 2.5, "rating": 4.7},
            {"name": "Elephant Rock Sunset Scramble & Beach", "category": "Nature", "cost": 0.0, "duration": 2.0, "rating": 4.8},
            {"name": "Kudumbigala Monastery Forest Hermitage", "category": "Hiking", "cost": 0.0, "duration": 3.0, "rating": 4.6},
            {"name": "Whiskey Point Beginner Surf & Beach", "category": "Swimming", "cost": 2500.0, "duration": 2.5, "rating": 4.5},
            {"name": "Panama Beach & Sand Dune Exploration", "category": "Relaxation", "cost": 0.0, "duration": 2.0, "rating": 4.4},
        ],
    },
    {
        "name": "Trincomalee",
        "country": "Sri Lanka",
        "region": "Eastern Province",
        "category": "Beach",
        "budget_level": "Medium",
        "description": "East coast coastal hub boasting one of the world's finest natural deep-water harbors, pristine turquoise beaches at Nilaveli, and historic Hindu temples.",
        "accommodation_cost": 6500.0,
        "food_cost": 3500.0,
        "transport_cost": 2000.0,
        "average_daily_cost": 12000.0,
        "best_season": "May-September",
        "activities": "Beach,Swimming,Culture",
        "rating": 4.7,
        "recommended_duration": 3,
        "activities_list": [
            {"name": "Pigeon Island Marine Park Coral Snorkeling", "category": "Swimming", "cost": 9500.0, "duration": 4.0, "rating": 4.8},
            {"name": "Nilaveli Beach Soft Sand & Watersports", "category": "Beach", "cost": 0.0, "duration": 3.0, "rating": 4.7},
            {"name": "Koneswaram Ancient Hindu Cliff Temple", "category": "Culture", "cost": 0.0, "duration": 2.0, "rating": 4.8},
            {"name": "Fort Frederick Historic Ramparts & Deer Walk", "category": "Sightseeing", "cost": 0.0, "duration": 1.5, "rating": 4.5},
            {"name": "Kanniya Seven Hot Water Springs", "category": "Culture", "cost": 200.0, "duration": 1.0, "rating": 4.2},
            {"name": "Marble Beach Pristine Bay Swim", "category": "Relaxation", "cost": 200.0, "duration": 3.0, "rating": 4.6},
        ],
    },
    {
        "name": "Anuradhapura",
        "country": "Sri Lanka",
        "region": "North Central Province",
        "category": "Culture",
        "budget_level": "Medium",
        "description": "Ancient first royal capital of Sri Lanka, featuring massive sacred brick stupas, ancient monastic ruins, and the revered Jaya Sri Maha Bodhi tree.",
        "accommodation_cost": 5500.0,
        "food_cost": 2800.0,
        "transport_cost": 1700.0,
        "average_daily_cost": 10000.0,
        "best_season": "January-April",
        "activities": "Culture,History,Sightseeing",
        "rating": 4.8,
        "recommended_duration": 2,
        "activities_list": [
            {"name": "Jaya Sri Maha Bodhi Sacred Tree Pilgrimage", "category": "Culture", "cost": 500.0, "duration": 2.0, "rating": 4.9},
            {"name": "Ruwanwelisaya Great White Stupa Pilgrimage", "category": "Culture", "cost": 0.0, "duration": 2.0, "rating": 4.9},
            {"name": "CCF Sacred City Monastic Complex Tour", "category": "Culture", "cost": 9500.0, "duration": 4.0, "rating": 4.8},
            {"name": "Isurumuniya Rock Temple & Lovers Carvings", "category": "Culture", "cost": 500.0, "duration": 1.5, "rating": 4.6},
            {"name": "Mihintale Sacred Mountain Summit Climb", "category": "Hiking", "cost": 1000.0, "duration": 3.0, "rating": 4.8},
            {"name": "Kuttam Pokuna Ancient Twin Ponds", "category": "Sightseeing", "cost": 0.0, "duration": 1.0, "rating": 4.5},
        ],
    },
    {
        "name": "Hikkaduwa",
        "country": "Sri Lanka",
        "region": "Southern Province",
        "category": "Beach",
        "budget_level": "Low",
        "description": "Vibrant south-coast beach resort renowned for protected coral reefs, marine turtle feeding, energetic surf breaks, and lively seaside dining.",
        "accommodation_cost": 5000.0,
        "food_cost": 3000.0,
        "transport_cost": 1500.0,
        "average_daily_cost": 9500.0,
        "best_season": "December-March",
        "activities": "Beach,Surfing,Diving",
        "rating": 4.5,
        "recommended_duration": 3,
        "activities_list": [
            {"name": "Coral Reef Sanctuary Marine Snorkeling", "category": "Swimming", "cost": 2500.0, "duration": 2.5, "rating": 4.6},
            {"name": "Sea Turtle Hatchery & Conservation Project", "category": "Wildlife", "cost": 1500.0, "duration": 1.5, "rating": 4.6},
            {"name": "Narigama Beach Surfing & Sunbathing", "category": "Surfing", "cost": 3000.0, "duration": 3.0, "rating": 4.5},
            {"name": "Tsunami Photo Museum & Memorial", "category": "Culture", "cost": 0.0, "duration": 1.0, "rating": 4.4},
            {"name": "Meetiyagoda Natural Moonstone Mines Tour", "category": "Sightseeing", "cost": 0.0, "duration": 1.5, "rating": 4.2},
            {"name": "Glass Bottom Boat Coral Tour", "category": "Sightseeing", "cost": 3500.0, "duration": 1.5, "rating": 4.3},
        ],
    },
    {
        "name": "Bentota",
        "country": "Sri Lanka",
        "region": "Southern Province",
        "category": "Relaxation",
        "budget_level": "High",
        "description": "Premier coastal haven famous for golden sandspits, calm lagoon watersports, architectural garden estates, and tranquil wellness resorts.",
        "accommodation_cost": 11000.0,
        "food_cost": 4500.0,
        "transport_cost": 2500.0,
        "average_daily_cost": 18000.0,
        "best_season": "December-April",
        "activities": "Beach,Relaxation,Nature",
        "rating": 4.6,
        "recommended_duration": 3,
        "activities_list": [
            {"name": "Madu River Mangrove Boat Safari", "category": "Nature", "cost": 5000.0, "duration": 2.5, "rating": 4.7},
            {"name": "Brief Garden by Bevis Bawa Architectural Tour", "category": "Culture", "cost": 2000.0, "duration": 2.0, "rating": 4.8},
            {"name": "Bentota Golden Sand Spit Beach Leisure", "category": "Relaxation", "cost": 0.0, "duration": 3.0, "rating": 4.6},
            {"name": "Kosgoda Sea Turtle Conservation Project", "category": "Wildlife", "cost": 1500.0, "duration": 1.5, "rating": 4.7},
            {"name": "Lagoon Watersports & Jet Skiing", "category": "Adventure", "cost": 6500.0, "duration": 1.5, "rating": 4.5},
            {"name": "Kande Viharaya Giant Seated Buddha", "category": "Sightseeing", "cost": 0.0, "duration": 1.0, "rating": 4.4},
        ],
    },
    {
        "name": "Haputale",
        "country": "Sri Lanka",
        "region": "Uva Province",
        "category": "Nature",
        "budget_level": "Low",
        "description": "Quiet highland ridge town overlooking dramatic southern plains, world-renowned for Sir Thomas Lipton's historic tea seat and cloud forest walks.",
        "accommodation_cost": 4500.0,
        "food_cost": 2500.0,
        "transport_cost": 1500.0,
        "average_daily_cost": 8500.0,
        "best_season": "December-April",
        "activities": "Hiking,Nature,Scenic",
        "rating": 4.7,
        "recommended_duration": 2,
        "activities_list": [
            {"name": "Lipton's Seat Sunrise Viewpoint Trek", "category": "Hiking", "cost": 1000.0, "duration": 3.5, "rating": 4.9},
            {"name": "Dambatenne Tea Factory Historic Tour", "category": "Culture", "cost": 1000.0, "duration": 1.5, "rating": 4.6},
            {"name": "Adisham Benedictine Monastery & Orchards", "category": "Culture", "cost": 500.0, "duration": 2.0, "rating": 4.7},
            {"name": "Diyaluma Falls Upper Natural Pool Hike", "category": "Hiking", "cost": 0.0, "duration": 3.5, "rating": 4.8},
            {"name": "Idalgashinna Highland Mist Railway Walk", "category": "Nature", "cost": 0.0, "duration": 2.5, "rating": 4.6},
        ],
    },
    {
        "name": "Jaffna",
        "country": "Sri Lanka",
        "region": "Northern Province",
        "category": "Culture",
        "budget_level": "Low",
        "description": "Distinct northern cultural hub rich in vibrant Dravidian Hindu heritage, historic coastal colonial forts, unique culinary flavors, and remote islands.",
        "accommodation_cost": 5000.0,
        "food_cost": 2500.0,
        "transport_cost": 1500.0,
        "average_daily_cost": 9000.0,
        "best_season": "January-September",
        "activities": "Culture,History,Sightseeing",
        "rating": 4.6,
        "recommended_duration": 3,
        "activities_list": [
            {"name": "Nallur Kandaswamy Kovil Temple Visit", "category": "Culture", "cost": 0.0, "duration": 2.0, "rating": 4.9},
            {"name": "Jaffna Dutch Fort & Lagoon Walk", "category": "Culture", "cost": 0.0, "duration": 2.0, "rating": 4.6},
            {"name": "Delft Island Wild Ponies Ferry Excursion", "category": "Sightseeing", "cost": 2500.0, "duration": 6.0, "rating": 4.7},
            {"name": "Casuarina Beach Karainagar Swim", "category": "Beach", "cost": 200.0, "duration": 3.0, "rating": 4.5},
            {"name": "Jaffna Public Library & Cultural Center", "category": "Sightseeing", "cost": 0.0, "duration": 1.0, "rating": 4.6},
            {"name": "Keerimalai Sacred Water Springs & Kovil", "category": "Relaxation", "cost": 0.0, "duration": 1.5, "rating": 4.4},
        ],
    },
    {
        "name": "Negombo",
        "country": "Sri Lanka",
        "region": "Western Province",
        "category": "Relaxation",
        "budget_level": "Medium",
        "description": "Charming coastal gateway town close to the international airport, known for lively fish markets, Dutch canal cruises, sandy beaches, and seafood dining.",
        "accommodation_cost": 5500.0,
        "food_cost": 3000.0,
        "transport_cost": 1500.0,
        "average_daily_cost": 10000.0,
        "best_season": "December-April",
        "activities": "Beach,Culture,Relaxation",
        "rating": 4.4,
        "recommended_duration": 2,
        "activities_list": [
            {"name": "Negombo Dutch Canal & Lagoon Boat Cruise", "category": "Nature", "cost": 3500.0, "duration": 2.0, "rating": 4.5},
            {"name": "Lellama Traditional Open-Air Fish Market", "category": "Culture", "cost": 0.0, "duration": 1.5, "rating": 4.4},
            {"name": "Negombo Beach Sunset Walk & Dining", "category": "Beach", "cost": 0.0, "duration": 2.0, "rating": 4.3},
            {"name": "St. Mary's Church Colonial Ceiling Art", "category": "Culture", "cost": 0.0, "duration": 1.0, "rating": 4.5},
            {"name": "Muthurajawela Wetland Sanctuary Bird Tour", "category": "Wildlife", "cost": 4000.0, "duration": 2.5, "rating": 4.6},
        ],
    },
    {
        "name": "Knuckles",
        "country": "Sri Lanka",
        "region": "Central Province",
        "category": "Adventure",
        "budget_level": "Low",
        "description": "Rugged UNESCO World Heritage mountain range featuring cloud forests, hidden villages like Meemure, cascading waterfalls, and world-class trekking.",
        "accommodation_cost": 5000.0,
        "food_cost": 2500.0,
        "transport_cost": 2000.0,
        "average_daily_cost": 9500.0,
        "best_season": "January-April",
        "activities": "Hiking,Nature,Adventure",
        "rating": 4.8,
        "recommended_duration": 3,
        "activities_list": [
            {"name": "Knuckles High Peak Ridge Trail Trek", "category": "Hiking", "cost": 2000.0, "duration": 5.0, "rating": 4.9},
            {"name": "Meemure Remote Village Cultural Expedition", "category": "Adventure", "cost": 4500.0, "duration": 6.0, "rating": 4.8},
            {"name": "Nitro Caves & Cloud Forest Wildlife Walk", "category": "Nature", "cost": 2000.0, "duration": 4.0, "rating": 4.7},
            {"name": "Deanston Mini World's End Escarpment Walk", "category": "Sightseeing", "cost": 1000.0, "duration": 2.5, "rating": 4.7},
            {"name": "Sera Ella Waterfall & Rock Cave Shelter", "category": "Nature", "cost": 0.0, "duration": 2.0, "rating": 4.6},
        ],
    },
]


def seed_database():
    """Idempotently seed destinations and activities."""
    run_database_migrations()

    db = SessionLocal()
    try:
        total_dest_added = 0
        total_act_added = 0

        for dest_data in DESTINATIONS_DATA:
            # Check if destination exists
            dest = db.query(Destination).filter(Destination.name == dest_data["name"]).first()

            if not dest:
                dest = Destination(
                    name=dest_data["name"],
                    country=dest_data["country"],
                    region=dest_data["region"],
                    category=dest_data["category"],
                    budget_level=dest_data["budget_level"],
                    description=dest_data["description"],
                    accommodation_cost=dest_data["accommodation_cost"],
                    food_cost=dest_data["food_cost"],
                    transport_cost=dest_data["transport_cost"],
                    average_daily_cost=dest_data["average_daily_cost"],
                    best_season=dest_data["best_season"],
                    activities=dest_data["activities"],
                    rating=dest_data["rating"],
                    recommended_duration=dest_data["recommended_duration"],
                )
                db.add(dest)
                db.flush()
                total_dest_added += 1
            else:
                # Update existing destination attributes to latest realistic dataset
                dest.country = dest_data["country"]
                dest.region = dest_data["region"]
                dest.category = dest_data["category"]
                dest.budget_level = dest_data["budget_level"]
                dest.description = dest_data["description"]
                dest.accommodation_cost = dest_data["accommodation_cost"]
                dest.food_cost = dest_data["food_cost"]
                dest.transport_cost = dest_data["transport_cost"]
                dest.average_daily_cost = dest_data["average_daily_cost"]
                dest.best_season = dest_data["best_season"]
                dest.activities = dest_data["activities"]
                dest.rating = dest_data["rating"]
                dest.recommended_duration = dest_data["recommended_duration"]
                db.flush()

            # Clean and re-seed activities for this destination to prevent duplicates
            db.query(Activity).filter(Activity.destination_id == dest.id).delete()

            for act_data in dest_data["activities_list"]:
                act = Activity(
                    destination_id=dest.id,
                    name=act_data["name"],
                    category=act_data["category"],
                    estimated_cost=act_data["cost"],
                    duration=act_data["duration"],
                    rating=act_data["rating"],
                )
                db.add(act)
                total_act_added += 1

        db.commit()
        print(f"[OK] Seed complete: {len(DESTINATIONS_DATA)} destinations synced, {total_act_added} activities seeded.")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error during seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()