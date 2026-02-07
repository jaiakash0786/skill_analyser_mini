import { Link, useLocation } from "react-router-dom";
import "./Navbar.css";

function Navbar() {

  const location = useLocation();

  const isActive = (path) =>
    location.pathname === path ? "nav-link active" : "nav-link";

  return (
    <div className="navbar">

      {/* Logo */}
      <div className="logo">
        MIMINI
      </div>

      {/* Links */}
      <div className="nav-links">
        <Link className={isActive("/login")} to="/login">
          Login
        </Link>

        <Link className={isActive("/register")} to="/register">
          Register
        </Link>

        <Link className={isActive("/student")} to="/student">
          Student
        </Link>

        <Link className={isActive("/recruiter")} to="/recruiter">
          Recruiter
        </Link>
      </div>

    </div>
  );
}

export default Navbar;
