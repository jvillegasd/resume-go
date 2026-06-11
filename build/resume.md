# Johnny Villegas
> Backend Engineer @ Quantum Lending Solutions | Python + AWS + MySQL | Building financial services for fueling Enterprises and SMBs Colombia
> johnnyvillegaslrs@gmail.com · +57 3147740148 · Barranquilla, Colombia · www.linkedin.com/in/jvillegasd · github.com/jvillegasd

## Summary
Results-driven Backend Engineer with over 6 years of experience designing and scaling backend systems across Fintech and SaaS industries. Specialized in Python (FastAPI, Flask, Django), with strong proficiency in Node.js, PHP, and modern development practices. Proven ability to build high-performance APIs, automate infrastructure with AWS, and manage deployment pipelines using CI/ CD tools like GitHub Actions and Terraform. Hands-on experience with both relational and NoSQL databases, containerization (Docker), and Infrastructure as Code (IaC) practices. Passionate about writing clean, maintainable code and continuously improving systems for reliability and scalability. Strong collaborator and fast learner who thrives in agile environments and loves turning complex requirements into elegant solutions.

## Education
### Universidad del Norte - Bachelor of Engineering - BE, Computer Science
*January 2016 - February 2021*

## Experience
### Quantum Lending Solutions - Software Engineer
*February 2024 - Present · Reston, Virginia, United States*
- Building and maintaining financial core services across loan origination, fraud detection, cashflow analysis, and payment processing (Plaid, MoneyThumb, HyperVerge) - serving ~14K loan applications/month (~$32M disbursed monthly) using Python, FastAPI, and Django-Ninja on AWS.
- Built an in-house graph-based fraud detection service using Neo4j to surface connected fraudulent applications across shared attributes (email, SSN, EIN, IPs) - integrating PostgreSQL, MySQL, and Snowflake with graph-visual PDF reports via FastAPI, meaningfully reducing manual fraud review overhead.
- Optimized Cypher queries for edge-case fraud graph traversals, cutting execution time by 99% (~11 min to ~480ms).
- Built a Plaid-powered payment processor microservice integrated with the legacy Back Office system, reducing overdue portfolio by 20-30%.
- Designed an event-driven architecture using RabbitMQ, AWS SQS/SNS, and Kubernetes, improving system throughput and decoupling 15+ platform services.
- Automated Salesforce data ingestion via AWS AppFlow, eliminating manual data transfers and saving the ops team ~5 hours/week.
- Optimized API endpoints and SQL queries, reducing response latency by 99% (~15 min to ~600ms) across core platform services.
- Built a FastAPI service that automatically runs 6 bank-statement validation checks (data coverage, name/address match, balance continuity, revenue consistency) via SNS triggers - replacing manual pre-underwriter review, publishing a downstream readiness event, and exposing results via REST API.
- Led code reviews across the platform team, enforcing design patterns that meaningfully reduced production regression incidents.
- Raised test coverage across platform services from 30% to 90%+ using Pytest and Moto, reducing production regressions.

### Camino Financial - Software Engineer
*February 2023 - February 2024 · Los Angeles, California, United States*
- Maintained and extended the legacy Django Back Office system for the Credit team, shipping features and resolving bugs that meaningfully unblocked loan processing workflows.
- Designed and implemented an event-driven architecture using AWS EventBridge and CDK, decoupling platform services and meaningfully improving system reliability.
- Shipped financial core microservices for Plaid and Socure integrations, lead management, and Salesforce sync - enabling automated fraud score routing to Salesforce lead objects via AWS EventBridge.
- Improved microservices observability using AWS Powertools, reducing root cause identification time from 3-4 hours to 30-45 minutes per incident.
- Delivered a serverless pipeline via AWS Lambda, Step Functions, and EventBridge that processes CSV files to generate targeted Plaid-linked campaign URLs - enabling the marketing team to launch their first automated loan campaigns.

### Globant - Software Engineer
*May 2022 - January 2023 · Barranquilla, Atlantico, Colombia*
- Shipped a Python/FastAPI microservice for a staffing-tech client that evaluates ML model outputs through a decisioning tree, returning human-readable candidate-to-job compatibility explanations at scale.

### Leanware - Software Engineer
*August 2021 - April 2022 · Barranquilla, Atlantico, Colombia*
- Built a PDF generation web app that batch-processes CSV input to populate document templates using Node.js on GCP, saving users ~2 hours per batch.
- Shipped a secure file hosting service for sensitive customer documents with end-to-end encryption using AWS KMS, Python, Flask, and AWS Serverless - eliminating reliance on third-party storage for regulated data.
- Shipped a near real-time algorithmic trading bot with 4 custom strategies - integrating Polygon, InteractiveBrokers, and TradingView webhooks for signal processing and order execution at ~650ms per signal using Python and AWS Serverless.

### ISWE GROUP - Software Engineer
*June 2020 - April 2022 · Buenos Aires Province, Argentina*
- Built a web scraper that automates FDA Priority Notice webform submissions using Python, Selenium, and RQ - increasing throughput from 1 to 4 submissions per 15 minutes and freeing staff to focus on order processing.
- Shipped a vehicle broker prototype enabling real-time insurance quote generation by integrating Argentinian SOAP insurance APIs using Python, Flask, Vue.js, and PostgreSQL.
- Shipped an inventory management system integrated with Shopify for product tracking and order fulfillment, generating shipping labels via FedEx, DHL, and UPS APIs - scaling order processing from 10 to 40+ orders/day using Python, Flask, Vue.js, and MongoDB.
- Extended the inventory management system with multi-store support, enabling creation and management of Shopify store clusters.

### City Lending Inc - Back End Developer
*October 2019 - May 2020 · Barranquilla, Atlantico, Colombia*
- Automated loan processing and status update workflows for the financial team via Encompass API integration using Python and AWS Serverless - eliminating manual status tracking.
- Shipped internal loan officer tooling and REST API integrations with the Encompass API using Python, PHP, and AWS Serverless - streamlining daily workflows for the originations team.
- Shipped a custom Salesforce Lightning chat component integrated with Twilio - used by all loan officers for lead follow-up, with automated assignment, lead sanitization, and data visualization dashboards using Apex, Node.js, and AWS Serverless.

## Skills
**Languages:** Python, Node.js, PHP, Java
**Frameworks:** FastAPI, Django, Django-Ninja, Flask, Express.js, Vue.js
**Cloud & DevOps:** AWS Lambda, AWS SQS, AWS SNS, AWS EventBridge, AWS CDK, AWS AppFlow, AWS Step Functions, AWS DynamoDB, AWS S3, Docker, Kubernetes, GitHub Actions, Coolify
**Observability:** AWS CloudWatch, Datadog
**Databases:** PostgreSQL, MySQL, Neo4j, MongoDB, Snowflake, RabbitMQ, Redis
**Fintech APIs:** Plaid, Salesforce, Socure, Encompass, Twilio
**Commerce & Trading APIs:** Shopify, InteractiveBrokers, Polygon, TradingView, FedEx, DHL, UPS
**Testing & Tools:** Pytest, Moto, LocalStack, MinIO, Selenium, RQ, Cryptography

## Honors & Awards
### ACM-ICPC Latin America 2018 Programming contest
### ACM-ICPC Latin America 2019 Programming contest Talento TI Scholarship
