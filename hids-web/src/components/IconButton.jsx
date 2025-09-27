// src/components/IconButton.jsx
export default function IconButton({ title, onClick, children, className }) {
    return (
        <button
        type="button"
        title={title}
        onClick={onClick}
        className={
            "inline-flex items-center justify-center rounded-xl border border-white/10 bg-panel/50 hover:bg-panel2/80 transition px-2.5 py-1.5 text-sm " +
            (className || "")
        }
        >
        {children}
        </button>
    )
}
