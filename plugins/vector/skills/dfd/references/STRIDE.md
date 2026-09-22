# STRIDE Threat Catalogue

Named attack patterns grouped by the STRIDE category they fall under, each
anchored to [CAPEC](https://capec.mitre.org/) where one exists —
`CAPEC-nnn` resolves to `https://capec.mitre.org/data/definitions/nnn.html`.

This is a catalogue of what to look for, not a mapping of what applies where.
Which categories apply to which element is `threat-mapping.md`'s job, and only
its job: two applicability tables that can disagree is the failure this file is
deliberately shaped to avoid. Entries carry no severity either — STRIDE
supplies no likelihood or impact model, so a rating here would be decoration
that invites false confidence.

A dash in the CAPEC column means the pattern has no CAPEC entry, not that it
matters less. Coverage is uneven by category: repudiation has one entry, and
patterns for data stores and data flows are far thinner than for processes.
Cite one when it fits and write the finding out in full when it does not.

The `LLM` entries are this catalogue's own, which is why none of them carries a
CAPEC. They are filed by **what the injection buys rather than by the
mechanism**, because the mechanism is the same one every time and the category
is not: text a component was told to read, read instead as direction. Where that
reaches authority — a tool call, a privileged action, a config it can rewrite —
it is `LLM01` or `LLM02` under elevation of privilege. Where the component holds
no authority at all and the only casualty is its own answer, it is `LLM10` under
tampering. An id belongs to one category here, so two ids is the only way to say
both, and citing the half that does not match the finding's category is what
`check_coverage.py` refuses.

## S — Spoofing

Violates **authentication**.

| ID | Attack pattern | CAPEC |
| :--- | :--- | :--- |
| AA01 | Authentication Abuse/ByPass | CAPEC-114 |
| AA02 | Principal Spoof | CAPEC-195 |
| AA03 | Exploitation of Trusted Credentials | CAPEC-21 |
| AA04 | Exploiting Trust in Client | CAPEC-22 |
| AC05 | Content Spoofing | CAPEC-148 |
| AC11 | Session Credential Falsification through Manipulation | CAPEC-226 |
| AC16 | Session Credential Falsification through Prediction | CAPEC-59 |
| AC17 | Session Hijacking - ServerSide | CAPEC-593 |
| AC18 | Session Hijacking - ClientSide | CAPEC-593 |
| AC19 | Reusing Session IDs (aka Session Replay) - ServerSide | CAPEC-60 |
| AC20 | Reusing Session IDs (aka Session Replay) - ClientSide | CAPEC-60 |
| AC21 | Cross Site Request Forgery | CAPEC-62 |
| AC22 | Credentials Aging | — |
| AC23 | Credentials Disclosure | — |
| AC24 | Use of hardcoded credentials | — |
| CR01 | Session Sidejacking | CAPEC-102 |
| CR03 | Dictionary-based Password Attack | CAPEC-16 |
| CR04 | Session Credential Falsification through Forging | CAPEC-196 |
| CR05 | Encryption Brute Forcing | CAPEC-20 |
| SC01 | JSON Hijacking (aka JavaScript Hijacking) | CAPEC-111 |

## T — Tampering

Violates **integrity**.

| ID | Attack pattern | CAPEC |
| :--- | :--- | :--- |
| AC02 | Shared Data Manipulation | CAPEC-124 |
| AC04 | XML Schema Poisoning | CAPEC-146 |
| AC08 | Manipulate Registry Information | CAPEC-203 |
| AC15 | Schema Poisoning | CAPEC-271 |
| CR06 | Communication Channel Manipulation | CAPEC-216 |
| CR07 | XML Routing Detour Attacks | CAPEC-219 |
| CR08 | Client-Server Protocol Manipulation | CAPEC-220 |
| DE02 | Double Encoding | CAPEC-120 |
| INP03 | Server Side Include (SSI) Injection | CAPEC-101 |
| INP04 | HTTP Request Splitting | CAPEC-105 |
| INP06 | SQL Injection through SOAP Parameter Tampering | CAPEC-110 |
| INP07 | Buffer Manipulation | CAPEC-123 |
| INP10 | Parameter Injection | CAPEC-137 |
| INP14 | Input Data Manipulation | CAPEC-153 |
| INP17 | XSS Using MIME Type Mismatch | — |
| INP20 | iFrame Overlay | CAPEC-222 |
| INP21 | DTD Injection | CAPEC-228 |
| INP23 | File Content Injection | CAPEC-23 |
| INP27 | XSS Targeting HTML Attributes | CAPEC-243 |
| INP28 | XSS Targeting URI Placeholders | CAPEC-244 |
| INP29 | XSS Using Doubled Characters | CAPEC-245 |
| INP30 | XSS Using Invalid Characters | CAPEC-247 |
| INP32 | XML Injection | CAPEC-250 |
| INP35 | Leverage Alternate Encoding | CAPEC-267 |
| INP36 | HTTP Response Smuggling | CAPEC-273 |
| INP37 | HTTP Request Smuggling | CAPEC-33 |
| INP38 | DOM-Based XSS | CAPEC-588 |
| INP39 | Reflected XSS | CAPEC-591 |
| INP40 | Stored XSS | CAPEC-592 |
| LB01 | API Manipulation | CAPEC-113 |
| LLM04 | Training Data Poisoning | — |
| LLM10 | Output Manipulation via Injected Content | — |
| SC02 | XSS Targeting Non-Script Elements | CAPEC-18 |
| SC03 | Embedding Scripts within Scripts | CAPEC-19 |
| SC04 | XSS Using Alternate Syntax | CAPEC-199 |
| SC05 | Removing Important Client Functionality | — |

## R — Repudiation

Violates **non-repudiation**.

| ID | Attack pattern | CAPEC |
| :--- | :--- | :--- |
| DE04 | Audit Log Manipulation | CAPEC-268 |

## I — Information Disclosure

Violates **confidentiality**.

| ID | Attack pattern | CAPEC |
| :--- | :--- | :--- |
| AC10 | Exploiting Incorrectly Configured SSL | CAPEC-217 |
| CR02 | Cross Site Tracing | CAPEC-107 |
| DE01 | Interception | CAPEC-117 |
| DE03 | Sniffing Attacks | CAPEC-157 |
| DR01 | Unprotected Sensitive Data | — |
| DS01 | Excavation | CAPEC-116 |
| DS02 | Try All Common Switches | CAPEC-133 |
| DS03 | Footprinting | CAPEC-169 |
| DS04 | XSS Targeting Error Pages | CAPEC-198 |
| DS05 | Lifting Sensitive Data Embedded in Cache | CAPEC-204 |
| DS06 | Data Leak | — |
| HA01 | Path Traversal | CAPEC-126 |
| HA02 | White Box Reverse Engineering | CAPEC-167 |
| HA03 | Web Application Fingerprinting | CAPEC-170 |
| HA04 | Reverse Engineering | CAPEC-188 |
| INP11 | Relative Path Traversal | CAPEC-139 |
| INP18 | Fuzzing and observing application log data/errors for application mapping | CAPEC-215 |
| LLM03 | Sensitive Data Leakage to Third-Party Provider | — |
| LLM08 | Sensitive Information Disclosure Through Output | — |

## D — Denial of Service

Violates **availability**.

| ID | Attack pattern | CAPEC |
| :--- | :--- | :--- |
| DO01 | Flooding | CAPEC-125 |
| DO02 | Excessive Allocation | CAPEC-130 |
| DO03 | XML Ping of the Death | CAPEC-147 |
| DO04 | XML Entity Expansion | CAPEC-197 |
| DO05 | XML Nested Payloads | CAPEC-230 |
| INP19 | XML External Entities Blowup | CAPEC-221 |
| INP22 | XML Attribute Blowup | CAPEC-229 |
| INP34 | SOAP Array Overflow | CAPEC-256 |

## E — Elevation of Privilege

Violates **authorisation**.

| ID | Attack pattern | CAPEC |
| :--- | :--- | :--- |
| AC01 | Privilege Abuse | CAPEC-122 |
| AC03 | Subverting Environment Variable Values | CAPEC-13 |
| AC06 | Using Malicious Files | CAPEC-17 |
| AC07 | Exploiting Incorrectly Configured Access Control Security Levels | CAPEC-180 |
| AC09 | Functionality Misuse | CAPEC-212 |
| AC12 | Privilege Escalation | CAPEC-233 |
| AC13 | Hijacking a privileged process | CAPEC-234 |
| AC14 | Catching exception throw/signal from privileged block | CAPEC-236 |
| API01 | Exploit Test APIs | CAPEC-121 |
| API02 | Exploit Script-Based APIs | CAPEC-160 |
| INP01 | Buffer Overflow via Environment Variables | CAPEC-10 |
| INP02 | Overflow Buffers | CAPEC-100 |
| INP05 | Command Line Execution through SQL Injection | CAPEC-108 |
| INP08 | Format String Injection | CAPEC-135 |
| INP09 | LDAP Injection | CAPEC-136 |
| INP12 | Client-side Injection-induced Buffer Overflow | CAPEC-14 |
| INP13 | Command Delimiters | CAPEC-15 |
| INP15 | IMAP/SMTP Command Injection | CAPEC-183 |
| INP16 | PHP Remote File Inclusion | CAPEC-193 |
| INP24 | Filter Failure through Buffer Overflow | CAPEC-24 |
| INP25 | Resource Injection | CAPEC-240 |
| INP26 | Code Injection | CAPEC-242 |
| INP31 | Command Injection | CAPEC-248 |
| INP33 | Remote Code Inclusion | CAPEC-253 |
| INP41 | Argument Injection | CAPEC-6 |
| LLM01 | Direct Prompt Injection | — |
| LLM02 | Indirect Prompt Injection via Retrieved Content | — |
| LLM05 | Excessive Agency via Unauthorized Tool Use | — |
| LLM06 | Arbitrary Code Execution via LLM Agent | — |
| LLM07 | Jailbreaking and Safety Bypass | — |
| LLM09 | Untrusted Tool Launch Configuration | — |

