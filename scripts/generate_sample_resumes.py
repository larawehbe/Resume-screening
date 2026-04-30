"""
Generate synthetic resume PDFs for testing the pipeline.

Run this once after `uv sync` to populate sample_data/resumes/ with five
fictional candidates of varying strength against sample_data/sample_jd.txt.
Students can edit the SAMPLE_RESUMES dict below and re-run to experiment.

Also writes tests/fixtures/sample_resume.pdf so the parser integration test
has something to read.
"""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parent.parent
RESUMES_DIR = ROOT / "sample_data" / "resumes"
FIXTURES_DIR = ROOT / "tests" / "fixtures"


SAMPLE_RESUMES: dict[str, str] = {
    "alice_chen.pdf": """
Alice Chen
alice.chen@example.com · github.com/alicec

Summary
Senior backend engineer with 8 years of experience building large-scale
payment and ledger systems. Python and Go in production, deep PostgreSQL
comfort, and on-call ownership of revenue-critical services.

Experience

Staff Engineer — Paywell Inc. (2021 – Present)
Led the rebuild of the merchant settlement pipeline serving 12k merchants.
Designed idempotent refund and capture APIs used by internal and partner
teams. Mentored three mid-level engineers. Primary on-call for the payments
service; wrote and ran postmortems for two sev-1 incidents.

Senior Engineer — Fintrail (2018 – 2021)
Built the ACH origination service from scratch in Python. Worked directly
with Stripe and Adyen integrations. Deep PostgreSQL schema work, including
partitioning and index tuning on the transactions table.

Backend Engineer — Contoso Bank (2016 – 2018)
Owned the core double-entry ledger service. Migrated from at-most-once to
at-least-once delivery with idempotency keys.

Skills
Python, Go, PostgreSQL, Kafka, gRPC, REST, Terraform, Kubernetes, Stripe,
PCI DSS.

Education
BS Computer Science, University of Waterloo, 2016.
""",
    "bob_patel.pdf": """
Bob Patel
bob.patel@example.com

Summary
Mid-level backend engineer with 4 years of experience building internal web
services at a large e-commerce company. Comfortable in Python and interested
in moving to a payments role.

Experience

Backend Engineer — ShopNexus (2021 – Present)
Built internal tools for the merchandising team. Owned a Python service that
computed daily product rollups. Participated in on-call for the internal
tools group.

Junior Backend Engineer — ShopNexus (2020 – 2021)
Worked on the catalog import pipeline. Wrote ETL jobs in Python.

Skills
Python, PostgreSQL, Redis, Docker, basic Kubernetes.

Education
BS Computer Science, SUNY Buffalo, 2020.
""",
    "carol_nakamura.pdf": """
Carol Nakamura
carol@nakamura.dev · linkedin.com/in/carolnak

Summary
Senior payments engineer with 9 years of experience, including 5 years at
Stripe. Expert in Go, production PostgreSQL at scale, and distributed-systems
patterns. Mentored seven engineers through promotion.

Experience

Senior Engineer — Stripe (2019 – Present)
Worked on the Issuing product. Designed and shipped the card-authorization
service in Go. Heavy use of Kafka for fan-out and at-least-once delivery.
Weekly on-call for Issuing. Co-authored the team's idempotency spec.

Engineer — Braintree (2016 – 2019)
Built merchant onboarding flows. PostgreSQL schema owner for the vault
service. Shipped the first internal Terraform module for the vault.

Software Engineer — Amazon Payments (2015 – 2016)
Contributed to the refund pipeline. First exposure to PCI DSS compliance.

Skills
Go, Python, PostgreSQL, Kafka, gRPC, Terraform, Kubernetes, Stripe APIs,
PCI DSS, SOC 2.

Education
MS Computer Science, Carnegie Mellon, 2015. BS Mathematics, UIUC, 2013.
""",
    "david_okonkwo.pdf": """
David Okonkwo
david.o@example.net

Summary
Frontend-leaning full-stack engineer with 6 years of experience. Most of my
backend work has been in Node.js for consumer-facing product features, not
transactional systems.

Experience

Senior Full-Stack Engineer — Glimmer Media (2020 – Present)
Led the rewrite of the subscriptions UI in React. On the backend, wrote
Node.js services for the content recommendation API. Some exposure to
Stripe Checkout integrations.

Full-Stack Engineer — Vista Publishing (2018 – 2020)
Built the paywall feature using Stripe Checkout. Mostly frontend work with a
thin Node.js BFF layer.

Skills
React, TypeScript, Node.js, some Python, PostgreSQL basics, Stripe Checkout.

Education
BS Software Engineering, University of Lagos, 2018.
""",
    "eve_jansson.pdf": """
Eve Jansson
eve@jansson.dev

Summary
Staff backend engineer with 11 years of experience building high-throughput
Go services at banks and payment processors. Ran the on-call rotation for
the core auth-and-capture service at my current company for three years.

Experience

Staff Engineer — NordCore Payments (2019 – Present)
Own the auth-and-capture service (2M transactions/day). Shipped the
migration from synchronous capture to an event-driven model on Kafka.
Rewrote the idempotency layer to handle multi-region deployments. On-call
lead; wrote the team's incident-response runbook.

Senior Engineer — Klarna (2015 – 2019)
Worked on merchant integrations for the pay-later product. Go and
PostgreSQL. Built the reconciliation pipeline with the finance team.

Engineer — SEB Bank (2013 – 2015)
Built internal tooling for the corporate banking team in Java. Moved to Go
for green-field work in 2014.

Skills
Go, PostgreSQL, Kafka, gRPC, Terraform, Kubernetes, card networks, ACH,
SOC 2, PCI DSS.

Education
MSc Computer Science, KTH Royal Institute of Technology, 2013.
""",
    "fatima_al_rashid.pdf": """
Fatima Al-Rashid
fatima.rashid@example.com · github.com/fatimarashid

Summary
Backend engineer with 6 years of experience in fintech. Built and maintained
payment processing services handling millions of transactions daily. Strong
Python background with growing Go expertise.

Experience

Senior Backend Engineer — PayStream (2022 – Present)
Owns the merchant payout service processing $50M daily. Migrated the
settlement engine from batch to near-real-time using Kafka Streams.
Implemented circuit breakers and retry logic for downstream payment
provider calls. On-call for the payouts squad.

Backend Engineer — PayStream (2020 – 2022)
Built the refund automation service in Python. Integrated with Adyen and
PayPal APIs. Designed PostgreSQL schemas for the dispute tracking system.

Junior Developer — TechBridge Solutions (2018 – 2020)
Full-stack work on a Django invoicing app. First exposure to Stripe and
payment integrations. Wrote REST APIs consumed by mobile clients.

Skills
Python, Go, PostgreSQL, Kafka, REST, Docker, Kubernetes, Adyen, Stripe,
Redis, Datadog.

Education
BS Computer Engineering, American University of Beirut, 2018.
""",
    "george_martinez.pdf": """
George Martinez
g.martinez@example.com

Summary
DevOps engineer with 7 years of experience. Strong infrastructure
background but limited application-level backend development. Looking to
transition into a backend engineering role.

Experience

Senior DevOps Engineer — CloudScale (2021 – Present)
Managed Kubernetes clusters running 200+ microservices. Built Terraform
modules for AWS infrastructure. Set up CI/CD pipelines with GitHub Actions.
Handled incident response and wrote postmortems.

DevOps Engineer — CloudScale (2019 – 2021)
Maintained monitoring dashboards in Grafana and Datadog. Managed PostgreSQL
RDS instances including backup and failover configuration.

Systems Administrator — NetOps Corp (2017 – 2019)
Linux server administration. Wrote automation scripts in Python and Bash.

Skills
Terraform, Kubernetes, AWS, Docker, Python, Bash, PostgreSQL (ops), Kafka
(ops), Grafana, Datadog, PagerDuty.

Education
BS Information Technology, University of Texas at Austin, 2017.
""",
    "hannah_kim.pdf": """
Hannah Kim
hannah.kim@example.com · linkedin.com/in/hannahkim

Summary
Senior backend engineer with 7 years of experience building billing and
subscription systems. Deep Python expertise with production PostgreSQL
and event-driven architecture experience.

Experience

Senior Engineer — BillFlow (2021 – Present)
Designed the usage-based billing engine processing 500M metering events
per month. Built idempotent charge creation APIs used by 3 internal teams.
PostgreSQL partitioning and query optimization for the invoices table.
Mentored two junior engineers.

Backend Engineer — BillFlow (2019 – 2021)
Built the subscription lifecycle service. Integrated with Stripe Billing
for recurring charges. Implemented webhook handlers for payment status
updates with at-least-once delivery guarantees.

Software Engineer — DataWorks (2017 – 2019)
Built data pipeline services in Python. REST API development with Flask.
Basic PostgreSQL schema design.

Skills
Python, PostgreSQL, Kafka, REST, gRPC, Stripe Billing, Redis, Docker,
Terraform, AWS.

Education
MS Computer Science, Georgia Tech, 2017. BS Computer Science, Seoul
National University, 2015.
""",
    "ivan_petrov.pdf": """
Ivan Petrov
ivan.petrov@example.com

Summary
Machine learning engineer with 5 years of experience. Strong Python skills
but focused on ML infrastructure rather than backend services or payments.

Experience

ML Engineer — DataMind AI (2022 – Present)
Built the feature store serving real-time predictions for fraud detection.
Python and PostgreSQL for feature pipelines. Deployed models on Kubernetes.

ML Engineer — DataMind AI (2020 – 2022)
Trained and deployed credit scoring models. Built batch inference pipelines
using Apache Spark and Airflow.

Data Scientist — AnalyticsPro (2019 – 2020)
Built dashboards and statistical models for marketing analytics. Python,
pandas, scikit-learn.

Skills
Python, PostgreSQL, Kubernetes, Docker, TensorFlow, PyTorch, Spark,
Airflow, scikit-learn, pandas.

Education
MS Machine Learning, ETH Zurich, 2019. BS Mathematics, Moscow State
University, 2017.
""",
    "julia_santos.pdf": """
Julia Santos
julia.santos@example.com · github.com/juliasantos

Summary
Backend engineer with 10 years of experience, last 6 in payments. Led the
migration of a legacy payment gateway to a modern microservices architecture.
Expert in Go and PostgreSQL with deep card network knowledge.

Experience

Principal Engineer — MercadoPago (2021 – Present)
Led the re-architecture of the payment gateway from a monolith to
event-driven microservices. Owns the authorization and capture services
handling 5M daily transactions. Designed the idempotency framework used
across all payment services. Mentored a team of 5 engineers.

Senior Engineer — MercadoPago (2019 – 2021)
Built the reconciliation service matching settlements from Visa and
Mastercard with internal ledger entries. Go and PostgreSQL. Implemented
PCI DSS controls for the card vault.

Backend Engineer — Globant (2016 – 2019)
Worked on banking integrations for enterprise clients. Built REST APIs
in Java, later migrated key services to Go.

Software Developer — Globant (2014 – 2016)
General backend development in Java. Built internal tools and batch
processing jobs.

Skills
Go, Java, PostgreSQL, Kafka, gRPC, REST, Terraform, Kubernetes, Visa/MC
networks, PCI DSS, SOC 2, ACH.

Education
BS Computer Science, University of Sao Paulo, 2014.
""",
}


def _write_pdf(text: str, out: Path) -> None:
    styles = getSampleStyleSheet()
    body = styles["BodyText"]
    heading = styles["Heading1"]

    out.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(out), pagesize=letter)
    flow = []

    lines = text.strip().splitlines()
    for i, line in enumerate(lines):
        if not line.strip():
            flow.append(Spacer(1, 8))
            continue
        if i == 0:
            flow.append(Paragraph(line, heading))
        else:
            flow.append(Paragraph(line, body))

    doc.build(flow)


def main() -> None:
    for filename, content in SAMPLE_RESUMES.items():
        out = RESUMES_DIR / filename
        _write_pdf(content, out)
        print(f"wrote {out.relative_to(ROOT)}")

    # Also seed the parser test fixture with the first resume.
    fixture = FIXTURES_DIR / "sample_resume.pdf"
    _write_pdf(next(iter(SAMPLE_RESUMES.values())), fixture)
    print(f"wrote {fixture.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
