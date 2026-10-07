        <h3>{busy ? 'جارٍ استيراد الملفات…' : 'اسحب ملفات التدريب إلى هنا'}</h3>
        <p>MD / TXT / JSON / JSONL / CSV / PDF / DOCX / Code</p>
        <div className="dropAction"><Paperclip size={15}/> اختيار ملفات Windows</div>
        <small>إذا لم تتوفر مسارات السحب داخل Electron، يحفظ التطبيق الملفات تلقائياً عبر عملية النظام ثم يرسلها إلى Runtime.</small>
      </section>

      <section className="pipelineCard">
        <PanelTitle Icon={Gauge} title="دورة الإصدار الحالية" pill={learn.state === 'running' ? 'RUNNING' : learn.state === 'failed' ? 'FAILED' : learn.state === 'completed' ? 'COMPLETED' : 'READY'} ok={learn.state !== 'failed'}/>
        <div className="pipeline"><Step n="1" title="Validate" done={pct >= 5}/><Step n="2" title="Dataset" done={pct >= 15}/><Step n="3" title="LoRA" done={pct >= 20}/><Step n="4" title="Evaluate" done={pct >= 85}/><Step n="5" title="Promote" done={learn.state === 'completed'}/></div>
        <div className="progressLarge"><div style={{ width: `${pct}%` }}/></div>
        <div className="progressMeta"><span>{learn.generation || '—'} · {learn.phase || 'idle'} · {learn.message || 'جاهز'}</span><strong>{pct}%</strong></div>
        <div className="trainingTelemetry">
          <div><span>الخطوة</span><b>{learn.step || 0} / {learn.total_steps || 0}</b></div>
          <div><span>العينات المعالجة</span><b>{learn.samples_seen || 0}</b></div>
          <div><span>الخطوات المتبقية</span><b>{remainingSteps ?? '—'}</b></div>
          <div><span>الوقت المنقضي</span><b>{elapsed}</b></div>
          <div><span>ETA</span><b>{eta}</b></div>
          <div><span>Tokens/s</span><b>{Number(learn.tokens_per_sec || 0).toFixed(1)}</b></div>
          <div><span>Loss</span><b>{learn.loss != null ? Number(learn.loss).toFixed(4) : '—'}</b></div>
          <div><span>LR</span><b>{learn.lr != null ? Number(learn.lr).toExponential(2) : '—'}</b></div><div><span>GPU</span><b>{learn.gpu_util_percent == null ? '—' : `${Number(learn.gpu_util_percent).toFixed(0)}%`}</b></div><div><span>VRAM متاحة</span><b>{learn.gpu_mem_free_gb == null ? '—' : `${Number(learn.gpu_mem_free_gb).toFixed(2)} GB`}</b></div>
        </div>
        <div className="learnFacts"><InfoRow label="الإصدار الأساسي" value={learn.active?.version || '—'}/><InfoRow label="بيانات جديدة" value={learn.pending_sources ?? 0}/><InfoRow label="مصادر مدرّبة" value={learn.trained_sources ?? 0}/></div>
      </section>
    </div>

    <div className="trainStats"><Stat icon={BookOpen} title="مصادر جديدة" value={status.pending?.length ?? 0} sub="جاهزة لـRAG والتدريب"/><Stat icon={History} title="الإصدارات" value={(status.versions || []).length} sub="v1 → vN مع Rollback"/><Stat icon={ShieldCheck} title="البوابات" value="5" sub="Integrity + Regression + Promotion"/><Stat icon={Database} title="RAG فقط" value={status.status?.rag_only ?? 0} sub="وثائق بلا أزواج تدريب"/></div>

    <div className="twoCards"><section className="tableCard"><div className="sectionHead"><div><h3>الملفات المقبولة</h3><p>Hash + provenance + حالة الدورة.</p></div><span className="countPill">{status.pending?.length || 0} جديد</span></div>{(status.pending || []).length ? <div className="fileList">{status.pending.slice(0, 80).map((r) => <div className="trainRow" key={r.id || r.source_hash}><div className="rowIcon"><FileText size={15}/></div><div className="grow"><b>{r.original_name}</b><small>{r.sample_count} عينة · {r.characters} حرف · {r.status}</small></div><code>{String(r.content_hash || '').slice(0, 16)}…</code></div>)}</div> : <div className="empty compact">لا توجد بيانات تدريب جديدة. عند نجاح الاستيراد سيظهر الملف هنا فوراً.</div>}</section><section className="tableCard"><PanelTitle Icon={Activity} title="السجل الحي"/><div className="eventLog">{events.length ? events.slice().reverse().map((e, i) => <div className="eventLine" key={`${e.ts}-${i}`}><span>{new Date((e.ts || Date.now()) * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span><b>{e.phase}</b><small>{e.message}</small></div>) : <div className="empty compact">سيظهر هنا كل حدث من الاستيراد والتدريب والتقييم والترقية.</div>}</div></section></div>

    <section className="tableCard"><div className="sectionHead"><div><h3>سجل الإصدارات</h3><p>كل إصدار يعتمد على السابق ولا يصبح Active إلا بعد البوابات.</p></div></div>{status.versions?.length ? <div className="versions">{status.versions.map((v) => <div className={`versionRow ${v.status === 'active' ? 'active' : ''}`} key={v.version}><div className="versionBadge">{v.version}</div><div className="grow"><b>{v.status === 'active' ? 'Active' : v.status === 'archived' ? 'Archived' : v.status}</b><small>Base: {v.base_version || '—'} · Loss: {v.evaluation?.loss != null ? Number(v.evaluation.loss).toFixed(4) : '—'}</small></div><div className="versionPath">{v.gguf || v.hf_dir || '—'}</div><span className={`statusBadge ${v.status}`}>{v.status}</span></div>)}</div> : <div className="empty">سيظهر الإصدار الجديد بعد أول دورة ناجحة.</div>}</section>
  </PageShell>;
}
function Step({ n, title, done }) { return <div className={`step ${done ? 'done' : ''}`}><span>{done ? <Check size={14}/> : n}</span><b>{title}</b></div>; }
function Stat({ icon:Icon, title, value, sub }) { return <div className="statCard"><div className="statIcon"><Icon size={16}/></div><div><span>{title}</span><b>{value}</b><small>{sub}</small></div></div>; }

function SettingsPage({ status, setStatus, refresh }) {
  const [settings, setSettings] = useState({ allow_internet: false }); const [doctor, setDoctor] = useState(null); const [busy, setBusy] = useState(false);
  useEffect(() => { api.settings().then(setSettings).catch(() => {}); }, []);
  const save = async (patch) => { setBusy(true); try { const r = await api.saveSettings({ ...settings, ...patch }); setSettings(r.settings || r); } finally { setBusy(false); } };
  const runDoctor = async () => { setDoctor(null); try { setDoctor(await api.doctor()); } catch (e) { setDoctor({ error: msg(e) }); } };
  return <PageShell title="الإعدادات" sub="التحكم في التشغيل المحلي والأمان والبيئة" actions={<button className="primaryBtn" onClick={runDoctor}><ShieldCheck size={15}/>فحص شامل</button>}>
    <div className="settingsGrid"><SettingCard icon={SlidersHorizontal} title="الوضع الاحترافي" text="واجهة ALI Studio القياسية." state="ON"/><SettingCard icon={Brain} title="ذاكرة متعددة الطبقات" text="Memory + Conversation Memory." state="READY"/><label className="settingCard"><Globe2/><div><b>البحث الخارجي</b><small>لا يستخدم الإنترنت إلا عند السماح الصريح.</small></div><input type="checkbox" checked={Boolean(settings.allow_internet)} onChange={(e) => save({ allow_internet: e.target.checked })} disabled={busy}/></label><SettingCard icon={ShieldCheck} title="Safe Path / Audit" text="قيود المسارات وتسجيل العمليات." state="ACTIVE"/></div>
    {doctor && <section className="tableCard"><PanelTitle Icon={ShieldCheck} title="تقرير الفحص"><div/></PanelTitle>{doctor.error ? <ErrorBox text={doctor.error}/> : (doctor.checks || []).map((c) => <div className="doctorRow" key={c.name}><span className={c.ok ? 'okIcon' : 'badIcon'}>{c.ok ? <CheckCircle2 size={15}/> : <X size={15}/>}</span><b>{c.name}</b><small>{c.detail}</small></div>)}</section>}
    <section className="tableCard"><PanelTitle Icon={Info} title="معلومات التشغيل"/><InfoRow label="الإصدار" value={status.version || '4.5.8'}/><InfoRow label="Python Runtime" value="3.11.9 (Embedded في حزمة Windows)"/><InfoRow label="Electron" value="40.10.2"/><InfoRow label="Renderer" value="React 19"/><InfoRow label="Terminal" value="node-pty / ConPTY"/></section>
  </PageShell>;
}
function SettingCard({ icon:Icon, title, text, state }) { return <div className="settingCard"><Icon/><div><b>{title}</b><small>{text}</small></div><strong>{state}</strong></div>; }

function ModelsPage({ models, active, onSelect, onPromote }) {
  return <PageShell title="النماذج" sub="Active / Candidate / Archived مع تحميل آمن وإرجاع النسخة السابقة" actions={<button className="softBtn" onClick={() => window.location.reload()}><RefreshCw size={14}/>تحديث</button>}><section className="tableCard">{models.length ? models.map((m) => <div className={`modelRow ${m.status === 'active' ? 'active' : ''}`} key={m.version}><div className="versionBadge">{m.version}</div><div className="grow"><b>{m.version} · {m.artifact_type}</b><small>Base: {m.base_version || '—'} · {m.hf_dir || m.checkpoint || '—'}</small></div><span className={`statusBadge ${m.status}`}>{m.status}</span><button className="softBtn" onClick={() => onSelect(m.version)} disabled={active === m.version}>{active === m.version ? 'محمل' : 'تحميل'}</button>{m.status === 'candidate' && <button className="primaryBtn" onClick={() => onPromote(m.version)}>اعتماد</button>}</div>) : <div className="empty">لا توجد نماذج قابلة للتحميل.</div>}</section></PageShell>;
}

function PageShell({ title, sub, actions, children }) { return <main className="centerPanel page"><div className="pageHeader"><div><h2>{title}</h2><p>{sub}</p></div><div className="headerActions">{actions}</div></div>{children}</main>; }
function ErrorBox({ text }) { return <div className="errorBox"><X size={15}/><span>{text}</span></div>; }

function Bottom({ status, model }) { return <footer className="bottom"><span><i className={status.online ? 'greenDot' : ''}/>{status.online ? 'جاهز' : 'انتظار Runtime'}</span><span>Python 3.11.9</span><span>Electron IPC</span><span>{model || status.modelVersion || 'No model'}</span><span className="grow"/><span>ALI Studio Pro — Adaptive Hybrid</span></footer>; }

export default function App() {
  const [active, setActive] = useState('chat'); const [mode, setMode] = useState('الوضع الاحترافي'); const [computeMode, setComputeMode] = useState(() => localStorage.getItem('ali.computeMode') || 'Auto (Smart)'); const [model, setModel] = useState('Auto (Active)'); const [modelItems, setModelItems] = useState(['Auto (Active)']); const [models, setModels] = useState([]); const [status, setStatus] = useState({ online: false, modelLoaded: false, version: '4.6.0' }); const [hw, setHw] = useState({}); const [workspace, setWorkspace] = useState(''); const [messages, setMessages] = useState([]); const [conversations, setConversations] = useState([]); const [conversationId, setConversationId] = useState(''); const [training, setTraining] = useState({ status: { state: 'idle' }, pending: [], versions: [] }); const [toast, setToast] = useState('');
  const refresh = useCallback(async () => { try { const [s, hwRes, m, t, c] = await Promise.all([api.status(), api.hardware(), api.models(), api.training(), api.conversations()]); setStatus({ online: true, ...s }); setHw({ ...s.hardware, ...hwRes.hardware }); setWorkspace(s.workspace || workspace); setModels(m.models || []); const names = ['Auto (Active)', ...(m.models || []).map((x) => x.version).filter(Boolean)]; setModelItems(names); if (!model || model === 'Auto (Active)') setModel(m.selectedVersion || s.modelVersion || 'Auto (Active)'); setTraining(t); setConversations(c.conversations || []); } catch (e) { setStatus((prev) => ({ ...prev, online: false, error: msg(e) })); } }, [workspace, model]);
  useEffect(() => { refresh(); const t = setInterval(refresh, 2500); return () => clearInterval(t); }, [refresh]);
  useEffect(() => window.electronAPI?.onWorkspaceChanged?.((p) => { setWorkspace(p); api.workspace(p).then(refresh).catch(() => {}); }), [refresh]);
  useEffect(() => { const h = (e) => { if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'p') setActive('settings'); }; window.addEventListener('keydown', h); return () => window.removeEventListener('keydown', h); }, []);
  useEffect(() => { const t = setInterval(() => document.title = `ALI Studio Pro · ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`, 1000); return () => clearInterval(t); }, []);
  const selectProject = async () => { const r = await window.electronAPI?.selectProject?.(); if (r?.path) { try { await api.workspace(r.path); setWorkspace(r.path); } catch (_) {} await refresh(); } };
  const selectedCompute = computeMode === 'GPU' ? 'gpu' : computeMode === 'CPU' ? 'cpu' : 'auto';
  const changeComputeMode = async (label) => { setComputeMode(label); localStorage.setItem('ali.computeMode', label); if (training.status?.state === 'running') return; try { const r = await api.selectModel(model === 'Auto (Active)' ? '' : model, label === 'GPU' ? 'gpu' : label === 'CPU' ? 'cpu' : 'auto'); setStatus((p) => ({ ...p, modelLoaded: true, modelVersion: r.version || p.modelVersion })); } catch (e) { setToast(msg(e)); } };
  const selectModel = async (v) => { setModel(v); if (v === 'Auto (Active)') { try { await api.selectModel('', selectedCompute);  await refresh(); } catch (e) { setToast(msg(e)); } return; } try { const r = await api.selectModel(v, selectedCompute); setStatus((p) => ({ ...p, modelLoaded: true, modelVersion: r.version || v })); setToast(`تم تحميل ${v}`); } catch (e) { setToast(msg(e)); } };
  const promote = async (v) => { try { await api.promoteModel(v); setToast(`تم اعتماد ${v} كنموذج Active.`); await refresh(); } catch (e) { setToast(msg(e)); } };
  useEffect(() => { if (!toast) return; const t = setTimeout(() => setToast(''), 3500); return () => clearTimeout(t); }, [toast]);
  const openTraining = () => setActive('training');
  const page = useMemo(() => { switch (active) { case 'projects': return <ProjectsPage workspace={workspace} onSelect={selectProject}/>; case 'files': return <FilesPage workspace={workspace}/>; case 'memory': return <MemoryPage/>; case 'improvement': return <ImprovementPage/>; case 'tools': return <ToolsPage workspace={workspace}/>; case 'web': return <WebPage/>; case 'training': return <TrainingPage computeMode={computeMode}/>; case 'settings': return <SettingsPage status={status} setStatus={setStatus} refresh={refresh}/>; default: return <ChatPage messages={messages} setMessages={setMessages} workspace={workspace} onOpenTraining={openTraining} onGo={setActive} conversationId={conversationId} setConversationId={setConversationId} conversations={conversations} reloadConversations={refresh} computeMode={computeMode} model={model}/>; } }, [active, workspace, messages, conversations, conversationId, computeMode, model, status, refresh]);
  return <div className="appShell"><TopBar mode={mode} setMode={setMode} computeMode={computeMode} setComputeMode={changeComputeMode} model={model} setModel={selectModel} modelItems={modelItems} hw={hw} learning={training.status} onRefresh={refresh}/><div className="content"><LeftSidebar active={active} setActive={setActive} hw={hw} workspace={workspace} onSelect={selectProject}/>{active === 'models' ? <ModelsPage models={models} active={status.modelVersion} onSelect={selectModel} onPromote={promote}/> : page}<RightSidebar hw={hw} status={status} training={training} onOpenTraining={openTraining}/></div><Bottom status={status} model={model}/>{toast && <div className="toast"><CheckCircle2 size={15}/>{toast}</div>}</div>;
}
```

---

### `490/588` `desktop/src/main.jsx`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\desktop/src/main.jsx`
- **الحجم:** 366 بايت (0.4 KB)
- **الامتداد:** `.jsx`

