import "./Help.css";
import EarthVideo from "../../earth.mp4";

function Help() {
  const steps = [
    {
      num: "01",
      title: "Enter Your Details",
      desc: "Go to Home. Enter your name, select your city, and set your monthly budget using the slider.",
    },
    {
      num: "02",
      title: "Click Find Apartments",
      desc: "Our ML model filters and scores apartments based on proximity, amenities, and value for money.",
    },
    {
      num: "03",
      title: "View on Map",
      desc: "Go to the Map page to see all matching apartments pinned on a live Google Map. Click any pin for details.",
    },
    {
      num: "04",
      title: "Pick Your Home",
      desc: "Browse the list, compare rent and amenities, and choose the apartment that suits you best.",
    },
  ];

  return (
    <div className="help-wrapper">
      
      {/* Background Video */}
      <div className="video-bg">
        <video autoPlay loop muted playsInline>
          <source src={EarthVideo} type="video/mp4" />
        </video>
        <div className="video-fade"></div>
      </div>

      <div className="scroll-content">
        <div className="help-hero-content">
          <h1 className="help-title">How to Use PRLSS</h1>
          <p className="help-subtitle">Follow these steps to find your perfect apartment.</p>
        </div>

        <div className="help-steps-container">
          {steps.map((step) => (
            <div className="help-step" key={step.num}>
              <div className="step-num">{step.num}</div>
              <div className="step-body">
                <h3 className="step-title">{step.title}</h3>
                <p className="step-desc">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Help;
