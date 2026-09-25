'use client';

import React, { useState, useEffect } from 'react';
import { api, Candidate, Job, Application } from '../lib/api';

export default function CareerDeskPage() {
  const [tab, setTab] = useState<'desk' | 'queue' | 'jobs' | 'applications' | 'profile' | 'resumes' | 'connectors' | 'audit'>('desk');
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [queue, setQueue] = useState<Application[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [resumes, setResumes] = useState<any[]>([]);
  const [sources, setSources] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [reviewApp, setReviewApp] = useState<Application | null>(null);

  const loadAll = async () => {
    try {
      const [candData, jobsData, queueData, appsData, resData, srcData, auditData] = await Promise.all([
        api.getCandidate(),
        api.getJobs(),
        api.getQueue(),
        api.getApplications(),
        api.getResumes(),
        api.getSources(),
        api.getAuditLogs(),
      ]);
      setCandidate(candData);
      setJobs(jobsData);
      setQueue(queueData);
      setApplications(appsData);
      setResumes(resData);
      setSources(srcData);
      setAuditLogs(auditData);
    } catch (err) {
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  const handleSync = async (platform = 'mock') => {
    try {
      const res = await api.triggerDiscovery(platform);
      await loadAll();
      alert(`Discovery complete: ${res.discovered || 0} discovered, ${res.new_imported || 0} new imported.`);
    } catch (err: any) {
      alert('Discovery error: ' + err.message);
    }
  };

  const handlePrepare = async (jobId: number) => {
    try {
      const app = await api.prepareApplication(jobId);
      await loadAll();
      setReviewApp(app);
    } catch (err: any) {
      alert('Error preparing application: ' + err.message);
    }
  };

  const handleApprove = async (appId: number) => {
    try {
      await api.approveApplication(appId);
      setReviewApp(null);
      await loadAll();
      alert('Application approved successfully! It is ready for submission.');
    } catch (err: any) {
      alert('Approval error: ' + err.message);
    }
  };

  const handleReject = async (appId: number) => {
    const reason = prompt('Reason for rejection:');
    try {
      await api.rejectApplication(appId, reason || 'User rejected');
      setReviewApp(null);
      await loadAll();
    } catch (err: any) {
      alert('Error: ' + err.message);
    }
  };

  const handleSubmit = async (appId: number) => {
    if (!confirm('Are you sure you want to submit this approved application?')) return;
    try {
      await api.submitApplication(appId);
      await loadAll();
      alert('Application submitted successfully!');
    } catch (err: any) {
      alert('Submission blocked: ' + err.message);
    }
  };

  return (
    <div className="max-w-[72rem] mx-auto px-6 py-8">
      {/* Top Editorial Header */}
      <header className="border-b border-[#e0d6c6] pb-5 mb-8">
        <div className="flex justify-between items-end mb-6">
          <div>
            <span className="text-[0.72rem] tracking-widest font-bold text-[#8d3f1e] uppercase block mb-1">
              ApplyForge V2.0 · Production Stack
            </span>
            <h1 className="text-3xl font-serif font-bold text-[#1c1914] tracking-tight">Career Desk</h1>
            <span className="text-sm text-[#5f584e]">Aryan Singh · Ground-Truth Verified Candidate</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-full bg-[#e5f0e8] text-[#1e4636] border border-[#c2dcc8]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#1e4636]"></span> Zero Silent Submissions ACTIVE
            </span>
            <button
              onClick={() => handleSync('mock')}
              className="text-xs font-semibold px-3 py-1.5 rounded-full bg-[#fffdf8] border border-[#e0d6c6] hover:bg-[#f7f1e6] transition"
            >
              ↻ Sync Connectors
            </button>
          </div>
        </div>

        {/* Top Horizontal Navigation Pills (NO SIDEBAR) */}
        <nav className="flex gap-2 overflow-x-auto pt-1">
          {[
            { id: 'desk', label: 'Desk Overview' },
            { id: 'queue', label: `Review Queue (${queue.length})` },
            { id: 'jobs', label: `Discovered Jobs (${jobs.length})` },
            { id: 'applications', label: `All Applications (${applications.length})` },
            { id: 'profile', label: 'Candidate Ground-Truth' },
            { id: 'resumes', label: 'ATS Resumes' },
            { id: 'connectors', label: 'Discovery Sources' },
            { id: 'audit', label: 'Audit Trail' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setTab(item.id as any)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition whitespace-nowrap ${
                tab === item.id
                  ? 'bg-[#1c1914] text-white font-semibold'
                  : 'text-[#5f584e] hover:bg-[#fffdf8] hover:text-[#1c1914] border border-transparent hover:border-[#e0d6c6]'
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </header>

      {/* Main Views */}
      <main>
        {tab === 'desk' && (
          <div>
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
              <div className="bg-[#fffdf8] border border-[#e0d6c6] p-5 rounded-lg">
                <div className="text-3xl font-serif font-bold text-[#1c1914]">{queue.length}</div>
                <div className="text-xs font-bold uppercase tracking-wider text-[#5f584e] mt-1">Awaiting Review</div>
              </div>
              <div className="bg-[#fffdf8] border border-[#e0d6c6] p-5 rounded-lg">
                <div className="text-3xl font-serif font-bold text-[#1e4636]">
                  {applications.filter((a) => a.status === 'APPROVED').length}
                </div>
                <div className="text-xs font-bold uppercase tracking-wider text-[#5f584e] mt-1">Approved (Ready)</div>
              </div>
              <div className="bg-[#fffdf8] border border-[#e0d6c6] p-5 rounded-lg">
                <div className="text-3xl font-serif font-bold text-[#1c1914]">
                  {applications.filter((a) => a.status === 'SUBMITTED').length}
                </div>
                <div className="text-xs font-bold uppercase tracking-wider text-[#5f584e] mt-1">Submitted</div>
              </div>
              <div className="bg-[#fffdf8] border border-[#e0d6c6] p-5 rounded-lg">
                <div className="text-3xl font-serif font-bold text-[#1c1914]">{jobs.length}</div>
                <div className="text-xs font-bold uppercase tracking-wider text-[#5f584e] mt-1">Discovered Jobs</div>
              </div>
            </div>

            <div className="bg-[#fffdf8] border border-[#e0d6c6] p-6 rounded-lg mb-6">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h2 className="text-xl font-serif font-bold text-[#1c1914]">Immediate Attention Queue</h2>
                  <p className="text-sm text-[#5f584e]">Prepared applications strictly awaiting your human approval.</p>
                </div>
                <button
                  onClick={() => setTab('queue')}
                  className="bg-[#1e4636] text-white text-xs font-semibold px-4 py-2 rounded hover:opacity-90 transition"
                >
                  Review All ({queue.length})
                </button>
              </div>
              {queue.length === 0 ? (
                <div className="text-center py-8 text-[#5f584e]">No applications awaiting review.</div>
              ) : (
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-[#e0d6c6] text-xs font-bold text-[#5f584e] uppercase">
                      <th className="py-2">Role & Company</th>
                      <th className="py-2">Status</th>
                      <th className="py-2">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {queue.slice(0, 4).map((app) => (
                      <tr key={app.id} className="border-b border-[#e0d6c6]/50">
                        <td className="py-3">
                          <strong>{app.job?.title || 'Security Engineer'}</strong>
                          <div className="text-xs text-[#5f584e]">{app.job?.company}</div>
                        </td>
                        <td>
                          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-[#fdf6ed] text-[#8d3f1e] border border-[#f2dbb3]">
                            Awaiting Review
                          </span>
                        </td>
                        <td>
                          <button
                            onClick={() => setReviewApp(app)}
                            className="bg-[#1e4636] text-white text-xs font-semibold px-3 py-1.5 rounded hover:opacity-90"
                          >
                            Review & Approve
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}

        {tab === 'queue' && (
          <div className="bg-[#fffdf8] border border-[#e0d6c6] p-6 rounded-lg">
            <h2 className="text-xl font-serif font-bold text-[#1c1914] mb-1">Application Review Queue</h2>
            <p className="text-sm text-[#5f584e] mb-6">
              Inviolable rule: Zero applications are submitted without explicit human review and approval.
            </p>
            {queue.length === 0 ? (
              <div className="text-center py-12 text-[#5f584e]">Review queue is clear!</div>
            ) : (
              <div className="space-y-4">
                {queue.map((app) => (
                  <div key={app.id} className="border border-[#e0d6c6] p-4 rounded-md flex justify-between items-center bg-[#fbf8f0]">
                    <div>
                      <h3 className="font-bold text-base text-[#1c1914]">{app.job?.title}</h3>
                      <p className="text-sm text-[#5f584e]">{app.job?.company} · {app.job?.location || 'Remote'}</p>
                      <span className="text-xs text-[#8d3f1e] font-semibold mt-1 inline-block">App #{app.id} · Awaiting Review</span>
                    </div>
                    <button
                      onClick={() => setReviewApp(app)}
                      className="bg-[#1e4636] text-white text-sm font-semibold px-4 py-2 rounded hover:opacity-90"
                    >
                      Review & Approve
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {tab === 'jobs' && (
          <div className="bg-[#fffdf8] border border-[#e0d6c6] p-6 rounded-lg">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-xl font-serif font-bold text-[#1c1914]">Discovered Jobs</h2>
                <p className="text-sm text-[#5f584e]">Verified opportunities normalized from configured connectors.</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleSync('mock')}
                  className="bg-[#1e4636] text-white text-xs font-semibold px-3 py-1.5 rounded hover:opacity-90"
                >
                  ↻ Mock Discovery
                </button>
                <button
                  onClick={() => handleSync('public_feed')}
                  className="bg-[#fffdf8] border border-[#e0d6c6] text-xs font-semibold px-3 py-1.5 rounded hover:bg-[#f7f1e6]"
                >
                  ↻ Public Remote Feed
                </button>
              </div>
            </div>
            <div className="space-y-3">
              {jobs.map((j) => (
                <div key={j.id} className="border border-[#e0d6c6] p-4 rounded-md flex justify-between items-center hover:bg-[#fbf8f0]">
                  <div>
                    <h3 className="font-bold text-base text-[#1c1914]">{j.title}</h3>
                    <p className="text-sm text-[#5f584e]">{j.company} · {j.location || 'Remote'} · {j.work_mode}</p>
                  </div>
                  <button
                    onClick={() => handlePrepare(j.id)}
                    className="bg-[#1e4636] text-white text-xs font-semibold px-4 py-2 rounded hover:opacity-90"
                  >
                    Prepare Application
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {tab === 'applications' && (
          <div className="bg-[#fffdf8] border border-[#e0d6c6] p-6 rounded-lg">
            <h2 className="text-xl font-serif font-bold text-[#1c1914] mb-1">Application Lifecycle Tracker</h2>
            <p className="text-sm text-[#5f584e] mb-6">Managed applications across all stages.</p>
            <div className="space-y-3">
              {applications.map((app) => (
                <div key={app.id} className="border border-[#e0d6c6] p-4 rounded-md flex justify-between items-center bg-[#fbf8f0]">
                  <div>
                    <h3 className="font-bold text-base text-[#1c1914]">{app.job?.title}</h3>
                    <p className="text-sm text-[#5f584e]">{app.job?.company}</p>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-[#e5f0e8] text-[#1e4636] border border-[#c2dcc8] mt-1 inline-block">
                      {app.status}
                    </span>
                  </div>
                  <div>
                    {app.status === 'APPROVED' ? (
                      <button
                        onClick={() => handleSubmit(app.id)}
                        className="bg-[#1e4636] text-white text-xs font-semibold px-4 py-2 rounded hover:opacity-90"
                      >
                        Submit Now
                      </button>
                    ) : (
                      <button
                        onClick={() => setReviewApp(app)}
                        className="bg-[#fffdf8] border border-[#e0d6c6] text-xs font-semibold px-4 py-2 rounded hover:bg-[#f7f1e6]"
                      >
                        View Details
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {tab === 'profile' && candidate && (
          <div className="bg-[#fffdf8] border border-[#e0d6c6] p-6 rounded-lg space-y-6">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-2xl font-serif font-bold text-[#1c1914]">{candidate.name}</h2>
                <p className="text-sm text-[#5f584e]">{candidate.email} · {candidate.phone} · {candidate.location}</p>
                <p className="text-xs font-semibold text-[#1e4636] mt-1">{candidate.work_authorization}</p>
              </div>
              <span className="text-xs font-bold px-3 py-1 rounded-full bg-[#e5f0e8] text-[#1e4636] border border-[#bedbc5]">
                GROUND-TRUTH VERIFIED
              </span>
            </div>

            <div>
              <h3 className="font-serif font-bold text-lg mb-2">Verified Skills</h3>
              <div className="flex flex-wrap gap-2">
                {candidate.skills?.map((s) => (
                  <span key={s.id} className="text-xs font-medium px-2.5 py-1 rounded bg-[#f3efe6] border border-[#e0d6c6]">
                    {s.name} ({s.proficiency})
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h3 className="font-serif font-bold text-lg mb-2">Certifications</h3>
              <div className="flex flex-wrap gap-2">
                {candidate.certifications?.map((c) => (
                  <span key={c.id} className="text-xs font-bold px-3 py-1 rounded-full bg-[#e5f0e8] text-[#1e4636] border border-[#bedbc5]">
                    🛡️ {c.name} ({c.issuer})
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h3 className="font-serif font-bold text-lg mb-2">Verified Projects</h3>
              <div className="space-y-2">
                {candidate.projects?.map((p) => (
                  <div key={p.id} className="p-3 bg-[#fbf8f0] border border-[#e0d6c6] rounded">
                    <strong>{p.name}</strong>
                    <p className="text-xs text-[#5f584e] my-1">{p.description}</p>
                    <span className="text-[0.7rem] text-[#8d3f1e] font-semibold">Tech: {p.technologies?.join(', ')}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {tab === 'resumes' && (
          <div className="bg-[#fffdf8] border border-[#e0d6c6] p-6 rounded-lg">
            <h2 className="text-xl font-serif font-bold text-[#1c1914] mb-1">ATS Resume Variants</h2>
            <p className="text-sm text-[#5f584e] mb-6">Ground-truth verified resume variants tailored for ATS parsers.</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {resumes.map((r) => (
                <div key={r.id} className="p-4 border border-[#e0d6c6] rounded bg-[#fbf8f0]">
                  <h3 className="font-bold text-base text-[#1c1914]">{r.name}</h3>
                  <span className="text-xs text-[#5f584e] block mb-3">Family: {r.job_family}</span>
                  <a
                    href={`/api/v1/resumes/variants/${r.id}/pdf`}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-block text-xs font-semibold px-3 py-1.5 bg-[#fffdf8] border border-[#e0d6c6] rounded hover:bg-[#f7f1e6]"
                  >
                    📄 Download ATS PDF
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}

        {tab === 'connectors' && (
          <div className="bg-[#fffdf8] border border-[#e0d6c6] p-6 rounded-lg">
            <h2 className="text-xl font-serif font-bold text-[#1c1914] mb-1">Discovery Sources & Connectors</h2>
            <p className="text-sm text-[#5f584e] mb-6">Configured compliant job sources.</p>
            <div className="space-y-3">
              {sources.map((s) => (
                <div key={s.id} className="border border-[#e0d6c6] p-4 rounded-md flex justify-between items-center bg-[#fbf8f0]">
                  <div>
                    <h3 className="font-bold text-base text-[#1c1914]">{s.name}</h3>
                    <p className="text-xs text-[#5f584e]">Type: {s.type}</p>
                  </div>
                  <button
                    onClick={() => handleSync(s.name)}
                    className="bg-[#1e4636] text-white text-xs font-semibold px-3 py-1.5 rounded hover:opacity-90"
                  >
                    Trigger Discovery
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {tab === 'audit' && (
          <div className="bg-[#fffdf8] border border-[#e0d6c6] p-6 rounded-lg">
            <h2 className="text-xl font-serif font-bold text-[#1c1914] mb-1">Security & Compliance Audit Trail</h2>
            <p className="text-sm text-[#5f584e] mb-6">Tamper-evident logs of approvals and system events.</p>
            <div className="space-y-2">
              {auditLogs.map((a) => (
                <div key={a.id} className="p-3 border border-[#e0d6c6] rounded text-xs bg-[#fbf8f0] flex justify-between">
                  <div>
                    <strong>{a.event_type}</strong>
                    <div className="text-[#5f584e]">{new Date(a.timestamp).toLocaleString()} by {a.actor}</div>
                  </div>
                  <code className="text-[#8d3f1e]">{a.payload_hash?.slice(0, 16)}...</code>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Review Modal */}
      {reviewApp && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-[#fffdf8] max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 rounded-lg border border-[#e0d6c6] shadow-xl">
            <div className="flex justify-between items-start border-b border-[#e0d6c6] pb-3 mb-4">
              <div>
                <span className="text-[0.7rem] font-bold text-[#8d3f1e] uppercase">Human Review Required</span>
                <h3 className="text-xl font-serif font-bold text-[#1c1914]">{reviewApp.job?.title}</h3>
                <p className="text-sm text-[#5f584e]">{reviewApp.job?.company}</p>
              </div>
              <button
                onClick={() => setReviewApp(null)}
                className="text-xs px-2 py-1 rounded bg-[#f3efe6] border border-[#e0d6c6]"
              >
                ✕ Close
              </button>
            </div>

            <div className="mb-4">
              <h4 className="font-bold text-sm mb-1">Tailored ATS Resume</h4>
              <div className="flex justify-between items-center p-3 bg-[#fbf8f0] border border-[#e0d6c6] rounded text-xs">
                <span>Aryan Singh (Ground-truth verified)</span>
                <a
                  href={`/api/v1/applications/${reviewApp.id}/resume/pdf`}
                  target="_blank"
                  rel="noreferrer"
                  className="font-semibold text-[#1e4636] underline"
                >
                  Preview ATS PDF
                </a>
              </div>
            </div>

            <div className="mb-6">
              <h4 className="font-bold text-sm mb-2">Ground-Truth Answers</h4>
              <div className="space-y-2">
                {(reviewApp.questions || []).map((q) => (
                  <div key={q.id} className="p-3 bg-[#fbf8f0] border border-[#e0d6c6] rounded text-xs">
                    <span className="text-[0.65rem] font-bold px-1.5 py-0.5 rounded bg-[#e5f0e8] text-[#1e4636]">
                      ✓ {q.answer_source}
                    </span>
                    <div className="font-semibold mt-1">Q: {q.question}</div>
                    <div className="text-[#1c1914] mt-0.5">{q.final_answer || q.answer}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-3 border-t border-[#e0d6c6]">
              <button
                onClick={() => handleReject(reviewApp.id)}
                className="text-xs font-semibold px-4 py-2 rounded bg-red-50 text-red-700 border border-red-200"
              >
                Reject / Skip
              </button>
              <button
                onClick={() => setReviewApp(null)}
                className="text-xs font-semibold px-4 py-2 rounded bg-[#fffdf8] border border-[#e0d6c6]"
              >
                Save for Later
              </button>
              <button
                onClick={() => handleApprove(reviewApp.id)}
                className="text-xs font-semibold px-4 py-2 rounded bg-[#1e4636] text-white hover:opacity-90"
              >
                ✓ Approve Application
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
