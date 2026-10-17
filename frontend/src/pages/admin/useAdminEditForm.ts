import { useEffect, useRef, useState } from "react";
import type { ChangeEvent } from "react";

const missingRecord = "Record not found. Enter an existing ID or leave it blank to create.";
const loadingRecord = "Wait for the selected record to load.";

/** Populate only the existing controls; never save or fetch a record automatically. */
export function useAdminEditForm<T extends { id: number }>(data: T[], loading: boolean, setError: (message: string) => void) {
  const formRef = useRef<HTMLFormElement>(null);
  const [editId, setEditId] = useState("");
  const loadedId = useRef<string | null>(null);

  function onIdChange(event: ChangeEvent<HTMLInputElement>) {
    const input = event.currentTarget;
    const id = input.value;
    input.form?.reset();
    input.value = id;
    input.setCustomValidity(id ? loadingRecord : "");
    loadedId.current = null;
    setError("");
    setEditId(id);
  }

  useEffect(() => {
    const form = formRef.current;
    const idInput = form?.elements.namedItem("id");
    if (!form || !(idInput instanceof HTMLInputElement) || !editId || loading || loadedId.current === editId) return;
    const record = data.find(item => item.id === Number(editId));
    if (!record) {
      idInput.setCustomValidity(missingRecord);
      setError(missingRecord);
      return;
    }
    for (const control of Array.from(form.elements)) {
      if ((control instanceof HTMLInputElement || control instanceof HTMLTextAreaElement || control instanceof HTMLSelectElement)
          && control.name !== "id" && Object.prototype.hasOwnProperty.call(record, control.name)) {
        const value = (record as Record<string, unknown>)[control.name];
        control.value = value == null ? "" : String(value);
      }
    }
    loadedId.current = editId;
    idInput.setCustomValidity("");
    setError("");
  }, [data, loading, editId, setError]);

  function canSubmit() {
    const input = formRef.current?.elements.namedItem("id");
    if (!(input instanceof HTMLInputElement) || !input.value) return true;
    if (loadedId.current !== input.value) {
      setError(input.validationMessage || loadingRecord);
      input.reportValidity();
      return false;
    }
    return input.checkValidity();
  }

  return { formRef, onIdChange, canSubmit };
}