```jsx
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './styles.css';

document.documentElement.lang = 'ar';
document.documentElement.dir = 'rtl';
document.documentElement.dataset.aliDesign = 'design4';
document.body.dataset.aliDesign = 'design4';

createRoot(document.getElementById('root')).render(<App />);
```

---

### `491/588` `desktop/src/styles.css`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\desktop/src/styles.css`
- **الحجم:** 42003 بايت (41.0 KB)
- **الامتداد:** `.css`

```css
:root{font-family:"Segoe UI",Tahoma,"Arial",sans-serif;color:#17324f;background:#f6f9fd;font-synthesis:none;text-rendering:optimizeLegibility}
*{box-sizing:border-box}html,body,#root{margin:0;width:100%;height:100%;overflow:hidden}button,input,textarea,select{font:inherit}button{cursor:pointer}button:disabled{opacity:.5;cursor:not-allowed}.grow{flex:1;min-width:0}
.appShell{direction:rtl;width:100%;height:100%;display:flex;flex-direction:column;background:linear-gradient(180deg,#f8fbff 0%,#eef4fa 100%)}
.topbar{height:70px;display:grid;grid-template-columns:300px minmax(430px,1fr) 470px;align-items:center;gap:18px;padding:0 14px;border-bottom:1px solid #dce5f1;background:rgba(255,255,255,.96);box-shadow:0 1px 10px rgba(18,54,92,.05);flex:none}
.brandWrap{display:flex;align-items:center;gap:10px;min-width:0}.brandWrap .logo{width:38px;height:38px}.brandWrap b{display:block;font-size:17px;line-height:1.1;color:#173c67}.brandWrap small{display:block;color:#7b899e;font-size:10px;margin-top:2px}.logo{display:block;object-fit:contain}.logo.small{width:30px;height:30px}
.topControls{display:flex;align-items:center;justify-content:center;gap:10px;min-width:0}.selectBox{position:relative;display:flex;align-items:center;gap:9px;min-width:185px;height:38px;padding:0 11px;border:1px solid #d7e2ef;border-radius:9px;background:#fbfdff;color:#214464;font-size:11px;overflow:hidden}.selectBox svg:first-child{color:#3979e9;flex:none}.selectBox span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1}.selectBox select{position:absolute;inset:0;opacity:0;cursor:pointer}.selectBox.disabled{background:#f2f5f9}.liveTrain{display:flex;align-items:center;gap:6px;padding:8px 10px;border-radius:999px;border:1px solid #cde7d7;background:#f0fbf4;color:#19864a;font-size:10px;white-space:nowrap}.pulseDot,.greenDot{display:inline-block;width:7px;height:7px;border-radius:50%;background:#1aae62}.pulseDot{animation:pulse 1.4s infinite}@keyframes pulse{50%{box-shadow:0 0 0 5px rgba(26,174,98,.12)}}
.machine{display:flex;align-items:center;justify-content:flex-end;gap:12px;min-width:0}.machineDevice{display:flex;align-items:center;gap:8px}.machineDevice svg{color:#1f3b63}.machineDevice b{display:block;font-size:10px;color:#193656}.machineDevice small,.clockBlock small{display:block;color:#8592a6;font-size:8px;margin-top:2px}.clockBlock{text-align:right;padding-right:4px}.clockBlock b{font-size:11px;color:#193856}.windowButtons{display:flex;gap:2px;border-right:1px solid #e1e7ef;padding-right:8px}.windowButtons button{border:0;background:transparent;width:28px;height:26px;border-radius:6px;color:#57708d;font-size:16px}.windowButtons button:hover{background:#eef4fb}.windowButtons button:last-child:hover{background:#fdeeee;color:#bf2828}.iconButton{display:grid;place-items:center;width:31px;height:30px;border:1px solid #d8e3ef;background:#fff;border-radius:7px;color:#55718e}.iconButton:hover{background:#eef5ff;color:#2d6ede}.dangerIcon{color:#ad3b3b}.primaryBtn,.softBtn,.dangerBtn{display:inline-flex;align-items:center;justify-content:center;gap:6px;border-radius:8px;padding:8px 12px;border:1px solid #cad9eb;font-size:10px;line-height:1;transition:.15s}.primaryBtn{border-color:#3779ee;background:#3f7ff0;color:#fff;box-shadow:0 3px 8px rgba(57,116,228,.14)}.primaryBtn:hover{background:#2f6fe3}.softBtn{background:#f7faff;color:#345875}.softBtn:hover{background:#edf4fd}.dangerBtn{background:#fff4f4;border-color:#efc7c7;color:#b33131}.full{width:100%;margin-top:10px}
.content{display:grid;grid-template-columns:255px minmax(520px,1fr) 345px;gap:0;min-height:0;flex:1}.leftbar{border-left:1px solid #dce5f1;background:#f9fbfe;padding:10px 9px 12px;display:flex;flex-direction:column;gap:10px;overflow:hidden}.navList{display:flex;flex-direction:column;gap:4px;overflow:auto;padding-left:2px}.navItem{display:flex;align-items:center;gap:11px;width:100%;padding:10px 10px;border:1px solid transparent;background:transparent;border-radius:10px;color:#213b59;text-align:right}.navItem svg{color:#355e83;flex:none}.navItem span{min-width:0}.navItem b{display:block;font-size:11px}.navItem small{display:block;color:#8492a7;font-size:8px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.navItem:hover{background:#eef5fc}.navItem.active{background:#e7f0ff;border-color:#d0e1fb;box-shadow:inset -3px 0 0 #397df0}.navItem.active svg,.navItem.active b{color:#2367d4}
.deviceCard{margin-top:auto;border:1px solid #d9e3ee;border-radius:10px;background:#fff;box-shadow:0 2px 8px rgba(22,53,90,.04);padding:10px}.deviceHead{display:flex;align-items:center;gap:8px;padding-bottom:8px;border-bottom:1px solid #edf1f5}.deviceHead>div:nth-child(2){min-width:0}.deviceHead b{display:block;font-size:10px;color:#193b5f;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.deviceHead small{display:block;color:#8a98aa;font-size:7px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.deviceHead button{margin-right:auto;border:0;background:#eef5ff;color:#3d74dd;border-radius:7px;width:28px;height:26px;display:grid;place-items:center}.deviceDot{width:8px;height:8px;border-radius:50%;background:#21ae63;flex:none}.metrics{display:grid;grid-template-columns:1fr 1fr;gap:2px 5px;padding:7px 0}.metric{display:flex;gap:6px;align-items:center;padding:6px 2px;min-width:0}.metric svg{color:#3979dd;flex:none}.metric div{min-width:0}.metric span,.metric small{display:block;color:#8b9aac;font-size:7px}.metric b{display:block;color:#294967;font-size:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin:2px 0}.workspaceLine{display:flex;align-items:center;gap:6px;color:#637e9b;border-top:1px solid #edf1f5;padding-top:8px;font-size:7px}.workspaceLine svg{flex:none;color:#4a7bd8}.workspaceLine span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.centerPanel{min-width:0;background:#fff;border-left:1px solid #dce5f1;border-right:1px solid #dce5f1;display:flex;flex-direction:column;min-height:0}.tabbar{height:45px;display:flex;align-items:stretch;padding:0 12px;border-bottom:1px solid #e1e7ef;background:#fff;flex:none;overflow:auto}.tab{display:flex;align-items:center;gap:7px;border:0;border-bottom:2px solid transparent;background:transparent;color:#71839b;padding:0 13px;font-size:10px;white-space:nowrap}.tab:hover{background:#f6f9fd;color:#315777}.tab.active{color:#1f6ce2;border-bottom-color:#3c7ff0;font-weight:700}.page{padding:14px;gap:10px;overflow:auto}.pageHeader{display:flex;align-items:flex-start;gap:12px;justify-content:space-between}.pageHeader h2{margin:0;color:#173c68;font-size:16px}.pageHeader p{margin:4px 0 0;color:#8997aa;font-size:9px}.headerActions{display:flex;align-items:center;gap:7px;flex-wrap:wrap}.searchMini{height:31px;display:flex;align-items:center;gap:6px;padding:0 9px;border:1px solid #d9e4ef;border-radius:8px;background:#fff}.searchMini svg{color:#6080a0}.searchMini input{width:130px;border:0;outline:0;font-size:9px;color:#274766;background:transparent}
.chatArea{flex:1;min-height:0;overflow:auto;padding:22px 22px 16px;background:radial-gradient(circle at 50% 5%,#fff 0,#fbfdff 52%,#f8fbfe 100%)}.welcome{display:flex;flex-direction:column;align-items:center;text-align:center;padding:35px 16px 18px}.welcome .logo{width:74px;height:74px;filter:drop-shadow(0 6px 12px rgba(43,109,221,.16))}.welcome h1{margin:10px 0 4px;color:#183e69;font-size:21px}.welcome p{margin:0;color:#8190a5;font-size:10px}.quickRow{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-top:18px;max-width:760px}.quickRow button{display:inline-flex;align-items:center;gap:6px;padding:8px 12px;border:1px solid #dce6f0;border-radius:999px;background:#f7faff;color:#355d83;font-size:9px}.quickRow button:hover{background:#edf4ff;border-color:#bfd6f7;color:#2b6bdc}.welcomeHint{display:flex;align-items:center;gap:6px;margin-top:13px;color:#98a5b5;font-size:8px}.messageRow{display:flex;gap:8px;align-items:flex-start;margin:13px 0}.messageRow.user{justify-content:flex-start}.messageRow.assistant{justify-content:flex-start}.avatar,.userAvatar{width:30px;height:30px;border-radius:50%;flex:none;display:grid;place-items:center}.avatar{background:#eaf2ff;border:1px solid #d5e4fa}.userAvatar{background:#3e7ef0;color:#fff}.bubble{max-width:min(86%,820px);border:1px solid #d9e4ef;border-radius:12px;background:#fff;box-shadow:0 3px 10px rgba(22,52,89,.035);padding:10px 12px}.messageRow.user .bubble{order:1;background:#eef5ff;border-color:#d6e6fb}.messageRow.user .userAvatar{order:2}.bubbleHead{display:flex;align-items:center;gap:7px;margin-bottom:5px}.bubbleHead b{font-size:10px;color:#234764}.bubbleHead span{font-size:7px;color:#9aa7b7}.bubbleHead em{font-style:normal;font-size:7px;color:#5482b3;background:#eef5fb;padding:2px 5px;border-radius:999px}.bubbleText{font-size:10px;line-height:1.75;color:#2b425b;white-space:pre-wrap;word-break:break-word}.messageActions{display:flex;gap:3px;margin-top:8px;padding-top:7px;border-top:1px solid #edf1f5}.messageActions button{display:grid;place-items:center;width:26px;height:23px;border:1px solid #e0e7ef;background:#fbfdff;border-radius:6px;color:#7190ad}.messageActions button:hover{background:#eff5fc;color:#376fd1}.messageActions .selectedGood{color:#1b9b57;background:#eefaf3;border-color:#cfe9db}.messageActions .selectedBad{color:#bc3f3f;background:#fff3f3;border-color:#f0d0d0}.sources,.toolResult{display:flex;align-items:center;gap:5px;margin-top:8px;padding:7px 8px;border-radius:7px;background:#f7faff;color:#6d8198;font-size:8px;flex-wrap:wrap}.sources button{border:0;background:#eaf2fc;color:#3974d5;border-radius:999px;padding:3px 6px;font-size:7px}.typing{display:inline-flex;align-items:center;gap:5px;padding:8px 10px;border-radius:9px;background:#f1f6fc;color:#7187a0;font-size:8px;margin-right:38px}.typing span{width:4px;height:4px;border-radius:50%;background:#4f85dd;animation:typing 1.2s infinite}.typing span:nth-child(2){animation-delay:.15s}.typing span:nth-child(3){animation-delay:.3s}@keyframes typing{40%{opacity:.25;transform:translateY(-2px)}}
.composer{display:flex;align-items:center;gap:7px;margin:0 18px 10px;padding:8px 9px;border:1px solid #d3dfec;background:#fff;border-radius:11px;box-shadow:0 4px 15px rgba(20,52,91,.05);flex:none}.composerTools{display:flex;gap:3px}.composerTools button{border:0;background:transparent;color:#567693;width:29px;height:29px;display:grid;place-items:center;border-radius:6px}.composerTools button:hover{background:#eef4fb;color:#306ed2}.composer textarea{flex:1;min-height:30px;max-height:115px;resize:vertical;outline:0;border:0;background:transparent;color:#294765;font-size:10px;line-height:1.6;padding:5px}.composer textarea::placeholder{color:#a1adbc}.sendButton{width:38px;height:34px;border:0;border-radius:9px;background:#417ff0;color:#fff;display:grid;place-items:center}.sendButton:hover{background:#2f6fe2}.sendButton:disabled{background:#cdd9ea}.spin{animation:spin .9s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}
.rightbar{padding:10px;background:#f7fafd;overflow:auto}.systemCard,.sysCard,.tableCard,.formCard,.heroCard,.pipelineCard,.dropZone{border:1px solid #dbe5f0;border-radius:10px;background:#fff;box-shadow:0 2px 9px rgba(22,51,86,.035);padding:11px}.rightbar>section+section{margin-top:9px}.panelTitle{display:flex;align-items:center;gap:7px;color:#234564;min-width:0}.panelTitle svg{color:#4877a6;flex:none}.panelTitle b{font-size:11px}.statusPill{display:inline-flex;align-items:center;gap:5px;padding:4px 7px;border-radius:999px;background:#f6ecec;color:#b14141;font-size:7px;margin-right:auto}.statusPill i{width:5px;height:5px;border-radius:50%;background:#c54c4c}.statusPill.ok{background:#edf9f1;color:#20874d}.statusPill.ok i{background:#1bb15f}.rings{display:flex;justify-content:space-between;gap:7px;margin:14px 0 8px}.ring{--p:0%;width:82px;height:82px;border-radius:50%;display:grid;place-items:center;background:conic-gradient(#3f7ff0 var(--p),#e9eef4 0);position:relative}.ring.green{background:conic-gradient(#34ad73 var(--p),#e9eef4 0)}.ring.violet{background:conic-gradient(#7d67e7 var(--p),#e9eef4 0)}.ring:before{content:"";position:absolute;inset:8px;border-radius:50%;background:#fff}.ringInner{position:relative;text-align:center}.ringInner span{display:block;color:#66809c;font-size:7px}.ringInner b{display:block;color:#183b64;font-size:12px;margin-top:4px}.temps{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;padding-bottom:10px;border-bottom:1px solid #edf1f5}.temps div{text-align:center}.temps b{display:block;color:#237c52;font-size:9px}.temps span{display:block;color:#93a0b0;font-size:7px;margin-top:2px}.batteryBox{display:flex;gap:9px;align-items:center;margin-top:10px}.batteryVisual{width:34px;height:34px;border-radius:9px;background:#eff9f3;color:#18a25b;display:grid;place-items:center}.row{display:flex;align-items:center;justify-content:space-between;gap:8px}.row b{font-size:10px;color:#244665}.row span{font-size:7px;color:#94a1b0}.batteryBox strong{font-size:12px;color:#234e76;display:block;margin:4px 0}.bar{height:6px;background:#e6ecf2;border-radius:99px;overflow:hidden}.bar span{display:block;height:100%;background:#20aa62;border-radius:99px}.infoRow{display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid #edf1f5}.infoRow:last-child{border-bottom:0}.infoRow span{color:#8391a4;font-size:8px;min-width:83px}.infoRow b{color:#294764;font-size:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.activityRow{display:grid;grid-template-columns:10px 1fr auto;gap:6px;align-items:center;padding:7px 0;border-top:1px solid #edf1f5}.activityRow i{width:6px;height:6px;border-radius:50%;background:#1eb067}.activityRow i.amberDot{background:#e9a22d}.activityRow b{font-size:8px;color:#35526f}.activityRow span{font-size:7px;color:#91a0b1}
.noticeCard{display:flex;align-items:flex-start;gap:9px;padding:10px;border-radius:9px;background:#eff7ff;border:1px solid #d3e5fa;color:#356187;font-size:9px}.noticeCard svg{color:#3476dc;flex:none}.noticeCard b{display:block;color:#28537a}.noticeCard p{margin:4px 0 0;color:#7690aa;font-size:8px}.errorBox{display:flex;align-items:flex-start;gap:7px;padding:9px;border-radius:8px;background:#fff3f3;border:1px solid #efcece;color:#a82f2f;font-size:9px}.twoCards{display:grid;grid-template-columns:1.35fr 1fr;gap:10px}.heroCard{display:flex;align-items:center;gap:12px}.heroIcon{width:52px;height:52px;border-radius:14px;background:#eaf2ff;color:#3a79e9;display:grid;place-items:center;flex:none}.heroCard h3{margin:0;color:#173c68;font-size:13px}.heroCard p{margin:5px 0;color:#8493a7;font-size:8px}.tags{display:flex;flex-wrap:wrap;gap:5px}.tags span,.tagRow span{font-size:7px;padding:3px 6px;background:#eef4fb;color:#63809f;border-radius:999px}.gitOutput{margin:9px 0 0;padding:10px;border-radius:8px;background:#0c1623;color:#dbe7f5;min-height:150px;white-space:pre-wrap;font:10px/1.65 Consolas,"Cascadia Mono",monospace;overflow:auto}.fileWorkspace{display:grid;grid-template-columns:280px 1fr;gap:10px;min-height:540px;flex:1}.fileTree{overflow:auto;border:1px solid #dbe5ef;border-radius:9px;background:#fbfdff;padding:6px}.fileRow,.backRow{width:100%;border:0;background:transparent;display:flex;align-items:center;gap:7px;text-align:right;padding:8px;border-radius:7px}.fileRow:hover,.backRow:hover{background:#eef5fd}.fileRow.selected{background:#eaf2ff}.fileRow div:nth-child(2){min-width:0}.fileRow b{display:block;color:#294864;font-size:9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.fileRow small{display:block;color:#8b9aac;font-size:7px;margin-top:2px}.rowIcon{width:29px;height:29px;border-radius:7px;background:#f0f5fb;color:#4b78a4;display:grid;place-items:center;flex:none}.editorPane{min-width:0;min-height:0;border:1px solid #dbe5ef;border-radius:9px;display:flex;flex-direction:column;overflow:hidden;background:#fff}.editorBar{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:7px 8px;border-bottom:1px solid #dbe5ef}.editorTitle{display:flex;align-items:center;gap:6px;min-width:0;color:#5a738e;font-size:8px}.editorTitle span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.editorTitle i{width:6px;height:6px;border-radius:50%;background:#e7a52c;display:inline-block}.editorActions{display:flex;gap:5px}.codeWrap{display:grid;grid-template-columns:42px 1fr;flex:1;min-height:0;background:#0d1724}.lineNumbers{padding:13px 7px 13px 0;background:#0a1320;color:#53677f;text-align:right;overflow:hidden;font:11px/1.65 Consolas,"Cascadia Mono",monospace;user-select:none}.lineNumbers span{display:block}.codeEditor{width:100%;height:100%;min-height:470px;resize:none;border:0;outline:0;padding:13px;background:#0d1724;color:#d9e6f5;font:11px/1.65 Consolas,"Cascadia Mono",monospace;tab-size:4}.codeEditor::placeholder{color:#647994}.formCard{padding:9px}.formGrid{display:flex;gap:7px}.formGrid select,.formGrid input{height:32px;border:1px solid #d9e4ef;border-radius:7px;padding:0 9px;outline:0;background:#fff;color:#365775;font-size:8px}.growInput{flex:1}.memoryTabs{display:flex;gap:5px}.memoryTabs button{border:1px solid #d9e4ef;background:#fff;border-radius:7px;padding:7px 11px;color:#65809a;font-size:8px}.memoryTabs button.active{background:#edf4ff;border-color:#c7dcfa;color:#2d6dd5}.listRow,.versionRow,.trainRow,.modelRow,.doctorRow{display:flex;align-items:center;gap:9px;padding:9px 0;border-top:1px solid #edf1f5}.listRow:first-child,.versionRow:first-child,.trainRow:first-child{border-top:0}.listRow b,.versionRow b,.trainRow b,.modelRow b{display:block;font-size:9px;color:#244461}.listRow small,.versionRow small,.trainRow small,.modelRow small{display:block;color:#8997a9;font-size:7px;margin-top:3px}.listRow code,.trainRow code{display:block;color:#8797a9;font-size:7px;margin-top:3px}.convRow{padding:10px;border-top:1px solid #edf1f5}.convRow:first-child{border-top:0}.convRow b{display:block;color:#6e8197;font-size:7px}.convRow span{display:block;color:#2d4c68;font-size:9px;line-height:1.6;margin-top:2px}.convRow small{display:block;color:#9aa8b6;font-size:7px;margin-top:5px}.searchBoxLarge{display:flex;align-items:center;gap:8px;padding:9px;border:1px solid #d6e2ef;background:#fff;border-radius:10px}.searchBoxLarge svg{color:#5c7fa4}.searchBoxLarge input{flex:1;border:0;outline:0;font-size:10px}.searchColumns{display:grid;grid-template-columns:1fr 1fr;gap:10px}.results{display:flex;flex-direction:column}.resultRow{display:flex;gap:8px;padding:10px 0;border-top:1px solid #edf1f5}.resultRow:first-child{border-top:0}.resultRow b{display:block;color:#294967;font-size:9px}.resultRow small{display:block;color:#8997a9;font-size:7px;line-height:1.55;margin-top:3px}.resultRow a{display:flex;align-items:center;gap:4px;color:#3975d6;text-decoration:none;font-size:7px;margin-top:5px}.switchLine{display:flex;align-items:center;gap:7px;color:#4a6580;font-size:8px}.switchLine input,.settingCard input,.autoToggle input{accent-color:#3d7ff0}.settingsGrid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.settingCard{display:flex;align-items:center;gap:10px;border:1px solid #dbe5ef;border-radius:9px;background:#fff;padding:12px}.settingCard>svg{color:#3d7be0;flex:none}.settingCard div{flex:1;min-width:0}.settingCard b{display:block;color:#294965;font-size:10px}.settingCard small{display:block;color:#8c99aa;font-size:8px;margin-top:3px}.settingCard strong{font-size:8px;color:#179451}.doctorRow{padding:8px 0}.doctorRow b{font-size:9px;color:#294965;min-width:140px}.doctorRow small{font-size:8px;color:#8b99aa}.okIcon{color:#179c55}.badIcon{color:#bd3838}.pipeline{display:grid;grid-template-columns:repeat(5,1fr);gap:5px;margin:13px 0 10px}.step{display:flex;align-items:center;gap:4px;padding:6px 5px;border:1px solid #e1e7ef;border-radius:7px;background:#fbfdff}.step span{width:20px;height:20px;border-radius:50%;display:grid;place-items:center;border:1px solid #d5dfeb;color:#8292a5;font-size:7px}.step b{font-size:7px;color:#72859b}.step.done{background:#effaf4;border-color:#cfe9da}.step.done span{background:#1fa45c;color:#fff;border-color:#1fa45c}.step.done b{color:#17894a}.progressLarge{height:8px;border-radius:99px;background:#e8edf3;overflow:hidden}.progressLarge>div{height:100%;background:linear-gradient(90deg,#377ef0,#54a5f2);border-radius:99px;transition:width .25s}.progressMeta{display:flex;justify-content:space-between;gap:7px;margin-top:5px;color:#8090a2;font-size:7px}.learnFacts{margin-top:8px}.trainGrid{display:grid;grid-template-columns:1fr 1.18fr;gap:10px}.dropZone{min-height:250px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;border-style:dashed;border-width:2px;cursor:pointer;transition:.15s}.dropZone:hover,.dropZone.dragging{border-color:#4a87ec;background:#f6faff}.dropIcon{width:58px;height:58px;border-radius:15px;background:#ebf3ff;color:#3b79e7;display:grid;place-items:center}.dropZone h3{margin:12px 0 4px;color:#294c6d;font-size:13px}.dropZone p{margin:0;color:#8d9aad;font-size:8px}.dropAction{display:flex;align-items:center;gap:5px;margin-top:13px;padding:8px 11px;background:#eff5ff;color:#3a74cf;border-radius:8px;font-size:8px}.dropZone small{max-width:360px;margin-top:11px;color:#9aa7b5;font-size:7px;line-height:1.6}.pipelineCard{min-width:0}.trainStats{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}.statCard{display:flex;gap:8px;align-items:center;border:1px solid #dbe5ef;border-radius:9px;background:#fff;padding:10px}.statIcon{width:32px;height:32px;border-radius:8px;background:#eef4ff;color:#3e78db;display:grid;place-items:center;flex:none}.statCard span{display:block;color:#8a98aa;font-size:7px}.statCard b{display:block;color:#1f4263;font-size:13px;margin-top:1px}.statCard small{display:block;color:#a0abb8;font-size:6px;margin-top:2px}.sectionHead{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}.sectionHead h3{margin:0;color:#254766;font-size:11px}.sectionHead p{margin:4px 0 0;color:#909cab;font-size:7px}.countPill,.statusBadge{display:inline-flex;align-items:center;padding:4px 7px;border-radius:999px;font-size:7px}.countPill{background:#edf4ff;color:#3973cf}.statusBadge{background:#f0f3f6;color:#75859a}.statusBadge.active{background:#eaf9f0;color:#14884a}.statusBadge.candidate{background:#edf4ff;color:#2f6fd3}.statusBadge.archived{background:#f1f2f5;color:#748296}.versionBadge{min-width:49px;height:33px;display:grid;place-items:center;border-radius:8px;background:#edf4ff;color:#2e6fd6;font-weight:700;font-size:10px}.versionRow.active .versionBadge{background:#e8f8ef;color:#168a43}.versionPath{max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#95a1ae;font-size:7px}.eventLog{max-height:220px;overflow:auto}.eventLine{display:grid;grid-template-columns:58px 68px 1fr;gap:6px;padding:6px 0;border-top:1px solid #edf1f5}.eventLine span,.eventLine b,.eventLine small{font-size:7px}.eventLine span{color:#9aa7b5}.eventLine b{color:#3a70aa}.eventLine small{color:#657c94;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.modelRow{padding:10px 0}.modelRow .softBtn,.modelRow .primaryBtn{margin-right:3px}.compact{min-height:70px}.fullTerminal{display:flex;flex-direction:column;min-height:0;flex:1;padding:0;overflow:hidden}.terminalHeader{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 10px;border-bottom:1px solid #dbe5ef}.terminalHeader div{display:flex;align-items:center;gap:6px;color:#345a7c;font-size:9px}.terminalHeader code{max-width:50%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#8494a6;font-size:7px}.terminalHost{flex:1;min-height:450px;padding:10px;background:#071220}.terminal{width:100%;height:100%}.autoToggle{display:flex;align-items:center;gap:6px;padding:8px 10px;border:1px solid #d6e2ef;background:#f8fbff;border-radius:8px;color:#315579;font-size:8px}.toast{position:fixed;left:50%;bottom:44px;transform:translateX(-50%);display:flex;align-items:center;gap:7px;padding:9px 12px;border:1px solid #cfe0f3;background:#fff;color:#2b567a;border-radius:8px;box-shadow:0 10px 28px rgba(20,52,91,.14);font-size:9px;z-index:50}.bottom{height:28px;display:flex;align-items:center;gap:16px;padding:0 12px;border-top:1px solid #dbe5ef;background:#fff;color:#7f8da1;font-size:7px;flex:none}.bottom i{display:inline-block;width:6px;height:6px;border-radius:50%;background:#c1cad5;margin-left:4px}
@media(max-width:1300px){.content{grid-template-columns:230px minmax(480px,1fr) 305px}.topbar{grid-template-columns:260px 1fr 390px}.selectBox{min-width:155px}.rightbar{font-size:90%}.trainStats{grid-template-columns:repeat(2,1fr)}}
@media(max-width:1060px){.rightbar{display:none}.content{grid-template-columns:215px 1fr}.topbar{grid-template-columns:245px 1fr 260px}.machineDevice{display:none}.topControls{justify-content:flex-start}.selectBox{min-width:145px}.twoCards,.searchColumns,.trainGrid{grid-template-columns:1fr}.settingsGrid{grid-template-columns:1fr}.fileWorkspace{grid-template-columns:215px 1fr}}
.composerMain{display:flex;align-items:center;gap:7px;flex:1;min-width:0}.attachmentChip{display:flex;align-items:center;gap:5px;padding:4px 7px;border:1px solid #d4e3f4;background:#f3f8ff;color:#3a6ca5;border-radius:999px;font-size:7px;max-width:220px}.attachmentChip button{border:0;background:transparent;color:#728aa4;display:grid;place-items:center;padding:0}


.trainingTelemetry .sectionHead p{margin:4px 0 0;color:var(--muted,#7a8797);font-size:12px}.telemetryGrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:12px}.telemetryGrid .infoRow{background:rgba(255,255,255,.55);border:1px solid rgba(30,50,80,.07);border-radius:12px;padding:10px}.completionBanner{display:flex;align-items:flex-start;gap:10px;margin-top:14px;padding:12px 14px;border-radius:12px;border:1px solid rgba(30,50,80,.08);background:rgba(246,249,253,.9)}.completionBanner.ready{border-color:rgba(35,175,110,.25);background:rgba(235,250,243,.75)}.completionBanner.failed{border-color:rgba(205,60,60,.25);background:rgba(255,242,242,.85)}.completionBanner b{display:block;font-size:13px}.completionBanner small{display:block;color:var(--muted,#7a8797);margin-top:3px}.eventLine{display:grid;grid-template-columns:76px 88px 1fr;gap:8px;align-items:center}.eventLine small{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}@media (max-width:1200px){.telemetryGrid{grid-template-columns:repeat(2,minmax(0,1fr))}}
.trainingTelemetry{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin-top:10px}
.trainingTelemetry>div{border:1px solid #e4ebf3;border-radius:7px;background:#fbfdff;padding:7px;min-width:0}
.trainingTelemetry span{display:block;color:#8b9aad;font-size:7px}
.trainingTelemetry b{display:block;color:#285071;font-size:9px;margin-top:3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.disabledDrop{opacity:.8;cursor:wait}
.errorNotice{background:#fff4f4;border-color:#efcccc}
.errorNotice svg{color:#b53e3e}
.errorNotice b{color:#9e3333}
@media(max-width:1200px){.trainingTelemetry{grid-template-columns:repeat(2,1fr)}}

.sessionBar{position:relative;display:flex;align-items:center;gap:8px;padding:8px 2px 10px}.sessionMeta{margin-inline-start:auto;font-size:12px;color:#718096}.historyMenu{position:absolute;z-index:30;top:48px;right:0;width:360px;max-height:360px;overflow:auto;padding:8px;border:1px solid #d8e2f0;border-radius:14px;background:#fff;box-shadow:0 18px 50px rgba(26,54,93,.16)}.historyMenu button{display:flex;width:100%;gap:8px;align-items:center;text-align:right;border:0;background:transparent;padding:10px;border-radius:10px;color:#20344d}.historyMenu button:hover{background:#f3f7fc}.trainingTelemetry{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}.trainingTelemetry>div{border:1px solid #e5edf7;border-radius:10px;padding:8px;background:#fbfdff}.trainingTelemetry span{display:block;font-size:11px;color:#718096}.trainingTelemetry b{display:block;margin-top:3px;font-size:13px;color:#20344d}.liveTrain{white-space:nowrap}.pulseDot{display:inline-block;width:7px;height:7px;border-radius:50%;background:#16a34a;box-shadow:0 0 0 4px rgba(22,163,74,.12)}
@media (max-width:1300px){.trainingTelemetry{grid-template-columns:repeat(4,minmax(0,1fr))}}

.historyItem{display:flex;align-items:center;gap:4px}.historyOpen{display:flex;align-items:center;gap:8px;flex:1;text-align:right!important}.historyAction{width:28px!important;height:28px!important;padding:0!important;border:0;background:transparent;color:#6b7b90;border-radius:8px}.historyAction:hover{background:#eef4fb}.historyAction.danger:hover{color:#dc2626;background:#fef2f2}

/* Professional conversation rendering */
.chatArea{scroll-behavior:smooth}
.messageRow{margin:16px 0;align-items:flex-start}
.messageRow.assistant .bubble{max-width:min(92%,940px);padding:13px 15px;border-radius:16px;box-shadow:0 5px 18px rgba(24,58,96,.06)}
.messageRow.user .bubble{max-width:min(84%,760px);padding:12px 14px;border-radius:16px}
.bubbleHead{min-height:22px;margin-bottom:8px}
.bubbleHead b{font-size:11px}.bubbleHead span{font-size:8px}.bubbleHead em{display:inline-flex;align-items:center;gap:4px}
.webMode{background:#eef8ff!important;color:#1769aa!important;border:1px solid #cfe8f7}
.bubbleText{font-size:14px;line-height:1.9;color:#20374f;white-space:normal;word-break:normal;overflow-wrap:anywhere;unicode-bidi:plaintext;direction:auto}
.messageRow.user .bubbleText{font-size:13px;line-height:1.8}
.richMessage{max-width:100%}.mdPara{margin:0 0 10px;white-space:pre-wrap}.mdPara:last-child{margin-bottom:0}
.mdSpacer{height:4px}.mdH{margin:14px 0 7px;color:#163e69;line-height:1.35}.mdH1{font-size:20px}.mdH2{font-size:17px}.mdH3{font-size:15px}.mdH4{font-size:14px}
.richMessage strong{font-weight:750;color:#173e67}.richMessage a{color:#2b6ed5;text-decoration:none;border-bottom:1px dotted #a9c6ee}.richMessage a:hover{color:#1854af}
.mdList{margin:6px 0 12px;padding-inline-start:22px}.mdList li{margin:4px 0;padding-inline-start:2px}.mdList ol{margin:0}
.inlineCode{display:inline-block;padding:1px 5px;border-radius:5px;background:#f2f5f9;border:1px solid #e0e7ef;color:#7b2fa2;font-family:Consolas,"Courier New",monospace;font-size:.9em;direction:ltr;unicode-bidi:isolate}
.codeBlock{margin:12px 0;border:1px solid #d7e1eb;border-radius:11px;overflow:hidden;background:#091521;direction:ltr}.codeHeader{display:flex;align-items:center;justify-content:space-between;padding:7px 9px;background:#0e1f30;border-bottom:1px solid rgba(255,255,255,.08);color:#9eb5ca;font-size:8px}.codeHeader button{display:inline-flex;align-items:center;gap:4px;border:1px solid rgba(255,255,255,.12);background:transparent;color:#c8d7e6;border-radius:6px;padding:4px 7px;font-size:8px}.codeHeader button:hover{background:rgba(255,255,255,.07)}.codeBlock pre{margin:0;padding:13px;overflow:auto;color:#e8f1f8;font:12px/1.65 Consolas,"Courier New",monospace;white-space:pre}
.workingTrace{margin:0 0 11px;padding:9px 10px;border:1px solid #dce9f7;border-radius:11px;background:linear-gradient(180deg,#f8fbff,#f4f8fd)}
.workingHead{display:flex;align-items:center;gap:6px;color:#3e6f9d}.workingHead svg{color:#4d82dc}.workingHead b{font-size:10px}.workingHead span{margin-inline-start:auto;font-size:7px;color:#8a9aac}
.traceSteps{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}.traceStep{display:flex;align-items:center;gap:4px;min-height:25px;padding:4px 7px;border:1px solid #dce6f0;background:#fff;border-radius:999px;color:#8492a3}.traceStep b{font-size:7px;font-weight:600}.traceStep small{max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:7px;color:#8e9bab}.traceIcon{width:16px;height:16px;border-radius:50%;display:grid;place-items:center;border:1px solid #d7e1ec;font-size:7px}.traceStep.completed{border-color:#cfe9da;background:#f1faf4;color:#19864b}.traceStep.completed .traceIcon{background:#20a75e;color:white;border-color:#20a75e}.traceStep.running{border-color:#cfe0fb;background:#f2f7ff;color:#2e6fd0}.traceStep.running .traceIcon{color:#2e6fd0}.traceStep.failed{border-color:#efcccc;background:#fff4f4;color:#a33b3b}
.webSources{margin-top:10px;border-top:1px solid #e8eef5;padding-top:10px}.webSourcesHead{display:flex;align-items:center;gap:6px;color:#2c5f88}.webSourcesHead svg{color:#3b79d9}.webSourcesHead b{font-size:9px}.webSourcesHead span{margin-inline-start:auto;font-size:7px;color:#8898aa}.webSourceGrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:7px;margin-top:7px}.webSource{display:block;text-align:right;border:1px solid #dce8f2;border-radius:9px;padding:8px;background:#fbfdff;color:#2c4863}.webSource:hover{background:#f3f8ff;border-color:#bcd5f0;transform:translateY(-1px)}.webSourceTop{display:flex;align-items:center;gap:5px}.webSourceTop b{font-size:8px;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.webSourceTop>svg{color:#4a7bd7}.webSource small{display:block;margin-top:5px;color:#7c8ea2;font-size:7px;line-height:1.5;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}.webSource em{display:block;margin-top:5px;color:#4b8bc2;font-size:6px;font-style:normal}.webIndex{display:inline-grid;place-items:center;width:17px;height:17px;border-radius:5px;background:#edf4ff;color:#2e6fd0;font-size:7px;flex:none}
.messageActions button{width:30px;height:27px}.typing{margin-right:44px;padding:9px 11px;font-size:9px}.typing span{width:5px;height:5px}
.errorNotice{direction:rtl}
@media(max-width:850px){.messageRow.assistant .bubble,.messageRow.user .bubble{max-width:94%}.bubbleText{font-size:13px}.webSourceGrid{grid-template-columns:1fr}.workingHead span{display:none}}
.improvementRow{display:flex;align-items:flex-start;gap:10px;padding:12px 0;border-top:1px solid #edf1f5}.improvementRow .rowIcon{background:#fff2f2;color:#b53d3d}.improvementRow b{display:block;color:#2a4965;font-size:10px}.improvementRow small{display:block;color:#7f90a4;font-size:8px;margin-top:3px}.improvementRow p{margin:6px 0;color:#40586f;font-size:9px;line-height:1.6;white-space:pre-wrap;overflow-wrap:anywhere}.improvementRow code{font-size:7px;color:#9a6b39}.correctionList{display:flex;flex-direction:column}.correctionRow{padding:12px 0;border-top:1px solid #edf1f5}.correctionHead{display:flex;justify-content:space-between;align-items:center}.correctionHead span{display:inline-flex;align-items:center;gap:4px;color:#16894a;font-size:8px}.correctionHead code{font-size:7px;color:#96a4b4}.correctionQ,.correctionA{margin-top:8px;padding:8px 10px;border-radius:8px}.correctionQ{background:#f5f8fc}.correctionA{background:#eefaf3;border:1px solid #d5ebdc}.correctionQ b,.correctionA b{font-size:8px;color:#58718a}.correctionQ p,.correctionA p{margin:3px 0 0;font-size:9px;line-height:1.6;color:#34536f;white-space:pre-wrap;overflow-wrap:anywhere}

/* 4.6 conversation polish */
.messageRow.user{justify-content:flex-end}.messageRow.assistant{justify-content:flex-start}.messageRow.user .bubble{order:1}.messageRow.user .userAvatar{order:2}
.mdTableWrap{overflow:auto;margin:8px 0 12px;border:1px solid #dde7f1;border-radius:10px;background:#fff}.mdTable{width:100%;border-collapse:collapse;min-width:420px;font-size:12px}.mdTable th,.mdTable td{padding:7px 9px;border-bottom:1px solid #e8eef5;vertical-align:top;text-align:right}.mdTable th{background:#f4f8fd;color:#244f76;font-weight:750}.mdTable tr:last-child td{border-bottom:0}.mdQuote{margin:8px 0 11px;padding:8px 11px;border-inline-start:3px solid #78a6dc;background:#f7faff;color:#56708b;border-radius:7px;white-space:pre-wrap}.sendButton.stopMode{background:#c84b55}.sendButton.stopMode:hover{background:#b93b45}.bubble.isStreaming .bubbleHead:after{content:'جارٍ التوليد';margin-inline-start:auto;font-size:7px;color:#4a7fc0;background:#eef5ff;border-radius:999px;padding:3px 6px}.messageRow.assistant .bubble{direction:rtl;text-align:start}.messageRow.user .bubble{direction:rtl;text-align:start}


/* ============================================================
   ALI 4.6 Professional UI foundation
   Direction-safe Arabic + isolated code / paths / identifiers.
   ============================================================ */
html, body, #root { direction: rtl; }
html, body { background: #eef3f8; }
body, button, input, textarea, select { -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility; }
input, textarea, .bubbleText, .mdPara, .mdQuote, .listRow, .convRow, .noticeCard, .errorBox, .infoRow { unicode-bidi: plaintext; }
textarea, .bubbleText, .mdPara, .mdQuote, .noticeCard, .errorBox { direction: auto; }
textarea { writing-mode: horizontal-tb; text-orientation: mixed; }
.inlineCode, .codeBlock, .codeBlock pre, code, .terminalHost { direction: ltr; unicode-bidi: isolate; }
.bubbleText { overflow-wrap: anywhere; word-break: normal; }
.messageRow .bubble { min-width: 0; }
.messageRow.user .bubbleText, .messageRow.assistant .bubbleText { text-align: start; }

/* Accessibility & polish */
button:focus-visible, input:focus-visible, textarea:focus-visible, select:focus-visible { outline: 2px solid rgba(57,125,240,.55); outline-offset: 2px; }
.navItem, .tab, .quickRow button, .webSource, .messageActions button, .primaryBtn, .softBtn, .dangerBtn { transition: transform .16s ease, box-shadow .16s ease, background .16s ease, border-color .16s ease, color .16s ease; }
.primaryBtn:hover:not(:disabled), .softBtn:hover:not(:disabled) { transform: translateY(-1px); }
.messageRow.assistant .bubble { animation: aliFadeIn .22s ease both; }
@keyframes aliFadeIn { from { opacity: .55; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

/* ============================================================
   DESIGN 4 — ADAPTIVE HYBRID
   Layered glass workspace + focused conversation canvas.
   ============================================================ */
html[data-ali-design="design4"] body { background:#dfe8f3; }
html[data-ali-design="design4"] .appShell {
  background:
    radial-gradient(850px 520px at 14% 12%, rgba(92,161,235,.30), transparent 65%),
    radial-gradient(780px 500px at 82% 86%, rgba(108,207,190,.24), transparent 65%),
    linear-gradient(145deg,#e9f0f7 0%,#dce7f2 52%,#e8edf5 100%);
}
html[data-ali-design="design4"] .topbar {
  height:76px; grid-template-columns:300px minmax(460px,1fr) 380px;
  background:rgba(255,255,255,.62); border-bottom:1px solid rgba(255,255,255,.7);
  box-shadow:0 12px 35px rgba(53,81,112,.08); backdrop-filter:blur(22px) saturate(140%);
}
html[data-ali-design="design4"] .content { grid-template-columns:260px minmax(600px,1fr) 350px; gap:10px; padding:10px; }
html[data-ali-design="design4"] .leftbar,
html[data-ali-design="design4"] .rightbar,
html[data-ali-design="design4"] .centerPanel {
  border:1px solid rgba(255,255,255,.78); border-radius:20px; overflow:hidden;
  background:rgba(255,255,255,.56); box-shadow:0 18px 44px rgba(47,74,104,.10); backdrop-filter:blur(18px) saturate(145%);
}
html[data-ali-design="design4"] .leftbar,html[data-ali-design="design4"] .rightbar { padding:10px; }
html[data-ali-design="design4"] .navItem { border-radius:14px; padding:11px 12px; }
html[data-ali-design="design4"] .navItem.active { background:rgba(71,132,225,.13); border-color:rgba(71,132,225,.26); box-shadow:inset -3px 0 0 #4a87e8, 0 8px 20px rgba(76,132,205,.10); }
html[data-ali-design="design4"] .deviceCard,
html[data-ali-design="design4"] .systemCard,
html[data-ali-design="design4"] .sysCard,
html[data-ali-design="design4"] .tableCard,
html[data-ali-design="design4"] .formCard,
html[data-ali-design="design4"] .statCard,
html[data-ali-design="design4"] .terminalCard,
html[data-ali-design="design4"] .settingsGrid .settingCard,
html[data-ali-design="design4"] .noticeCard {
  background:rgba(255,255,255,.70); border-color:rgba(210,222,234,.85); border-radius:16px;
  box-shadow:0 10px 28px rgba(58,84,111,.07);
}
html[data-ali-design="design4"] .tabbar { height:48px; padding:0 16px; background:rgba(255,255,255,.55); border-color:rgba(216,227,238,.9); }
html[data-ali-design="design4"] .chatArea { padding:25px 26px 18px; background:linear-gradient(180deg,rgba(247,250,253,.40),rgba(237,244,250,.32)); }
html[data-ali-design="design4"] .welcome { padding-top:50px; }
html[data-ali-design="design4"] .welcome .logo { width:84px;height:84px; filter:drop-shadow(0 12px 22px rgba(49,109,195,.22)); }
html[data-ali-design="design4"] .welcome h1 { font-size:28px; color:#173c63; }
html[data-ali-design="design4"] .welcome p { font-size:11px; }
html[data-ali-design="design4"] .quickRow button { background:rgba(255,255,255,.66); border-color:rgba(207,220,234,.95); box-shadow:0 5px 16px rgba(63,92,122,.05); }
html[data-ali-design="design4"] .messageRow.assistant .bubble,
html[data-ali-design="design4"] .messageRow.user .bubble { border-radius:19px; backdrop-filter:blur(12px); }
html[data-ali-design="design4"] .messageRow.assistant .bubble { background:rgba(255,255,255,.80); border-color:rgba(213,225,237,.95); box-shadow:0 12px 34px rgba(54,81,109,.08); }
html[data-ali-design="design4"] .messageRow.user .bubble { background:rgba(229,240,255,.78); border-color:rgba(184,211,242,.95); }
html[data-ali-design="design4"] .workingTrace { background:rgba(247,251,255,.72); backdrop-filter:blur(8px); }
html[data-ali-design="design4"] .composer { margin:0 12px 12px; padding:11px; border:1px solid rgba(255,255,255,.82); border-radius:18px; background:rgba(255,255,255,.62); box-shadow:0 15px 35px rgba(45,74,104,.10); backdrop-filter:blur(18px); }
html[data-ali-design="design4"] .composerMain { border-radius:15px; background:rgba(255,255,255,.76); border-color:#d4e0eb; }
html[data-ali-design="design4"] .sendButton { border-radius:14px; width:48px; height:48px; }
html[data-ali-design="design4"] .bottom { margin:0 10px 8px; border:1px solid rgba(255,255,255,.76); border-radius:12px; background:rgba(255,255,255,.56); }
html[data-ali-design="design4"] .page { padding:16px; }
```

