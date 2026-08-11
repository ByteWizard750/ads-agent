import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.supabase import get_supabase_client

def trace_lineage():
    client = get_supabase_client()
    target_run_id = "1b12362d-d2f1-4e79-9fb9-bbdf5bc0aea4"
    
    print(f"=== AUDIT TASK 2: DATA LINEAGE TRACE FOR RUN '{target_run_id}' ===")
    
    # 1. Fetch ads for this run
    ads_res = client.table("ads").select("*").eq("run_id", target_run_id).execute()
    ads = ads_res.data
    print(f"Fetched {len(ads)} ads for run '{target_run_id}'.")
    
    if not ads:
        print("[ERROR] No ads found for this run_id.")
        return
        
    sample_ad = ads[0]
    sample_ad_id = sample_ad["id"]
    apify_ad_id = sample_ad["apify_ad_id"]
    advertiser = sample_ad["advertiser_name"]
    headline = sample_ad["headline"]
    
    print(f"\n1. TARGET AD SELECTED:")
    print(f"   • Database Ad UUID: {sample_ad_id}")
    print(f"   • Apify Ad Archive ID: {apify_ad_id}")
    print(f"   • Advertiser Name: {advertiser}")
    print(f"   • Headline: {headline}")
    
    # 2. Fetch concepts citing this ad UUID
    concepts_res = client.table("concepts").select("*").eq("run_id", target_run_id).execute()
    concepts = concepts_res.data
    
    matching_concept = None
    for c in concepts:
        source_ids = c.get("source_ad_ids", [])
        if sample_ad_id in source_ids:
            matching_concept = c
            break
            
    print(f"\n2. MATCHING CONCEPT TRACED:")
    if matching_concept:
        concept_id = matching_concept["id"]
        print(f"   • Concept UUID: {concept_id}")
        print(f"   • Angle Name: {matching_concept.get('angle_name')}")
        print(f"   • Pain Point: {matching_concept.get('pain_point')}")
        print(f"   • Cited Source Ad IDs: {matching_concept.get('source_ad_ids')}")
    else:
        print(f"   • Ad UUID '{sample_ad_id}' was not in the top cited subset for concepts. Checking all concepts...")
        for c in concepts:
            print(f"     - Concept '{c['id']}' cites: {c.get('source_ad_ids')}")
        matching_concept = concepts[0]
        concept_id = matching_concept["id"]
        sample_ad_id = matching_concept.get("source_ad_ids", [sample_ad_id])[0]
        print(f"   • Tracing directly from Concept's cited Ad UUID: {sample_ad_id}")

    # 3. Fetch script referencing this concept UUID
    scripts_res = client.table("scripts").select("*").eq("run_id", target_run_id).execute()
    scripts = scripts_res.data
    
    print(f"\n3. MATCHING SCRIPT VARIANTS TRACED:")
    matching_scripts = [s for s in scripts if s.get("concept_id") == concept_id]
    if matching_scripts:
        for s in matching_scripts:
            print(f"   • Script UUID: {s['id']}")
            print(f"     Variant Type: {s['variant_type']}")
            print(f"     Approval Status: {s['approval_status']}")
            print(f"     Concept ID Link: {s.get('concept_id')}")
            print(f"     Hook: \"{s.get('hook_text')}\"")
    else:
        print(f"   • [NOTICE] Scripts in DB have concept_id: {[s.get('concept_id') for s in scripts]}")

if __name__ == "__main__":
    trace_lineage()
