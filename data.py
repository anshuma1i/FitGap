"""Synthetic data for the FitGap demo — 50 assignments, 10 candidates, 5 domains.

Domains (10 assignments each):
  1. Finance & Accounting
  2. Data & AI
  3. Software Engineering
  4. Cloud & Infrastructure
  5. Product & Delivery

Candidates: 2 per domain, free-text blurbs. Skills are extracted at match time.
"""

from typing import TypedDict


class Assignment(TypedDict):
    id: str
    title: str
    description: str
    required_skills: list[str]
    nice_to_have: list[str]


# ---- Canonical skill vocabulary (~80, lowercased) --------------------------
# Single source of truth: every assignment and keyword extraction references
# this list. In prod this comes from a curated taxonomy / ATS tag system.
CANONICAL_SKILLS: list[str] = [
    # Programming languages
    "python", "sql", "java", "javascript", "typescript", "c++", "c#", ".net",
    "abap", "go", "rust", "swift", "kotlin",
    # Web / frameworks
    "react", "react native", "next.js", "spring boot", "node.js", "fastapi",
    "rest api", "graphql",
    # Cloud platforms
    "aws", "azure", "gcp",
    # Infrastructure / DevOps
    "kubernetes", "docker", "terraform", "linux", "ci/cd", "gitlab ci",
    "ansible", "nginx", "prometheus", "grafana", "splunk", "elasticsearch",
    "helm",
    # Data platform
    "airflow", "databricks", "spark", "kafka", "snowflake", "etl",
    "postgresql", "mongodb", "redis", "sql server", "hadoop", "dbt",
    # ML / AI
    "pytorch", "tensorflow", "machine learning", "mlops", "statistics",
    "mlflow", "langchain", "llm", "deep learning",
    # BI / analytics
    "power bi", "tableau", "dax", "data modeling", "looker",
    # Finance / accounting
    "ifrs", "sap", "month-end close", "financial planning", "m&a",
    "audit", "financial modeling", "variance analysis", "consolidation",
    "transfer pricing", "accounts payable", "payroll",
    # Process / delivery
    "scrum", "jira", "stakeholder management", "business process",
    "confluence",
    # Testing
    "selenium", "cypress", "junit",
    # Security
    "siem", "penetration testing", "incident response", "iso 27001",
    # CRM / enterprise
    "salesforce", "apex", "service now",
    # Design
    "figma", "user research",
    # Languages (nice-to-have only in most roles)
    "dutch", "english",
    # Misc
    "okta",
]


# ---- 50 assignments (10 per domain) ----------------------------------------