---

### `492/588` `desktop/vite.config.js`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\desktop/vite.config.js`
- **الحجم:** 182 بايت (0.2 KB)
- **الامتداد:** `.js`

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({ plugins:[react()], base:'./', build:{outDir:'dist',emptyOutDir:true} });
```

---

### `493/588` `FINAL_ARTIFACT_HASHES_4.5.8.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\FINAL_ARTIFACT_HASHES_4.5.8.json`
- **الحجم:** 2414 بايت (2.4 KB)
- **الامتداد:** `.json`

```json
{
  "release": "4.5.8",
  "artifacts": {
    "backend/models/active/ALI-v1/model.safetensors": {
      "sha256": "50b9c5ec66a1cd19035d93f969c412cc7fc87922e03b0a557d5d565ab5123eca",
      "size_bytes": 14435744
    },
    "backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/checkpoint.pt": {
      "sha256": "67d6d4297242854e8268b32dd775372eb5c02e70144ee5132b89492fececa5d0",
      "size_bytes": 16216409
    },
    "backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/internal_model.safetensors": {
      "sha256": "b8ce83adb606742998ad7841ecd5905239b0d52831ce0bc9a4aa998362ae024c",
      "size_bytes": 15006408
    },
    "backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/adapter_model.safetensors": {
      "sha256": "66430925b5f6d6f270a9def44ea52fb90adca14381186dbbb031b5078f4e8938",
      "size_bytes": 570696
    },
    "backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/adapter/adapter_model.safetensors": {
      "sha256": "66430925b5f6d6f270a9def44ea52fb90adca14381186dbbb031b5078f4e8938",
      "size_bytes": 570696
    },
    "backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/merged_hf/model.safetensors": {
      "sha256": "50b9c5ec66a1cd19035d93f969c412cc7fc87922e03b0a557d5d565ab5123eca",
      "size_bytes": 14435744
    },
    "backend/data/training/testdata/ALI_User_Understanding_Bundle_V4.md": {
      "sha256": "371d2e0de7e109848ee8246801e4de80e1f339a9d3be9d0f5add36bc241087bb",
      "size_bytes": 1007239
    },
    "backend/runtime_knowledge.sqlite3": {
      "sha256": "f7b81746c8b131437904890c108548fb6205fd06111c4b9b334297c6cd914988",
      "size_bytes": 6262784
    },
    "backend/models/models.sqlite3": {
      "sha256": "30495891e486d6bd699ffd4b2958913c6099d1ef9a41233da225b41e61017773",
      "size_bytes": 12288
    },
    "PROJECT_MANIFEST.json": {
      "sha256": "44f462b625e25e48bce2a5d50958e15251d4a182bc3f8e76a85224f3f55a6ca0",
      "size_bytes": 3284
    },
    "PROJECT_VERSION.json": {
      "sha256": "08ad87c563a12a01fabd4c7a4b5e43a0b596a96038cb7e3da73f8d79ba9eb283",
      "size_bytes": 763
    }
  },
  "knowledge_db": {
    "trained_bundle_docs": 1,
    "training_qa_chunks": 215,
    "absolute_paths": 0
  },
  "verification": {
    "pytest": "242 passed, 34 skipped, 2 warnings",
    "release_audit": "PASS",
    "api_quiz": "216/216"
  }
}
```

---

### `494/588` `FINAL_BUILD_GUIDE_4.2.0.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\FINAL_BUILD_GUIDE_4.2.0.md`
- **الحجم:** 347 بايت (0.3 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.2.0 — Windows Final Build Guide

## 1. Required host tools

Use a Windows 10/11 x64 build host with:

- Node.js 22.x + npm
- .NET 8 SDK
- Python 3.11.9 only for preparing the embedded runtime, not for end users
- Git
- Visual Studio Build Tools / native toolchain needed by node-pty and PyTorch wheels

## 2. Prepare Electron
```

