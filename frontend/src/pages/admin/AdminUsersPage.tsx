import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { apiFetch } from "../../services/api";
import type { User } from "../../types/api";
import { AdminActionButton, AdminLoading, AdminStatus, errorText } from "./adminUtils";
import { AdminPagination, useAdminPagedList } from "./adminPaging";
import "./owner-permissions.css";

export function AdminUsersPage() {
  const { user: currentUser } = useAuth();
  const page = useAdminPagedList<User>("/users/page");
  const { data: users, total, loading, error: loadError, reload, token } = page;
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState<number | null>(null);
  const isOwner = currentUser?.role === "admin" && currentUser.is_owner === true;
  const canManage = (user: User) => user.is_owner !== true && (user.role !== "admin" || isOwner);

  async function patch(id: number, payload: { role?: string; is_active?: boolean }) {
    if (!token || busyId !== null) return;
    const target = users.find((user) => user.id === id);
    if (!target || !canManage(target) || (payload.role === "admin" && !isOwner)) {
      setError(target?.is_owner ? "The Owner account is protected." : "Only the Owner can change Admin accounts.");
      return;
    }
    setBusyId(id); setError(""); setMessage("");
    try {
      await apiFetch(`/users/${id}`, { method: "PATCH", body: JSON.stringify(payload) }, token);
      setMessage("User updated.");
      await reload();
    } catch (err) { setError(errorText(err)); }
    finally { setBusyId(null); }
  }

  const roleControl = (user: User) => <>
    {user.is_owner === true && <span className="owner-account-badge">Owner</span>}
    <select aria-label={`Role for ${user.full_name} (${user.email})`} value={user.role}
      disabled={busyId !== null || !canManage(user)}
      onChange={(event) => void patch(user.id, { role: event.target.value })}>
      {(isOwner || user.role === "admin") && <option value="admin">admin</option>}
      <option value="free_user">free_user</option>
      <option value="paid_user">paid_user</option>
      <option value="reporter">reporter</option>
    </select>
    {user.is_owner === true ? <small className="owner-account-note">Protected Owner account</small>
      : user.role === "admin" && !isOwner && <small className="owner-account-note">Only the Owner can change Admin accounts.</small>}
  </>;

  const statusControl = (user: User) => <AdminActionButton className="button button-small button-secondary"
    busy={busyId === user.id} disabled={!canManage(user) || (busyId !== null && busyId !== user.id)}
    onClick={() => void patch(user.id, { is_active: !user.is_active })}>
    {user.is_active ? "Deactivate" : "Activate"}
  </AdminActionButton>;

  return <div>
    <h2>Users</h2>
    <p className="muted">Manage approved roles and active/inactive account status. Only the Owner can appoint or remove Admins.</p>
    {!loading && <p className="muted"><strong>Total users:</strong> {total}</p>}
    <AdminStatus error={error || loadError} success={message} />
    {loading ? <AdminLoading label="Loading users…" /> : <>
      <div className="table-wrap admin-table-view"><table className="admin-table">
        <thead><tr><th>User</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>{users.map((user) => <tr key={user.id} data-owner={user.is_owner === true}>
          <td><strong>{user.full_name}</strong><small>{user.email}</small></td>
          <td>{roleControl(user)}</td>
          <td>{user.is_active ? "Active" : "Inactive"}</td>
          <td>{statusControl(user)}</td>
        </tr>)}</tbody>
      </table></div>
      <div className="admin-card-list admin-mobile-list">{users.map((user) => <article className="card" key={user.id} data-owner={user.is_owner === true}>
        <div><strong>{user.full_name}</strong><p className="muted">{user.email}</p></div>
        <div className="mini-grid">
          <span><strong>Role</strong>{roleControl(user)}</span>
          <span><strong>Status</strong>{user.is_active ? "Active" : "Inactive"}</span>
        </div>
        {statusControl(user)}
      </article>)}</div>
    </>}
    <AdminPagination page={page} label="Users" />
  </div>;
}
