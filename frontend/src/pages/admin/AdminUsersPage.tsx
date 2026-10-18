import { useState } from "react";
import { apiFetch } from "../../services/api";
import type { User } from "../../types/api";
import { AdminActionButton, AdminLoading, AdminStatus, errorText } from "./adminUtils";
import { AdminPagination, useAdminPagedList } from "./adminPaging";

export function AdminUsersPage() {
  const page = useAdminPagedList<User>("/users/page");
  const { data: users, total, loading, error: loadError, reload, token } = page;
  const [message, setMessage] = useState(""); const [error, setError] = useState(""); const [busyId, setBusyId] = useState<number | null>(null);
  async function patch(id: number, payload: { role?: string; is_active?: boolean }) {
    if (!token || busyId !== null) return; setBusyId(id); setError(""); setMessage("");
    try { await apiFetch(`/users/${id}`, { method: "PATCH", body: JSON.stringify(payload) }, token); setMessage("User updated."); await reload(); }
    catch (err) { setError(errorText(err)); }
    finally { setBusyId(null); }
  }
  return <div><h2>Users</h2><p className="muted">Manage approved roles and active/inactive account status.</p>{!loading && <p className="muted"><strong>Total users:</strong> {total}</p>}<AdminStatus error={error || loadError} success={message} />
    {loading ? <AdminLoading label="Loading users…" /> : <>
      <div className="table-wrap admin-table-view"><table className="admin-table"><thead><tr><th>User</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead><tbody>{users.map((user) => <tr key={user.id}><td><strong>{user.full_name}</strong><small>{user.email}</small></td><td><select aria-label={`Role for ${user.full_name} (${user.email})`} value={user.role} disabled={busyId !== null} onChange={(e) => void patch(user.id, { role: e.target.value })}><option value="admin">admin</option><option value="free_user">free_user</option><option value="paid_user">paid_user</option><option value="reporter">reporter</option></select></td><td>{user.is_active ? "Active" : "Inactive"}</td><td><AdminActionButton className="button button-small button-secondary" busy={busyId === user.id} disabled={busyId !== null && busyId !== user.id} onClick={() => void patch(user.id, { is_active: !user.is_active })}>{user.is_active ? "Deactivate" : "Activate"}</AdminActionButton></td></tr>)}</tbody></table></div>
      <div className="admin-card-list admin-mobile-list">{users.map((user) => <article className="card" key={user.id}>
        <div><strong>{user.full_name}</strong><p className="muted">{user.email}</p></div>
        <div className="mini-grid">
          <span><strong>Role</strong><select aria-label={`Role for ${user.full_name} (${user.email})`} value={user.role} disabled={busyId !== null} onChange={(e) => void patch(user.id, { role: e.target.value })}><option value="admin">admin</option><option value="free_user">free_user</option><option value="paid_user">paid_user</option><option value="reporter">reporter</option></select></span>
          <span><strong>Status</strong>{user.is_active ? "Active" : "Inactive"}</span>
        </div>
        <AdminActionButton className="button button-small button-secondary" busy={busyId === user.id} disabled={busyId !== null && busyId !== user.id} onClick={() => void patch(user.id, { is_active: !user.is_active })}>{user.is_active ? "Deactivate" : "Activate"}</AdminActionButton>
      </article>)}</div>
    </>}
    <AdminPagination page={page} label="Users" />
  </div>;
}