ASSIGNMENTS: list[Assignment] = [
    # =====================================================================
    # DOMAIN 1: Finance & Accounting (ASG-001 to ASG-010)
    # =====================================================================
    {
        "id": "ASG-001",
        "title": "Interim Finance Controller",
        "description": (
            "PE-backed manufacturing group needs an interim controller to "
            "stabilise month-end close and reporting during a finance "
            "transformation. Hands-on with SAP, owns IFRS-compliant statements."
        ),
        "required_skills": ["ifrs", "sap", "month-end close"],
        "nice_to_have": ["power bi", "dutch"],
    },
    {
        "id": "ASG-002",
        "title": "Interim CFO",
        "description": (
            "Interim CFO for a scale-up preparing for a Series C raise. Lead "
            "financial planning, IFRS reporting, and M&A workstreams; manage "
            "investor and board stakeholders."
        ),
        "required_skills": ["financial planning", "ifrs", "m&a", "stakeholder management"],
        "nice_to_have": ["audit", "dutch"],
    },
    {
        "id": "ASG-003",
        "title": "SAP FICO Consultant",
        "description": (
            "Functional SAP consultant on the FI/CO module for an S/4HANA "
            "rollout. Configure, document, and align with business process "
            "owners. Some ABAP debugging expected."
        ),
        "required_skills": ["sap", "abap", "business process"],
        "nice_to_have": ["ifrs", "dutch"],
    },
    {
        "id": "ASG-004",
        "title": "Financial Planning Analyst",
        "description": (
            "FP&A analyst for a consumer goods group. Own the annual budgeting "
            "cycle, run variance analysis against actuals, build financial "
            "models for new product launches. Heavy Excel and Power BI."
        ),
        "required_skills": ["financial planning", "financial modeling", "variance analysis"],
        "nice_to_have": ["power bi", "dax"],
    },
    {
        "id": "ASG-005",
        "title": "External Auditor",
        "description": (
            "Statutory audit senior for Big 4 firm, seconded to a listed "
            "client. IFRS audit procedures, consolidation review, SOX testing. "
            "Client-facing, deadline-driven environment."
        ),
        "required_skills": ["audit", "ifrs", "consolidation"],
        "nice_to_have": ["sql", "stakeholder management"],
    },
    {
        "id": "ASG-006",
        "title": "Tax Specialist",
        "description": (
            "In-house tax specialist for a multinational. Own transfer pricing "
            "documentation, corporate income tax filings, and VAT compliance "
            "across 6 EU jurisdictions."
        ),
        "required_skills": ["transfer pricing", "ifrs"],
        "nice_to_have": ["dutch", "english"],
    },
    {
        "id": "ASG-007",
        "title": "FP&A Manager",
        "description": (
            "Lead the FP&A function for a SaaS business. Drive annual planning, "
            "rolling forecasts, board reporting, and scenario analysis. Partner "
            "with CFO and department heads on resource allocation."
        ),
        "required_skills": ["financial planning", "financial modeling", "stakeholder management"],
        "nice_to_have": ["power bi", "data modeling"],
    },
    {
        "id": "ASG-008",
        "title": "Accounts Payable Lead",
        "description": (
            "Manage a 4-person AP team during an ERP migration. Oversee invoice "
            "processing, payment runs, vendor reconciliation. SAP experience "
            "critical for the migration workstream."
        ),
        "required_skills": ["accounts payable", "sap"],
        "nice_to_have": ["business process", "dutch"],
    },
    {
        "id": "ASG-009",
        "title": "Payroll Specialist",
        "description": (
            "End-to-end payroll for 800 employees across the Netherlands and "
            "Belgium. Handle tax filings, pension administration, and "
            "year-end reporting. Experience with Dutch payroll legislation."
        ),
        "required_skills": ["payroll", "dutch"],
        "nice_to_have": ["sap", "english"],
    },
    {
        "id": "ASG-010",
        "title": "M&A Analyst",
        "description": (
            "M&A execution analyst for a corporate development team. Build "
            "financial models, run due diligence workstreams, prepare "
            "investment committee memos. Transaction experience required."
        ),
        "required_skills": ["m&a", "financial modeling", "ifrs"],
        "nice_to_have": ["stakeholder management", "power bi"],
    },

    # =====================================================================
    # DOMAIN 2: Data & AI (ASG-011 to ASG-020)
    # =====================================================================
    {
        "id": "ASG-011",
        "title": "Senior Data Engineer",
        "description": (
            "Build and own production data pipelines on Databricks and AWS. "
            "Daily Python and SQL, Airflow orchestration, Snowflake warehouse. "
            "Partner with analytics and ML teams on schema design and SLAs."
        ),
        "required_skills": ["python", "sql", "databricks", "airflow", "aws"],
        "nice_to_have": ["snowflake", "kafka", "terraform"],
    },
    {
        "id": "ASG-012",
        "title": "Machine Learning Engineer",
        "description": (
            "Ship ML models to production: training in PyTorch, deployment on "
            "AWS, MLOps tooling for monitoring and rollback. Python and SQL "
            "daily, partner with data engineering on features."
        ),
        "required_skills": ["python", "pytorch", "mlops", "aws", "sql"],
        "nice_to_have": ["machine learning", "databricks"],
    },
    {
        "id": "ASG-013",
        "title": "Data Scientist",
        "description": (
            "End-to-end data science for a retail analytics team. Python, "
            "SQL, classical machine learning and statistics; partner with the "
            "data engineering team for production hand-off."
        ),
        "required_skills": ["python", "sql", "machine learning", "statistics"],
        "nice_to_have": ["pytorch", "databricks"],
    },
    {
        "id": "ASG-014",
        "title": "AI Engineer",
        "description": (
            "Build LLM-powered features for a customer support platform. "
            "Fine-tune open-source models, design RAG pipelines with LangChain, "
            "deploy inference endpoints on AWS. Strong Python and prompt "
            "engineering skills."
        ),
        "required_skills": ["python", "llm", "langchain", "aws"],
        "nice_to_have": ["pytorch", "deep learning"],
    },
    {
        "id": "ASG-015",
        "title": "MLOps Engineer",
        "description": (
            "Own the ML platform: model registry, feature store, automated "
            "retraining pipelines. MLflow for experiment tracking, Kubernetes "
            "for serving, Databricks for training. Strong Python and infra "
            "background."
        ),
        "required_skills": ["mlops", "mlflow", "python", "kubernetes"],
        "nice_to_have": ["databricks", "aws"],
    },
    {
        "id": "ASG-016",
        "title": "Data Analyst",
        "description": (
            "Embedded data analyst for the marketing team. Write SQL to answer "
            "campaign performance questions, build Looker dashboards, run A/B "
            "test analysis. Strong storytelling with data."
        ),
        "required_skills": ["sql", "looker"],
        "nice_to_have": ["python", "statistics"],
    },
    {
        "id": "ASG-017",
        "title": "BI Developer",
        "description": (
            "Build executive dashboards and self-service semantic models in "
            "Power BI. Strong DAX, solid SQL, hands-on data modeling for a "
            "finance audience. Manage the BI workspace and refresh schedules."
        ),
        "required_skills": ["power bi", "dax", "sql", "data modeling"],
        "nice_to_have": ["tableau", "azure"],
    },
    {
        "id": "ASG-018",
        "title": "Data Architect",
        "description": (
            "Design the target data architecture for a cloud migration from "
            "on-prem SQL Server to Snowflake on AWS. Define data modeling "
            "standards, governance, and ingestion patterns for structured "
            "and semi-structured data."
        ),
        "required_skills": ["data modeling", "sql", "snowflake", "aws"],
        "nice_to_have": ["sql server", "airflow"],
    },
    {
        "id": "ASG-019",
        "title": "Analytics Engineer",
        "description": (
            "Build curated data models in dbt on Snowflake for the analytics "
            "layer. Own transformations, testing, and documentation. Write "
            "performant SQL, partner with data analysts on metric definitions."
        ),
        "required_skills": ["sql", "snowflake", "data modeling", "dbt"],
        "nice_to_have": ["python", "airflow"],
    },
    {
        "id": "ASG-020",
        "title": "NLP Engineer",
        "description": (
            "Build text classification and entity extraction pipelines for a "
            "legal-tech product. Python, PyTorch, transformer model fine-tuning, "
            "deployed on AWS with MLOps practices."
        ),
        "required_skills": ["python", "pytorch", "deep learning", "mlops"],
        "nice_to_have": ["aws", "llm"],
    },

    # =====================================================================
    # DOMAIN 3: Software Engineering (ASG-021 to ASG-030)
    # =====================================================================
    {
        "id": "ASG-021",
        "title": "Frontend Developer (React)",
        "description": (
            "Senior React/TypeScript developer for a customer portal rebuild. "
            "Strong CSS, accessibility-minded, comfortable owning the design "
            "system end-to-end."
        ),
        "required_skills": ["react", "typescript", "javascript"],
        "nice_to_have": ["node.js", "figma"],
    },
    {
        "id": "ASG-022",
        "title": "Backend Developer (Java / Spring)",
        "description": (
            "Backend developer for an event-driven order platform. Java with "
            "Spring Boot, SQL, Kafka for inter-service messaging. Strong "
            "ownership and testing culture, REST and GraphQL APIs."
        ),
        "required_skills": ["java", "spring boot", "sql", "kafka"],
        "nice_to_have": ["ci/cd", "aws", "graphql"],
    },
    {
        "id": "ASG-023",
        "title": "Full-Stack Developer (Next.js / Node)",
        "description": (
            "Full-stack developer for a B2B SaaS product. Next.js frontend, "
            "Node.js/TypeScript backend on AWS Lambda, PostgreSQL. Own features "
            "from API design through deployment."
        ),
        "required_skills": ["next.js", "typescript", "node.js", "postgresql"],
        "nice_to_have": ["react", "aws"],
    },
    {
        "id": "ASG-024",
        "title": "Mobile Developer (React Native)",
        "description": (
            "Build cross-platform mobile features for a fintech app using "
            "React Native and TypeScript. Integrate REST APIs, manage offline "
            "state, and own the release pipeline for iOS and Android."
        ),
        "required_skills": ["react native", "typescript", "rest api"],
        "nice_to_have": ["javascript", "ci/cd"],
    },
    {
        "id": "ASG-025",
        "title": ".NET Developer",
        "description": (
            "Maintain and extend a .NET 8 / C# microservices platform for an "
            "insurance client. SQL Server backend, Azure DevOps pipelines, "
            "REST APIs. Strong testing discipline with xUnit."
        ),
        "required_skills": [".net", "c#", "sql server", "azure"],
        "nice_to_have": ["docker", "rest api"],
    },
    {
        "id": "ASG-026",
        "title": "QA Automation Engineer",
        "description": (
            "Build test automation for a web platform. Selenium / Cypress for "
            "UI tests, JUnit for API contract tests, integrated into the CI/CD "
            "pipeline. Shift-left culture, partner with developers on testability."
        ),
        "required_skills": ["selenium", "cypress", "ci/cd"],
        "nice_to_have": ["junit", "python"],
    },
    {
        "id": "ASG-027",
        "title": "API Developer (Go)",
        "description": (
            "Build high-throughput REST and GraphQL APIs in Go for a logistics "
            "platform. PostgreSQL and Redis, Kubernetes deployment, gRPC for "
            "internal services. Strong focus on latency and observability."
        ),
        "required_skills": ["go", "rest api", "kubernetes", "postgresql"],
        "nice_to_have": ["graphql", "redis", "prometheus"],
    },
    {
        "id": "ASG-028",
        "title": "Embedded Systems Developer (C++)",
        "description": (
            "Develop firmware in C++ for IoT sensor devices. RTOS, low-level "
            "hardware interfaces, Bluetooth LE stack. Optimise for power "
            "consumption and memory footprint."
        ),
        "required_skills": ["c++", "linux"],
        "nice_to_have": ["python", "ci/cd"],
    },
    {
        "id": "ASG-029",
        "title": "iOS Developer (Swift)",
        "description": (
            "Build and maintain the iOS consumer app for a health-tech "
            "company. Swift with SwiftUI and Combine, XCTest for unit "
            "coverage, REST API integration. Own feature releases, App "
            "Store submissions, and performance monitoring."
        ),
        "required_skills": ["swift", "rest api"],
        "nice_to_have": ["ci/cd"],
    },
    {
        "id": "ASG-030",
        "title": "Android Developer (Kotlin)",
        "description": (
            "Android developer for a payment app. Kotlin, Jetpack Compose, "
            "retrofit for REST APIs. Unit testing with JUnit, CI/CD with "
            "GitHub Actions. Strong focus on accessibility and offline support."
        ),
        "required_skills": ["kotlin", "rest api"],
        "nice_to_have": ["ci/cd", "junit"],
    },

    # =====================================================================
    # DOMAIN 4: Cloud & Infrastructure (ASG-031 to ASG-040)
    # =====================================================================
    {
        "id": "ASG-031",
        "title": "DevOps Engineer",
        "description": (
            "Own AWS infrastructure-as-code and CI/CD for a fintech platform. "
            "Kubernetes in production, Terraform for everything, strong Linux "
            "fundamentals."
        ),
        "required_skills": ["aws", "kubernetes", "terraform", "ci/cd", "linux"],
        "nice_to_have": ["python", "prometheus"],
    },
    {
        "id": "ASG-032",
        "title": "Cloud Architect",
        "description": (
            "Lead a multi-cloud migration across AWS and Azure. Define landing "
            "zones, Terraform standards, and Kubernetes platform patterns for "
            "engineering teams."
        ),
        "required_skills": ["aws", "azure", "terraform", "kubernetes"],
        "nice_to_have": ["gcp", "stakeholder management"],
    },
    {
        "id": "ASG-033",
        "title": "Site Reliability Engineer",
        "description": (
            "SRE for a high-traffic SaaS platform. Kubernetes in production, "
            "Prometheus and Grafana observability stack, Python tooling and "
            "CI/CD pipelines, deep Linux."
        ),
        "required_skills": ["kubernetes", "prometheus", "linux", "python", "ci/cd"],
        "nice_to_have": ["grafana", "terraform"],
    },
    {
        "id": "ASG-034",
        "title": "Platform Engineer",
        "description": (
            "Build an internal developer platform on Kubernetes. Design "
            "self-service infrastructure with Terraform, Helm, and custom "
            "operators. Own the GitLab CI pipeline templates used across "
            "engineering."
        ),
        "required_skills": ["kubernetes", "terraform", "gitlab ci", "linux"],
        "nice_to_have": ["go", "prometheus", "helm"],
    },
    {
        "id": "ASG-035",
        "title": "Network Engineer",
        "description": (
            "Manage WAN/LAN for a 20-site enterprise. Cisco and Juniper kit, "
            "NGINX reverse proxies, VPN gateways, Cloudflare WAF. Plan and "
            "execute SD-WAN rollout."
        ),
        "required_skills": ["linux", "nginx"],
        "nice_to_have": ["aws", "ansible"],
    },
    {
        "id": "ASG-036",
        "title": "Systems Administrator",
        "description": (
            "Manage 200+ Linux servers in a hybrid cloud/on-prem environment. "
            "Ansible automation, patching and hardening, LDAP/Okta SSO "
            "integration. Own backup and disaster recovery procedures."
        ),
        "required_skills": ["linux", "ansible"],
        "nice_to_have": ["okta", "aws"],
    },
    {
        "id": "ASG-037",
        "title": "Kubernetes Administrator",
        "description": (
            "Own the Kubernetes platform for a multi-tenant SaaS. Cluster "
            "lifecycle, RBAC, network policies, autoscaling, monitoring with "
            "Prometheus and Grafana. Support engineering teams on workload "
            "onboarding."
        ),
        "required_skills": ["kubernetes", "prometheus", "grafana", "linux"],
        "nice_to_have": ["terraform", "docker"],
    },
    {
        "id": "ASG-038",
        "title": "Cloud Security Engineer",
        "description": (
            "Design and implement cloud security controls across AWS and Azure. "
            "SIEM tuning, CSPM tooling, identity governance, incident response "
            "playbooks for cloud-native threats."
        ),
        "required_skills": ["aws", "siem", "incident response"],
        "nice_to_have": ["azure", "iso 27001", "terraform"],
    },
    {
        "id": "ASG-039",
        "title": "Database Administrator",
        "description": (
            "Manage PostgreSQL, SQL Server, and MongoDB clusters for a SaaS "
            "platform. Performance tuning, backup strategy, replication, and "
            "disaster recovery. Support engineering on schema design and "
            "query optimization."
        ),
        "required_skills": ["postgresql", "sql server", "linux"],
        "nice_to_have": ["mongodb", "aws"],
    },
    {
        "id": "ASG-040",
        "title": "Infrastructure Manager",
        "description": (
            "Lead the infrastructure team (6 engineers) for a mid-sized "
            "enterprise. Own the cloud budget (~2M/year), vendor relationships, "
            "and roadmap. Drive the shift from on-prem to hybrid cloud."
        ),
        "required_skills": ["aws", "stakeholder management", "linux"],
        "nice_to_have": ["terraform", "kubernetes"],
    },

    # =====================================================================
    # DOMAIN 5: Product & Delivery (ASG-041 to ASG-050)
    # =====================================================================
    {
        "id": "ASG-041",
        "title": "Agile Project Manager",
        "description": (
            "PM for a cross-functional delivery squad migrating a legacy "
            "platform. Scrum facilitation, Jira hygiene, stakeholder "
            "management across business and engineering."
        ),
        "required_skills": ["scrum", "jira", "stakeholder management"],
        "nice_to_have": ["business process", "confluence"],
    },
    {
        "id": "ASG-042",
        "title": "Salesforce Administrator",
        "description": (
            "Senior Salesforce admin for a commercial team. Configure and "
            "extend with Apex where needed, work directly with sales ops on "
            "business process redesign."
        ),
        "required_skills": ["salesforce", "apex", "business process"],
        "nice_to_have": ["jira", "stakeholder management"],
    },
    {
        "id": "ASG-043",
        "title": "Product Manager",
        "description": (
            "Product manager for a B2B SaaS analytics product. Own the roadmap, "
            "write specs, run user research interviews, and prioritise with "
            "engineering leads. Data-informed, user-obsessed."
        ),
        "required_skills": ["user research", "stakeholder management"],
        "nice_to_have": ["sql", "jira"],
    },
    {
        "id": "ASG-044",
        "title": "Scrum Master",
        "description": (
            "Dedicated scrum master for two engineering squads in a digital "
            "agency. Facilitate ceremonies, remove blockers, coach teams on "
            "agile practices. Manage Jira boards and sprint reporting."
        ),
        "required_skills": ["scrum", "jira"],
        "nice_to_have": ["confluence", "stakeholder management"],
    },
    {
        "id": "ASG-045",
        "title": "Technical Program Manager",
        "description": (
            "TPM for a cloud infrastructure programme. Coordinate engineering "
            "workstreams across 4 teams, manage dependencies and risks, report "
            "to VP level. Deep technical understanding of AWS and Kubernetes."
        ),
        "required_skills": ["stakeholder management", "jira"],
        "nice_to_have": ["aws", "kubernetes"],
    },
    {
        "id": "ASG-046",
        "title": "Business Analyst",
        "description": (
            "BA for an insurance core-system replacement. Elicit requirements, "
            "document business processes, write user stories, facilitate "
            "workshops with claims and underwriting stakeholders."
        ),
        "required_skills": ["business process", "stakeholder management"],
        "nice_to_have": ["jira", "confluence"],
    },
    {
        "id": "ASG-047",
        "title": "UX Designer",
        "description": (
            "End-to-end UX designer for a mobile banking app. Conduct user "
            "research, produce Figma prototypes, run usability tests, and "
            "partner with developers on implementation fidelity."
        ),
        "required_skills": ["figma", "user research"],
        "nice_to_have": ["stakeholder management"],
    },
    {
        "id": "ASG-048",
        "title": "Delivery Lead",
        "description": (
            "Own the delivery of a 12-month digital transformation programme. "
            "Manage the delivery team, vendor relationships, budget, and "
            "executive reporting. Agile + traditional delivery governance."
        ),
        "required_skills": ["stakeholder management", "scrum", "jira"],
        "nice_to_have": ["business process", "confluence"],
    },
    {
        "id": "ASG-049",
        "title": "Change Manager",
        "description": (
            "Lead OCM for a global ERP rollout. Stakeholder engagement, "
            "communications planning, training strategy, business readiness "
            "assessments. PROSCI or equivalent methodology."
        ),
        "required_skills": ["business process", "stakeholder management"],
        "nice_to_have": ["jira", "confluence"],
    },
    {
        "id": "ASG-050",
        "title": "ERP Implementation Consultant",
        "description": (
            "Configure and deploy ERP modules (finance, procurement) for "
            "mid-market clients. Gather requirements, map business processes, "
            "run UAT, and deliver end-user training. 80% travel within Benelux."
        ),
        "required_skills": ["business process", "stakeholder management"],
        "nice_to_have": ["dutch", "jira"],
    },
]


