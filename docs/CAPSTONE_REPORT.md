![ASU Logo](./asu_logo.png)

# Autonomous OSINT Investigation Swarm: A Multi-Agent AI System for Financial Risk Assessment

**FSE 570 Data Science Capstone Project**
**Team Members:** Taljinder Singh, Aditya Pokharna, Raj Kumar Mahto, Arnab Mitra, Jacob Kuriakose
**Date:** April 23, 2026

---

<div align="right"><img src="./asu_logo.png" width="200" /></div>

## Abstract

This paper presents the Autonomous Open-Source Intelligence (OSINT) Investigation Swarm, a multi-agent AI framework designed to accelerate corporate Anti-Money Laundering (AML) and financial risk assessment workflows. Leveraging a Model Context Protocol (MCP) cache-first architecture, the system queries four diverse, large-scale public data sources—SEC EDGAR, OFAC SDN, CourtListener, and GDELT—to synthesize actionable risk reports. The integration of advanced Machine Learning methodologies, specifically a Large Language Model (Llama 3.1) for strict policy orchestration and a Reflexion layer for gap detection and cross-validation, allows the system to achieve a ~3,100x speedup in investigation time compared to manual analyst workflows. NetworkX-driven graph analytics provide deep relational insights, achieving a 98% citation integrity rate. The developed application drastically reduces the burden of compliance, proving highly applicable to modern banking and financial security operations.

---

<div align="right"><img src="./asu_logo.png" width="200" /></div>

## 1. Introduction

Financial institutions face increasing regulatory scrutiny, demanding exhaustive Anti-Money Laundering (AML) and Know Your Customer (KYC) investigations. Traditionally, a compliance analyst spends approximately 2.5 hours aggregating evidence across disparate governmental and news databases. This manual workflow is highly susceptible to human error, coverage gaps, and slow turnaround times.

This project introduces the **Autonomous OSINT Investigation Swarm**, a modular, multi-agent AI application designed to automate this exact workflow. By receiving a plain-English query, the system dynamically orchestrates data retrieval, executes cross-source validation, constructs a knowledge graph of relational risks, and generates an audit-ready narrative report—all in under four seconds. The solution emphasizes source-grounded determinism alongside advanced Large Language Model (LLM) orchestration, ensuring that all findings are fully auditable and legally defensible.

---

<div align="right"><img src="./asu_logo.png" width="200" /></div>

## 2. Data Sources and Data Analysis

The system integrates four highly heterogeneous data sources to generate a comprehensive risk profile. These sources span structured government filings, semi-structured court dockets, raw XML sanctions lists, and unstructured global media.

### 2.1 Heterogeneous Data Integration
1. **SEC EDGAR (US Public Company Filings):** Provides corporate governance data via JSON API. It acts as the anchor for corporate risk assessment, supplying 10-K, 8-K, Form 4, and DEF 14A disclosures.
2. **OFAC SDN (US Treasury Sanctions List):** A 27 MB structured XML dataset containing 18,712 sanctioned entities globally.
3. **CourtListener (RECAP):** Provides access to US federal court dockets via REST API, critical for identifying active or past corporate litigation.
4. **GDELT DOC 2.0:** A global database of adverse media and news events.

### 2.2 Data Cleaning, Preprocessing, and Handling
To ensure high-performance execution without API rate-limit bottlenecks, the system employs a **Model Context Protocol (MCP) cache-first layer**.
- **Caching Mechanism:** All retrieved data is stored locally in `.json` or `.xml` formats. If a query matches an existing entity, data is instantly loaded from the cache.
- **Preprocessing:** The `GdeltProcessor` rigorously filters news items, discarding non-English articles to reduce noise. It also applies a relevance threshold based on the co-occurrence of the entity name and risk keywords (e.g., "fraud", "penalty") within the headline.
- **Entity Resolution:** To normalize data across sources, the system resolves any plain-English company name (e.g., "Microsoft") to its official SEC Central Index Key (CIK) using EDGAR’s full-text search index, enabling automated normalization across all retrieved records.

---

<div align="right"><img src="./asu_logo.png" width="200" /></div>

## 3. Methodology and Application

The architecture is divided into a deterministic evidence retrieval pipeline and a probabilistic LLM-orchestrated synthesis layer. This dual-layered approach maximizes accuracy and minimizes hallucinations.

