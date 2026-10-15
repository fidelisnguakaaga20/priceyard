import { AdminLoading, useAdminList } from "./adminUtils";
import { shortDate } from "../../utils";
type Audit={id:number;user_id:number;action:string;table_name:string;record_id:number|null;old_value:unknown;new_value:unknown;created_at:string};
export function AdminAuditLogsPage() {
  const { data, loading, error, pagination } = useAdminList<Audit>("/audit-logs");
  return <div>
    <h2>Audit logs</h2>
    <p className="muted">Administrative change history. Secrets and private source identities must never appear here.</p>
    {error && <div className="status-box error">{error}</div>}
    {loading ? <AdminLoading label="Loading audit logs…" /> : <div className="table-wrap"><table className="admin-table">
      <thead><tr><th>Time (Nigeria)</th><th>Actor</th><th>Action</th><th>Record</th><th>Change</th></tr></thead>
      <tbody>{data.map((item) => <tr key={item.id}>
        <td>{shortDate(item.created_at)}</td><td>User #{item.user_id}</td><td>{item.action}</td>
        <td>{item.table_name} #{item.record_id ?? "—"}</td>
        <td><small>{item.old_value ? `Old: ${JSON.stringify(item.old_value)}` : ""}</small><small>{item.new_value ? `New: ${JSON.stringify(item.new_value)}` : ""}</small></td>
      </tr>)}</tbody>
    </table></div>}
    {pagination}
  </div>;
}
