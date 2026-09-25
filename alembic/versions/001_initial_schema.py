"""Initial schema with PostgreSQL and pgvector support

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-25 18:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Try enabling pgvector if on PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        'candidates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('work_authorization', sa.String(255), server_default="Citizen / Authorized"),
        sa.Column('preferred_roles', sa.JSON(), nullable=True),
        sa.Column('preferred_locations', sa.JSON(), nullable=True),
        sa.Column('work_preferences', sa.JSON(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('profile_version', sa.Integer(), server_default="1"),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'educations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('degree', sa.String(255), nullable=False),
        sa.Column('field', sa.String(255), nullable=False),
        sa.Column('institution', sa.String(255), nullable=False),
        sa.Column('start_date', sa.String(50), nullable=True),
        sa.Column('end_date', sa.String(50), nullable=True),
        sa.Column('status', sa.String(50), server_default="Completed"),
        sa.Column('grade', sa.String(50), nullable=True)
    )

    op.create_table(
        'skills',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('category', sa.String(100), server_default="General"),
        sa.Column('proficiency', sa.String(50), server_default="INTERMEDIATE"),
        sa.Column('evidence', sa.JSON(), nullable=True)
    )

    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('technologies', sa.JSON(), nullable=True),
        sa.Column('url', sa.String(500), nullable=True),
        sa.Column('start_date', sa.String(50), nullable=True),
        sa.Column('end_date', sa.String(50), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True)
    )

    op.create_table(
        'experiences',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization', sa.String(255), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('type', sa.String(100), server_default="Full-time"),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('start_date', sa.String(50), nullable=True),
        sa.Column('end_date', sa.String(50), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True)
    )

    op.create_table(
        'certifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('issuer', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), server_default="Active"),
        sa.Column('date', sa.String(50), nullable=True),
        sa.Column('credential_url', sa.String(500), nullable=True)
    )

    op.create_table(
        'resumes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('job_family', sa.String(100), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('content_text', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), server_default="1"),
        sa.Column('source', sa.String(100), server_default="manual"),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'job_sources',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('enabled', sa.Boolean(), server_default=sa.text('1'))
    )

    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('source_id', sa.Integer(), sa.ForeignKey('job_sources.id'), nullable=False),
        sa.Column('external_id', sa.String(255), nullable=False),
        sa.Column('url', sa.String(1000), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('company', sa.String(255), nullable=False),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('work_mode', sa.String(50), server_default="UNKNOWN"),
        sa.Column('employment_type', sa.String(50), server_default="FULL_TIME"),
        sa.Column('description_raw', sa.Text(), nullable=False),
        sa.Column('description_normalized', sa.Text(), nullable=True),
        sa.Column('duplicate_fingerprint', sa.String(255), nullable=True),
        sa.Column('discovered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closing_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('source_id', 'external_id', name='uq_source_external_id')
    )

    op.create_table(
        'job_requirements',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('job_id', sa.Integer(), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('requirement_type', sa.String(50), server_default="SKILL"),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('normalized_skill', sa.String(100), nullable=True),
        sa.Column('mandatory', sa.Boolean(), server_default=sa.text('1')),
        sa.Column('evidence', sa.JSON(), nullable=True)
    )

    op.create_table(
        'matches',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('job_id', sa.Integer(), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id'), nullable=False),
        sa.Column('match_version', sa.Integer(), server_default="1"),
        sa.Column('score', sa.Float(), server_default="0.0"),
        sa.Column('required_coverage', sa.Float(), server_default="0.0"),
        sa.Column('preferred_coverage', sa.Float(), server_default="0.0"),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('hard_gaps', sa.JSON(), nullable=True),
        sa.Column('strengths', sa.JSON(), nullable=True),
        sa.Column('uncertainties', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'applications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id'), nullable=False),
        sa.Column('job_id', sa.Integer(), sa.ForeignKey('jobs.id'), nullable=False),
        sa.Column('resume_id', sa.Integer(), sa.ForeignKey('resumes.id'), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('external_application_id', sa.String(255), nullable=True),
        sa.Column('application_url', sa.String(1000), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'application_questions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('application_id', sa.Integer(), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=True),
        sa.Column('answer_source', sa.String(100), server_default="candidate_profile"),
        sa.Column('requires_review', sa.Boolean(), server_default=sa.text('1')),
        sa.Column('final_answer', sa.Text(), nullable=True)
    )

    op.create_table(
        'audit_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('application_id', sa.Integer(), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=True),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('actor', sa.String(100), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('payload_hash', sa.String(64), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True)
    )

def downgrade() -> None:
    op.drop_table('audit_events')
    op.drop_table('application_questions')
    op.drop_table('applications')
    op.drop_table('matches')
    op.drop_table('job_requirements')
    op.drop_table('jobs')
    op.drop_table('job_sources')
    op.drop_table('resumes')
    op.drop_table('certifications')
    op.drop_table('experiences')
    op.drop_table('projects')
    op.drop_table('skills')
    op.drop_table('educations')
    op.drop_table('candidates')
