from pathlib import Path
import subprocess,os
lab=Path(r'C:/Users/HP/Downloads/priceyard-current/audit-prep/p00')
env={key:os.environ[key] for key in ('SYSTEMROOT','WINDIR','TEMP','TMP','PATH') if key in os.environ}
env.update(PLAYWRIGHT_BROWSERS_PATH=str(lab/'runtime/browser-binaries'),USERPROFILE=str(lab/'runtime/browser-profile-base'),APPDATA=str(lab/'runtime/browser-appdata'),LOCALAPPDATA=str(lab/'runtime/browser-localappdata'))
result=subprocess.run([r'C:/Program Files/nodejs/node.exe','--require',str(lab/'node_transport_guard.cjs'),str(lab/'runtime/verify_preview.mjs'),str(lab)],cwd=lab/'runtime',env=env)
raise SystemExit(result.returncode)
