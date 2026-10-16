# Local verification only

This tooling is separate from application startup. Never run the application with
real configuration to test changes. The guard scrubs inherited configuration,
disables dotenv reads, denies external sockets/DNS/native PostgreSQL/children,
and permits only newly created in-memory SQLite engines.

Existing local verification tools are reused from the preserved recovery archive;
no application credentials or new dependency installs are needed. Runtime files,
snapshots and fabricated data are ignored. The preview uses the real API and the
compiled frontend, with a small external testing notice. External links, native
sharing, push permission and service-worker registration are disabled by the
preview wrapper. Production application components are not changed for this.

These process guards do not constitute a virtual machine or certify protection
against malicious native code. Browser verification also blocks external page
requests. Never claim production/provider compatibility from these tests.
