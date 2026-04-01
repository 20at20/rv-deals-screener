"""
Test: VC Screener agent
Usage: python tests/test_vc_screener.py

Runs the screener with hardcoded sample data so you can calibrate
the prompt without touching Apify or web search.
Edit TEAM_DATA and MARKET_DATA below to test different scenarios.
"""

from dotenv import load_dotenv
load_dotenv()

from agents.vc_screener import score_deal

# ── Sample scenarios ───────────────────────────────────────────────────────────
# Switch SCENARIO to "strong", "medium", or "weak" to test different inputs.

SCENARIO = "strong"

SCENARIOS = {
    "strong": {
        "team_data": """
FOUNDER: Alex Petrov
Location: United States
Followers: 12,400

Profile Summary:
Co-founder of DataFlow (acq. by Snowflake 2021). Previously VP Engineering at Segment (Series C, $175M raised).
Built and shipped real-time event pipeline from 0 to $8M ARR.

Top Experience:
- Co-Founder & CTO at DataFlow (2018–2021)
- VP Engineering at Segment (2015–2018)
- Senior Engineer at Palantir (2012–2015)

Education:
- BS Computer Science, MIT
""",
        "market_data": """
1. MARKET SIZE
• Data orchestration market: $6.4B in 2024, 16.7% CAGR, projected $29.6B by 2033.

2. TIMING / WHY NOW
• AI agents require reliable data pipelines; enterprise demand surging post-GPT-4 (2023–2024).

3. REVENUE BENCHMARKS
• Databricks: $5.4B ARR (2026). Prefect: ~$20M ARR (2024). Dagster: Series B $33M (2023).

4. COMPETITION
• Airflow, Dagster, Prefect dominate; no clear Python-native winner for AI workloads.
""",
    },

    "medium": {
        "team_data": """
FOUNDER: Sophie Chen
Location: Germany
Followers: 3,200

Profile Summary:
10 years in enterprise software. Former product manager at SAP. Domain expert in supply chain.

Top Experience:
- Senior Product Manager at SAP (2016–2023)
- Product Analyst at McKinsey & Company (2013–2016)

Education:
- MBA, INSEAD
- BS Industrial Engineering, TU Munich
""",
        "market_data": """
1. MARKET SIZE
• Supply chain software market: $28B in 2024, 11% CAGR.

2. TIMING / WHY NOW
• Post-COVID supply chain disruptions accelerated digitization investment (2022–2024).

3. REVENUE BENCHMARKS
• o9 Solutions: $200M ARR (2024). Llamasoft (acq. by Coupa): $50M ARR at acquisition.

4. COMPETITION
• SAP, Oracle dominate enterprise. Blue Yonder, o9 Solutions in mid-market. Fragmented SMB space.
""",
    },

    "weak": {
        "team_data": """
FOUNDER: James Miller
Location: United Kingdom
Followers: 890

Profile Summary:
Consultant with background in financial services. Recently launched first startup.

Top Experience:
- Senior Consultant at Deloitte (2018–2024)
- Analyst at Barclays (2015–2018)

Education:
- BA Economics, University of Leeds
""",
        "market_data": """
1. MARKET SIZE
• Fintech market broadly: $500B+ TAM. Specific niche unclear.

2. TIMING / WHY NOW
• Open banking regulations expanding in EU (PSD2, 2024 updates).

3. REVENUE BENCHMARKS
• Stripe: $4B ARR. Plaid: ~$250M ARR. Limited comparable early-stage data.

4. COMPETITION
• Heavily crowded. Stripe, Plaid, Brex, Ramp, Mercury all well-funded.
""",
    },
}

# ── Run ────────────────────────────────────────────────────────────────────────

data = SCENARIOS[SCENARIO]
print(f"\n{'='*60}")
print(f"SCENARIO: {SCENARIO.upper()}")
print(f"{'='*60}\n")
print("TEAM DATA:\n" + data["team_data"])
print("\nMARKET DATA:\n" + data["market_data"])
print(f"\n{'='*60}")
print("SCREENER OUTPUT")
print(f"{'='*60}\n")

result = score_deal(team_data=data["team_data"], market_data=data["market_data"])

print(f"Decision:  {result['decision']} ({'High' if result['decision'] == 1 else 'Medium' if result['decision'] == 2 else 'Low'} Priority)")
print(f"Conviction: {result.get('conviction', 'N/A')}")
print(f"\nComment:\n{result['comment']}")
