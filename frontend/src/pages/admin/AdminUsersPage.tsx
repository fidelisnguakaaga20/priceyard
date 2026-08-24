import { useState } from "react";
import { apiFetch } from "../../services/api";
import type { User } from "../../types/api";
import { AdminActionButton, AdminLoading, AdminStatus, errorText, useAdminList } from "./adminUtils";

export function AdminUsersPage() {
  const { data: users, loading, error: loadError, reload, token } = useAdminList<User>("/users");
  const [message, setMessage] = useState(""); const [error, setError] = useState(""); const [busyId, setBusyId] = useState<number | null>(null);
  async function patch(id: number, payload: { role?: string; is_active?: boolean }) {
    if (!token || busyId !== null) return; setBusyId(id); setError(""); setMessage("");
    try { await apiFetch(`/users/${id}`, { method: "PATCH", body: JSON.stringify(payload) }, token); setMessage("User updated."); await reload(); }
    catch (err) { setError(errorText(err)); }
    finally { setBusyId(null); }
  }
  return <div><h2>Users</h2><p className="muted">Manage approved roles and active/inactive account status.</p><AdminStatus error={error || loadError} success={message} />
    {loading ? <AdminLoading label="Loading users…" /> : <div className="table-wrap"><table className="admin-table"><thead><tr><th>User</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead><tbody>{users.map((user) => <tr key={user.id}><td><strong>{user.full_name}</strong><small>{user.email}</small></td><td><select value={user.role} disabled={busyId !== null} onChange={(e) => void patch(user.id, { role: e.target.value })}><option value="admin">admin</option><option value="free_user">free_user</option><option value="paid_user">paid_user</option></select></td><td>{user.is_active ? "Active" : "Inactive"}</td><td><AdminActionButton className="button button-small button-secondary" busy={busyId === user.id} disabled={busyId !== null && busyId !== user.id} onClick={() => void patch(user.id, { is_active: !user.is_active })}>{user.is_active ? "Deactivate" : "Activate"}</AdminActionButton></td></tr>)}</tbody></table></div>}
  </div>;
}
