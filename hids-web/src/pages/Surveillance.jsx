// src/pages/Surveillance.jsx
import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthProvider";
import { api } from "../lib/api";
import IconButton from "../components/IconButton";
import { Pencil, ScanLine, Trash2, Upload } from "lucide-react";

const FREQS = ["minutely", "hourly", "daily", "weekly"];

/* --------------------------------------------------------------
   Utils
-------------------------------------------------------------- */
function stripAndNormalizePath(raw) {
  if (!raw) return "";
  let s = String(raw).trim();
  // supprime les guillemets si “Copy as path” (Windows/macOS) les ajoute
  if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) {
    s = s.slice(1, -1);
  }
  // normalise / et \
  s = s.replace(/\\\\+/g, "\\").replace(/\/{2,}/g, "/");
  return s;
}

/* --------------------------------------------------------------
   Modal: Edit frequency (affichage uniquement + édition via crayon)
-------------------------------------------------------------- */
function EditFrequencyModal({ open, onClose, item, onSave }) {
  const [freq, setFreq] = useState(item?.frequency || "hourly");
  useEffect(() => setFreq(item?.frequency || "hourly"), [item]);
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />
      <div className="relative z-10 w-[420px] rounded-xl bg-panel p-4 border border-white/10 shadow-lg">
        <div className="text-lg font-medium mb-3">Edit frequency</div>

        <div className="space-y-2">
          <div className="text-sm text-muted">
            {item?.path || item?.ip || item?.hostname || "entity"}
          </div>
          <label className="text-xs text-muted">Frequency</label>
          <select
            value={freq}
            onChange={(e) => setFreq(e.target.value)}
            className="w-full bg-panel2 border border-white/10 rounded-md text-sm px-2 py-2 focus:outline-none"
          >
            {FREQS.map((f) => (
              <option key={f} value={f}>
                {f}
              </option>
            ))}
          </select>
        </div>

        <div className="mt-4 flex justify-end gap-2">
          <button
            className="px-3 py-1 rounded-md bg-panel/50 border border-white/10 hover:bg-panel transition"
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            className="px-3 py-1 rounded-md bg-green-600 hover:bg-green-500 text-white transition"
            onClick={() => onSave(freq)}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

/* --------------------------------------------------------------
    Modal: Add file/folder (helper local + instruction copier/coller)
-------------------------------------------------------------- */
function AddPathModal({ open, onClose, kind, onSave }) {
  const [path, setPath] = useState("");
  const [frequency, setFrequency] = useState("hourly");
  const [helperHint, setHelperHint] = useState(""); // juste pour afficher le nom/indice

  useEffect(() => {
    if (open) {
      setPath("");
      setFrequency("hourly");
      setHelperHint("");
    }
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />
      <div className="relative z-10 w-[520px] rounded-xl bg-panel p-4 border border-white/10 shadow-lg">
        <div className="text-lg font-medium mb-4">
          {kind === "files" ? "Add File" : "Add Folder"}
        </div>

        <div className="grid gap-3">
          {/* PATH */}
          <div className="grid gap-2">
            <label className="text-xs text-muted">Absolute path (server)</label>
            <input
              value={path}
              onChange={(e) => setPath(stripAndNormalizePath(e.target.value))}
              placeholder={kind === "files" ? "/etc/hosts" : "/var/log"}
              className="bg-panel2 border border-white/10 rounded-md px-3 py-2"
            />

            <div className="flex items-center gap-2">
              {/* Helper: ouvre le sélecteur local pour récupérer un indice (nom) */}
              <button
                type="button"
                className="px-2 py-1 rounded-md border border-white/10 bg-panel2 flex items-center gap-2"
                onClick={() => {
                  const inp = document.createElement("input");
                  inp.type = "file";
                  if (kind === "folders") inp.webkitdirectory = true;
                  inp.onchange = (ev) => {
                    const f = ev.target.files?.[0];
                    if (!f) return;
                    const hint =
                      kind === "folders"
                        ? (f.webkitRelativePath?.split("/")[0] || "")
                        : (f.name || "");
                    setHelperHint(hint);
                  };
                  inp.click();
                }}
                title={kind === "files" ? "Choose file (helper)" : "Choose folder (helper)"}
              >
                <Upload size={16} />
                {kind === "files" ? "Choose file" : "Choose folder"}
              </button>

              <span className="text-xs text-muted">
                Le navigateur ne peut pas lire les chemins absolus. <b>Faites un clic droit</b> sur
                le fichier/dossier dans votre OS → <b>Copier le chemin complet</b> puis collez‑le ci‑dessus.
              </span>
            </div>

            {helperHint && (
              <div className="text-xs text-muted">
                Helper picked: <span className="text-white/80">{helperHint}</span> (nom seulement)
              </div>
            )}

            <div className="text-[11px] leading-relaxed text-muted mt-1">
              Tips:
              <ul className="list-disc pl-4">
                <li>Windows: Shift + clic droit → “Copy as path”.</li>
                <li>macOS: clic droit → maintenir <b>Option</b> → “Copy “…” as Pathname”.</li>
                <li>Linux: la plupart des explorateurs ont “Copy location”.</li>
                <li>Les guillemets autour du chemin seront retirés automatiquement.</li>
              </ul>
            </div>
          </div>

          {/* FREQUENCY */}
          <div className="grid gap-2">
            <label className="text-xs text-muted">Frequency</label>
            <select
              value={frequency}
              onChange={(e) => setFrequency(e.target.value)}
              className="bg-panel2 border border-white/10 rounded-md text-sm px-2 py-2"
            >
              {FREQS.map((f) => (
                <option key={f} value={f}>
                  {f}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-4 flex justify-end gap-2">
          <button className="px-3 py-1.5 rounded-md bg-panel/50 border border-white/10" onClick={onClose}>
            Cancel
          </button>
          <button
            className="px-3 py-1.5 rounded-md bg-green-600 hover:bg-green-500 text-white transition disabled:opacity-50"
            onClick={() => onSave({ path: stripAndNormalizePath(path), frequency })}
            disabled={!stripAndNormalizePath(path)}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

/* --------------------------------------------------------------
    Modal: Add IP
-------------------------------------------------------------- */
function AddIpModal({ open, onClose, onSave }) {
  const [ip, setIp] = useState("");
  const [hostname, setHostname] = useState("");
  const [frequency, setFrequency] = useState("hourly");

  useEffect(() => {
    if (open) {
      setIp("");
      setHostname("");
      setFrequency("hourly");
    }
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />
      <div className="relative z-10 w-[460px] rounded-xl bg-panel p-4 border border-white/10 shadow-lg">
        <div className="text-lg font-medium mb-4">Add IP</div>

        <div className="grid gap-3">
          <div className="grid gap-2">
            <label className="text-xs text-muted">IP address</label>
            <input
              value={ip}
              onChange={(e) => setIp(e.target.value)}
              placeholder="10.0.0.1"
              className="bg-panel2 border border-white/10 rounded-md px-3 py-2"
            />
          </div>
          <div className="grid gap-2">
            <label className="text-xs text-muted">Hostname (optional)</label>
            <input
              value={hostname}
              onChange={(e) => setHostname(e.target.value)}
              placeholder="lab"
              className="bg-panel2 border border-white/10 rounded-md px-3 py-2"
            />
          </div>
          <div className="grid gap-2">
            <label className="text-xs text-muted">Frequency</label>
            <select
              value={frequency}
              onChange={(e) => setFrequency(e.target.value)}
              className="bg-panel2 border border-white/10 rounded-md text-sm px-2 py-2"
            >
              {FREQS.map((f) => (
                <option key={f} value={f}>
                  {f}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-4 flex justify-end gap-2">
          <button
            className="px-3 py-1 rounded-md bg-panel/50 border border-white/10"
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            className="px-3 py-1 rounded-md bg-green-600 hover:bg-green-700 text-white transition disabled:opacity-50"
            onClick={() => onSave({ ip, hostname, frequency })}
            disabled={!ip}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

/* --------------------------------------------------------------
    Page
-------------------------------------------------------------- */
export default function Surveillance() {
  const { token } = useAuth();
  const [tab, setTab] = useState("files"); // 'files' | 'folders' | 'ips'
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);

  // Modals
  const [editing, setEditing] = useState(null); // { entity, item }
  const [openAddFile, setOpenAddFile] = useState(false);
  const [openAddFolder, setOpenAddFolder] = useState(false);
  const [openAddIp, setOpenAddIp] = useState(false);

  // API maps
  const loaders = {
    files: () => api.listFiles(token),
    folders: () => api.listFolders(token),
    ips: () => api.listIps(token),
  };
  const deleters = {
    files: (id) => api.deleteFile(token, id),
    folders: (id) => api.deleteFolder(token, id),
    ips: (id) => api.deleteIp(token, id),
  };
  const scanners = {
    files: (id) => api.scanNowFile(token, id),
    folders: (id) => api.scanNowFolder(token, id),
    ips: (id) => api.scanNowIp(token, id),
  };
  const updaters = {
    files: (id, frequency) => api.setFileFreq(token, id, frequency),
    folders: (id, frequency) => api.setFolderFreq(token, id, frequency),
    ips: (id, frequency) => api.setIpFreq(token, id, frequency),
  };
  const creators = {
    files: (data) => api.createFile(token, data),
    folders: (data) => api.createFolder(token, data),
    ips: (data) => api.createIp(token, data),
  };

  const reload = async () => {
    setLoading(true);
    try {
      const data = await loaders[tab]();
      setRows(Array.isArray(data) ? data : data?.items || []);
    } catch (e) {
      console.error("load failed", e);
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    reload().catch(console.error);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab, token]);

  const onScan = async (id) => {
    await scanners[tab](id).catch(console.error);
  };

  const onDelete = async (id) => {
    if (!confirm("Delete item?")) return;
    await deleters[tab](id).catch(console.error);
    await reload();
  };

  const openEdit = (item) => setEditing({ entity: tab, item });

  const saveEdit = async (newFreq) => {
    if (!editing) return;
    const { entity, item } = editing;
    try {
      await updaters[entity](item.id, newFreq);
      setEditing(null);
      await reload();
    } catch (e) {
      console.error("update failed", e);
    }
  };

  const openAdd = () => {
    if (tab === "files") setOpenAddFile(true);
    else if (tab === "folders") setOpenAddFolder(true);
    else setOpenAddIp(true);
  };

  const submitAddFile = async ({ path, frequency }) => {
    try {
      await creators.files({ path, frequency, status: "active" });
      setOpenAddFile(false);
      await reload();
    } catch (e) {
      console.error("create file failed", e);
    }
  };
  const submitAddFolder = async ({ path, frequency }) => {
    try {
      await creators.folders({ path, frequency, status: "active" });
      setOpenAddFolder(false);
      await reload();
    } catch (e) {
      console.error("create folder failed", e);
    }
  };
  const submitAddIp = async ({ ip, hostname, frequency }) => {
    try {
      await creators.ips({ ip, hostname, frequency, status: "active" });
      setOpenAddIp(false);
      await reload();
    } catch (e) {
      console.error("create ip failed", e);
    }
  };

  return (
    <div className="space-y-4">
      {/* Tabs + Add */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {["files", "folders", "ips"].map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-3 py-1.5 rounded-md border capitalize ${
                tab === t ? "bg-panel2 border-white/10" : "bg-panel/50 border-white/5"
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        <button
          onClick={openAdd}
          className="px-3 py-1.5 rounded-md border border-white/10 bg-panel2 hover:bg-panel transition"
        >
          + Add
        </button>
      </div>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-white/5 text-muted">
            <tr>
              <th className="text-left px-4 py-3 w-[45%]">Path / IP</th>
              <th className="text-left px-4 py-3 w-[20%]">Frequency</th>
              <th className="text-left px-4 py-3 w-[15%]">Status</th>
              <th className="text-right px-4 py-3 w-[20%]">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-muted">
                  Loading…
                </td>
              </tr>
            )}
            {!loading && rows.length === 0 && (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-muted">
                  No data
                </td>
              </tr>
            )}
            {!loading &&
              rows.map((it) => (
                <tr key={it.id} className="border-t border-white/5">
                  <td className="px-4 py-3">
                    <div className="text-white truncate">{it.path || it.ip || "-"}</div>
                    {it.hostname && <div className="text-xs text-muted">{it.hostname}</div>}
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-block rounded-md bg-white/5 border border-white/10 px-2 py-1">
                      {it.frequency || "hourly"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`badge ${
                        it.status === "active"
                          ? "bg-emerald-500/20 text-emerald-300"   // vert
                          : it.status === "paused"
                          ? "bg-orange-500/20 text-orange-300"     // orange
                          : "bg-red-500/20 text-red-300"           // rouge (stopped ou autre)
                      }`}
                    >
                      {it.status || "inactive"}
                    </span>

                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end gap-2">
                      <IconButton title="Edit" onClick={() => openEdit(it)}>
                        <Pencil size={16} />
                      </IconButton>
                      <IconButton title="Scan now" onClick={() => onScan(it.id)}>
                        <ScanLine size={16} />
                      </IconButton>
                      <IconButton title="Delete" onClick={() => onDelete(it.id)}>
                        <Trash2 size={16} />
                      </IconButton>
                    </div>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {/* Modals */}
      <EditFrequencyModal
        open={!!editing}
        item={editing?.item}
        onClose={() => setEditing(null)}
        onSave={saveEdit}
      />

      <AddPathModal
        open={openAddFile}
        kind="files"
        onClose={() => setOpenAddFile(false)}
        onSave={submitAddFile}
      />
      <AddPathModal
        open={openAddFolder}
        kind="folders"
        onClose={() => setOpenAddFolder(false)}
        onSave={submitAddFolder}
      />
      <AddIpModal
        open={openAddIp}
        onClose={() => setOpenAddIp(false)}
        onSave={submitAddIp}
      />
    </div>
  );
}
