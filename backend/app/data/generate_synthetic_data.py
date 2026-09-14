"""
Generates a synthetic industrial near-miss / incident dataset and a small
regulatory excerpt corpus for the Incident Pattern Intelligence Agent.

IMPORTANT: This data is entirely synthetic and illustrative. It is templated
from realistic industrial-safety categories (confined space entry, hot work,
gas leaks, permit-to-work violations, lockout-tagout, working-at-height,
electrical isolation) but does not represent any real facility, company, or
incident. This is documented here and in the README so the provenance of
every number in the project is honest and traceable.
"""
import json
import random
from pathlib import Path

random.seed(42)

DATA_DIR = Path(__file__).parent
OUT_INCIDENTS = DATA_DIR / "incidents.json"
OUT_REGULATIONS = DATA_DIR / "regulations.json"
OUT_EVAL = DATA_DIR / "eval_questions.json"

LOCATIONS = ["Plant A - Coke Oven", "Plant A - Utilities Yard", "Plant B - Rolling Mill",
             "Plant B - Tank Farm", "Plant C - Warehouse", "Plant C - Compressor House"]

CATEGORIES = {
    "confined_space": {
        "label": "Confined Space Entry",
        "templates": [
            "Worker entered {loc} confined space without a valid gas-test reading on the permit.",
            "Gas detector alarm ignored during confined space entry at {loc}; entry continued for 6 minutes before evacuation.",
            "Confined space permit at {loc} was signed off without a second worker posted outside the vessel.",
            "Oxygen levels in a vessel at {loc} were not re-tested after a 40-minute work break, entry resumed anyway.",
            "Vessel entry log at {loc} shows no record of who was inside when the shift changed over.",
            "Ventilation blower at {loc} was switched off mid-task to reduce noise, no one flagged the atmosphere risk.",
            "Rescue equipment for a tank entry at {loc} was found to be missing from the designated staging point.",
            "A contractor at {loc} climbed into a pit to retrieve a dropped tool without opening a new entry permit.",
        ],
        "severity_weights": [2, 4, 3, 5, 3, 3, 4, 3],
    },
    "hot_work": {
        "label": "Hot Work / Ignition Source",
        "templates": [
            "Hot work permit issued at {loc} despite an active gas leak alert within 15 metres.",
            "Welding operation at {loc} proceeded without a fire watch, sparks landed near stored solvent drums.",
            "Grinding work at {loc} generated sparks near an open hydrocarbon vent, no isolation confirmed.",
            "Cutting torch used at {loc} on a pipeline that had not been purged of residual product.",
            "Fire extinguisher required for hot work at {loc} was expired and not replaced before the job started.",
            "Spark-generating repair at {loc} was carried out 5 metres from an open drum of flammable solvent.",
        ],
        "severity_weights": [5, 4, 5, 5, 3, 4],
    },
    "loto": {
        "label": "Lockout-Tagout Violation",
        "templates": [
            "Maintenance technician at {loc} began equipment teardown before lockout-tagout was verified by a second person.",
            "LOTO tags removed at {loc} by someone other than the technician who applied them.",
            "Equipment at {loc} was re-energized while a technician was still inside the guard enclosure.",
            "Isolation point at {loc} was locked out but the stored hydraulic pressure was never bled off first.",
            "Two crews at {loc} worked on the same line, each unaware the other had already removed a lock.",
            "A supervisor at {loc} authorised an exception to remove another technician's lock without the documented sign-off procedure.",
        ],
        "severity_weights": [4, 3, 5, 4, 4, 5],
    },
    "gas_leak": {
        "label": "Gas / Chemical Release",
        "templates": [
            "Minor ammonia leak detected near {loc}; shift log shows the same valve flagged for repair three weeks earlier.",
            "H2S sensor at {loc} triggered a low-level alarm that was acknowledged and silenced without investigation.",
            "Pressure relief valve at {loc} released process gas during a shift changeover with no handover note.",
            "Flange gasket at {loc} began weeping hydrocarbon vapour, discovered only during a routine walk-round.",
            "Chemical storage area at {loc} showed a strong odour for over an hour before anyone raised an alert.",
            "A gas sensor at {loc} had been in fault mode for two shifts before the failure was logged.",
        ],
        "severity_weights": [4, 4, 3, 3, 4, 4],
    },
    "height": {
        "label": "Working at Height",
        "templates": [
            "Worker at {loc} used a mobile scaffold without outriggers deployed on an uneven surface.",
            "Fall-arrest harness at {loc} was worn but not clipped to an anchor point during platform work.",
            "Guardrail section at {loc} was left open after material hoisting, no barricade or signage placed.",
            "Ladder used at {loc} for a 4-metre task exceeded its rated duty and was not inspected beforehand.",
            "A worker at {loc} leaned outside the fall-arrest zone to reach a valve, unclipping the lanyard briefly.",
            "Rooftop access at {loc} lacked a permanently fixed anchor point, so a temporary strap was used instead.",
        ],
        "severity_weights": [3, 5, 3, 3, 5, 3],
    },
    "electrical": {
        "label": "Electrical Isolation",
        "templates": [
            "Electrician at {loc} worked on a panel marked isolated, but downstream feeder was still live.",
            "Temporary electrical connection at {loc} bypassed the earth-fault relay during a trial run.",
            "Cable insulation damage at {loc} was reported in a shift log but not entered into the maintenance system for 9 days.",
            "A junction box at {loc} was opened for inspection without confirming absence of voltage first.",
            "Portable test equipment at {loc} was out of calibration when used to check an isolated circuit.",
            "Two isolation points at {loc} were confused during a switching operation, briefly energising the wrong panel.",
        ],
        "severity_weights": [5, 4, 3, 5, 3, 4],
    },
}

