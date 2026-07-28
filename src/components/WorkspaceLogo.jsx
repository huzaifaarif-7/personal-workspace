export default function WorkspaceLogo({ size = 32, showText = false }) {
  const bg = "#07070d"
  const blue = "#5b8df7"
  const radius = size * 0.18
  return (
    <div style={{ display: "flex", alignItems: "center", gap: size * 0.35 }}>
      <svg
        width={size} height={size}
        viewBox="0 0 100 100"
        xmlns="http://www.w3.org/2000/svg"
      >
        <rect width="100" height="100" rx={radius} fill={bg}/>
        <path
          d="M22 22 L34 22 L50 62 L66 22 L78 22 L78 78 L66 78 L66 44 L53 78 L47 78 L34 44 L34 78 L22 78 Z"
          fill={blue}
        />
      </svg>
      {showText && (
        <span style={{
          fontSize: size * 0.44,
          fontWeight: 500,
          color: "var(--text)",
          letterSpacing: "-0.02em",
          fontFamily: "var(--font-sans, Inter, system-ui, sans-serif)"
        }}>
          Workspace
        </span>
      )}
    </div>
  )
}
