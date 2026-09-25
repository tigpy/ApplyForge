from packages.domain.enums import SkillProficiency
from packages.domain.models import (
    Candidate, Certification, Education, Experience,
    JobSource, Project, Resume, Skill
)

SEED_CANDIDATE = {
    "name": "Aryan Singh",
    "email": "aryan.singh@example.com",
    "phone": "+1 (555) 019-2834",
    "location": "San Francisco, CA (Open to Remote)",
    "work_authorization": "Citizen / Authorized to work without restriction",
    "preferred_roles": [
        "Cybersecurity Analyst",
        "SOC Analyst",
        "Backend Python Engineer",
        "Security Engineer",
        "Cloud Security Associate"
    ],
    "preferred_locations": ["Remote", "San Francisco, CA", "New York, NY"],
    "work_preferences": {
        "remote_only": False,
        "hybrid_ok": True,
        "sponsorship_needed": False,
        "salary_range": "$90,000 - $130,000"
    },
    "summary": (
        "Disciplined Software & Cybersecurity Engineer with hands-on expertise in Python, "
        "FastAPI, SIEM monitoring, secure backend architectures, and automated threat analysis. "
        "Experienced in building reliable, auditable systems with strong focus on security, testing, and compliance."
    )
}

SEED_EDUCATIONS = [
    {
        "degree": "Bachelor of Science",
        "field": "Computer Science & Cybersecurity",
        "institution": "State University of Technology",
        "start_date": "2020",
        "end_date": "2024",
        "status": "Completed",
        "grade": "3.8 / 4.0 GPA"
    }
]

SEED_SKILLS = [
    {"name": "Python", "category": "Programming", "proficiency": SkillProficiency.ADVANCED, "evidence": ["project:evidentia", "project:job_automation"]},
    {"name": "FastAPI", "category": "Backend", "proficiency": SkillProficiency.ADVANCED, "evidence": ["project:evidentia", "api:rest"]},
    {"name": "PostgreSQL", "category": "Backend", "proficiency": SkillProficiency.INTERMEDIATE, "evidence": ["project:evidentia", "db:relational"]},
    {"name": "Docker", "category": "Cloud/DevOps", "proficiency": SkillProficiency.INTERMEDIATE, "evidence": ["deployment:docker-compose"]},
    {"name": "Redis", "category": "Backend", "proficiency": SkillProficiency.INTERMEDIATE, "evidence": ["caching:task_queue"]},
    {"name": "Linux", "category": "Infrastructure", "proficiency": SkillProficiency.ADVANCED, "evidence": ["sysadmin:bash_scripting"]},
    {"name": "Bash", "category": "Programming", "proficiency": SkillProficiency.INTERMEDIATE, "evidence": ["scripts:automation"]},
    {"name": "SIEM", "category": "Cybersecurity", "proficiency": SkillProficiency.INTERMEDIATE, "evidence": ["experience:apex_tech_labs", "tool:splunk"]},
    {"name": "Splunk", "category": "Cybersecurity", "proficiency": SkillProficiency.INTERMEDIATE, "evidence": ["logs:triage_monitoring"]},
    {"name": "Incident Response", "category": "Cybersecurity", "proficiency": SkillProficiency.INTERMEDIATE, "evidence": ["labs:mitre_att&ck"]},
    {"name": "Network Security", "category": "Cybersecurity", "proficiency": SkillProficiency.INTERMEDIATE, "evidence": ["tool:wireshark", "analysis:packet_capture"]},
    {"name": "Wireshark", "category": "Cybersecurity", "proficiency": SkillProficiency.INTERMEDIATE, "evidence": ["project:packet_inspector"]},
    {"name": "REST APIs", "category": "Backend", "proficiency": SkillProficiency.ADVANCED, "evidence": ["project:evidentia"]},
    {"name": "CI/CD", "category": "Cloud/DevOps", "proficiency": SkillProficiency.INTERMEDIATE, "evidence": ["github:actions_pipeline"]},
    {"name": "Vulnerability Management", "category": "Cybersecurity", "proficiency": SkillProficiency.INTERMEDIATE, "evidence": ["security:owasp_top_10"]}
]

