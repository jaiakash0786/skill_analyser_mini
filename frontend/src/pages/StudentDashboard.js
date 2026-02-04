import { useEffect, useState } from "react";
import { getToken } from "../utils/auth";

function StudentDashboard() {
  const [resumes, setResumes] = useState([]);
  const [error, setError] = useState("");
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [file, setFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");

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

      // 🔥 ALWAYS refetch from backend
      fetchResumes();

    } catch {
      setUploadMessage("Server error during upload");
    }
  };

  const fetchAnalysis = async (resumeId) => {
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

      {selectedAnalysis && (
        <div style={{ marginTop: "30px" }}>
          <h3>ATS Analysis</h3>

          <p>
            <strong>Resume:</strong> {selectedAnalysis.filename}
          </p>

          <p>
            <strong>ATS Score:</strong>{" "}
            {selectedAnalysis.analysis?.ats?.ats_score ?? "N/A"}
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

export default StudentDashboard;
