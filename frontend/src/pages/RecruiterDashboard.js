import { useEffect, useState } from "react";
import { getToken } from "../utils/auth";

function RecruiterDashboard() {
  const [candidates, setCandidates] = useState([]);
  const [error, setError] = useState("");
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchCandidates = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/recruiter/candidates",
          {
            headers: {
              Authorization: `Bearer ${getToken()}`
            }
          }
        );

        const data = await response.json();

        if (!response.ok) {
          setError(data.detail || "Failed to load candidates");
          return;
        }

        const sorted = [...data].sort(
          (a, b) => (b.ats_score || 0) - (a.ats_score || 0)
        );

        setCandidates(sorted);
      } catch {
        setError("Server error");
      }
    };

    fetchCandidates();
  }, []);

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
    if (!score) return "black";
    if (score >= 75) return "green";
    if (score >= 50) return "orange";
    return "red";
  };

  return (
    <div>
      <h2>Recruiter Dashboard</h2>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {candidates.length === 0 ? (
        <p>No candidates found.</p>
      ) : (
        <table border="1" cellPadding="8">
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

                <td style={{ color: scoreColor(c.ats_score), fontWeight: "bold" }}>
                  {c.ats_score ?? "N/A"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {loading && <p>Loading analysis...</p>}

      {selectedAnalysis && (
        <div style={{ marginTop: "30px" }}>
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
                ),
                fontWeight: "bold"
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

          <h4>Missing Skills</h4>
          <ul>
            {selectedAnalysis.analysis?.ats?.missing_skills?.map((s, idx) => (
              <li key={idx}>{s}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default RecruiterDashboard;
