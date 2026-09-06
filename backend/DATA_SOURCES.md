# Sri Lankan Travel Dataset & Price Sources

**Dataset Version:** 2.0 (Curated Sri Lanka Regional Dataset)  
**Last Reviewed Date:** September 2026  
**Currency:** Sri Lankan Rupee (LKR / Rs.)

---

## 1. Overview & Dataset Contents

This dataset contains structured, deterministic travel data for **18 popular travel destinations** across Sri Lanka and **100 curated activities and attractions**.

### Covered Destinations:
1. **Ella** (Uva Province) — Nature / Adventure
2. **Nuwara Eliya** (Central Province) — Nature / Relaxation
3. **Kandy** (Central Province) — Culture / Heritage
4. **Galle** (Southern Province) — Culture / Coastal Fort
5. **Mirissa** (Southern Province) — Beach / Marine Wildlife
6. **Sigiriya** (Central / Cultural Triangle) — Adventure / Heritage Rock Fortress
7. **Dambulla** (Central / Cultural Triangle) — Culture / Ancient Cave Temples
8. **Yala** (Southern / Uva Province) — Wildlife / Leopard Safari
9. **Udawalawe** (Sabaragamuwa Province) — Wildlife / Elephant Safari
10. **Arugam Bay** (Eastern Province) — Beach / Surfing
11. **Trincomalee** (Eastern Province) — Beach / Coral Snorkeling
12. **Anuradhapura** (North Central Province) — Culture / Ancient Sacred Capital
13. **Hikkaduwa** (Southern Province) — Beach / Coral Reef & Watersports
14. **Bentota** (Southern Province) — Relaxation / Coastal Watersports & Mangroves
15. **Haputale** (Uva Province) — Nature / Mountain Tea Country
16. **Jaffna** (Northern Province) — Culture / Northern Peninsula & Islands
17. **Negombo** (Western Province) — Relaxation / Coastal Gateway & Lagoon
18. **Knuckles** (Central Province) — Adventure / Cloud Forest Trekking

---

## 2. Cost Categories & Estimation Methodology

To support modular budget optimization without hardcoded UI logic, each destination provides estimated daily baseline costs across three distinct categories:
- **Accommodation Cost (Daily Avg)**: Mid-range guesthouse / 3-star boutique accommodation per room/night basis.
- **Food Cost (Daily Avg)**: Three daily local meals, fresh juices, and refreshments per traveler.
- **Transportation Cost (Daily Avg)**: Local tuk-tuks, shared taxis, and regional train / bus transit.
- **Activity & Attraction Ticket Costs**: Specific per-activity ticket / entry / equipment rental tariffs.

All costs are calculated deterministically on the backend service layer (`app.services.recommendation_service` and `app.services.trip_planner`).

---

## 3. Verified Information Sources

Price estimates and attraction logistics are synthesized from verified, publicly available tourism authorities and standard operator norms:

1. **Central Cultural Fund (CCF) Sri Lanka**
   - Sigiriya Rock Fortress standard foreign tourist entry ticket (~$30–$36 / ~Rs. 11,000 LKR equivalent).
   - Anuradhapura Sacred City CCF Round Ticket (~$25–$30 / ~Rs. 9,500 LKR equivalent).
   - Dambulla Royal Rock Cave Temple preservation ticket (~Rs. 2,000 LKR).

2. **Department of Wildlife Conservation (DWC) Sri Lanka**
   - National Park entrance fees, vehicle permits, service charges, and VAT (e.g., Yala National Park, Udawalawe National Park, Horton Plains National Park, Minneriya National Park, and Pigeon Island Marine National Park).
   - Typical shared safari jeep hire rates (~Rs. 12,000–16,000 per half-day jeep split among travelers).

3. **Sri Lanka Tourism Development Authority (SLTDA)**
   - Destination regional classifications, seasonal weather patterns (South/West vs. East Coast monsoonal shifts), and regional tourist amenities.

4. **Temple & Community Preservation Trusts**
   - Sri Dalada Maligawa (Temple of the Sacred Tooth Relic, Kandy) entrance ticket (~Rs. 2,000 LKR).
   - Royal Botanic Gardens, Peradeniya admission (~Rs. 3,000 LKR).
   - Elephant Transit Home (ETH), Udawalawe public milk feeding visitor fee (~Rs. 1,000 LKR).
   - Brief Garden (Bentota) admission (~Rs. 2,000 LKR).

5. **Community & Local Operator Standard Tariffs**
   - Mirissa Whale Watching Boat Cruise (SLTDA / coastguard-regulated vessels: ~Rs. 14,000 LKR).
   - Local surf lessons and board rentals in Arugam Bay and Hikkaduwa (~Rs. 3,000–4,000 LKR).
   - River safaris (Madu Ganga, Bentota & Pottuvil Lagoon: ~Rs. 4,500–5,000 LKR).
   - Tea factory guided walking tours (Pedro, Halpewatte, Dambatenne: ~Rs. 1,000–1,500 LKR).

---

## 4. Public / Free Attractions

Natural landmarks, public ocean ramparts, beaches, and scenic trekking routes are explicitly marked with `0.0` estimated cost and rendered as **"Free Entry"** in the application:
- *Little Adam's Peak*, *Nine Arch Bridge*, *Ella Rock*, and *Ravana Falls* (Ella)
- *Galle Fort Ramparts* and *Lighthouse* (Galle)
- *Coconut Tree Hill*, *Mirissa Beach*, and *Secret Beach* (Mirissa)
- *Lover's Leap Waterfall* (Nuwara Eliya)
- *Nilaveli Beach* and *Koneswaram Temple* (Trincomalee)
- *Ruwanwelisaya Great Stupa* (Anuradhapura)
- *Nallur Kandaswamy Kovil* (Jaffna)
- *Elephant Rock* (Arugam Bay)

---

## 5. Assumptions & Limitations

1. **Approximate Ranges**: All prices and entrance fees reflect standard 2025/2026 approximate tariffs and are subject to currency fluctuations, seasonal operator adjustments, and government gazette revisions.
2. **Standard Traveler Basis**: Estimates represent individual independent travelers or couples traveling on a moderate budget (comfortable AC guesthouse/boutique hotel, a mix of local and casual dining, and tuk-tuk/train transit).
3. **No Dynamic Runtime Scraping**: To maintain instant page loads, offline predictability, and explainable recommendations, all figures are pre-compiled and served directly from the database without external runtime API dependencies.
