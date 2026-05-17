import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useUser } from "../Contexts/User.jsx";
import "./Home.css";
import EarthVideo from "../../earth.mp4";

function Home() {
  const defaultMapSrc = "https://maps.google.com/maps?q=Chhatrapati%20Sambhajinagar,%20Maharashtra&t=&z=13&ie=UTF8&iwloc=&output=embed";
  const [mapSrc, setMapSrc] = useState(defaultMapSrc);

  const navigate = useNavigate();
  const { updateUser } = useUser();
  const [cities, setCities] = useState([]);
  const [searchCity, setSearchCity] = useState("nashik");
  const [budget, setBudget] = useState(25000);
  const [timelineFile, setTimelineFile] = useState(null);

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

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/cities/")
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setCities(data);
        else if (data.data && Array.isArray(data.data)) setCities(data.data);
        else if (data.results && Array.isArray(data.results)) setCities(data.results);
        else setCities([]); // Fallback if API fails
      })
      .catch(err => {
        console.error("Error loading cities", err);
        setCities([]);
      });
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    
    if (timelineFile) {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const json = JSON.parse(event.target.result);
          let lat = null;
          let lon = null;
          
          if (json.locations && json.locations.length > 0) {
            // Get the last location (usually the most recent in timeline arrays)
            const loc = json.locations[json.locations.length - 1];
            lat = loc.latitudeE7 / 1e7;
            lon = loc.longitudeE7 / 1e7;
          } else if (Array.isArray(json) && json.length > 0) {
            const loc = json[json.length - 1];
            if (loc.latitudeE7) {
                lat = loc.latitudeE7 / 1e7;
                lon = loc.longitudeE7 / 1e7;
            } else if (loc.lat) {
                lat = parseFloat(loc.lat);
                lon = parseFloat(loc.lon || loc.lng);
            }
          }
          updateUser({ city: searchCity, budget: budget, college_lat: lat, college_lon: lon });
          navigate("/map");
        } catch (err) {
          console.error("Error parsing JSON", err);
          updateUser({ city: searchCity, budget: budget, college_lat: null, college_lon: null });
          navigate("/map");
        }
      };
      reader.readAsText(timelineFile);
    } else {
      updateUser({ city: searchCity, budget: budget, college_lat: null, college_lon: null });
      navigate("/map");
    }
  };

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

          {/* Right: Search Form */}
          <div className="upload-form-container">
            <h2 className="upload-title">Find Your Next Home</h2>
            <form className="upload-form" onSubmit={handleSearch}>
              <div style={{ marginBottom: "1rem" }}>
                <label style={{ display: "block", marginBottom: "0.5rem", color: "#eee" }}>Select City</label>
                <select
                  className="upload-input"
                  value={searchCity}
                  onChange={(e) => setSearchCity(e.target.value)}
                  required
                >
                  {cities.length === 0 && <option value="nashik">Nashik</option>}
                  {cities.map(c => (
                    <option key={c.slug} value={c.slug}>{c.name}, {c.state_name}</option>
                  ))}
                </select>
              </div>
              <div style={{ marginBottom: "1rem" }}>
                <label style={{ display: "block", marginBottom: "0.5rem", color: "#eee" }}>Monthly Budget (₹)</label>
                <input
                  type="number"
                  className="upload-input"
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                  min="5000"
                  step="1000"
                  required
                />
              </div>
              <div style={{ marginBottom: "1rem" }}>
                <label style={{ display: "block", marginBottom: "0.5rem", color: "#eee" }}>Google Timeline (JSON)</label>
                <input
                  type="file"
                  accept=".json,.csv"
                  className="upload-file-input"
                  onChange={(e) => setTimelineFile(e.target.files[0])}
                  required
                />
              </div>
              <div className="upload-buttons" style={{ marginTop: "2rem" }}>
                <button type="submit" className="btn-submit">Search</button>
              </div>
            </form>
          </div>

        </div>

      </div>

    </div>
  );
}

export default Home;
