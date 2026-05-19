import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useUser } from "../Contexts/User.jsx";
import "./Home.css";
import EarthVideo from "../../earth.mp4";

const MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_KEY || "";

function Home() {
  const mapRef = useRef(null);
  const googleMap = useRef(null);
  const marker = useRef(null);
  const searchInputRef = useRef(null);

  const [targetLocation, setTargetLocation] = useState(null);
  const [userDetectedCity, setUserDetectedCity] = useState(null);

  const navigate = useNavigate();
  const { updateUser } = useUser();
  const [cities, setCities] = useState([]);
  const [searchCity, setSearchCity] = useState("nashik");
  const [budget, setBudget] = useState(25000);
  const [timelineFile, setTimelineFile] = useState(null);

  const initGoogleMap = (centerLat, centerLng) => {
    if (!mapRef.current) return;
    
    const loadMap = () => {
      if (!googleMap.current) {
        googleMap.current = new window.google.maps.Map(mapRef.current, {
          center: { lat: centerLat, lng: centerLng },
          zoom: 13,
          mapTypeId: "roadmap",
          styles: [
            { elementType: "geometry", stylers: [{ color: "#1a1a2e" }] },
            { elementType: "labels.text.fill", stylers: [{ color: "#8b949e" }] },
            { elementType: "labels.text.stroke", stylers: [{ color: "#1a1a2e" }] },
            { featureType: "road", elementType: "geometry", stylers: [{ color: "#2d2d4a" }] },
            { featureType: "road.highway", elementType: "geometry", stylers: [{ color: "#3d3d6a" }] },
            { featureType: "water", elementType: "geometry", stylers: [{ color: "#0f172a" }] },
          ],
          disableDefaultUI: false,
        });

        // Reverse geocode to detect city automatically
        const detectCity = (lat, lng) => {
          const geocoder = new window.google.maps.Geocoder();
          geocoder.geocode({ location: { lat, lng } }, (results, status) => {
            if (status === "OK" && results[0]) {
              let localityComp = results[0].address_components.find(c => c.types.includes("locality"));
              if (!localityComp) {
                localityComp = results[0].address_components.find(c => c.types.includes("administrative_area_level_3"));
              }
              if (!localityComp) {
                localityComp = results[0].address_components.find(c => c.types.includes("administrative_area_level_2"));
              }
              if (localityComp) {
                setUserDetectedCity(localityComp.long_name.toLowerCase());
              }
            }
          });
        };

        detectCity(centerLat, centerLng);

        googleMap.current.addListener("click", (e) => {
          const lat = e.latLng.lat();
          const lng = e.latLng.lng();
          setTargetLocation({ lat, lng });

          if (marker.current) {
            marker.current.setPosition({ lat, lng });
          } else {
            marker.current = new window.google.maps.Marker({
              position: { lat, lng },
              map: googleMap.current,
              title: "Target Location",
              animation: window.google.maps.Animation.DROP,
              icon: {
                path: window.google.maps.SymbolPath.CIRCLE,
                scale: 10,
                fillColor: "#3b82f6",
                fillOpacity: 1,
                strokeColor: "#ffffff",
                strokeWeight: 2,
              },
            });
          }
        });

        if (searchInputRef.current) {
          const autocomplete = new window.google.maps.places.Autocomplete(searchInputRef.current);
          autocomplete.bindTo("bounds", googleMap.current);
          
          autocomplete.addListener("place_changed", () => {
            const place = autocomplete.getPlace();
            if (!place.geometry || !place.geometry.location) return;

            const lat = place.geometry.location.lat();
            const lng = place.geometry.location.lng();
            
            googleMap.current.panTo({ lat, lng });
            googleMap.current.setZoom(15);
            setTargetLocation({ lat, lng });

            if (marker.current) {
              marker.current.setPosition({ lat, lng });
            } else {
              marker.current = new window.google.maps.Marker({
                position: { lat, lng },
                map: googleMap.current,
                title: "Target Location",
                animation: window.google.maps.Animation.DROP,
                icon: {
                  path: window.google.maps.SymbolPath.CIRCLE,
                  scale: 10,
                  fillColor: "#3b82f6",
                  fillOpacity: 1,
                  strokeColor: "#ffffff",
                  strokeWeight: 2,
                },
              });
            }
          });
        }
      } else {
        googleMap.current.panTo({ lat: centerLat, lng: centerLng });
        
        // Also geocode if map was already created
        const geocoder = new window.google.maps.Geocoder();
        geocoder.geocode({ location: { lat: centerLat, lng: centerLng } }, (results, status) => {
          if (status === "OK" && results[0]) {
            let localityComp = results[0].address_components.find(c => c.types.includes("locality"));
            if (!localityComp) {
              localityComp = results[0].address_components.find(c => c.types.includes("administrative_area_level_3"));
            }
            if (!localityComp) {
              localityComp = results[0].address_components.find(c => c.types.includes("administrative_area_level_2"));
            }
            if (localityComp) {
              setUserDetectedCity(localityComp.long_name.toLowerCase());
            }
          }
        });
      }
    };

    if (window.google && window.google.maps) {
      loadMap();
    } else {
      let script = document.getElementById("google-maps-script");
      if (!script) {
        script = document.createElement("script");
        script.id = "google-maps-script";
        script.src = `https://maps.googleapis.com/maps/api/js?key=${MAPS_API_KEY}&libraries=places`;
        script.async = true;
        document.head.appendChild(script);
      }
      script.addEventListener('load', loadMap);
    }
  };

  useEffect(() => {
    let locationFound = false;

    const fallbackToIP = () => {
      if (locationFound) return;
      fetch("https://ipapi.co/json/")
        .then(res => res.json())
        .then(data => {
          if (!locationFound && data && data.latitude && data.longitude) {
            initGoogleMap(data.latitude, data.longitude);
          }
        })
        .catch(() => {
          if (!locationFound) initGoogleMap(19.8762, 75.3433);
        });
    };

    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          locationFound = true;
          initGoogleMap(position.coords.latitude, position.coords.longitude);
        },
        (error) => {
          console.error("Error getting location: ", error);
          fallbackToIP();
        },
        { timeout: 5000 }
      );
    } else {
      fallbackToIP();
    }

    // If geolocation takes too long or is ignored, fallback to IP after 4 seconds
    setTimeout(() => {
      if (!locationFound && !googleMap.current) {
        fallbackToIP();
      }
    }, 4000);
  }, []);

  useEffect(() => {
    if (searchCity && cities.length > 0) {
      const cityObj = cities.find(c => c.slug === searchCity);
      if (cityObj && googleMap.current) {
        const lat = parseFloat(cityObj.latitude);
        const lng = parseFloat(cityObj.longitude);
        if (!isNaN(lat) && !isNaN(lng)) {
          googleMap.current.panTo({ lat, lng });
        }
      }
    }
  }, [searchCity, cities]);

  useEffect(() => {
    if (userDetectedCity && cities.length > 0) {
      const cityObj = cities.find(c => {
        if (!c || !c.slug || !c.name) return false;
        const slugLower = c.slug.toLowerCase();
        const nameLower = c.name.toLowerCase();
        return slugLower === userDetectedCity || 
               nameLower === userDetectedCity ||
               userDetectedCity.includes(nameLower) || 
               nameLower.includes(userDetectedCity);
      });
      if (cityObj) {
        setSearchCity(cityObj.slug);
      } else {
        const newSlug = userDetectedCity.replace(/\s+/g, '-');
        setCities(prev => {
          if (prev.some(c => c.slug === newSlug)) return prev;
          let lat = null, lng = null;
          if (googleMap.current) {
            const center = googleMap.current.getCenter();
            lat = center.lat();
            lng = center.lng();
          }
          return [{
            id: 'detected',
            name: userDetectedCity.charAt(0).toUpperCase() + userDetectedCity.slice(1),
            slug: newSlug,
            state_name: 'Current Location',
            latitude: lat,
            longitude: lng
          }, ...prev];
        });
        setSearchCity(newSlug);
      }
    }
  }, [userDetectedCity, cities.length]);

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

    if (targetLocation) {
      updateUser({ city: searchCity, budget: budget, college_lat: targetLocation.lat, college_lon: targetLocation.lng });
      navigate("/map");
      return;
    }
    
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
          <div className="home-map-container" style={{ position: "relative" }}>
            <div ref={mapRef} style={{ width: "100%", height: "100%", borderRadius: "8px", overflow: "hidden" }} />
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Search for your college, office, or workplace..."
              style={{
                position: "absolute", top: "15px", left: "15px", width: "calc(100% - 80px)",
                padding: "12px 15px", borderRadius: "8px", border: "none",
                fontSize: "1rem", boxShadow: "0 2px 10px rgba(0,0,0,0.3)", zIndex: 10,
                outline: "none", boxSizing: "border-box", fontFamily: "inherit"
              }}
            />
            {!targetLocation && (
              <div style={{
                position: "absolute", bottom: "20px", left: "50%", transform: "translateX(-50%)",
                background: "rgba(0,0,0,0.75)", color: "white", padding: "10px 20px", borderRadius: "30px",
                fontSize: "0.95rem", pointerEvents: "none", zIndex: 10, boxShadow: "0 4px 10px rgba(0,0,0,0.3)"
              }}>
                📍 Click or search to set your target location
              </div>
            )}
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
