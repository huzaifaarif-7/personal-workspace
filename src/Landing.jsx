import React, { useEffect, useRef } from "react";
import { Lock, Palette, Zap, ShieldCheck } from "lucide-react";
import "./Landing.css";

export default function Landing() {
  const streamRef = useRef(null);

  useEffect(() => {
    // Notification card stagger animation
    const cards = document.querySelectorAll(".notif-card");
    cards.forEach(function (card) {
      const delay = parseInt(card.dataset.delay) || 0;
      setTimeout(function () {
        card.classList.add("visible");
      }, 600 + delay);
    });

    // Scroll reveal
    const reveals = document.querySelectorAll(".reveal");
    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add("visible");
            observer.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    reveals.forEach(function (el) {
      observer.observe(el);
    });

    // Notification loop — re-animates cards every 6s
    function loopNotifs() {
      cards.forEach(function (card, i) {
        card.classList.remove("visible");
        setTimeout(function () {
          card.classList.add("visible");
        }, 300 + i * 180);
      });
    }
    const interval = setInterval(loopNotifs, 6000);
    return () => {
      clearInterval(interval);
      observer.disconnect();
    };
  }, []);

  return (
    <div id="landing-page">
      {/* NAV */}
      <nav>
        <div className="nav-right">
          <a href="/login" className="btn-ghost">
            Log in
          </a>
          <a href="/signup" className="btn-primary">
            Get started
          </a>
        </div>
        <a href="/" className="logo">
          <div className="logo-mark">
            <svg viewBox="0 0 14 14">
              <path d="M7 1L13 4V10L7 13L1 10V4L7 1Z" />
            </svg>
          </div>
          <span className="logo-text">Personal Workspace</span>
        </a>
      </nav>

      {/* HERO */}
      <section className="hero">
        <div className="hero-left">
          <h1>
            One tab for<br />
            <em>everything</em><br />
            that matters
          </h1>
          <p className="hero-sub">
            GitHub notifications, emails, Slack messages, and calendar events —
            all in one place instead of five open tabs.
          </p>
          <div className="hero-actions">
            <a href="/signup" className="btn-hero">
              Get started free
              <svg viewBox="0 0 16 16">
                <line x1="3" y1="8" x2="13" y2="8" />
                <polyline points="9,4 13,8 9,12" />
              </svg>
            </a>
          </div>
          <p className="hero-note" style={{ marginTop: "16px" }}>
            No credit card required
          </p>
        </div>

        <div className="hero-right">
          <div className="notif-stream" id="stream" ref={streamRef}>
            <div className="notif-card" data-delay="0">
              <div className="notif-icon icon-gh">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="var(--text-secondary)"
                >
                  <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844a9.59 9.59 0 012.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
                </svg>
              </div>
              <div className="notif-body">
                <div className="notif-source">GitHub</div>
                <div className="notif-title">
                  PR review requested: add OAuth2 flow
                </div>
                <div className="notif-meta">personal-workspace · 2 min ago</div>
              </div>
              <div className="notif-dot"></div>
            </div>

            <div className="notif-card" data-delay="180">
              <div className="notif-icon icon-gm">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"
                    stroke="#EA4335"
                    strokeWidth="1.5"
                  />
                  <polyline
                    points="22,6 12,13 2,6"
                    stroke="#EA4335"
                    strokeWidth="1.5"
                    fill="none"
                  />
                </svg>
              </div>
              <div className="notif-body">
                <div className="notif-source">Gmail</div>
                <div className="notif-title">
                  Vercel: Your deployment succeeded
                </div>
                <div className="notif-meta">
                  noreply@vercel.com · 15 min ago
                </div>
              </div>
              <div className="notif-dot"></div>
            </div>

            <div className="notif-card" data-delay="360">
              <div className="notif-icon icon-sl">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M14.5 10c-.83 0-1.5-.67-1.5-1.5v-5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5v5c0 .83-.67 1.5-1.5 1.5z"
                    fill="#E01E5A"
                  />
                  <path
                    d="M20.5 10H19V8.5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"
                    fill="#E01E5A"
                  />
                  <path
                    d="M9.5 14c.83 0 1.5.67 1.5 1.5v5c0 .83-.67 1.5-1.5 1.5S8 21.33 8 20.5v-5c0-.83.67-1.5 1.5-1.5z"
                    fill="#2EB67D"
                  />
                  <path
                    d="M3.5 14H5v1.5c0 .83-.67 1.5-1.5 1.5S2 16.33 2 15.5 2.67 14 3.5 14z"
                    fill="#2EB67D"
                  />
                  <path
                    d="M14 14.5c0-.83.67-1.5 1.5-1.5h5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5h-5c-.83 0-1.5-.67-1.5-1.5z"
                    fill="#ECB22E"
                  />
                  <path
                    d="M14 19.5V18h1.5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5-1.5-.67-1.5-1.5z"
                    fill="#ECB22E"
                  />
                  <path
                    d="M10 9.5c0 .83-.67 1.5-1.5 1.5h-5C2.67 11 2 10.33 2 9.5S2.67 8 3.5 8h5c.83 0 1.5.67 1.5 1.5z"
                    fill="#36C5F0"
                  />
                  <path
                    d="M10 4.5V6H8.5C7.67 6 7 5.33 7 4.5S7.67 3 8.5 3 10 3.67 10 4.5z"
                    fill="#36C5F0"
                  />
                </svg>
              </div>
              <div className="notif-body">
                <div className="notif-source">Slack</div>
                <div className="notif-title">
                  Mohsin: pushed the Rang Adda fix
                </div>
                <div className="notif-meta">#dev-channel · 1 hr ago</div>
              </div>
              <div className="notif-dot"></div>
            </div>

            <div className="notif-card" data-delay="540">
              <div className="notif-icon icon-cal">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#4285F4"
                  strokeWidth="1.6"
                  strokeLinecap="round"
                >
                  <rect x="3" y="4" width="18" height="18" rx="3" />
                  <line x1="3" y1="9" x2="21" y2="9" />
                  <line x1="8" y1="2" x2="8" y2="6" />
                  <line x1="16" y1="2" x2="16" y2="6" />
                </svg>
              </div>
              <div className="notif-body">
                <div className="notif-source">Calendar</div>
                <div className="notif-title">FYP sync meeting in 30 minutes</div>
                <div className="notif-meta">Today · 3:00 PM PKT</div>
              </div>
              <div className="notif-dot"></div>
            </div>
          </div>
        </div>
      </section>

      {/* INTEGRATIONS BAR */}
      <div className="divider"></div>
      <div className="integrations reveal">
        <div className="integrations-label">Works with tools you already use</div>
        <div className="integrations-logos">
          <div className="int-logo">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844a9.59 9.59 0 012.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
            GitHub
          </div>
          <div className="int-logo" style={{ color: "#EA4335" }}>
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M24 5.457v13.909c0 .904-.732 1.636-1.636 1.636h-3.819V11.73L12 16.64l-6.545-4.91v9.273H1.636A1.636 1.636 0 010 19.366V5.457c0-2.023 2.309-3.178 3.927-1.964L5.455 4.64 12 9.548l6.545-4.91 1.528-1.145C21.69 2.28 24 3.434 24 5.457z" />
            </svg>
            Gmail
          </div>
          <div className="int-logo">
            <svg viewBox="0 0 24 24" fill="none">
              <path
                d="M14.5 10c-.83 0-1.5-.67-1.5-1.5v-5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5v5c0 .83-.67 1.5-1.5 1.5z"
                fill="#E01E5A"
              />
              <path
                d="M20.5 10H19V8.5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"
                fill="#E01E5A"
              />
              <path
                d="M9.5 14c.83 0 1.5.67 1.5 1.5v5c0 .83-.67 1.5-1.5 1.5S8 21.33 8 20.5v-5c0-.83.67-1.5 1.5-1.5z"
                fill="#2EB67D"
              />
              <path
                d="M3.5 14H5v1.5c0 .83-.67 1.5-1.5 1.5S2 16.33 2 15.5 2.67 14 3.5 14z"
                fill="#2EB67D"
              />
              <path
                d="M14 14.5c0-.83.67-1.5 1.5-1.5h5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5h-5c-.83 0-1.5-.67-1.5-1.5z"
                fill="#ECB22E"
              />
              <path
                d="M14 19.5V18h1.5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5-1.5-.67-1.5-1.5z"
                fill="#ECB22E"
              />
              <path
                d="M10 9.5c0 .83-.67 1.5-1.5 1.5h-5C2.67 11 2 10.33 2 9.5S2.67 8 3.5 8h5c.83 0 1.5.67 1.5 1.5z"
                fill="#36C5F0"
              />
              <path
                d="M10 4.5V6H8.5C7.67 6 7 5.33 7 4.5S7.67 3 8.5 3 10 3.67 10 4.5z"
                fill="#36C5F0"
              />
            </svg>
            Slack
          </div>
          <div className="int-logo" style={{ color: "#4285F4" }}>
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
            >
              <rect x="3" y="4" width="18" height="18" rx="3" />
              <line x1="3" y1="9" x2="21" y2="9" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="16" y1="2" x2="16" y2="6" />
            </svg>
            Google Calendar
          </div>
        </div>
      </div>
      <div className="divider"></div>

      {/* HOW IT WORKS */}
      <section className="how">
        <div className="reveal">
          <div className="section-label">How it works</div>
          <div className="section-title">Set up in three steps</div>
          <p className="section-sub">
            Connect your accounts once. Everything updates automatically so you
            never miss what matters.
          </p>
        </div>
        <div className="steps">
          <div className="step reveal" style={{ transitionDelay: "0s" }}>
            <div className="step-num">01</div>
            <div className="step-icon">
              <svg viewBox="0 0 24 24">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
            </div>
            <div className="step-title">Create your account</div>
            <p className="step-desc">
              Sign up in seconds. No payment info, no setup calls — just a name
              and a password.
            </p>
          </div>
          <div className="step reveal" style={{ transitionDelay: "0.1s" }}>
            <div className="step-num">02</div>
            <div className="step-icon">
              <svg viewBox="0 0 24 24">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
              </svg>
            </div>
            <div className="step-title">Connect your services</div>
            <p className="step-desc">
              Authorize GitHub, Gmail, Slack, and Calendar through their official
              OAuth flows. Personal Workspace never stores your data — only the access
              token.
            </p>
          </div>
          <div className="step reveal" style={{ transitionDelay: "0.2s" }}>
            <div className="step-num">03</div>
            <div className="step-icon">
              <svg viewBox="0 0 24 24">
                <rect x="3" y="3" width="7" height="7" />
                <rect x="14" y="3" width="7" height="7" />
                <rect x="14" y="14" width="7" height="7" />
                <rect x="3" y="14" width="7" height="7" />
              </svg>
            </div>
            <div className="step-title">Open one tab</div>
            <p className="step-desc">
              Everything you need is on a single dashboard. Your preferences,
              connections, and theme stay saved across every session.
            </p>
          </div>
        </div>
      </section>

      {/* FEATURE STRIP */}
      <div className="feature-strip">
        <div className="feat reveal">
          <div className="feat-icon"><Lock size={24} color="var(--primary)" /></div>
          <div className="feat-title">OAuth only, no passwords stored</div>
          <p className="feat-desc">
            Every integration uses the official OAuth2 flow. We never see your
            GitHub or Google password — only a scoped access token, encrypted at
            rest.
          </p>
        </div>
        <div className="feat reveal" style={{ transitionDelay: "0.1s" }}>
          <div className="feat-icon"><Palette size={24} color="var(--primary)" /></div>
          <div className="feat-title">Your theme, your font</div>
          <p className="feat-desc">
            Pick a color theme and font that suits you. Your choice is saved to
            your account so it follows you across every device you log into.
          </p>
        </div>
        <div className="feat reveal" style={{ transitionDelay: "0.2s" }}>
          <div className="feat-icon"><Zap size={24} color="var(--primary)" /></div>
          <div className="feat-title">One request, everything loaded</div>
          <p className="feat-desc">
            On login, all your connection statuses and preferences load in a
            single API call. The dashboard is ready before you finish blinking.
          </p>
        </div>
        <div className="feat reveal" style={{ transitionDelay: "0.3s" }}>
          <div className="feat-icon"><ShieldCheck size={24} color="var(--primary)" /></div>
          <div className="feat-title">Read-only by design</div>
          <p className="feat-desc">
            Personal Workspace only requests read scopes. It can't push commits, send
            emails, or post messages — it's a viewer, not an actor.
          </p>
        </div>
      </div>

      {/* CTA */}
      <div className="cta-strip reveal">
        <div className="cta-box">
          <h2>
            Stop switching tabs.<br />
            Start actually working.
          </h2>
          <p>Free to use. Connect up to four services. No card needed.</p>
          <a href="/signup" className="btn-cta">
            Create your workspace
            <svg viewBox="0 0 16 16">
              <line x1="3" y1="8" x2="13" y2="8" />
              <polyline points="9,4 13,8 9,12" />
            </svg>
          </a>
        </div>
      </div>

      {/* FOOTER */}
      <footer>
        <div className="footer-left">
          <div
            className="logo-mark"
            style={{ width: "22px", height: "22px", borderRadius: "5px" }}
          >
            <svg
              viewBox="0 0 14 14"
              style={{ width: "11px", height: "11px", fill: "#fff" }}
            >
              <path d="M7 1L13 4V10L7 13L1 10V4L7 1Z" />
            </svg>
          </div>
          <span className="footer-brand">Personal Workspace</span>
          <span className="footer-copy">© 2025</span>
        </div>
        <div className="footer-links">
          <a href="/privacy.html">Privacy policy</a>
          <a href="/terms.html">Terms & conditions</a>
          <a href="/login">Log in</a>
          <a href="/signup">Sign up</a>
        </div>
      </footer>
    </div>
  );
}
