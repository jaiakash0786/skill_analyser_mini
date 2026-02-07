import { useEffect, useState } from "react";
import "./SplashScreen.css";

import logo from "../assets/logo.png";
import brand from "../assets/brand.png";

function SplashScreen({ onFinish }) {

  const [phase, setPhase] = useState("logo");

  useEffect(() => {

    // preload images (VERY senior trick)
    new Image().src = logo;
    new Image().src = brand;

    const timer1 = setTimeout(() => {
      setPhase("brand");
    }, 2000);

    const timer2 = setTimeout(() => {
      onFinish();
    }, 3000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };

  }, [onFinish]);

  return (
    <div className="splash-container">

      {phase === "logo" && (
        <img
          src={logo}
          className="logo-spin"
          alt="logo"
        />
      )}

      {phase === "brand" && (
        <img
          src={brand}
          className="brand-fade"
          alt="brand"
        />
      )}

    </div>
  );
}

export default SplashScreen;