# ---- 10 sample candidates (2 per domain) -----------------------------------
# Free-text blurbs. Skills are extracted at match time from the canonical
# vocabulary. In prod this would be an LLM/NER extractor over a parsed CV.

CANDIDATES: list[dict[str, str]] = [
    # === Finance & Accounting ===
    {
        "name": "Interim Finance Controller",
        "blurb": (
            "Interim finance controller with 12 years' experience in mid-market "
            "manufacturing. Strong on IFRS, month-end close and budget cycles, "
            "daily SAP user. Recently led a finance transformation at a "
            "PE-backed group, including a Power BI rollout for management "
            "reporting. Fluent Dutch and English."
        ),
    },
    {
        "name": "Financial Planning Analyst",
        "blurb": (
            "FP&A analyst, 6 years in consumer goods. Own budgeting and "
            "forecasting cycles, run variance analysis and build financial "
            "models for business cases. Advanced Excel modelling, Power BI "
            "dashboards, and SAP for actuals extraction. Experience with "
            "M&A due diligence from prior corporate development rotation."
        ),
    },

    # === Data & AI ===
    {
        "name": "Senior Data Engineer",
        "blurb": (
            "Senior data engineer, 8 years building production pipelines. "
            "Daily Python and SQL, deep experience with Airflow on AWS and "
            "Databricks. Built CI/CD for data with GitHub Actions and "
            "Terraform, comfortable owning Snowflake and Kafka. Interested in "
            "moving toward MLOps."
        ),
    },
    {
        "name": "Machine Learning Engineer",
        "blurb": (
            "ML engineer with 5 years shipping models to production. PyTorch "
            "for training, MLflow for experiment tracking, Kubernetes for "
            "serving. SQL daily for feature engineering, strong Python. Built "
            "a recommendation system on Databricks, recently exploring LLM "
            "fine-tuning with LangChain."
        ),
    },

    # === Software Engineering ===
    {
        "name": "Backend Developer (Java)",
        "blurb": (
            "Senior backend Java developer, 10 years. Spring Boot microservices "
            "with Kafka messaging, REST and GraphQL APIs, PostgreSQL and Redis. "
            "Own CI/CD pipelines with GitLab CI, Docker, and Kubernetes "
            "deployment on AWS. Strong testing practice with JUnit."
        ),
    },
    {
        "name": "Frontend Developer (React)",
        "blurb": (
            "Frontend developer, 7 years building React and TypeScript apps. "
            "Owned the design system at a fintech, close collaboration with "
            "UX designers in Figma. Experience with Next.js for SSR, REST API "
            "integration, and Cypress end-to-end testing. Comfortable with "
            "Node.js for BFF layers."
        ),
    },

    # === Cloud & Infrastructure ===
    {
        "name": "Cloud Architect",
        "blurb": (
            "Cloud architect with 12 years across AWS, Azure, and GCP. "
            "Design multi-cloud landing zones with Terraform, define Kubernetes "
            "platform standards, and advise CTOs on cloud strategy. Hands-on "
            "with CI/CD, Prometheus observability, and cost optimization. "
            "Strong stakeholder management from pre-sales through delivery."
        ),
    },
    {
        "name": "DevOps Engineer",
        "blurb": (
            "DevOps engineer, 6 years. AWS infrastructure with Terraform, "
            "Kubernetes in production, GitLab CI pipelines, Prometheus and "
            "Grafana monitoring. Python scripting for automation, strong Linux "
            "fundamentals. Currently migrating a monolith to microservices on "
            "EKS with zero-downtime requirements."
        ),
    },

    # === Product & Delivery ===
    {
        "name": "Technical Product Manager",
        "blurb": (
            "Technical product manager, 8 years in B2B SaaS. Own the roadmap "
            "for a data platform product, run user research interviews, write "
            "detailed specs with SQL-backed analysis. Jira for backlog "
            "management, strong stakeholder communication with engineering "
            "and commercial teams. Background as a data analyst."
        ),
    },
    {
        "name": "Business Analyst",
        "blurb": (
            "Business analyst, 5 years in financial services. Requirements "
            "elicitation and business process mapping for regulatory change "
            "programmes. Write user stories in Jira, facilitate workshops with "
            "compliance and operations stakeholders, Confluence documentation. "
            "Experience with insurance core-system replacement."
        ),
    },

    # === Demo-maker: semantically AI-adjacent, not engineering-qualified ===
    # Intentional REVIEW trigger for the live demo. Heavy LLM/RAG vocabulary
    # gives high semantic_sim to ASG-014 (AI Engineer); but the blurb is
    # advisory, no Python / LangChain / AWS, so skill_overlap stays low and
    # the "sounds relevant but missing required skills" rule fires correctly.
    {
        "name": "AI Strategy Consultant",
        "blurb": (
            "AI strategy consultant with 7 years advising enterprise clients "
            "on AI adoption. Define LLM use cases for customer support, "
            "evaluate RAG vs fine-tuning architectures, run AI maturity "
            "assessments and build business cases for AI investment. Strong "
            "stakeholder management at C-suite level. Non-coding background; "
            "partner with engineering teams on delivery."
        ),
    },
]