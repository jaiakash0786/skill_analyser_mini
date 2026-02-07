import { useEffect, useState } from "react";
import { getToken } from "../utils/auth";
import "./RecruiterDashboard.css";

function RecruiterDashboard() {
  const [allCandidates, setAllCandidates] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [error, setError] = useState("");
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const [minAts, setMinAts] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [skillFilter, setSkillFilter] = useState("");

  const loadCandidates = async () => {
    try {
      setLoading(true);

      const response = await fetch(
        "http://127.0.0.1:8000/recruiter/candidates",
        {
          headers: {
            Authorization: `Bearer ${getToken()}`
          }
        }
      );

      const baseCandidates = await response.json();

      if (!response.ok) {
        setError(baseCandidates.detail || "Failed to load candidates");
        return;
      }

      const candidatesWithAnalysis = await Promise.all(
        baseCandidates.map(async (c) => {
          try {
            const res = await fetch(
              `http://127.0.0.1:8000/recruiter/resume/${c.resume_id}`,
              {
                headers: {
                  Authorization: `Bearer ${getToken()}`
                }
              }
            );

            const data = await res.json();

            return {
              ...c,
              analysis: data.analysis
            };
          } catch {
            return c;
          }
        })
      );

      const sorted = candidatesWithAnalysis.sort(
        (a, b) =>
          (b.analysis?.ats?.ats_score || 0) -
          (a.analysis?.ats?.ats_score || 0)
      );

      setAllCandidates(sorted);
      setCandidates(sorted);
      setError("");
    } catch {
      setError("Server error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCandidates();
  }, []);

  const applyFilters = () => {
    let filtered = [...allCandidates];

    if (minAts) {
      filtered = filtered.filter(
        (c) => (c.analysis?.ats?.ats_score || 0) >= Number(minAts)
      );
    }

    if (roleFilter.trim()) {
      filtered = filtered.filter((c) =>
        c.analysis?.roles?.some((r) =>
          r.role.toLowerCase().includes(roleFilter.toLowerCase())
        )
      );
    }

    if (skillFilter.trim()) {
      const skills = skillFilter
        .toLowerCase()
        .split(",")
        .map((s) => s.trim());

      filtered = filtered.filter((c) => {
        const matched =
          c.analysis?.ats?.matched_skills?.map((s) =>
            s.toLowerCase()
          ) || [];

        return skills.every((skill) => matched.includes(skill));
      });
    }

    const sorted = filtered.sort(
      (a, b) =>
        (b.analysis?.ats?.ats_score || 0) -
        (a.analysis?.ats?.ats_score || 0)
    );

    setCandidates(sorted);
  };

  const clearFilters = () => {
    setMinAts("");
    setRoleFilter("");
    setSkillFilter("");
    setCandidates(allCandidates);
  };

  const fetchAnalysis = async (resumeId) => {
    setLoading(true);
    setSelectedAnalysis(null);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/recruiter/resume/${resumeId}`,
        {
          headers: {
            Authorization: `Bearer ${getToken()}`
          }
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert(data.detail || "Failed to load analysis");
        return;
      }

      setSelectedAnalysis(data);
    } catch {
      alert("Server error");
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (score) => {
    if (!score) return "#cbd5e1";
    if (score >= 75) return "#22c55e";
    if (score >= 50) return "#f59e0b";
    return "#ef4444";
  };

  /* ✅ Scroll lock when modal opens */
  useEffect(() => {
    if (selectedAnalysis) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
    }

    return () => {
      document.body.style.overflow = "auto";
    };
  }, [selectedAnalysis]);

  return (
    <div className="recruiter-shell">

      <div className="recruiter-header">
        <h2>Recruiter Dashboard</h2>
      </div>

      <div className="filter-box">
        <h4>Filters</h4>

        <input
          type="number"
          placeholder="Min ATS"
          value={minAts}
          onChange={(e) => setMinAts(e.target.value)}
        />

        <input
          type="text"
          placeholder="Role (e.g. Backend Engineer)"
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
        />

        <input
          type="text"
          placeholder="Skills (react,javascript)"
          value={skillFilter}
          onChange={(e) => setSkillFilter(e.target.value)}
        />

        <button onClick={applyFilters}>Apply Filters</button>
        <button onClick={clearFilters}>Clear</button>
      </div>

      {error && <p className="error-text">{error}</p>}
      {loading && <p>Loading...</p>}

      {candidates.length === 0 && !loading ? (
        <p>No candidates found.</p>
      ) : (
        <table className="candidate-table">
          <thead>
            <tr>
              <th>Candidate Email</th>
              <th>Resume</th>
              <th>ATS Score</th>
            </tr>
          </thead>

          <tbody>
            {candidates.map((c) => (
              <tr key={c.resume_id}>
                <td>{c.candidate_email}</td>

                <td>
                  <button onClick={() => fetchAnalysis(c.resume_id)}>
                    {c.filename}
                  </button>
                </td>

                <td
                  style={{
                    color: scoreColor(c.analysis?.ats?.ats_score),
                    fontWeight: "bold"
                  }}
                >
                  {c.analysis?.ats?.ats_score ?? "N/A"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* ✅ REAL MODAL */}
      {selectedAnalysis && (
        <div
          className="popup-overlay"
          onClick={() => setSelectedAnalysis(null)}
        >
          <div
            className="analysis-popup"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className="close-btn"
              onClick={() => setSelectedAnalysis(null)}
            >
              ✕
            </button>

            <h3>Candidate Analysis</h3>

            <p>
              <strong>Email:</strong> {selectedAnalysis.candidate_email}
            </p>

            <p>
              <strong>ATS Score:</strong>{" "}
              <span
                style={{
                  color: scoreColor(
                    selectedAnalysis.analysis?.ats?.ats_score
                  )
                }}
              >
                {selectedAnalysis.analysis?.ats?.ats_score ?? "N/A"}
              </span>
            </p>

            <h4>Suggested Roles</h4>
            <ul>
              {selectedAnalysis.analysis?.roles?.map((r, idx) => (
                <li key={idx}>{r.role}</li>
              ))}
            </ul>

            <h4>Matched Skills</h4>
            <ul>
              {selectedAnalysis.analysis?.ats?.matched_skills?.map((s, idx) => (
                <li key={idx}>{s}</li>
              ))}
            </ul>

            <h4>Missing Skills</h4>
            <ul>
              {selectedAnalysis.analysis?.ats?.missing_skills?.map((s, idx) => (
                <li key={idx}>{s}</li>
              ))}
            </ul>

          </div>
        </div>
      )}
    </div>
  );
}

export default RecruiterDashboard;
