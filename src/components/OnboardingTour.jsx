import React, { useState, useEffect, useRef, useCallback } from "react";

/* ============================================================
   OnboardingTour — spotlight-based guided walkthrough
   Uses SVG mask (evenodd fill) to cut a "hole" in the overlay.
   ============================================================ */

const PADDING = 12;        // spotlight padding around element
const RADIUS  = 12;        // spotlight border-radius
const TIP_W   = 300;       // tooltip width px
const TIP_MIN_MARGIN = 16; // minimum distance from viewport edge

/* Wait helper */
const wait = (ms) => new Promise((r) => setTimeout(r, ms));

/* Clamp a value between min and max */
const clamp = (v, min, max) => Math.max(min, Math.min(max, v));

export default function OnboardingTour({ steps, onComplete }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [targetRect, setTargetRect] = useState(null);
  const [visible, setVisible]         = useState(false); // controls tooltip fade
  const [svgRect, setSvgRect]         = useState(null);  // spotlight (may differ from targetRect during transition)

  const stepCount = steps.length;
  const step      = steps[currentStep];
  const isLast    = currentStep === stepCount - 1;

  /* ─── measure element and move spotlight ─── */
  const measureAndShow = useCallback(async (stepObj) => {
    // 1. Run beforeStep if present
    if (stepObj.beforeStep) {
      await stepObj.beforeStep();
    }

    // 2. Find element
    const el = document.querySelector(stepObj.selector);
    if (!el) {
      // Guard: selector not found — skip to next step
      return null;
    }

    // 3. Scroll into view and wait for settle
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    await wait(400);

    // 4. Measure
    const rect = el.getBoundingClientRect();
    return rect;
  }, []);

  /* ─── initial mount: show step 0 ─── */
  useEffect(() => {
    let alive = true;
    (async () => {
      const rect = await measureAndShow(steps[0]);
      if (!alive) return;
      if (!rect) {
        // skip unfound first step
        advanceToStep(1);
        return;
      }
      setTargetRect(rect);
      setSvgRect(rect);
      // Small delay so SVG renders before fade-in
      await wait(50);
      if (alive) setVisible(true);
    })();
    return () => { alive = false; };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /* ─── resize: re-measure current element ─── */
  useEffect(() => {
    const handler = () => {
      if (!step) return;
      const el = document.querySelector(step.selector);
      if (!el) return;
      const rect = el.getBoundingClientRect();
      setTargetRect(rect);
      setSvgRect(rect);
    };
    window.addEventListener("resize", handler);
    return () => window.removeEventListener("resize", handler);
  }, [step]);

  /* ─── keyboard ─── */
  useEffect(() => {
    const handler = (e) => {
      if (e.key === "Escape")      handleSkip();
      if (e.key === "ArrowRight")  handleNext();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentStep]);

  /* ─── advance to a given step index ─── */
  const advanceToStep = useCallback(async (nextIndex) => {
    if (nextIndex >= stepCount) {
      // Tour complete
      setVisible(false);
      await wait(250);
      onComplete();
      return;
    }

    // 1. Fade tooltip out
    setVisible(false);
    await wait(200);

    // 2. Set new current step (re-renders SVG to new element)
    setCurrentStep(nextIndex);
    const nextStep = steps[nextIndex];

    // 3. Measure new element
    const rect = await measureAndShow(nextStep);

    if (!rect) {
      // Skip unfound step
      await advanceToStep(nextIndex + 1);
      return;
    }

    // 4. Snap SVG to new rect, then fade tooltip back in
    setTargetRect(rect);
    setSvgRect(rect);
    await wait(80);
    setVisible(true);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentStep, stepCount, steps, measureAndShow, onComplete]);

  const handleNext = useCallback(() => {
    advanceToStep(currentStep + 1);
  }, [currentStep, advanceToStep]);

  const handleSkip = useCallback(() => {
    setVisible(false);
    setTimeout(() => onComplete(), 220);
  }, [onComplete]);

  if (!svgRect) return null;

  /* ─── Spotlight geometry ─── */
  const sl = svgRect.left   - PADDING;
  const st = svgRect.top    - PADDING;
  const sw = svgRect.width  + PADDING * 2;
  const sh = svgRect.height + PADDING * 2;

  /* ─── Tooltip positioning ─── */
  const vw = window.innerWidth;
  const vh = window.innerHeight;

  // Default: position below spotlight
  let tipTop;
  let arrowDir = "up"; // arrow points up (tooltip is below element)
  const TOOLTIP_HEIGHT_EST = 220;
  const ARROW_SIZE = 10;

  if (svgRect.bottom + PADDING + ARROW_SIZE + TOOLTIP_HEIGHT_EST > vh) {
    // Not enough room below — position above
    tipTop   = svgRect.top - PADDING - ARROW_SIZE - TOOLTIP_HEIGHT_EST;
    arrowDir = "down";
  } else {
    tipTop   = svgRect.bottom + PADDING + ARROW_SIZE;
    arrowDir = "up";
  }

  // Horizontal: center on the spotlight, then clamp to viewport
  let tipLeft = svgRect.left + svgRect.width / 2 - TIP_W / 2;
  tipLeft     = clamp(tipLeft, TIP_MIN_MARGIN, vw - TIP_W - TIP_MIN_MARGIN);

  // Vertical clamp
  tipTop = clamp(tipTop, TIP_MIN_MARGIN, vh - TOOLTIP_HEIGHT_EST - TIP_MIN_MARGIN);

  // Arrow horizontal position (relative to tooltip left)
  const arrowTargetX = svgRect.left + svgRect.width / 2;
  const arrowLeft    = clamp(arrowTargetX - tipLeft - 8, 16, TIP_W - 32);

  return (
    <>
      {/* ── SVG Spotlight Overlay ── */}
      <svg
        style={{
          position: "fixed",
          inset: 0,
          zIndex: 9998,
          pointerEvents: "none",
          transition: "all 0.3s cubic-bezier(.4,0,.2,1)",
        }}
        width="100%"
        height="100%"
      >
        <defs>
          <mask id="tour-spotlight-mask">
            {/* White = show dark overlay */}
            <rect width="100%" height="100%" fill="white" />
            {/* Black = cut-out / spotlight hole */}
            <rect
              x={sl}
              y={st}
              width={sw}
              height={sh}
              rx={RADIUS}
              fill="black"
              style={{ transition: "all 0.3s cubic-bezier(.4,0,.2,1)" }}
            />
          </mask>
        </defs>
        <rect
          width="100%"
          height="100%"
          fill="rgba(0,0,0,0.72)"
          mask="url(#tour-spotlight-mask)"
          style={{ transition: "opacity 0.2s ease" }}
        />
        {/* Spotlight ring — subtle glowing border */}
        <rect
          x={sl - 1}
          y={st - 1}
          width={sw + 2}
          height={sh + 2}
          rx={RADIUS + 1}
          fill="none"
          stroke="rgba(255,255,255,0.15)"
          strokeWidth="1"
          style={{ transition: "all 0.3s cubic-bezier(.4,0,.2,1)" }}
        />
      </svg>

      {/* ── Tooltip Card ── */}
      <div
        style={{
          position: "fixed",
          top: tipTop,
          left: tipLeft,
          zIndex: 9999,
          width: TIP_W,
          background: "var(--card)",
          border: "0.5px solid var(--border-strong, var(--border))",
          borderRadius: 14,
          padding: "20px 20px 16px",
          boxShadow: "0 8px 32px rgba(0,0,0,0.45)",
          pointerEvents: "auto",
          opacity: visible ? 1 : 0,
          transform: visible ? "translateY(0)" : (arrowDir === "up" ? "translateY(-8px)" : "translateY(8px)"),
          transition: "opacity 0.22s ease, transform 0.22s ease",
          fontFamily: "var(--font-sans)",
        }}
      >
        {/* Arrow */}
        {arrowDir === "up" && (
          <div
            style={{
              position: "absolute",
              top: -ARROW_SIZE,
              left: arrowLeft,
              width: 0,
              height: 0,
              borderLeft: `${ARROW_SIZE}px solid transparent`,
              borderRight: `${ARROW_SIZE}px solid transparent`,
              borderBottom: `${ARROW_SIZE}px solid var(--border-strong, var(--border))`,
            }}
          />
        )}
        {arrowDir === "down" && (
          <div
            style={{
              position: "absolute",
              bottom: -ARROW_SIZE,
              left: arrowLeft,
              width: 0,
              height: 0,
              borderLeft: `${ARROW_SIZE}px solid transparent`,
              borderRight: `${ARROW_SIZE}px solid transparent`,
              borderTop: `${ARROW_SIZE}px solid var(--border-strong, var(--border))`,
            }}
          />
        )}

        {/* Step counter */}
        <div
          style={{
            fontSize: 11,
            color: "var(--text-muted)",
            float: "right",
            marginTop: 2,
          }}
        >
          {currentStep + 1} of {stepCount}
        </div>

        {/* Icon */}
        <div style={{ fontSize: 28, marginBottom: 10, lineHeight: 1 }}>
          {step.icon}
        </div>

        {/* Title */}
        <div
          style={{
            fontSize: 15,
            fontWeight: 500,
            color: "var(--text)",
            marginBottom: 6,
            lineHeight: 1.3,
          }}
        >
          {step.title}
        </div>

        {/* Description */}
        <div
          style={{
            fontSize: 13,
            color: "var(--text-secondary)",
            lineHeight: 1.6,
          }}
        >
          {step.description}
        </div>

        {/* Progress dots */}
        <div
          style={{
            display: "flex",
            gap: 6,
            marginTop: 14,
            marginBottom: 2,
          }}
        >
          {Array.from({ length: stepCount }, (_, i) => (
            <div
              key={i}
              style={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                background:
                  i === currentStep
                    ? "var(--primary)"
                    : "var(--border)",
                transition: "background 0.2s",
                flexShrink: 0,
              }}
            />
          ))}
        </div>

        {/* Button row */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginTop: 16,
          }}
        >
          <button
            onClick={handleSkip}
            style={{
              fontSize: 12,
              color: "var(--text-muted)",
              background: "none",
              border: "none",
              cursor: "pointer",
              padding: "4px 0",
              fontFamily: "var(--font-sans)",
            }}
          >
            Skip tour
          </button>
          <button
            onClick={handleNext}
            style={{
              fontSize: 13,
              fontWeight: 500,
              padding: "8px 18px",
              borderRadius: "var(--radius)",
              background: "var(--primary)",
              color: "#fff",
              border: "none",
              cursor: "pointer",
              fontFamily: "var(--font-sans)",
              transition: "opacity 0.15s",
            }}
            onMouseEnter={(e) => { e.currentTarget.style.opacity = "0.85"; }}
            onMouseLeave={(e) => { e.currentTarget.style.opacity = "1"; }}
          >
            {isLast ? "Get started ✓" : "Next →"}
          </button>
        </div>
      </div>
    </>
  );
}
