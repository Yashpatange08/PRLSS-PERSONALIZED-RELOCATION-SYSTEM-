import { useEffect, useRef, useState } from "react";
import { useUser } from "../Contexts/User.jsx";
import "./Map.css";

// Your Google Maps API key — set in .env as VITE_GOOGLE_MAPS_KEY
const MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_KEY || "";

// City center coordinates
const CITY_CENTERS = {
  nashik: { lat: 19.9975, lng: 73.7898, zoom: 13 },
  pune:   { lat: 18.5204, lng: 73.8567, zoom: 13 },
  mumbai: { lat: 19.0760, lng: 72.8777, zoom: 12 },
};

function Map() {
  const { user } = useUser();
  const mapRef    = useRef(null);
  const googleMap = useRef(null);
  const markers   = useRef([]);

  const [apartments, setApartments]   = useState([]);
  const [selected, setSelected]       = useState(null);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState("");

  // ── Load apartments from Django API ──────────────────────────────────────
  useEffect(() => {
    const city   = user.city || "nashik";
    const budget = user.budget || 25000;

    fetch(`http://127.0.0.1:8000/api/apartments/?city=${city}&max_rent=${budget}`)
      .then((r) => r.json())
      .then((data) => {
        setApartments(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(() => {
        setError("Could not load apartments. Make sure the Django server is running.");
        setLoading(false);
      });
  }, [user.city, user.budget]);

  // ── Load Google Maps + place pins ────────────────────────────────────────
  useEffect(() => {
    if (!mapRef.current) return;

    const city   = user.city || "nashik";
    const center = CITY_CENTERS[city] || CITY_CENTERS.nashik;

    const loadMap = () => {
      // Init map
      googleMap.current = new window.google.maps.Map(mapRef.current, {
        center,
        zoom: center.zoom,
        mapTypeId: "roadmap",
        styles: DARK_MAP_STYLES,
        disableDefaultUI: false,
        zoomControl: true,
        streetViewControl: false,
        mapTypeControl: false,
        fullscreenControl: true,
      });

      // Place pins for each apartment
      pinApartments(apartments);
    };

    if (window.google && window.google.maps) {
      loadMap();
    } else {
      // Load Maps script dynamically
      if (document.getElementById("google-maps-script")) return;
      const script = document.createElement("script");
      script.id  = "google-maps-script";
      script.src = `https://maps.googleapis.com/maps/api/js?key=${MAPS_API_KEY}&libraries=places`;
      script.async = true;
      script.onload = loadMap;
      script.onerror = () => setError("Google Maps failed to load. Check your API key.");
      document.head.appendChild(script);
    }
  }, [user.city]);

  // ── Update pins when apartments data arrives ──────────────────────────────
  useEffect(() => {
    if (googleMap.current && apartments.length > 0) {
      pinApartments(apartments);
    }
  }, [apartments]);

  // ── Place marker pins on the map ──────────────────────────────────────────
  const pinApartments = (apts) => {
    if (!googleMap.current || !window.google) return;

    // Clear old markers
    markers.current.forEach((m) => m.setMap(null));
    markers.current = [];

    apts.forEach((apt, i) => {
      const marker = new window.google.maps.Marker({
        position: { lat: parseFloat(apt.lat), lng: parseFloat(apt.lon) },
        map: googleMap.current,
        title: apt.name,
        label: {
          text: String(i + 1),
          color: "#ffffff",
          fontSize: "12px",
          fontWeight: "bold",
        },
        icon: {
          path: window.google.maps.SymbolPath.CIRCLE,
          scale: 16,
          fillColor: "#f97316",
          fillOpacity: 0.95,
          strokeColor: "#ffffff",
          strokeWeight: 2,
        },
        animation: window.google.maps.Animation.DROP,
      });

      // Info window on click
      const infoWindow = new window.google.maps.InfoWindow({
        content: `
          <div style="
            background:#1a1a2e;
            color:#fff;
            padding:12px 16px;
            border-radius:8px;
            font-family:sans-serif;
            min-width:180px;
          ">
            <div style="font-weight:700;font-size:0.95rem;margin-bottom:4px;">
              ${apt.name}
            </div>
            <div style="color:#f97316;font-weight:700;margin-bottom:2px;">
              ₹${Number(apt.rent).toLocaleString("en-IN")}/mo
            </div>
            <div style="font-size:0.78rem;color:#aaa;">
              ${apt.bhk} BHK · ${apt.furnished ? "Furnished" : "Unfurnished"}
            </div>
            <div style="font-size:0.78rem;color:#aaa;margin-top:2px;">
              Amenity score: ${Math.round(apt.amenity_score * 100)}%
            </div>
          </div>
        `,
      });

      marker.addListener("click", () => {
        infoWindow.open(googleMap.current, marker);
        setSelected(apt);
      });

      markers.current.push(marker);
    });
  };

  const city = user.city || "nashik";

  return (
    <div className="map-page">

      {/* ── Sidebar: apartment list ─────────────────────────────────── */}
      <aside className="map-sidebar">
        <div className="sidebar-header">
          <h2 className="sidebar-title">Apartments</h2>
          {user.city && (
            <span className="sidebar-city">
              {user.city.charAt(0).toUpperCase() + user.city.slice(1)}
              {user.budget && ` · ₹${Number(user.budget).toLocaleString("en-IN")}`}
            </span>
          )}
        </div>

        {loading && (
          <div className="sidebar-loading">
            <div className="spinner" />
            <span>Loading apartments…</span>
          </div>
        )}

        {error && (
          <div className="sidebar-error">{error}</div>
        )}

        {!loading && !error && apartments.length === 0 && (
          <div className="sidebar-empty">
            No apartments found. Try adjusting your budget or city.
          </div>
        )}

        <div className="apartment-list">
          {apartments.map((apt, i) => (
            <div
              key={apt.id}
              className={`apt-card ${selected?.id === apt.id ? "apt-card-selected" : ""}`}
              onClick={() => {
                setSelected(apt);
                // Pan map to this apartment
                if (googleMap.current) {
                  googleMap.current.panTo({
                    lat: parseFloat(apt.lat),
                    lng: parseFloat(apt.lon),
                  });
                  googleMap.current.setZoom(15);
                }
              }}
            >
              <div className="apt-rank">#{i + 1}</div>
              <div className="apt-info">
                <div className="apt-name">{apt.name}</div>
                <div className="apt-rent">
                  ₹{Number(apt.rent).toLocaleString("en-IN")}/mo
                </div>
                <div className="apt-meta">
                  {apt.bhk} BHK ·{" "}
                  {apt.furnished ? "Furnished" : "Unfurnished"} ·{" "}
                  {Math.round(apt.amenity_score * 100)}% amenity
                </div>
              </div>
            </div>
          ))}
        </div>
      </aside>

      {/* ── Google Map ─────────────────────────────────────────────── */}
      <div className="map-container">
        {!MAPS_API_KEY && (
          <div className="map-key-warning">
            Add <code>VITE_GOOGLE_MAPS_KEY=your_key</code> to your <code>.env</code> file
          </div>
        )}
        <div ref={mapRef} className="google-map" />
      </div>

    </div>
  );
}

// ── Dark map style ────────────────────────────────────────────────────────────
const DARK_MAP_STYLES = [
  { elementType: "geometry",           stylers: [{ color: "#1a1a2e" }] },
  { elementType: "labels.text.fill",  stylers: [{ color: "#8b949e" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#1a1a2e" }] },
  { featureType: "road", elementType: "geometry",
    stylers: [{ color: "#2d2d4a" }] },
  { featureType: "road.highway", elementType: "geometry",
    stylers: [{ color: "#3d3d6a" }] },
  { featureType: "water", elementType: "geometry",
    stylers: [{ color: "#0f172a" }] },
  { featureType: "poi", stylers: [{ visibility: "off" }] },
  { featureType: "transit", stylers: [{ visibility: "off" }] },
];

export default Map;