OUTCOMES = ["Near miss - no injury", "First aid only", "Minor injury - restricted duty", "Property damage only"]

def build_incidents(n_per_category=35):
    incidents = []
    idx = 1
    for cat_key, cat in CATEGORIES.items():
        for _ in range(n_per_category):
            template = random.choice(cat["templates"])
            loc = random.choice(LOCATIONS)
            severity = random.choices([1, 2, 3, 4, 5], weights=[1, 2, 3, 3, 2])[0]
            day_offset = random.randint(0, 730)
            incidents.append({
                "id": idx,
                "category": cat_key,
                "category_label": cat["label"],
                "location": loc,
                "description": template.format(loc=loc),
                "severity": severity,
                "outcome": random.choice(OUTCOMES),
                "days_ago": day_offset,
            })
            idx += 1
    random.shuffle(incidents)
    return incidents

REGULATIONS = [
    {
        "id": "OISD-STD-105-4.2",
        "source": "OISD-STD-105 (Work Permit System)",
        "text": ("Before issuing a confined space entry permit, the atmosphere shall be tested for "
                  "oxygen content, flammable gases, and toxic contaminants. Testing shall be repeated "
                  "if entry is interrupted for more than 30 minutes or if conditions change."),
    },
    {
        "id": "OISD-STD-105-4.5",
        "source": "OISD-STD-105 (Work Permit System)",
        "text": ("A hot work permit shall not be issued within the vicinity of a confirmed or suspected "
                  "flammable gas release until the area has been re-tested and cleared by an authorised "
                  "gas tester."),
    },
    {
        "id": "OISD-STD-105-5.1",
        "source": "OISD-STD-105 (Work Permit System)",
        "text": ("A standby attendant, trained in rescue procedures and equipped with communication "
                  "means, shall remain at the entry point for the entire duration of confined space work."),
    },
    {
        "id": "FactoryAct-Sec-36",
        "source": "Factories Act, 1948 - Section 36",
        "text": ("No person shall enter or be permitted to enter any confined space in which dangerous "
                  "fumes are likely to be present unless it is provided with a manhole or other "
                  "effective means of egress and appropriate breathing apparatus."),
    },
    {
        "id": "FactoryAct-Sec-38",
        "source": "Factories Act, 1948 - Section 38",
        "text": ("Effective measures shall be taken to prevent outbreak of fire and its spread, both "
                  "internally and externally, including safe means of escape and fire-fighting equipment "
                  "maintained in efficient working order."),
    },
    {
        "id": "DGMS-Circular-LOTO-1",
        "source": "DGMS Technical Circular - Lockout-Tagout",
        "text": ("Isolation of energy sources shall be verified by an independent test before work "
                  "begins. Locks and tags applied by a technician shall be removed only by that same "
                  "technician, except under a documented and authorised exception procedure."),
    },
    {
        "id": "DGMS-Circular-Height-1",
        "source": "DGMS Technical Circular - Working at Height",
        "text": ("Fall-arrest systems shall be worn and physically anchored to a rated anchor point "
                  "at all times when working above 1.8 metres where guardrails are not present."),
    },
    {
        "id": "OISD-GDN-192-3.1",
        "source": "OISD-GDN-192 (Electrical Safety)",
        "text": ("Electrical isolation shall be confirmed by testing for absence of voltage at the point "
                  "of work, not solely by inspection of the isolation point or panel labelling."),
    },
]

EVAL_QUESTIONS = [
    {"question": "What atmosphere tests are required before confined space entry?",
     "relevant_ids": ["OISD-STD-105-4.2", "FactoryAct-Sec-36"]},
    {"question": "When must confined space gas testing be repeated during a job?",
     "relevant_ids": ["OISD-STD-105-4.2"]},
    {"question": "Can hot work be permitted near a gas leak?",
     "relevant_ids": ["OISD-STD-105-4.5"]},
    {"question": "Is a standby attendant required for confined space work?",
     "relevant_ids": ["OISD-STD-105-5.1"]},
    {"question": "Who is allowed to remove a lockout-tagout lock?",
     "relevant_ids": ["DGMS-Circular-LOTO-1"]},
    {"question": "How should energy isolation be verified before maintenance work?",
     "relevant_ids": ["DGMS-Circular-LOTO-1", "OISD-GDN-192-3.1"]},
    {"question": "What fall protection is required when working above 1.8 metres?",
     "relevant_ids": ["DGMS-Circular-Height-1"]},
    {"question": "What fire safety measures are required in a factory?",
     "relevant_ids": ["FactoryAct-Sec-38"]},
    {"question": "How should electrical isolation be confirmed before work begins?",
     "relevant_ids": ["OISD-GDN-192-3.1"]},
    {"question": "What breathing apparatus rules apply to confined spaces with dangerous fumes?",
     "relevant_ids": ["FactoryAct-Sec-36"]},
]

if __name__ == "__main__":
    incidents = build_incidents()
    OUT_INCIDENTS.write_text(json.dumps(incidents, indent=2))
    OUT_REGULATIONS.write_text(json.dumps(REGULATIONS, indent=2))
    OUT_EVAL.write_text(json.dumps(EVAL_QUESTIONS, indent=2))
    print(f"Wrote {len(incidents)} incidents to {OUT_INCIDENTS}")
    print(f"Wrote {len(REGULATIONS)} regulation excerpts to {OUT_REGULATIONS}")
    print(f"Wrote {len(EVAL_QUESTIONS)} eval questions to {OUT_EVAL}")
