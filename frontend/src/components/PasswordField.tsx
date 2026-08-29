type PasswordFieldProps = {
  id: string;
  value: string;
  onChange: (value: string) => void;
  visible: boolean;
  onToggle: () => void;
  autoComplete: string;
  minLength?: number;
  maxLength?: number;
};

export function PasswordField({ id, value, onChange, visible, onToggle, autoComplete, minLength, maxLength }: PasswordFieldProps) {
  const label = visible ? "Hide password" : "Show password";
  return <div className="password-field">
    <input id={id} type={visible ? "text" : "password"} required minLength={minLength} maxLength={maxLength} autoComplete={autoComplete} value={value} onChange={(event) => onChange(event.target.value)} />
    <button type="button" className="password-toggle" onClick={onToggle} aria-controls={id} aria-pressed={visible} aria-label={label} title={label}>
      {visible ? <EyeOffIcon /> : <EyeIcon />}
    </button>
  </div>;
}

function EyeIcon() {
  return <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></svg>;
}

function EyeOffIcon() {
  return <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m3 3 18 18"/><path d="M10.6 5.2A10.8 10.8 0 0 1 12 5c6.5 0 10 7 10 7a18 18 0 0 1-2.1 3.2M6.6 6.6C3.6 8.5 2 12 2 12s3.5 7 10 7a9.8 9.8 0 0 0 4.1-.9"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/></svg>;
}
