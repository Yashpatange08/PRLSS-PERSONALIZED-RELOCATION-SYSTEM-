import { useState, useEffect } from "react";
import "./Home.css";
import EarthVideo from "../../earth.mp4";

function Home() {
  const defaultMapSrc = "https://maps.google.com/maps?q=Chhatrapati%20Sambhajinagar,%20Maharashtra&t=&z=13&ie=UTF8&iwloc=&output=embed";
  const [mapSrc, setMapSrc] = useState(defaultMapSrc);

  useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          setMapSrc(`https://maps.google.com/maps?q=${lat},${lng}&t=&z=13&ie=UTF8&iwloc=&output=embed`);
        },
        (error) => {
          console.error("Error getting location: ", error);
        }
      );
    }
  }, []);

  return (
    <div className="home-wrapper">

      {/* Background Video (Fixed to the top 100vh) */}
      <div className="video-bg">
        <video autoPlay loop muted playsInline>
          <source src={EarthVideo} type="video/mp4" />
        </video>
        {/* Subtle fade at the bottom of the video */}
        <div className="video-fade"></div>
      </div>

      {/* ── Content Container (Scrolls over the video) ── */}
      <div className="scroll-content">

        {/* Central Hero Text */}
        <div className="hero-content">
          <p className="hero-title">We find house which feels home !</p>
          <p className="hero-subtitle">
            Finding the right apartment is no longer just about location—it's about how well a space aligns with your daily habits, preferences, and lifestyle patterns. Our intelligent relocation platform goes beyond traditional search by analyzing your past behavior and identifying the amenities you consistently rely on, whether it's proximity to gyms, cafés, public transport, healthcare, or quiet green spaces. Instead of overwhelming you with generic listings, we curate a refined selection of apartments that closely match your personal usage patterns, ranked by relevance and convenience. By combining data-driven insights with real-world geographic intelligence, we help you transition into a new city seamlessly—minimizing uncertainty and maximizing comfort from day one. This is not just apartment hunting; it's a smarter, personalized way to relocate, designed entirely around you.
          </p>
        </div>

        {/* Components Section (Map & Upload Form overlapping the Earth) */}
        <div className="components-container">

          {/* Left: Map Preview */}
          <div className="home-map-container">
            <iframe
              src={mapSrc}
              width="100%"
              height="100%"
              style={{
                border: 0,
                filter: "invert(90%) hue-rotate(190deg) saturate(80%) brightness(85%) contrast(100%)"
              }}
              allowFullScreen=""
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
              title="Your Location Map"
            ></iframe>
          </div>

          {/* Right: Upload Form */}
          <div className="upload-form-container">
            <h2 className="upload-title">Upload Apartment Data</h2>
            <form className="upload-form" onSubmit={(e) => e.preventDefault()}>
              <input
                type="text"
                className="upload-input"
                placeholder="Enter City Name"
                required
              />
              <input
                type="file"
                className="upload-file-input"
                required
              />
              <div className="upload-buttons">
                <button type="submit" className="btn-submit">Submit</button>
                <button type="button" className="btn-cancel">Cancel</button>
              </div>
            </form>
          </div>

        </div>

      </div>

    </div>
  );
}

export default Home;
