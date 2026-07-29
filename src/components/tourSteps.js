/* ============================================================
   tourSteps — factory that returns the 6 onboarding tour steps.

   Receives { setView, setAssistOpen } so that beforeStep
   callbacks can programmatically navigate the app before the
   spotlight element is measured.
   ============================================================ */

/**
 * @param {{ setView: Function, setAssistOpen: Function }} ctx
 * @returns {Array<import('./OnboardingTour').TourStep>}
 */
export function createTourSteps({ setView, setAssistOpen }) {
  return [
    /* ── Step 1 — Welcome ─────────────────────────────────── */
    {
      selector: ".brand",
      icon: "👋",
      title: "Welcome to Workspace",
      description:
        "This is your personal command center. Let us show you around — it takes less than a minute.",
      position: "right",
    },

    /* ── Step 2 — Settings nav ────────────────────────────── */
    {
      selector: '[data-tour-nav="settings"]',
      icon: "🔗",
      title: "Connect your services",
      description:
        "Link GitHub, Gmail, Slack, and Calendar here. Once connected, your updates appear on the dashboard automatically.",
      position: "right",
      beforeStep: async () => {
        // Make sure we are on the dashboard so the sidebar is fully visible
        setView("dashboard");
        // Wait a tick for the view to settle
        await new Promise((r) => setTimeout(r, 120));
      },
    },

    /* ── Step 3 — Dashboard cards ─────────────────────────── */
    {
      selector: ".tour-integrations",
      icon: "📋",
      title: "Everything in one view",
      description:
        "Your notifications, emails, messages, and events all appear here as cards. Click any item to open it directly.",
      position: "above",
      beforeStep: async () => {
        setView("dashboard");
        await new Promise((r) => setTimeout(r, 150));
      },
    },

    /* ── Step 4 — AI Assistant ────────────────────────────── */
    {
      selector: ".tour-assistant",
      icon: "🤖",
      title: "Your AI assistant",
      description:
        "Click this button anytime to open your personal AI assistant. Ask it anything about your workspace or just chat.",
      position: "above",
      beforeStep: async () => {
        // Ensure the assistant panel is closed so the floating button is visible
        setAssistOpen(false);
        await new Promise((r) => setTimeout(r, 150));
      },
    },

    /* ── Step 5 — Theme settings ──────────────────────────── */
    {
      selector: ".tour-appearance",
      icon: "🎨",
      title: "Make it yours",
      description:
        "Switch between light and dark mode, or choose a custom font from the font picker in Settings → Appearance.",
      position: "left",
      beforeStep: async () => {
        // Navigate to settings so the appearance card is rendered
        setView("settings");
        await new Promise((r) => setTimeout(r, 350));
      },
    },

    /* ── Step 6 — Done ────────────────────────────────────── */
    {
      selector: ".side-foot",
      icon: "✅",
      title: "You're all set",
      description:
        "Your workspace is ready. Connect your first service to start seeing your updates here.",
      position: "right",
      beforeStep: async () => {
        // Go back to dashboard for the closing step
        setView("dashboard");
        await new Promise((r) => setTimeout(r, 150));
      },
    },
  ];
}
