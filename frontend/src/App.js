import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

import Login from "./pages/Login";
import StudentDashboard from "./pages/StudentDashboard";
import ProtectedRoute from "./components/ProtectedRoute";

import RecruiterDashboard from "./pages/RecruiterDashboard";

function App() {
  return (
    <BrowserRouter>
      <div style={{ padding: "20px" }}>
        <h1>Mimini AI Resume Platform</h1>

        <nav style={{ marginBottom: "20px" }}>
          <Link to="/login">Login</Link> |{" "}
          <Link to="/student">Student</Link> |{" "}
          <Link to="/recruiter">Recruiter</Link>
        </nav>

        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
  path="/student"
  element={
    <ProtectedRoute>
      <StudentDashboard />
    </ProtectedRoute>
  }
/>

<Route
  path="/recruiter"
  element={
    <ProtectedRoute>
      <RecruiterDashboard />
    </ProtectedRoute>
  }
/>

        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
