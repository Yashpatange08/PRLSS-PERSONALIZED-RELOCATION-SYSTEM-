import "./Footer.css";

function Footer() {
  return (
    <footer className="global-footer">
      <div className="footer-logo">PRlss</div>
      <div className="footer-links">
        <a href="/">Home</a>
        <a href="/about">About</a>
        <a href="#services">Services</a>
        <a href="#contact">Contact</a>
      </div>
      <div className="footer-copyright">
        © 2026 All rights reserved
      </div>
    </footer>
  );
}

export default Footer;
