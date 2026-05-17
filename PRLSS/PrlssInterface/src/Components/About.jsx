import "./About.css";
import EarthVideo from "../../earth.mp4";

function About() {
  return (
    <div className="about-wrapper">
      
      {/* Background Video */}
      <div className="video-bg">
        <video autoPlay loop muted playsInline>
          <source src={EarthVideo} type="video/mp4" />
        </video>
        <div className="video-fade"></div>
      </div>

      <div className="scroll-content">
        
        <div className="about-hero-content">
          <h1 className="about-title">About PRLSS</h1>
          <p className="about-subtitle">
            PRLSS — Personalized Relocation Suggestion System — is a B.Tech
            final year project that uses machine learning to recommend the best
            apartments when you move to a new city.
          </p>
        </div>

        {/* Sleek Minimalist Info Section */}
        <div className="about-cards-container">
          
          <div className="about-card">
            <div className="about-card-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect>
                <rect x="9" y="9" width="6" height="6"></rect>
                <line x1="9" y1="1" x2="9" y2="4"></line>
                <line x1="15" y1="1" x2="15" y2="4"></line>
                <line x1="9" y1="20" x2="9" y2="23"></line>
                <line x1="15" y1="20" x2="15" y2="23"></line>
                <line x1="20" y1="9" x2="23" y2="9"></line>
                <line x1="20" y1="14" x2="23" y2="14"></line>
                <line x1="1" y1="9" x2="4" y2="9"></line>
                <line x1="1" y1="14" x2="4" y2="14"></line>
              </svg>
            </div>
            <h3>XGBoost ML</h3>
            <p>Trained model predicts apartment value scores with 85% accuracy, ensuring you only see the most viable options.</p>
          </div>

          <div className="about-card">
            <div className="about-card-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"></polygon>
                <line x1="9" y1="3" x2="9" y2="21"></line>
                <line x1="15" y1="3" x2="15" y2="21"></line>
              </svg>
            </div>
            <h3>Google Maps</h3>
            <p>Search seamlessly by area name. Our live map interface visualizes all optimized apartment locations natively.</p>
          </div>

          <div className="about-card">
            <div className="about-card-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect>
                <path d="M9 22v-4h6v4"></path>
                <path d="M8 6h.01"></path>
                <path d="M16 6h.01"></path>
                <path d="M12 6h.01"></path>
                <path d="M12 10h.01"></path>
                <path d="M12 14h.01"></path>
                <path d="M16 10h.01"></path>
                <path d="M16 14h.01"></path>
                <path d="M8 10h.01"></path>
                <path d="M8 14h.01"></path>
              </svg>
            </div>
            <h3>3 Major Cities</h3>
            <p>Currently covering Nashik, Pune, and Mumbai with a growing dataset of premium apartments.</p>
          </div>

        </div>

      </div>
    </div>
  );
}

export default About;