---

### `495/588` `FINAL_CONTINUATION_REPORT_4.5.3.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\FINAL_CONTINUATION_REPORT_4.5.3.md`
- **الحجم:** 1163 بايت (1.1 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.3 — تقرير الاستكمال

هذه النسخة تكمل العمل من 4.5.2. الإصلاحات الأساسية تركزت على:

1. جعل المعرفة العربية الخاصة بجهاز المستخدم متاحة لـRAG بشكل مباشر.
2. جعل البحث المحلي أكثر تحملاً للصياغات العربية مثل «ما هو معالج جهازي؟».
3. إزالة الاعتماد الصلب على المنفذ 8765 في Electron؛ يختار التطبيق منفذاً محلياً متاحاً ويربطه بالواجهة تلقائياً.
4. إضافة اختبار انشغال المنفذ واختبار استرجاع مواصفات P50 بالعربية.
5. الحفاظ على سياسة GPU الحالية: CUDA تُستخدم فقط بعد self-test حقيقي، ومع 2GB VRAM لا يفترض ALI أن كامل الذاكرة متاحة.

## الحالة
- Python static checks: PASS
- pytest: يجب تشغيل الاختبارات الكاملة بعد هذه الإضافات على بيئة الإصدار النظيفة.
- Windows native gates: غير منفذة هنا.
```

---

### `496/588` `FINAL_CONTINUATION_REPORT_4.5.6.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\FINAL_CONTINUATION_REPORT_4.5.6.md`
- **الحجم:** 1666 بايت (1.6 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.6 — Continuation Report

This release continues the previous 4.5.x line and closes the code-level issues verified in the available environment.

## Source findings carried forward
The previous report documented that 4.4.0 still had a 30MB bootstrap model with 0/8 model-only tests, only 1,566 unique generated samples, unreliable GPU detection, a memory endpoint mismatch, incomplete Vite dist, and Windows-specific tests that were skipped. This release treats those as release gates rather than silently declaring them complete.

## Changes completed
- Version coherence and clean runtime seed.
- Grounded local QA with authoritative precedence over stale conversation memory.
- Arabic explicit tool routing for safe commands.
- GGUF bridge contract: `-ngl`, correct completion text, SSE streaming, preferred/fallback port.
- Windows release gate and dependency manifest.
- Full user/device knowledge seed for the target ThinkPad P50.
- Continuous learning retained as `vN` with validation, evaluation, promotion and rollback.

## Verification
- Backend compile: PASS
- Backend tests: **171 passed, 34 skipped, 2 warnings**
- Final release audit: PASS
- API E2E smoke: PASS
- Grounded Arabic Q&A smoke: PASS
- Real isolated LoRA smoke: PASS (`v2`, then cumulative `v3`)

## Windows production gate
The package is source-complete and build-ready, but the final native Windows release requires a Windows host to install/build Electron dependencies, publish the self-contained .NET launcher, assemble Embedded CPython 3.11.9, rebuild `node-pty` for Windows, execute the real CUDA test on the Quadro M1000M and run the final llama.cpp/GGUF path.
```

---

### `497/588` `FINAL_CONTINUATION_REPORT_4.5.8.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\FINAL_CONTINUATION_REPORT_4.5.8.md`
- **الحجم:** 822 بايت (0.8 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.8 — Continuation Report

تمت متابعة إصدار 4.5.7 إلى حزمة كاملة 4.5.8 تضم الأوزان الناتجة من آخر دورة تدريبية بدلاً من تركها خارج المشروع. تم جعل `ALI-v1` هو الـActive model في registry، مع الإبقاء على `ALI-Bootstrap-v2.5` كخيار احتياطي. كما تم تجهيز `runtime_knowledge.sqlite3` مسبقاً ببيانات الحزمة، وإضافة seeding تلقائي عند بدء backend لضمان إعادة بناء المعرفة حتى بعد إنشاء قاعدة جديدة.

النتيجة الحالية: 242 اختباراً ناجحاً و34 متجاوزاً بسبب قيود البيئة، مع اختبار API فعلي على 216 سؤالاً نجح بالكامل.
```

---

### `498/588` `FINAL_E2E_USER_BUNDLE_SUMMARY_4.5.7.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\FINAL_E2E_USER_BUNDLE_SUMMARY_4.5.7.md`
- **الحجم:** 722 بايت (0.7 KB)
- **الامتداد:** `.md`

```markdown
# ALI User Bundle V4 — E2E Validation Receipt

الملف المرفوع استُورد إلى نسخة نظيفة، نتج عنه 215 عينة فريدة من 216 قسم محادثة، ثم أُجري تدريب LoRA حقيقي ونتج v1 مع checkpoint وadapter وmerged HF weights. تم اختبار 216 سؤالاً: 216/216 ردًا من training_qa و216/216 مطابقاً لإحدى الإجابات المصدرية الصحيحة. إعادة الاستيراد أصبحت duplicate_source، وإعادة تحميل v1 عبر ModelManager نجحت.

الاختبارات النهائية للمشروع: 239 passed, 34 skipped, 2 warnings. GGUF وWindows native gates خارج بيئة Linux الحالية.
```

---

### `499/588` `FINAL_FILE_TRAINING_E2E_RECEIPT_4.5.8.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\FINAL_FILE_TRAINING_E2E_RECEIPT_4.5.8.json`
- **الحجم:** 4793 بايت (4.7 KB)
- **الامتداد:** `.json`

```json
{
  "release": "4.5.7",
  "fixture": "ALI_User_Understanding_Bundle_V4.md",
  "fixture_sha256": "371d2e0de7e109848ee8246801e4de80e1f339a9d3be9d0f5add36bc241087bb",
  "actual_conversation_headings": 216,
  "unique_samples": 215,
  "duplicate_exact_qa_samples": 1,
  "duplicate_question_groups": 3,
  "unique_questions": 213,
  "postfix_regression": {
    "relative_base_checkpoint_tokenizer_reuse": "fixed_and_passed",
    "tokenizer_long_input": "65 passed in 1.89s"
  },
  "import": {
    "status": "validated",
    "sample_count": 215,
    "routed_to_rag": true,
    "warnings": [
      "declared_conversation_count_mismatch:50!=216",
      "duplicate_samples_in_file:1"
    ]
  },
  "training": {
    "run_id": "continuous-v1-20261004-224649-e71dab",
    "generation": "v1",
    "status": "success",
    "base_version": "2.5.0-bootstrap-micro",
    "device": "cpu",
    "steps": 13,
    "samples_seen": 208,
    "tokens_seen": 26624,
    "last_loss": 7.509772777557373,
    "evaluation": {
      "loss": 6.771079858144124,
      "perplexity": 872.2532954340983,
      "samples": 60
    },
    "new_data_holdout": {
      "loss": 7.454573845863342,
      "perplexity": 1727.7475515931083,
      "samples": 20
    },
    "promoted_active": true,
    "tokenizer_lineage": {
      "reused_base_tokenizer": true,
      "base_tokenizer_sha256": "5c1ca7b2eb4a855452c133adbdc52d15306ee2dcdf2590cdf78102ba1c5a3d4b",
      "merged_tokenizer_sha256": "5c1ca7b2eb4a855452c133adbdc52d15306ee2dcdf2590cdf78102ba1c5a3d4b"
    }
  },
  "quiz": {
    "questions": 216,
    "unique_questions": 213,
    "training_qa_mode": 216,
    "source_answer_match": 216,
    "failures": 0
  },
  "streaming": {
    "mode": "training_qa",
    "exact_answer": true
  },
  "reimport": {
    "status": "duplicate",
    "reason": "duplicate_source"
  },
  "model_manager_reload": {
    "pass": true,
    "version": "v1",
    "engine": "LocalInference"
  },
  "artifacts": {
    "checkpoint_pt": "backend/models/runs/20261004-224649-233144/checkpoints/final-000013",
    "internal_model_safetensors": "backend/models/runs/20261004-224649-233144/checkpoints/final-000013/model.safetensors",
    "adapter_safetensors": "backend/models/runs/20261004-224649-233144/checkpoints/final-000013/adapter/adapter_model.safetensors",
    "merged_model_safetensors": "backend/models/runs/20261004-224649-233144/checkpoints/final-000013/merged_hf/model.safetensors"
  },
  "artifact_hashes": {
    "checkpoint.pt": {
      "size_bytes": 16216409,
      "sha256": "67d6d4297242854e8268b32dd775372eb5c02e70144ee5132b89492fececa5d0"
    },
    "model.safetensors": {
      "size_bytes": 15006408,
      "sha256": "b8ce83adb606742998ad7841ecd5905239b0d52831ce0bc9a4aa998362ae024c"
    },
    "adapter_model.safetensors": {
      "size_bytes": 570696,
      "sha256": "66430925b5f6d6f270a9def44ea52fb90adca14381186dbbb031b5078f4e8938"
    },
    "merged_model.safetensors": {
      "size_bytes": 14435744,
      "sha256": "50b9c5ec66a1cd19035d93f969c412cc7fc87922e03b0a557d5d565ab5123eca"
    },
    "checkpoint_pt": {
      "size_bytes": 16216409,
      "sha256": "67d6d4297242854e8268b32dd775372eb5c02e70144ee5132b89492fececa5d0"
    },
    "internal_model_safetensors": {
      "size_bytes": 15006408,
      "sha256": "b8ce83adb606742998ad7841ecd5905239b0d52831ce0bc9a4aa998362ae024c"
    },
    "adapter_safetensors": {
      "size_bytes": 570696,
      "sha256": "66430925b5f6d6f270a9def44ea52fb90adca14381186dbbb031b5078f4e8938"
    },
    "merged_model_safetensors": {
      "size_bytes": 14435744,
      "sha256": "50b9c5ec66a1cd19035d93f969c412cc7fc87922e03b0a557d5d565ab5123eca"
    }
  },
  "merge_equivalence": {
    "logit_max_diff": 0.016632080078125,
    "logit_mean_diff": 0.0008416299242526293,
    "weight_formula_max_diff": 0.0,
    "weight_disk_max_diff": 0.0,
    "argmax_equal": true,
    "pass": true,
    "logit_note": "Logit difference is due to float32 operation-order associativity; the stored merged Q projection weight exactly equals base + B@A*scale (max diff 0.0), and the serialized merged weight equals the in-memory merged weight (max diff 0.0)."
  },
  "gguf": {
    "status": "pending_converter",
    "reason": "No Windows llama.cpp converter/quantizer is bundled or executable in this Linux container."
  },
  "native_windows": {
    "electron_net_conpty_cuda": "not executed in Linux container"
  },
  "initial_bug_fixed": {
    "description": "Relative base-checkpoint paths were resolved from process CWD during continuation-tokenizer lookup, causing tokenizer retraining and a possible embedding index mismatch. The lookup is now anchored to the pipeline root and covered by regression tests."
  },
  "test_suite": {
    "pytest": "239 passed, 34 skipped, 2 warnings",
    "release_audit": "PASS"
  }
}
```

---

### `500/588` `FINAL_PROJECT_STATUS_4.6.0.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\FINAL_PROJECT_STATUS_4.6.0.md`
- **الحجم:** 2293 بايت (2.2 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.6.0 — Final Project Status

## Delivered architecture

- Cumulative generation pipeline: V1 → V2 → V3 → V4 → future V5/V6.
- Each new generation uses the active parent plus a verified cumulative dataset and new delta.
- Old generations remain archive/rollback artifacts and are not inference dependencies.
- Persistent error-learning store: incidents are captured; only explicitly approved corrections become training data.
- Web research is integrated into the normal chat pipeline and displayed inside the same assistant message, with source cards.
- Safe execution trace shows route/analyze/retrieve/web/generate/verify stages without exposing private chain-of-thought.
- Rich Markdown/code/table/message rendering in the modern desktop renderer, plus improved Tk fallback bubbles.
- Portable generation package creation with checksums and manifests.
- Windows launcher performs setup, preflight, and lineage verification before launching.

## V4 current artifact

- Generation: v4
- Parent: v3
- Ancestors: v1, v2, v3
- Delta samples: 84
- Cumulative samples: 1532
- Cumulative hash: `90f96c89541770624c60f416a1ce02f42dc9557c11dd5e06737219f32878cdcd`
- Active HF model: `backend/models/active/ALI-v4`
- GGUF: pending Windows llama.cpp converter; no false-ready GGUF is claimed.

## Validation performed in the build environment

- Python compileall: PASS
- Backend tests: 246 passed, 34 skipped, 0 failed
- Generation lineage verifier for v4: PASS
- V4 runtime model load smoke test: PASS
- Future V5 cumulative dataset simulation: PASS

## Environment-specific limits

- Windows GUI/Electron packaging was not executable inside this Linux build environment. The project contains the Windows launcher and Electron source, but `desktop/node_modules` and a packaged Windows `.exe` are not bundled in this build because they must be installed/built on Windows.
- The source report included references to historical binary model/database artifacts that were not embedded in the markdown itself. They were not fabricated or silently reconstructed.
- Live public Internet fetches cannot be proven from this build environment; the application contains the in-chat web research implementation and will use DuckDuckGo/Bing when Internet access is available on Windows.
```

---

### `501/588` `FINAL_RELEASE_REPORT_4.5.6.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\FINAL_RELEASE_REPORT_4.5.6.md`
- **الحجم:** 2695 بايت (2.6 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.6 — Final Release Report

## What was corrected

1. Version identity was synchronized to 4.5.6 across the current project manifest, backend server, desktop package and UI status text while preserving the legacy foundation test contract.
2. The GGUF llama-server bridge now passes `-ngl`, returns actual completion text, supports streaming SSE, keeps a preferred port (48921) and automatically selects a free port when the preferred port is busy.
3. Verified local FAQ routing was placed ahead of conversation-memory matches so a stale previous answer cannot override a bundled verified fact.
4. Added high-confidence Arabic FAQ variants for project name, RAM, device, GPU/VRAM, architecture, training, conversations and cumulative learning.
5. Cleared runtime conversation/memory/audit/KCA databases from the release seed so the shipped package starts clean; bundled knowledge remains available.
6. Added a Windows-native release gate script and dependency manifest.

## Tests completed

- `python -m compileall -q backend`: PASS
- `pytest -q backend`: **171 passed, 34 skipped, 2 warnings**
- `scripts/FINAL_RELEASE_AUDIT.py`: PASS
- API smoke: `/api/health` + `/api/status` + grounded chat: PASS
- Grounded questions tested successfully for project name, RAM, VRAM, CPU and Memory/RAG/Training.
- Isolated real continuous-training smoke: imported a new Markdown source, created **v2**, promoted it, then imported another source and created cumulative **v3** with base version `v2`.

## Known release-host gates

These cannot be honestly marked PASS from the current Linux environment:

- Windows production Electron build and native `node-pty`/ConPTY.
- C#/.NET self-contained portable executable build.
- Real embedded CPython 3.11.9 Windows runtime plus all Windows wheels.
- CUDA kernel execution on the Quadro M1000M.
- llama.cpp Windows CPU/CUDA binaries and Qwen GGUF runtime.

The project includes the setup and verification scripts required to close these gates on the Windows target host.

## Model quality statement

The included `ALI-Bootstrap-v2.5` is a small local model. The project therefore uses deterministic local Q&A, RAG, Memory and tools to provide grounded behavior even when raw model generation is weak. A stronger GGUF model can be added through `SETUP_QWEN_LOCAL.bat` without changing the desktop architecture.


## Final smoke results

- API E2E: PASS
- Conversation create/list/detail/rename/delete: PASS
- `/api/memory/list` compatibility: PASS
- Arabic explicit read-file command: PASS
- Grounded FAQ precedence over stale memory: PASS
- Continuous learning isolated smoke: `v2` promoted, then `v3` promoted from `v2` with new source only.
```

---

### `502/588` `FINAL_RELEASE_REPORT_4.5.7.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\FINAL_RELEASE_REPORT_4.5.7.md`
- **الحجم:** 7707 بايت (7.5 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.7 — Final Verification Report

## النتيجة التنفيذية

تمت إعادة تنفيذ الاختبار على نسخة نظيفة من المشروع باستخدام **ملف التدريب الذي رفعته في هذه المحادثة نفسه**. الملف يعرّف في رأسه 50 محادثة و35 Train و8 Validation و7 Test، لكن محلل المشروع وجد فعلياً 216 قسم محادثة؛ كما أُخذت الازدواجية في الحسبان أثناء الاستيراد.  
تم تنفيذ المسار الفعلي: **استيراد → فحص/تكرار → فهرسة RAG → تدريب LoRA حقيقي بـ PyTorch → استخراج checkpoint وadapter → دمج الأوزان → إعادة تحميل النموذج → اختبار جميع أسئلة الملف → إعادة الاستيراد**.

## مشكلة اكتُشفت أثناء التحقق وأُصلحت

أثناء أول إعادة تشغيل بعد إصلاح أداء tokenizer ظهر خطأ `index out of range in self` أثناء التدريب. تم تتبع السبب إلى مسار نسبي لـ `base_checkpoint`: جزء اختيار tokenizer كان يحل المسار بالنسبة إلى مجلد تشغيل Python بدلاً من جذر المشروع. عندها كان يمكن أن يعيد النظام تدريب tokenizer جديد بدلاً من إعادة استخدام tokenizer النموذج الأساسي.

تم إصلاح المسار ليُحل دائماً بالنسبة إلى جذر `TrainingPipeline`، وأُضيف اختبار انحدار فعلي يغطي هذه الحالة. بعد الإصلاح اكتملت دورة التدريب الجديدة بنجاح.

## نتيجة ملف التدريب المرفوع

- رأس الملف يذكر: **50** محادثة، Train **35**، Validation **8**، Test **7**. 
- التحليل الفعلي: **216** قسم محادثة.
- العينات الفريدة بعد إزالة التكرار الدقيق: **215**.
- يوجد **تكرار Q/A مطابق واحد**.
- توجد **3 مجموعات أسئلة مكررة**؛ بعضها يملك إجابات مصدر مختلفة، ولذلك اعتبر الاختبار إحدى الإجابات المصدرية الصحيحة لكل سؤال.
- الأسئلة الفريدة نصياً: **213**.

## الاستيراد

الاستيراد الأول: **PASS**.

- `sample_count = 215`
- `routed_to_rag = true`
- تم قبول البيانات للتدريب.
- ظهرت التحذيرات المتوقعة فقط: اختلاف العدد المعلن عن العدد الفعلي، وتكرار Q/A واحد.
- إعادة استيراد الملف نفسه بعد نجاح العملية: **PASS** على مستوى الحماية من التكرار؛ النتيجة `duplicate_source` ولم تُنشأ دورة تدريب ثانية.

## التدريب الحقيقي وضبط الأوزان

تم تنفيذ تدريب LoRA فعلي باستخدام PyTorch على CPU داخل بيئة التحقق الحالية، وليس تدريباً وهمياً.

- الجيل: **v1**
- الأساس: `2.5.0-bootstrap-micro`
- الحالة: **SUCCESS / ACTIVE**
- خطوات التحسين: **13**
- Samples seen: **208**
- Tokens seen: **26,624**
- آخر loss: **7.50977**
- تقييم ثابت: loss **6.77108**، perplexity **872.2533**، samples **60**
- New-data holdout: loss **7.45457**، perplexity **1727.7476**، samples **20**

والأهم: تم التحقق من أن tokenizer في الجيل الجديد **أعيد استخدامه من النموذج الأساسي**، وليس إعادة تدريبه من ملف المستخدم. هذا يمنع اختلاف IDs عن embedding الخاص بالنموذج الأساسي.

## استخراج الأوزان

تم إنشاء ملفات فعلية قابلة لإعادة التحميل:

- `checkpoint.pt`
- `model.safetensors`
- `adapter/adapter_model.safetensors`
- `merged_hf/model.safetensors`
- `merged_hf/config.json`
- `merged_hf/tokenizer.model`
- ملفات manifest وmetadata

تمت إعادة تحميل `v1` بواسطة `ModelManager` بنجاح عبر `LocalInference`.

## التحقق من الدمج

تمت مقارنة مسار `base + LoRA` مع الأوزان المدمجة.

- فرق وزن طبقة LoRA بعد تنفيذ صيغة الدمج الصريحة `W + B@A*scale`: **0.0**.
- فرق الوزن المحفوظ على القرص عن الوزن المدمج في الذاكرة: **0.0**.
- تطابق Top-1 logits على المدخل الاختباري: **نعم**.
- وجود فرق صغير عند مقارنة logits الخام مباشرة (`max ≈ 0.0166`) سببه ترتيب عمليات float32 بين `(xA)B` و`x(AB)`؛ لذلك معيار الدمج الأساسي هنا هو تطابق Tensor الوزن نفسه، وقد كان **0.0**.

## اختبار البرنامج بأسئلة الملف

تم سؤال البرنامج بجميع أقسام المحادثات التي استخرجها محلل الاستيراد: **216 سؤالاً**.

- `training_qa` mode: **216/216**
- تطابق الرد مع إحدى الإجابات المصدرية الصحيحة: **216/216**
- حالات فشل: **0**
- Streaming لسؤال تمثيلي: **PASS**

هذا الاختبار يثبت أن ALI يستطيع بعد الاستيراد استخدام الـQ/A المرفوع مباشرة من مسار المعرفة المحلي الموثوق. ولا يعتمد في هذا الاختبار على جودة bootstrap-micro لتخمين الإجابة.

## الاختبارات البرمجية النهائية

- Python compile: **PASS**
- Node syntax: **PASS**
- JSON validation: **PASS**
- Version coherence: **PASS**
- Release Audit: **PASS**
- الاختبارات الكاملة: **239 passed, 34 skipped, 2 warnings**.

الـ34 skip تعود لاختبارات GUI/Desktop التي تتطلب بيئة سطح مكتب فعلية، إضافةً إلى حالات tokenizer/Tk التي لا تتوفر في بيئة Linux الحالية. لا توجد اختبارات فاشلة في المجموعة المنفذة هنا.

## GGUF

مسار التدريب والتصدير أصبح سليماً حتى الأوزان المدمجة، لكن **GGUF فعلي لم يُنتج داخل هذه البيئة** لعدم وجود converter/quantizer قابل للتنفيذ لـ `llama.cpp`. المشروع يسجل ذلك صراحةً كـ `pending_converter` بدلاً من إنشاء ملف وهمي.

## حدود تحقق Windows

لم يتم الادعاء بتشغيل Electron الإنتاجي و.NET/C# وConPTY وNode `node-pty` وWindows Python 3.11.9 وتعريف NVIDIA/CUDA وbinary الخاص بـ `llama.cpp` من داخل حاوية Linux. هذه بوابات Windows حقيقية يجب تنفيذها على Windows نفسه.

## الحكم النهائي

ضمن جميع المسارات التي أمكن تنفيذها والتحقق منها هنا، النتيجة هي:

**0 اختبارات فاشلة، 0 أخطاء تشغيل مرصودة في مسار الاستيراد/التدريب/الدمج/الأسئلة/إعادة التحميل الذي تم تنفيذه.**

لا يصح تحويل ذلك إلى ضمان أن المشروع مستحيل أن يحتوي على أي خطأ في بيئة Windows، لأن بوابات Windows الأصلية لم تُنفذ في هذه البيئة. لكن المسار الذي طلبته لتدريب الملف واختباره وإصلاح المشاكل قد تم تنفيذه فعلياً بعد الإصلاح النهائي.
```

---

### `503/588` `FINAL_RELEASE_REPORT_4.5.8.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\FINAL_RELEASE_REPORT_4.5.8.md`
- **الحجم:** 2352 بايت (2.3 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.8 — Final Full Bundle Verification

## الحكم
تم تجميع إصدار كامل يضم المصدر + الإصلاحات + نموذج ALI-v1 المدرّب + الـcheckpoint + LoRA adapter + merged HF weights + بيانات التدريب + قاعدة المعرفة المحلية.

## نتائج التحقق
- Full backend suite: **242 passed, 34 skipped, 2 warnings**
- Release audit: **PASS**
- Clean-start server health: **PASS**
- Active model: **ALI-v1**, reload: **PASS**
- Fixture: 216 parsed conversation sections
- Unique Q/A samples: 215
- Pre-seeded training-QA chunks: 215
- Full fixture quiz via API: **216/216**
- Source-answer match: **216/216**
- Re-import protection remains covered by existing tests (`duplicate_source`)
- Checkpoint loads successfully and reports global step 13
- Active merged model weights equal bundled merged HF weights byte-for-byte (SHA256 identical)

## الأوزان
تم تضمين: `checkpoint.pt`, `internal_model.safetensors`, `adapter_model.safetensors`, `adapter/adapter_model.safetensors`, `adapter/adapter_config.json`, و`merged_hf/model.safetensors`، إضافة إلى tokenizer/config/manifests.

## الإصلاحات المضمّنة
1. إصلاح مسار الـbase checkpoint النسبي لمنع إعادة تدريب tokenizer وحدوث embedding index mismatch.
2. أولوية deterministic local QA على الذاكرة القديمة.
3. مسار training-QA deterministic من ملفات المحادثات.
4. إصلاح bridge الخاص بـllama-server و`-ngl` وstreaming.
5. منفذ llama-server ديناميكي عند تعارض المنفذ المفضل.
6. تماسك الإصدار 4.5.8.
7. نموذج مدرّب Active مع fallback إلى bootstrap.
8. قاعدة معرفة محلية مهيأة مسبقاً لتعمل النسخة النظيفة دون إعادة استيراد.
9. تنظيف قواعد بيانات المحادثات/الذاكرة القابلة للتغيير عند الشحن.

## حدود Windows
لم تُنفّذ بوابات Windows-native داخل Linux: Electron production، .NET publish، embedded CPython 3.11.9، node-pty/ConPTY، CUDA، llama.cpp Windows binaries، وGGUF inference. المشروع يحتوي على سكربتات التشغيل والتحقق اللازمة على Windows.
```

---

### `504/588` `FINAL_RELEASE_STATUS_4.5.6.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\FINAL_RELEASE_STATUS_4.5.6.md`
- **الحجم:** 2047 بايت (2.0 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.6 — Final Release Status

## What this release fixes
- Grounded local Q&A router answers high-confidence local/project questions before the tiny bootstrap model.
- Full P50 user hardware profile is bundled into local knowledge.
- llama.cpp bridge now passes `-ngl` and returns the actual completion text instead of the raw response object.
- llama-server uses a free localhost port instead of a fixed port to prevent collisions.
- Chat streaming supports true delta parsing when llama-server is available.
- Version metadata is coherent at 4.5.6.
- Existing continuous-learning pipeline, RAG, Memory, session history and training progress remain intact.

## Target hardware policy
Lenovo ThinkPad P50, i7-6820HQ, 32 GB RAM, Quadro M1000M 2 GB GDDR5.

Auto mode never assumes all 2 GB are free. CUDA training is attempted only after a real self-test; otherwise CPU is used. GGUF inference uses adaptive layer offload when a compatible llama.cpp CUDA build is installed.

## Local QA strategy
The small bootstrap model is retained as a trainable/diagnostic model. For project facts and curated operational questions, ALI first uses deterministic local Q&A and RAG. This gives reliable answers without pretending the 30 MB bootstrap model is a strong general-purpose model.

## Training lifecycle
`Import → Validate → Dedup → RAG → Dataset → LoRA → Evaluate → Candidate → Promote → Runtime Reload → vN+1`

## Verification in this environment
- Python compile: PASS
- pytest: 167 passed, 34 skipped, 2 warnings
- Release audit: PASS
- Arabic P50 RAG/Q&A smoke: PASS

## Windows-only release gates
The following must be run on the target Windows machine:
- Embedded Python 3.11.9 preparation
- Node/npm installation and `npm install`
- Vite/Electron production build
- native `node-pty` rebuild / ConPTY
- C#/.NET 8 publish
- real NVIDIA CUDA kernel test on Quadro M1000M
- compatible llama.cpp Windows CUDA binary

The package contains scripts for these gates and does not claim they were executed on Linux.
```

---

### `505/588` `FINAL_VERIFICATION_REPORT_4.5.3.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\FINAL_VERIFICATION_REPORT_4.5.3.md`
- **الحجم:** 1686 بايت (1.6 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.4 — Final Verification Report

## Verified in the current Linux environment
- Python static/source verification: PASS
- pytest: 163 passed, 34 skipped, 2 warnings
- Desktop source verification: PASS
- Node syntax (`main.cjs`, `preload.cjs`, renderer JS): PASS
- Arabic P50 knowledge retrieval: PASS
- Dynamic backend-port fallback: PASS
- New-chat/history/rename/delete API path: PASS
- Training import of the bundled V1 conversation pack: PASS (504 samples validated in prior end-to-end import)
- Real training progress path: PASS; an isolated 504-sample training run reached step 25/31 with live progress, elapsed time, ETA, loss and throughput before the external test timeout.

## Packaged assets
- ALI-Bootstrap-v2.5 active base model
- V1 LoRA + merged-HF candidate artifacts
- V1 training data and conversation documentation
- Arabic ThinkPad P50 reference
- ALI core operational Q&A reference
- Continuous-learning scripts and manifests

## Target hardware
- Lenovo ThinkPad P50
- Intel Core i7-6820HQ, 4C/8T
- 32 GB DDR4
- NVIDIA Quadro M1000M, 2 GB GDDR5, compute capability 5.0

## Native Windows release gates
The following still require the target Windows machine and are not claimed as PASS here: Embedded Python 3.11.9 runtime, Electron production build, C#/.NET publish, node-pty/ConPTY, NVIDIA CUDA kernel test, and Windows llama.cpp binary execution.

## Model quality honesty
The bundled bootstrap model is intentionally small. RAG can answer bundled/project facts immediately; general model-only quality is not claimed to be equivalent to a large instruction-tuned model. The V1 candidate is therefore shipped as Candidate, not forced Active.
```

---

### `506/588` `GPU_MAXWELL_SETUP_4.5.2.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\GPU_MAXWELL_SETUP_4.5.2.md`
- **الحجم:** 1317 بايت (1.3 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.5 — Quadro M1000M 2GB / GPU Setup

The P50 profile records a Quadro M1000M with 2GB VRAM and compute capability 5.0. ALI never assumes the full 2GB is free.

## Runtime policy
- Auto: probe CUDA with a real kernel and query current free VRAM.
- Inference: use llama.cpp GGUF with adaptive `n_gpu_layers` when enough VRAM is free.
- Training: use CUDA only when the real CUDA self-test succeeds; otherwise use CPU.
- Shared GPU: lower sequence length / increase gradient accumulation / lower offload layers as free VRAM drops.

## Thresholds used by the project
- >= 1.35GB free: full 24-layer Qwen GGUF offload / seq 256 training profile.
- >= 0.95GB free: half-layer GGUF offload / seq 192 profile.
- >= 0.65GB free: low-layer GGUF offload / seq 128 profile.
- < 0.65GB or unknown occupancy: CPU-safe fallback in Auto.

## Windows setup
1. Run `backend\RUN-GPU-DOCTOR.bat`.
2. Run `scripts\SETUP_QWEN_LOCAL.bat` to install Qwen GGUF + llama.cpp locally.
3. Run `scripts\VERIFY_ALL.bat`.
4. Select `Auto (Smart)` in the top bar.

## Important
The repository includes exact download/verification scripts, but this Linux build environment cannot download the 398MB Qwen GGUF or execute Windows CUDA/ConPTY tests. The Windows release host must run the setup scripts and final native verification.
```

---

### `507/588` `GPU_MAXWELL_SETUP_4.5.5.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\GPU_MAXWELL_SETUP_4.5.5.md`