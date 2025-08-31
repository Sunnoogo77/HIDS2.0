// components/Modal.jsx
export default function Modal({ title, open, onClose, children, actions }) {
    if (!open) return null
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="absolute inset-0 bg-black/60" onClick={onClose} />
        <div className="relative w-full max-w-lg rounded-2xl bg-panel border border-white/10 shadow-xl">
            <div className="px-5 py-4 border-b border-white/10 text-sm text-muted">{title}</div>
            <div className="p-5">{children}</div>
            <div className="px-5 py-4 border-t border-white/10 flex justify-end gap-2">
            {actions}
            </div>
        </div>
        </div>
    )
}