### 3.1 Multi-Agent Architecture
The system employs three specialized AI agents managed by a central **Lead Agent**:
- **Corporate Agent:** Ingests SEC EDGAR data, calculating tiered confidence scores based on filing materiality (e.g., 8-K scores 0.95; Form 4 scores 0.75).
- **Legal Agent:** Executes exact and fuzzy matching algorithms against the OFAC sanctions XML and CourtListener APIs. Suffixes like "Inc" or "LLC" are stripped prior to comparison to minimize false negatives, while rigid false-positive guards prevent generic matches.
- **Social Graph Agent:** Retrieves and scores adverse media from GDELT, prioritizing high-signal alerts.

### 3.2 Advanced Machine Learning and Validation Techniques
- **LLM Orchestration (Llama 3.1):** Llama 3.1-8b-instant provides strict, bounded planning. The LLM dictates tool selection (`action_policy`), follows stopping criteria (`orchestrator`), and generates the final narrative. To prevent hallucinations, the LLM is restricted to observing aggregated metrics, strictly isolated from raw evidence generation.
- **Reflexion Layer:** An automated self-correction and validation module. It executes cross-checks (flagging conflicting evidence summaries on the same date) and gap detection (identifying missing data lanes).
- **Knowledge Graph Analytics:** The pipeline constructs a deterministic graph of the entity and its evidence using **NetworkX**. It calculates **degree centrality** and connected components, effectively mapping out tightly-linked risk clusters and identifying the hub nodes of systemic issues.

---

<div align="right"><img src="./asu_logo.png" width="200" /></div>

## 4. Results, Visualizations, and Recommendations

### 4.1 System Performance and Evaluation Metrics
Extensive evaluation across five diverse public companies (Tesla, Ford, Boeing, Alphabet, JPMorgan) yielded the following results:
- **Investigation Speedup:** Average runtime is 2.67 seconds per entity, producing ~1,010 evidence rows. This represents a **3,100x speedup** over the manual benchmark of ~2.5 hours.
- **Citation Integrity:** The system achieves a **97.7% average citation rate**, maintaining strict auditability.
- **Adverse Media Signal Rate:** The targeted GDELT processing achieved a 74% average signal rate, peaking at 100% relevance for JPMorgan.

### 4.2 Visual Outputs and Dashboarding
The results are presented via a Flask web application, featuring:
- **Risk Dashboards:** Presenting unified confidence scores across Governance, Regulatory, Legal, and Network categories.
- **Interactive Knowledge Graphs:** A dynamic `vis-network` canvas visualizes the NetworkX graph. Nodes are color-coded by source (Blue for SEC, Red for Sanctions, etc.), allowing analysts to visually isolate dense risk clusters.

### 4.3 Actionable Recommendations for Compliance Teams
Based on the data output, we recommend that financial institutions adopting this architecture:
1. **Implement Automated Pre-Screening:** Route all Level 1 KYC/AML checks through the OSINT Swarm. Analysts should only intervene when the Risk Category confidence scores exceed 0.80 or when specific Reflexion gaps are triggered.
2. **Utilize Graph Centrality for Deep Investigations:** Instead of reading linear evidence, compliance teams should prioritize review of the "Top 5 Most-Connected Nodes" generated by the NetworkX analysis, as these represent recursive or compounding risk events.
3. **Audit Trail Archiving:** Maintain the JSON-lines audit trail output for regulatory compliance reviews, ensuring full transparency of the AI’s decision-making process.

---

<div align="right"><img src="./asu_logo.png" width="200" /></div>

## 5. Conclusion

The Autonomous OSINT Investigation Swarm successfully bridges the gap between deterministic legal auditing and probabilistic AI orchestration. By fusing highly reliable data retrieval pipelines with Llama 3.1-powered synthesis and NetworkX graph analysis, the system dramatically accelerates AML operations. The framework not only demonstrates a 3,100x reduction in task duration but also maintains the strict 98% evidentiary citation integrity required in real-world financial risk management environments.

---

<div align="right"><img src="./asu_logo.png" width="200" /></div>

## References

1. Securities and Exchange Commission (SEC) EDGAR Database API. *https://data.sec.gov*
2. US Department of the Treasury. Office of Foreign Assets Control (OFAC) Specially Designated Nationals List. *https://www.treasury.gov/ofac*
3. Free Law Project. CourtListener RECAP API. *https://www.courtlistener.com*
4. The GDELT Project. Global Database of Events, Language, and Tone DOC 2.0 API. *https://api.gdeltproject.org*
5. NetworkX Graph Analytics Documentation. *https://networkx.org*
6. Groq Llama 3.1-8b API Integration. *https://console.groq.com*
