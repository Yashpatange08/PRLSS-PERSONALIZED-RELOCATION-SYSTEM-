import { NavLink } from "react-router-dom";
import "./NavBar.css";

function NavBar() {
  return (
    <div className="navbar-container">
      <nav className="navbar">
        <NavLink to="/" end className="nav-link">Home</NavLink>
        <NavLink to="/about" className="nav-link">About</NavLink>
        <NavLink to="/help" className="nav-link">Help</NavLink>
        <NavLink to="/cart" className="nav-link">Cart</NavLink>
      </nav>
    </div>
  );
}

export default NavBar;
