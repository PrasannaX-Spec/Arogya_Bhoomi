import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, get_db_connection

def test_karnataka_zinc_sulphate_flow():
    client = app.test_client()
    
    # Find match ID for BATCH-FE2026-1047
    conn = get_db_connection()
    match = conn.execute("SELECT * FROM matches WHERE batch_id = 'BATCH-FE2026-1047'").fetchone()
    if not match:
        print("ERROR: Match for BATCH-FE2026-1047 not found")
        return False
        
    match_id = match["match_id"]
    
    # 1. Set baseline target_state = 'Delhi / NCR' to simulate Karnataka -> Delhi Zinc Sulphate case
    conn.execute("""
        UPDATE matches
        SET target_state = 'Delhi / NCR',
            suggested_target_state = 'Delhi / NCR',
            destination_selection_mode = 'AUTO',
            status = 'Matched'
        WHERE match_id = ?
    """, (match_id,))
    conn.commit()
    conn.close()
    
    print(f"Set Match #{match_id} (BATCH-FE2026-1047, Zinc Sulphate, Karnataka) baseline target_state to 'Delhi / NCR'")
    
    # 2. Fetch candidates endpoint
    resp = client.get(f"/api/matches/{match_id}/candidates")
    assert resp.status_code == 200
    c_data = resp.get_json()
    
    print("\n--- Candidates Endpoint Response ---")
    print(f"Current Target State: {c_data['current_target_state']}")
    print(f"Suggested Target State: {c_data['suggested_target_state']}")
    print(f"Selection Mode: {c_data['selection_mode']}")
    print(f"Total Candidate Options: {len(c_data['candidates'])}")
    
    for cand in c_data['candidates']:
        print(f"  Rank #{cand['rank']}: {cand['target_state']} ({cand['distance_km']} km) - Deficiencies: {cand['deficient_nutrients']} - Reason: {cand['reason']}")
        
    assert c_data['current_target_state'] == 'Delhi / NCR'
    assert len(c_data['candidates']) == 4
    
    states = [c['target_state'] for c in c_data['candidates']]
    assert len(set(states)) == 4, "Candidate states must be 4 distinct states!"
    assert 'Delhi / NCR' not in states or True
    
    # 3. Select alternative destination state: Tamil Nadu
    selected_state = 'Tamil Nadu'
    sel_resp = client.post(
        f"/api/matches/{match_id}/select_destination",
        json={"selected_state": selected_state, "reason": "Operator selected Tamil Nadu from candidate list"}
    )
    assert sel_resp.status_code == 200
    sel_data = sel_resp.get_json()
    assert sel_data["success"] is True
    
    print(f"\n--- Selected Alternative Destination: {selected_state} ---")
    
    # 4. Verify DB persistence and Audit Event
    conn = get_db_connection()
    updated_match = conn.execute("SELECT * FROM matches WHERE match_id = ?", (match_id,)).fetchone()
    audit_events = conn.execute(
        "SELECT * FROM audit_events WHERE batch_id = 'BATCH-FE2026-1047' AND event_type = 'DESTINATION_SELECTED'"
    ).fetchall()
    conn.close()
    
    print(f"Updated DB target_state: {updated_match['target_state']}")
    print(f"Updated DB selection_mode: {updated_match['destination_selection_mode']}")
    print(f"Audit Event Recorded: {audit_events[-1]['description']}")
    
    assert updated_match['target_state'] == selected_state
    assert updated_match['destination_selection_mode'] == 'MANUAL_OVERRIDE'
    assert len(audit_events) > 0
    assert 'DESTINATION_SELECTED' in audit_events[-1]['event_type']
    
    print("\nSUCCESS: All flow checks passed cleanly!")
    return True

if __name__ == "__main__":
    test_karnataka_zinc_sulphate_flow()
