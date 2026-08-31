/*
 * MAHI SOLAR — 3D SCROLL INTRO & SCENE COORDINATOR
 * Ties standard document scrolling to GSAP ScrollTrigger timelines.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Register GreenSock ScrollTrigger
    gsap.registerPlugin(ScrollTrigger);

    // 2. Select DOM elements
    const header = document.getElementById('main-header');
    const content1 = document.getElementById('content1');
    const content2 = document.getElementById('content2');
    const content3 = document.getElementById('content3');
    const content4 = document.getElementById('content4');

    // 3. Initialize dynamic WebGL mock (to be bound to the Three.js class)
    console.log("Mahi Solar: 3D Scene Controller initialized successfully.");

    // 4. Create the Master GSAP Timeline mapped to ScrollTrigger
    const introTimeline = gsap.timeline({
        scrollTrigger: {
            trigger: "body",
            start: "top top",
            end: "bottom bottom",
            scrub: 1.2, // Smooth scrub delay
            onUpdate: (self) => {
                const progress = self.progress;
                
                // Track stages based on overall progress (0.0 to 1.0)
                
                // Keep header permanently visible and fixed at top across all stages
                if (header) {
                    header.classList.add('visible');
                    header.classList.add('subpage-header');
                }

                // Stage 1 active (0% - 20%)
                if (progress < 0.20) {
                    toggleActiveContent(content1);
                }
                // Stage 2 active (20% - 45%)
                else if (progress >= 0.20 && progress < 0.45) {
                    toggleActiveContent(content2);
                }
                // Stage 3 active (45% - 70%)
                else if (progress >= 0.45 && progress < 0.70) {
                    toggleActiveContent(content3);
                }
                // Stage 4 active (70% - 88%)
                else if (progress >= 0.70 && progress < 0.88) {
                    toggleActiveContent(content4);
                }
                // Stage 5 active (88% - 100%) - Hero reveal
                else if (progress >= 0.88) {
                    clearAllActive();
                }
            }
        }
    });

    // Helper functions to manage screen content fades
    function toggleActiveContent(activeEl) {
        const contents = [content1, content2, content3, content4];
        contents.forEach(el => {
            if (el === activeEl) {
                el.classList.add('active');
            } else {
                el.classList.remove('active');
            }
        });
    }

    function clearAllActive() {
        const contents = [content1, content2, content3, content4];
        contents.forEach(el => el.classList.remove('active'));
    }

    // 5. Setup dynamic text entry micro-animations
    gsap.from(".hero-title", {
        scrollTrigger: {
            trigger: "#stage5",
            start: "top 60%",
            toggleActions: "play none none reverse"
        },
        y: 40,
        opacity: 0,
        filter: "blur(10px)",
        duration: 1.2,
        ease: "power4.out"
    });

    gsap.from(".hero-desc, .hero-cta", {
        scrollTrigger: {
            trigger: "#stage5",
            start: "top 50%",
            toggleActions: "play none none reverse"
        },
        y: 30,
        opacity: 0,
        duration: 1.5,
        stagger: 0.2,
        ease: "power3.out"
    });
});

