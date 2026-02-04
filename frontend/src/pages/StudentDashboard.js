import { useEffect, useState } from "react";
import { getToken } from "../utils/auth";

function StudentDashboard() {
  const [resumes, setResumes] = useState([]);
  const [error, setError] = useState("");
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [file, setFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");

  const [roles, setRoles] = useState([]);
  const [selectedRole, setSelectedRole] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [selectedResumeId, setSelectedResumeId] = useState(null);

  const fetchResumes = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/student/resumes",
        {
          headers: {
            Authorization: `Bearer ${getToken()}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Failed to load resumes");
        return;
      }

      setResumes(data);
    } catch {
      setError("Server error");
    }
  };

  useEffect(() => {
    fetchResumes();
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!file) {
      setUploadMessage("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("resume", file);

    try {
      setUploadMessage("Uploading... ⏳");

      const response = await fetch(
        "http://127.0.0.1:8000/student/resume/upload",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${getToken()}`
          },
          body: formData
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setUploadMessage(data.detail || "Upload failed");
        return;
      }

      setUploadMessage("Resume uploaded successfully ✅");
      setFile(null);
      fetchResumes();

    } catch {
      setUploadMessage("Server error during upload");
    }
  };

  const fetchAnalysis = async (resumeId) => {
    setSelectedResumeId(resumeId);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/student/resume/${resumeId}`,
        {
          headers: {
            Authorization: `Bearer ${getToken()}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert(data.detail || "Failed to load analysis");
        return;
      }

      setSelectedAnalysis(data);

      // 🔥 Expect roles only initially
      setRoles(data.analysis?.roles || []);
      setEvaluation(null);
      setSelectedRole(null);

    } catch {
      alert("Server error");
    }
  };

  const handleRoleSelection = async (role) => {
    setSelectedRole(role);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/student/resume/${selectedResumeId}/evaluate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${getToken()}`
          },
          body: JSON.stringify({ target_role: role })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert("Failed to evaluate resume for selected role");
        return;
      }

      setEvaluation(data);

    } catch {
      alert("Server error");
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "Unknown";

    return new Date(dateString).toLocaleString("en-IN", {
      dateStyle: "medium",
      timeStyle: "medium",
    });
  };

  return (
    <div>
      <h2>Student Dashboard</h2>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <h3>Upload Resume</h3>

      <form onSubmit={handleUpload}>
        <input
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <br />
        <button type="submit">Upload</button>
      </form>

      <p>{uploadMessage}</p>

      <h3>Your Resumes</h3>

      {resumes.length === 0 ? (
        <p>No resumes uploaded yet.</p>
      ) : (
        <ul>
          {resumes.map((resume) => (
            <li key={resume.resume_id}>
              <button onClick={() => fetchAnalysis(resume.resume_id)}>
                {resume.filename}
              </button>
              <br />
              Uploaded at: {formatDate(resume.uploaded_at)}
            </li>
          ))}
        </ul>
      )}

      {/* ROLE SELECTION */}
      {roles.length > 0 && (
        <div style={{ marginTop: "20px" }}>
          <h3>Select a Target Role</h3>

          {roles.map((r, idx) => (
            <button
              key={idx}
              style={{ marginRight: "10px" }}
              onClick={() => handleRoleSelection(r.role)}
            >
              {r.role} ({Math.round(r.confidence * 100)}%)
            </button>
          ))}
        </div>
      )}

      {/* ATS AFTER ROLE SELECTION */}
      {evaluation && (
        <div style={{ marginTop: "30px" }}>
          <h3>ATS Evaluation — {evaluation.target_role}</h3>

          <p>
            <strong>ATS Score:</strong>{" "}
            {evaluation.ats?.ats_score ?? "N/A"}
          </p>

          <h4>Missing Skills</h4>
          <ul>
            {(evaluation.ats?.missing_skills?.core ||
              evaluation.ats?.missing_skills ||
              []).map((s, idx) => (
              <li key={idx}>{s}</li>
            ))}
          </ul>

          <h4>Learning Path</h4>
          <pre>{JSON.stringify(evaluation.learning_path, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default StudentDashboard;
