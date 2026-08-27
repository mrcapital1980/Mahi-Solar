/* ===================================================
   MAHI SOLAR – Cinematic GSAP Intro Logic
   =================================================== */

document.addEventListener("DOMContentLoaded", () => {
  const introCont = document.getElementById("intro-container");
  
  // 1. Session Storage Logic to play only once
  if (sessionStorage.getItem("mahiIntroPlayed") || !introCont) {
    if (introCont) introCont.style.display = "none";
    
    // Ensure the rest of the site is perfectly responsive
    document.documentElement.style.overflowX = 'hidden';
    document.body.style.overflowX = 'hidden';
    return; // Fast exit
  }

  // Mark as played
  sessionStorage.setItem("mahiIntroPlayed", "true");

  // Hide scrollbar globally for a cleaner experience
  document.documentElement.style.overflowX = 'hidden';
  document.body.style.overflowX = 'hidden';

  // Force scroll user to top on reload
  window.scrollTo(0, 0);

  // 2. Setup GSAP ScrollTrigger
  gsap.registerPlugin(ScrollTrigger);

  // The main scrub timeline
  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: "#intro-container",
      start: "top top",
      end: "+=5000", // Smooth scrolling length
      scrub: 1, // Smooth scrub easing
      pin: true, // Pin the container while going through scenes
      anticipatePin: 1
    }
  });

  // Scene 1: Welcome
  tl.fromTo("#scene1", { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 2 })
    .to("#scene1", { opacity: 0, scale: 1.1, duration: 1.5 });

  // Scene 2: Energy is Future
  tl.fromTo("#scene2", { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 1.5 })
    .fromTo(".glow-orb", { scale: 0.5, opacity: 0 }, { scale: 1.2, opacity: 0.6, duration: 2 }, "<")
    .to("#scene2", { opacity: 0, y: -50, duration: 1.5 });

  // Scene 3: Solar Concept Parallax
  tl.fromTo("#scene3", { opacity: 0 }, { opacity: 1, duration: 1 })
    .fromTo(".sunrays", { rotation: 0, scale: 0.5, opacity: 0 }, { rotation: 180, scale: 1, opacity: 1, duration: 4 }, "<")
    .fromTo(".earth", { scale: 0, y: 50 }, { scale: 1, y: 0, duration: 2 }, "<")
    .to(".earth", { rotation: 90, duration: 2 }, "<")
    .to("#scene3", { opacity: 0, scale: 1.5, duration: 1.5 });

  // Scene 4: Glassmorphism Panels floating
  tl.fromTo("#scene4", { opacity: 0 }, { opacity: 1, duration: 1 })
    .fromTo(".intro-panel.p1", { y: window.innerHeight }, { y: -200, duration: 4 }, "<")
    .fromTo(".intro-panel.p2", { y: window.innerHeight + 100 }, { y: -300, duration: 4.5 }, "<")
    .fromTo(".intro-panel.p3", { y: window.innerHeight - 50 }, { y: -100, duration: 3.5 }, "<")
    .to("#scene4", { opacity: 0, duration: 1 });

  // Scene 5: Power Your Home
  tl.fromTo("#scene5", { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: 1.5 })
    .to("#scene5 h1", { scale: 8, opacity: 0, duration: 2, delay: 0.5 }); // Final pop and fade
    
  // Unpinning seamlessly aligns and brings in `.hero`
  // The CSS z-index inherently hides the navbar natively during the intro
});