SEED_PROJECTS = [
    {
        "name": "Evidentia",
        "description": "Evidence-grounded cybersecurity and intelligence analysis platform featuring real-time event parsing, provenance tracking, and tamper-evident audit logs.",
        "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
        "url": "https://github.com/aryansingh/evidentia",
        "start_date": "2023",
        "end_date": "2024",
        "evidence": ["repo:evidentia", "live_demo:available"]
    },
    {
        "name": "Job Application Automation",
        "description": "Enterprise-grade job matching, resume tailoring, and application management system with explainable signals and human-in-the-loop review.",
        "technologies": ["Python", "FastAPI", "SQLAlchemy", "ReportLab", "Pytest"],
        "url": "https://github.com/aryansingh/job-application-automation",
        "start_date": "2024",
        "end_date": "2024",
        "evidence": ["codebase:active"]
    },
    {
        "name": "Network Packet Inspector",
        "description": "Custom intrusion detection helper inspecting PCAP packets, identifying anomalous beaconing behavior, and generating alert summaries.",
        "technologies": ["Python", "Wireshark", "Linux", "Bash"],
        "url": "https://github.com/aryansingh/network-packet-inspector",
        "start_date": "2023",
        "end_date": "2023",
        "evidence": ["lab_reports:cybersecurity"]
    }
]

SEED_EXPERIENCES = [
    {
        "organization": "Apex Tech Labs",
        "title": "Security Engineering Intern",
        "type": "Internship",
        "description": (
            "Monitored security telemetry in SIEM, evaluated suspicious alerts, and created Python automation scripts "
            "to accelerate endpoint artifact triage by 35%. Assisted with quarterly vulnerability scanning."
        ),
        "start_date": "Jun 2023",
        "end_date": "Dec 2023",
        "evidence": ["employment_verification:apex_tech_labs"]
    }
]

SEED_CERTIFICATIONS = [
    {
        "name": "CompTIA Security+",
        "issuer": "CompTIA",
        "status": "Active",
        "date": "2023",
        "credential_url": "https://www.credly.com/org/comptia"
    },
    {
        "name": "AWS Certified Cloud Practitioner",
        "issuer": "Amazon Web Services",
        "status": "Active",
        "date": "2023",
        "credential_url": "https://www.credly.com/org/aws"
    }
]

SEED_RESUME_VARIANTS = [
    {
        "name": "Cybersecurity & SOC Resume",
        "job_family": "Cybersecurity",
        "version": 1,
        "content_text": "Tailored for SOC Analyst, Cybersecurity Analyst, and Incident Response positions."
    },
    {
        "name": "Backend Python Engineer Resume",
        "job_family": "Backend",
        "version": 1,
        "content_text": "Tailored for Python, FastAPI, API development, and distributed systems."
    },
    {
        "name": "Cloud & DevOps Resume",
        "job_family": "Cloud/DevOps",
        "version": 1,
        "content_text": "Tailored for Cloud Infrastructure, Docker, Linux, and CI/CD automation."
    },
    {
        "name": "General Tech Resume",
        "job_family": "General",
        "version": 1,
        "content_text": "General software engineering and security resume."
    }
]

def seed_database(db):
    existing_candidate = db.query(Candidate).first()
    if not existing_candidate:
        candidate = Candidate(**SEED_CANDIDATE)
        db.add(candidate)
        db.flush()

        for edu in SEED_EDUCATIONS:
            db.add(Education(candidate_id=candidate.id, **edu))

        for sk in SEED_SKILLS:
            db.add(Skill(candidate_id=candidate.id, **sk))

        for proj in SEED_PROJECTS:
            db.add(Project(candidate_id=candidate.id, **proj))

        for exp in SEED_EXPERIENCES:
            db.add(Experience(candidate_id=candidate.id, **exp))

        for cert in SEED_CERTIFICATIONS:
            db.add(Certification(candidate_id=candidate.id, **cert))

        for res in SEED_RESUME_VARIANTS:
            db.add(Resume(candidate_id=candidate.id, **res))

    sources = [
        {"name": "manual", "type": "manual", "configuration": {"description": "Manual job entry & URL import"}},
        {"name": "mock", "type": "mock", "configuration": {"description": "Sandbox mock job source and test application handler"}},
        {"name": "public_feed", "type": "public_feed", "configuration": {"description": "Permitted public remote job feeds (Jobicy/RemoteOK API)"}}
    ]
    for src in sources:
        existing_src = db.query(JobSource).filter_by(name=src["name"]).first()
        if not existing_src:
            db.add(JobSource(**src))

    db.commit()
