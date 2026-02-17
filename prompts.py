from langchain_core.prompts import PromptTemplate

prompt_v1 = PromptTemplate(
    input_variables=["question", "port_codes"],
    template="""
You extract structured logistics data from emails.

Hard rules:
- Return ONLY valid JSON 
- No markdown, no explanations, no extra text

Domain rules:
- Product line:
  - India as origin → pl_sea_export_lcl
  - India as destination → pl_sea_import_lcl
- India ports have UN/LOCODE starting with "IN"
- Incoterm:
  - Unrecognizable or ambiguous → FOB
  - normalize to uppercase
- Missing / unknown values → null
- Explicit zero (e.g. "0 kg") → 0
- UN/LOCODE format: CCXXX (5 letters)

Ports:
- Use canonical port names strictly from PORT_CODES
- Multiple destinations → body order, canonical names joined by " / "
- If port_code is null → port_name must be null

Dangerous goods:
- true if contains: DG, dangerous, hazardous, IMO, IMDG, Class + number
- false if negated: non-DG, non-hazardous, not dangerous
- default → false

Extraction rules:
- Body overrides subject
- First shipment only if multiple
- Use origin → destination only (ignore transshipment)
- Weight / CBM:
  - Weight and CBM must be positive numbers or null
  - "TBD", "N/A", "to be confirmed" → extract as null
  - Explicit zero (e.g., "0 kg") → extract as 0, not null
  - round to 1 decimal
  - lbs → kg (× 0.453592)
  - tonnes/MT → kg (× 1000)
  - dimensions → CBM = null
  - extract weight and CBM independently

PORT_CODES (canonical):
{port_codes}

EMAIL (JSON):
{question}
"""
)

prompt_v2 = PromptTemplate(
    input_variables=["question", "port_codes"],
    template="""
You extract structured logistics data from emails.

Hard rules:
- Return ONLY valid JSON 
- No markdown, no explanations, no extra text

Ports:
- Extract origin and destination port names exactly as written in the email.
- Normalize to canonical names using PORT_CODES list.
- If not confidently matched to a canonical name, return null.

Domain rules:
- Product line:
  - India as origin → pl_sea_export_lcl
  - India as destination → pl_sea_import_lcl
- Incoterm:
  - Unrecognizable or ambiguous → FOB
  - normalize to uppercase
- Missing / unknown values → null
- Explicit zero (e.g. "0 kg") → 0

Dangerous goods:
- true if contains: DG, dangerous, hazardous, IMO, IMDG, Class + number
- false if negated: non-DG, non-hazardous, not dangerous
- default → false

Extraction rules:
- Body overrides subject
- First shipment only if multiple
- Use origin → destination only (ignore transshipment)
- Weight / CBM:
  - Weight and CBM must be positive numbers or null
  - "TBD", "N/A", "to be confirmed" → extract as null
  - Explicit zero (e.g., "0 kg") → extract as 0, not null
  - round to 1 decimal
  - lbs → kg (× 0.453592)
  - tonnes/MT → kg (× 1000)
  - dimensions → CBM = null
  - extract weight and CBM independently

PORT_CODES:
{port_codes}

EMAIL (JSON):
{question}
"""
)

prompt_v3 = PromptTemplate(
    input_variables=["email", "port_codes"],
    template="""
You extract structured freight forwarding shipment data from pricing enquiry emails.

Your task is to analyze the EMAIL (JSON) and return structured shipment data.

----------------------------------------------------
OUTPUT REQUIREMENTS
----------------------------------------------------
- Return ONLY valid JSON.
- No markdown.
- No explanations.
- No extra text.
- All fields must be present.
- Missing values must be null (not empty string, not 0 unless explicitly stated).

----------------------------------------------------
BUSINESS RULES
----------------------------------------------------

PRODUCT LINE:
- If destination port is in India → "pl_sea_import_lcl"
- If origin port is in India → "pl_sea_export_lcl"
- All shipments are LCL.

INDIA DETECTION:
- Indian ports have UN/LOCODE starting with "IN".

INCOTERMS:
- Recognize and normalize to uppercase:
  FOB, CIF, CFR, EXW, DDP, DAP, FCA, CPT, CIP, DPU
- If not mentioned → default to "FOB".
- If ambiguous (e.g., "FOB or CIF") → default to "FOB".

DANGEROUS GOODS:
- true if contains: DG, dangerous, hazardous, IMO, IMDG, "Class" + number.
- false if contains negation: non-hazardous, non hazardous, non-DG, not dangerous.
- If no mention → false.

CONFLICT RESOLUTION:
- Body overrides subject.
- If multiple shipments mentioned → extract the FIRST shipment only.
- If multiple ports mentioned → use origin → destination pair only (ignore transshipment/intermediate ports).

----------------------------------------------------
PORT MATCHING RULES
----------------------------------------------------

You are provided PORT_CODES_REFERENCE.

Each entry has:
- code: 5-letter UN/LOCODE
- name: canonical port name

Rules:
- Match origin and destination ports to the correct UN/LOCODE.
- UN/LOCODE format: 5 letters (2-letter country + 3-letter location).
- Always return the canonical port name from PORT_CODES_REFERENCE.
- If no confident match → return null for both code and name.
- If code is null → name must be null.
- Handle common abbreviations (e.g., HK → Hong Kong).
- Some ports may have multiple name variations mapping to the same code.

----------------------------------------------------
NUMERIC EXTRACTION RULES
----------------------------------------------------

WEIGHT:
- Must be positive number or null.
- Round to 2 decimal places.
- lbs → convert to kg using: lbs × 0.453592
- tonnes / MT → kg × 1000
- "TBD", "N/A", "to be confirmed" → null
- Explicit zero (e.g., "0 kg") → 0

CBM:
- Must be positive number or null.
- Round to 2 decimal places.
- If dimensions (L×W×H) provided → cargo_cbm = null (do not calculate).
- If both weight and CBM present → extract both independently.

----------------------------------------------------
OUTPUT SCHEMA (STRICT)
----------------------------------------------------

Return exactly this structure:

{{
  "id": string,
  "product_line": string,
  "origin_port_code": string | null,
  "origin_port_name": string | null,
  "destination_port_code": string | null,
  "destination_port_name": string | null,
  "incoterm": string,
  "cargo_weight_kg": number | null,
  "cargo_cbm": number | null,
  "is_dangerous": boolean
}}

----------------------------------------------------
PORT_CODES_REFERENCE
----------------------------------------------------
{port_codes}

----------------------------------------------------
EMAIL (JSON)
----------------------------------------------------
{email}
"""
)





