import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Terminal as XTerminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';
import {
  Activity, Archive, BatteryCharging, BookOpen, Bot, Box, Brain, BriefcaseBusiness, Check, CheckCircle2,
  ChevronDown, Clipboard, Cpu, Database, Download, FileCode2, FilePlus2, FileText, FolderOpen,
  Gauge, GitBranch, Globe2, HardDrive, History, Home, Info, Layers3, Loader2, Lock, MessageCircle, MoreHorizontal,
  Paperclip, Play, Plus, RefreshCw, Save, Search, Send, Settings, ShieldCheck, SlidersHorizontal, Sparkles, Square,
  Star, Trash2, UploadCloud, UserRound, Wrench, X, Zap, ThumbsDown, ThumbsUp, TerminalSquare, ExternalLink,
} from 'lucide-react';
import { api, msg } from './api.js';

const NAV = [
  ['chat', 'المحادثة', 'مساعدك الذكي دائماً', MessageCircle],
  ['projects', 'المشاريع', 'إدارة المشاريع والمهام', BriefcaseBusiness],
  ['files', 'الملفات', 'تحليل ومعالجة الملفات', FileText],
  ['memory', 'الذاكرة', 'ذاكرة متعددة الطبقات', Brain],
  ['improvement', 'التعلم من الأخطاء', 'تصحيح محفوظ للجيل القادم', ShieldCheck],
  ['tools', 'الأدوات', 'أدوات وموارد النظام', Wrench],
  ['web', 'البحث والويب', 'بحث محلي ومصادر موثوقة', Globe2],
  ['training', 'النموذج والتدريب', 'تدريب تراكمي وإصدارات v1 → vN', Gauge],
  ['models', 'النماذج', 'الإصدارات والتحميل والترقية', Box],
  ['settings', 'الإعدادات', 'إعدادات النظام والتخصيص', Settings],
];

const QUICK_ACTIONS = [
  ['files', 'تحليل الملفات', FileText],
  ['web', 'البحث في الويب', Search],
  ['chat', 'كتابة وتطوير', Sparkles],
  ['chat', 'تحليل البيانات', Database],
  ['training', 'تدريب النموذج', Gauge],
];

const nowTime = () => new Date().toLocaleTimeString('ar', { hour: '2-digit', minute: '2-digit' });
const dateTime = () => new Date().toLocaleDateString('ar-SA', { day: '2-digit', month: '2-digit', year: 'numeric' });

function Logo({ small = false }) { return <img className={`logo ${small ? 'small' : ''}`} src="./assets/ali-logo.svg" alt="ALI" />; }

function SelectBox({ value, onChange, items, Icon, disabled = false }) {
  return <label className={`selectBox ${disabled ? 'disabled' : ''}`}>
    <Icon size={16} />
    <span>{value}</span>
    <ChevronDown size={14} />
    <select aria-label={value} value={value} onChange={(e) => onChange?.(e.target.value)} disabled={disabled}>
      {items.map((item) => <option key={item} value={item}>{item}</option>)}
    </select>
  </label>;
}

function TopBar({ mode, setMode, computeMode, setComputeMode, model, setModel, modelItems, hw, learning, onRefresh }) {
  return <header className="topbar">
    <div className="brandWrap">
      <Logo />
      <div><b>ALI Studio Pro</b><small>AI Assistant &amp; Workstation</small></div>
    </div>
    <div className="topControls">
      <SelectBox value={mode} onChange={setMode} items={['الوضع الاحترافي', 'Auto (Smart)', 'Agent Mode', 'Research Mode']} Icon={Sparkles} />
      <SelectBox value={computeMode} onChange={setComputeMode} items={['Auto (Smart)', 'CPU', 'GPU']} Icon={Zap} />
      <SelectBox value={model} onChange={setModel} items={modelItems.length ? modelItems : ['Auto (Active)']} Icon={Box} disabled={!modelItems.length} />
      {learning?.state === 'running' && <div className="liveTrain"><span className="pulseDot"/> {learning.generation || 'جديد'} · {Math.round((learning.progress || 0) * 100)}%</div>}
    </div>
    <div className="machine">
      <div className="machineDevice"><HardDrive size={19}/><div><b>{hw.osLabel || 'Windows 11 Pro'}</b><small>{hw.deviceName || 'Windows PC'}</small></div></div>
      <button className="iconButton" onClick={onRefresh} title="تحديث حالة النظام"><RefreshCw size={15}/></button>
      <div className="clockBlock"><b>{new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</b><small>{dateTime()}</small></div>
      <div className="windowButtons"><button title="تصغير" onClick={() => window.electronAPI?.window?.minimize?.()}>—</button><button title="تكبير" onClick={() => window.electronAPI?.window?.maximize?.()}>□</button><button title="إغلاق" onClick={() => window.electronAPI?.window?.close?.()}>×</button></div>
    </div>
  </header>;
}

function Metric({ Icon, label, value, sub }) {
  return <div className="metric"><Icon size={14}/><div><span>{label}</span><b title={String(value)}>{value}</b><small>{sub}</small></div></div>;
}

function LeftSidebar({ active, setActive, hw, workspace, onSelect }) {
  return <aside className="leftbar">
    <nav className="navList" aria-label="التنقل الرئيسي">
      {NAV.map(([id, label, desc, Icon]) => <button key={id} className={`navItem ${active === id ? 'active' : ''}`} onClick={() => setActive(id)}>
        <Icon size={21}/><span><b>{label}</b><small>{desc}</small></span>
      </button>)}
    </nav>
    <section className="deviceCard">
      <div className="deviceHead"><div className="deviceDot"/><div><b>{hw.deviceName || 'Windows PC'}</b><small>{hw.cpu_model || 'Local workstation'}</small></div><button onClick={onSelect} title="اختيار مساحة العمل"><FolderOpen size={15}/></button></div>
      <div className="metrics">
        <Metric Icon={Cpu} label="CPU" value={`${hw.cpu_percent ?? '—'}%`} sub={hw.cpu_temp == null ? 'حرارة غير متاحة' : `${hw.cpu_temp}°C`}/>
        <Metric Icon={Activity} label="GPU" value={hw.gpu_percent == null ? '—' : `${hw.gpu_percent}%`} sub={hw.gpu_name || 'GPU / CPU'}/>
        <Metric Icon={Database} label="RAM" value={`${hw.ram_used_gb ?? '—'} / ${hw.ram_gb ?? '—'} GB`} sub={hw.ram_percent == null ? '—' : `${hw.ram_percent}%`}/>
        <Metric Icon={HardDrive} label="SSD" value={`${hw.disk_used_gb ?? '—'} / ${hw.disk_total_gb ?? '—'} GB`} sub={hw.disk_percent == null ? '—' : `${hw.disk_percent}%`}/>
        <Metric Icon={BatteryCharging} label="Battery" value={hw.battery_percent == null ? '—' : `${hw.battery_percent}%`} sub={hw.battery_minutes ? `~${hw.battery_minutes} دقيقة` : 'AC / Unknown'}/>
      </div>
      <div className="workspaceLine"><FolderOpen size={13}/><span title={workspace}>{workspace || 'مساحة العمل المحلية'}</span></div>
    </section>
  </aside>;
}

function PanelTitle({ Icon, title, pill, ok, action }) {
  return <div className="panelTitle"><Icon size={17}/><b>{title}</b><div className="grow"/>{pill && <span className={`statusPill ${ok ? 'ok' : ''}`}><i/>{pill}</span>}{action}</div>;
}

function Ring({ label, value, kind = '' }) {
  const p = Math.max(0, Math.min(100, Number(value || 0)));
  return <div className={`ring ${kind}`} style={{ '--p': `${p}%` }}><div className="ringInner"><span>{label}</span><b>{value == null ? '—' : `${Math.round(p)}%`}</b></div></div>;
}

function InfoRow({ label, value }) { return <div className="infoRow"><span>{label}</span><b title={String(value)}>{value}</b></div>; }

function RightSidebar({ hw, status, training, onOpenTraining }) {
  const learn = training?.status || {};
  return <aside className="rightbar">
    <section className="systemCard">
      <PanelTitle Icon={Bot} title="حالة النظام" pill={status.online ? 'متصل' : 'غير متصل'} ok={status.online}/>
      <div className="rings"><Ring label="CPU" value={hw.cpu_percent}/><Ring label="GPU" value={hw.gpu_percent} kind="green"/><Ring label="RAM" value={hw.ram_percent} kind="violet"/></div>
      <div className="temps"><div><b>{hw.cpu_temp == null ? '—' : `${hw.cpu_temp}°C`}</b><span>CPU</span></div><div><b>{hw.gpu_temp == null ? '—' : `${hw.gpu_temp}°C`}</b><span>GPU</span></div><div><b>{hw.ram_used_gb ? `${hw.ram_used_gb} / ${hw.ram_gb}` : '—'}</b><span>RAM GB</span></div></div>
      <div className="batteryBox"><div className="batteryVisual"><BatteryCharging size={22}/></div><div className="grow"><div className="row"><b>البطارية</b><span>{hw.battery_minutes ? `~${hw.battery_minutes} دقيقة متبقية` : 'متصل بالطاقة'}</span></div><strong>{hw.battery_percent == null ? '—' : `${hw.battery_percent}%`}</strong><div className="bar"><span style={{ width: `${hw.battery_percent || 0}%` }}/></div></div></div>
    </section>
    <section className="sysCard"><PanelTitle Icon={Cpu} title="الملخص السريع"/><InfoRow label="نظام التشغيل" value={hw.osLabel || 'Windows 11 Pro'}/><InfoRow label="المعالج" value={hw.cpu_model || '—'}/><InfoRow label="الذاكرة" value={hw.ram_gb ? `${hw.ram_gb} GB` : '—'}/><InfoRow label="التخزين" value={hw.disk_total_gb ? `${hw.disk_total_gb} GB` : '—'}/><InfoRow label="وضع الحوسبة" value={hw.cuda_self_test ? 'CUDA / GPU جاهز' : 'CPU / GPU fallback'}/></section>
    <section className="sysCard"><PanelTitle Icon={Layers3} title="التعلم التراكمي"/><InfoRow label="الإصدار التالي" value={learn.generation || 'بانتظار البيانات'}/><InfoRow label="بيانات جديدة" value={learn.pending_sources ?? 0}/><InfoRow label="الحالة" value={learn.state === 'running' ? 'تدريب جارٍ' : learn.state === 'completed' ? 'اكتمل' : learn.state === 'failed' ? 'فشل ويمكن إعادة المحاولة' : 'جاهز'}/><button className="softBtn full" onClick={onOpenTraining}><Gauge size={15}/>فتح مركز التدريب</button></section>
    <section className="sysCard"><PanelTitle Icon={Activity} title="الأنشطة الجارية"/>{[['المحادثة', 'محلي'], ['النموذج', status.modelLoaded ? 'محمل' : 'غير محمل'], ['التعلم', learn.state === 'running' ? 'Running' : 'Ready'], ['RAG', 'متصل']].map(([a, b]) => <div className="activityRow" key={a}><i className={learn.state === 'running' && a === 'التعلم' ? 'amberDot' : ''}/><b>{a}</b><span>{b}</span></div>)}</section>
  </aside>;
}

function CodeBlock({ code, language = '' }) {
  const copyCode = async () => { try { await navigator.clipboard.writeText(code); } catch (_) {} };
  return <div className="codeBlock">
    <div className="codeHeader"><span>{language || 'code'}</span><button onClick={copyCode} title="نسخ الكود"><Clipboard size={12}/><span>نسخ</span></button></div>
    <pre><code>{code}</code></pre>
  </div>;
}

function InlineMarkdown({ text }) {
  const parts = String(text || '').split(/(`[^`]+`|\*\*[^*]+\*\*|\[[^\]]+\]\([^\)]+\))/g).filter(Boolean);
  return parts.map((part, i) => {
    if (/^`[^`]+`$/.test(part)) return <code className="inlineCode" key={i}>{part.slice(1, -1)}</code>;
    if (/^\*\*[^*]+\*\*$/.test(part)) return <strong key={i}>{part.slice(2, -2)}</strong>;
    const link = part.match(/^\[([^\]]+)\]\(([^\)]+)\)$/);
    if (link) return <a key={i} href={link[2]} onClick={(e) => { e.preventDefault(); window.electronAPI?.openExternal?.(link[2]); }}>{link[1]}</a>;
    return part;
  });
}

function MarkdownTable({ rows }) {
  if (!rows?.length) return null;
  const cells = (line) => line.trim().replace(/^\|/,'').replace(/\|$/,'').split('|').map((x) => x.trim());
  const header = cells(rows[0]);
  const body = rows.slice(1).filter((line) => !/^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line));
  return <div className="mdTableWrap"><table className="mdTable"><thead><tr>{header.map((x,i)=><th key={i}><InlineMarkdown text={x}/></th>)}</tr></thead><tbody>{body.map((line,r)=><tr key={r}>{cells(line).map((x,i)=><td key={i}><InlineMarkdown text={x}/></td>)}</tr>)}</tbody></table></div>;
}

function RichMessage({ content = '' }) {
  const lines = String(content || '').replace(/\r/g, '').split('\n');
  const nodes = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (/^\s*```/.test(line)) {
      const language = line.trim().slice(3).trim();
      const code = [];
      i += 1;
      while (i < lines.length && !/^\s*```/.test(lines[i])) { code.push(lines[i]); i += 1; }
      if (i < lines.length) i += 1;
      nodes.push(<CodeBlock key={`code-${i}`} code={code.join('\n')} language={language}/>);
      continue;
    }
    if (/^\s*\|?.+\|.+\|?\s*$/.test(line) && i + 1 < lines.length && /\|/.test(lines[i + 1]) && /^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(lines[i + 1])) {
      const tableRows = [line]; i += 1;
      while (i < lines.length && /^\s*\|?.+\|.+\|?\s*$/.test(lines[i]) && lines[i].trim()) { tableRows.push(lines[i]); i += 1; }
      nodes.push(<MarkdownTable key={`table-${i}`} rows={tableRows}/>);
      continue;
    }
    if (/^>\s?/.test(line)) {
      const quote = []; while (i < lines.length && /^>\s?/.test(lines[i])) { quote.push(lines[i].replace(/^>\s?/,'')); i += 1; }
      nodes.push(<blockquote className="mdQuote" key={`q-${i}`}><InlineMarkdown text={quote.join('\n')}/></blockquote>); continue;
    }
    const heading = line.match(/^\s{0,3}(#{1,4})\s+(.+)$/);
    if (heading) { nodes.push(<h3 className={`mdH mdH${heading[1].length}`} key={`h-${i}`}><InlineMarkdown text={heading[2]}/></h3>); i += 1; continue; }
    const bullet = line.match(/^\s*[-*•]\s+(.+)$/);
    if (bullet) {
      const items = [];
      while (i < lines.length) {
        const m = lines[i].match(/^\s*[-*•]\s+(.+)$/); if (!m) break;
        items.push(<li key={i}><InlineMarkdown text={m[1]}/></li>); i += 1;
      }
      nodes.push(<ul className="mdList" key={`ul-${i}`}>{items}</ul>); continue;
    }
    const ordered = line.match(/^\s*\d+[.)]\s+(.+)$/);
    if (ordered) {
      const items = [];
      while (i < lines.length) {
        const m = lines[i].match(/^\s*\d+[.)]\s+(.+)$/); if (!m) break;
        items.push(<li key={i}><InlineMarkdown text={m[1]}/></li>); i += 1;
      }
      nodes.push(<ol className="mdList" key={`ol-${i}`}>{items}</ol>); continue;
    }
    if (!line.trim()) { nodes.push(<div className="mdSpacer" key={`sp-${i}`}/>); i += 1; continue; }
    const paragraph = [line]; i += 1;
    while (i < lines.length && lines[i].trim() && !/^\s*```/.test(lines[i]) && !/^\s{0,3}#{1,4}\s+/.test(lines[i]) && !/^\s*[-*•]\s+/.test(lines[i]) && !/^\s*\d+[.)]\s+/.test(lines[i])) { paragraph.push(lines[i]); i += 1; }
    nodes.push(<p className="mdPara" key={`p-${i}`}><InlineMarkdown text={paragraph.join('\n')}/></p>);
  }
  return <div className="richMessage">{nodes}</div>;
}

function WorkingTrace({ message }) {
  const stages = message.steps || [];
  if (!message.streaming && !stages.length) return null;
  const labels = { route:'تحديد المهمة', retrieve:'استرجاع المعرفة', web:'البحث عبر الإنترنت', analyze:'تحليل الطلب', generate:'صياغة الإجابة', verify:'التحقق من الإجابة', tool:'تنفيذ الأداة', done:'اكتملت الإجابة' };
  const fallback = message.streaming && !stages.length ? ['route','analyze','generate','verify'] : [];
  const display = stages.length ? stages : fallback.map((name, idx) => ({ name, status: idx === fallback.length - 1 && message.streaming ? 'running' : 'queued', progress: 0 }));
  return <div className="workingTrace"><div className="workingHead"><Sparkles size={13}/><b>{message.streaming ? 'ALI يعمل على الطلب' : 'مسار التنفيذ'}</b><span>{message.streaming ? 'يتم إخفاء التفاصيل الداخلية ويُعرض التقدم فقط' : 'ملخص قابل للفهم'}</span></div><div className="traceSteps">{display.map((s, i) => <div className={`traceStep ${s.status || ''}`} key={`${s.name}-${i}`}><span className="traceIcon">{s.status === 'completed' ? <CheckCircle2 size={12}/> : s.status === 'failed' ? <X size={12}/> : s.status === 'running' ? <Loader2 className="spin" size={12}/> : <span>{i+1}</span>}</span><b>{labels[s.name] || s.name || 'تنفيذ'}</b>{s.detail && <small>{s.detail}</small>}</div>)}</div></div>;
}

function WebSources({ web }) {
  const docs = (web?.documents || []).filter((d) => d?.url).slice(0, 5);
  if (!docs.length) return null;
  return <div className="webSources"><div className="webSourcesHead"><Globe2 size={14}/><b>مصادر الإنترنت</b><span>{docs.length} مصادر</span></div><div className="webSourceGrid">{docs.map((d, i) => <button className="webSource" key={`${d.url}-${i}`} onClick={() => window.electronAPI?.openExternal?.(d.url)}><div className="webSourceTop"><span className="webIndex">{i+1}</span><b>{d.title || d.url}</b><ExternalLink size={12}/></div><small>{d.snippet || d.text?.slice(0, 150) || d.url}</small><em>{d.source || 'web'}</em></button>)}</div></div>;
}

function Message({ message, onFeedback, onCopy, onRemember, onTrain }) {
  const user = message.role === 'user';
  const cleanText = (value) => String(value || '').replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '');
  return <div className={`messageRow ${user ? 'user' : 'assistant'}`}>
    {!user && <div className="avatar"><Logo small/></div>}
    <div className={`bubble ${message.streaming ? 'isStreaming' : ''}`}>
      <div className="bubbleHead"><b>{user ? 'أنت' : 'ALI'}</b><span>{message.time}</span>{!user && message.mode && <em>{message.mode}</em>}{!user && message.web?.documents?.length ? <em className="webMode"><Globe2 size={10}/> ويب</em> : null}</div>
      {!user && <WorkingTrace message={message}/>} 
      <div className="bubbleText" dir="auto"><RichMessage content={cleanText(message.content)}/></div>
      {!user && <div className="messageActions">
        <button title="نسخ" onClick={() => onCopy(message.content)}><Clipboard size={13}/></button>
        <button title="حفظ في الذاكرة" onClick={() => onRemember(message)}><Brain size={13}/></button>
        <button title="إضافة للتدريب" onClick={() => onTrain(message)}><Gauge size={13}/></button>
        <button title="مفيد" className={message.feedback === 'up' ? 'selectedGood' : ''} onClick={() => onFeedback(message, true)}><ThumbsUp size={13}/></button>
        <button title="غير مفيد" className={message.feedback === 'down' ? 'selectedBad' : ''} onClick={() => onFeedback(message, false)}><ThumbsDown size={13}/></button>
      </div>}
      {message.sources?.length > 0 && <div className="sources"><Layers3 size={13}/><span>المعرفة المحلية · {message.sources.length}</span>{message.sources.slice(0, 3).map((s) => <button key={s.id || s.path} onClick={() => s.url ? window.electronAPI?.openExternal?.(s.url) : window.electronAPI?.openPath?.(s.path)}>{s.title || s.path}</button>)}</div>}
      <WebSources web={message.web}/>
      {message.tool && <div className="toolResult"><Wrench size={13}/> نتيجة الأداة: {message.tool.name || message.tool.tool || 'tool'}</div>}
    </div>
    {user && <div className="userAvatar"><UserRound size={16}/></div>}
  </div>;
}
function ChatPage({ messages, setMessages, workspace, onOpenTraining, onGo, conversationId, setConversationId, conversations, reloadConversations, computeMode, model }) {
  const [input, setInput] = useState(''); const [busy, setBusy] = useState(false); const [showHistory, setShowHistory] = useState(false); const [attachment, setAttachment] = useState(null); const area = useRef(null); const textarea = useRef(null); const abortRef = useRef(null);
  const parseStoredMeta = (x) => { try { return typeof x?.meta_json === 'string' ? JSON.parse(x.meta_json || '{}') : (x?.meta_json || {}); } catch (_) { return {}; } };
  const hydrateMessage = (x) => ({ role:x.role, content:x.content, time:new Date((x.created_at||Date.now()/1000)*1000).toLocaleTimeString('ar',{hour:'2-digit',minute:'2-digit'}), ...parseStoredMeta(x) });
  useEffect(() => area.current?.scrollTo({ top: area.current.scrollHeight, behavior: 'smooth' }), [messages, busy]);
  useEffect(() => { const h = (e) => { if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); textarea.current?.focus(); } }; window.addEventListener('keydown', h); return () => window.removeEventListener('keydown', h); }, []);
  useEffect(() => { if (!conversationId) return; api.conversation(conversationId).then(r => setMessages((r.conversation?.messages || []).filter(x => x.role !== 'system').map(hydrateMessage))).catch(() => {}); }, [conversationId, setMessages]);
  const newChat = async () => { const r = await api.createConversation('محادثة جديدة'); setConversationId(r.conversation.id); setMessages([]); setShowHistory(false); reloadConversations?.(); };
  const loadChat = async (id) => { const r = await api.conversation(id); setConversationId(id); setMessages((r.conversation?.messages || []).filter(x => x.role !== 'system').map(hydrateMessage)); setShowHistory(false); };
  const renameChat = async (c) => { const title = window.prompt('اسم المحادثة الجديدة:', c.title || 'محادثة جديدة'); if (!title?.trim()) return; await api.renameConversation(c.id, title.trim()); reloadConversations?.(); };
  const deleteChat = async (c) => { if (!window.confirm(`حذف المحادثة «${c.title}»؟`)) return; await api.deleteConversation(c.id); if (conversationId === c.id) { setConversationId(''); setMessages([]); } reloadConversations?.(); };
  const send = async () => {
    let text = input.trim(); if (!text || busy) return;
    if (attachment) { text += `\n\n[مرفق: ${attachment.name}]${attachment.content ? `\n${attachment.content.slice(0, 24000)}` : ''}`; }
    const user = { role: 'user', content: text, time: nowTime(), direction: 'auto' }; const next = [...messages, user]; setMessages(next); setInput(''); setAttachment(null); setBusy(true);
    const assistantIndex = next.length;
    setMessages([...next, { role: 'assistant', content: '', time: nowTime(), streaming: true }]);
    try {
      let finalMeta = {};
      const controller = new AbortController();
      abortRef.current = controller;
      await api.streamChat(next.map(({ role, content }) => ({ role, content })), workspace, model === 'Auto (Active)' ? '' : model, (ev) => { if (ev.type === 'session' && ev.conversation_id) { setConversationId(ev.conversation_id); reloadConversations?.(); }
        if (ev.type === 'stage') setMessages((prev) => { const copy = [...prev]; const prior = copy[assistantIndex] || {}; const steps = Array.isArray(prior.steps) ? [...prior.steps] : []; const item = { name: ev.name || ev.phase || 'work', status: ev.status || 'running', detail: ev.message || '', progress: ev.progress }; const existing = steps.findIndex((x) => x.name === item.name); if (existing >= 0) steps[existing] = { ...steps[existing], ...item }; else steps.push(item); copy[assistantIndex] = { ...prior, steps }; return copy; });
        if (ev.type === 'delta') setMessages((prev) => { const copy = [...prev]; copy[assistantIndex] = { ...copy[assistantIndex], content: `${copy[assistantIndex]?.content || ''}${ev.text || ''}` }; return copy; });
        if (ev.type === 'replace') setMessages((prev) => { const copy = [...prev]; copy[assistantIndex] = { ...copy[assistantIndex], content: ev.text || copy[assistantIndex]?.content || '', replaced: true }; return copy; });
        if (ev.type === 'tool') finalMeta = { ...finalMeta, tool: ev.tool || ev.result };
        if (ev.type === 'web') finalMeta = { ...finalMeta, web: ev.web || ev };
        if (ev.type === 'final') finalMeta = { ...finalMeta, ...ev };
      }, conversationId, computeMode === 'GPU' ? 'gpu' : computeMode === 'CPU' ? 'cpu' : 'auto', controller.signal);
      setMessages((prev) => { const copy = [...prev]; copy[assistantIndex] = { ...copy[assistantIndex], content: finalMeta.text || copy[assistantIndex]?.content || '—', mode: finalMeta.mode, sources: finalMeta.sources || [], tool: finalMeta.tool, web: finalMeta.web, confidence: finalMeta.confidence, steps: finalMeta.steps || copy[assistantIndex]?.steps || [], streaming: false }; return copy; });
    } catch (e) {
      if (e?.code === 'ABORTED') {
        setMessages((prev) => { const copy = [...prev]; copy[assistantIndex] = { ...copy[assistantIndex], content: (copy[assistantIndex]?.content || 'تم إيقاف إنشاء الإجابة.') + '\n\n— تم الإيقاف بواسطة المستخدم —', streaming: false, stopped: true }; return copy; });
      } else {
        try {
          const result = await api.chat(next.map(({ role, content }) => ({ role, content })), workspace, model === 'Auto (Active)' ? '' : model, conversationId, computeMode === 'GPU' ? 'gpu' : computeMode === 'CPU' ? 'cpu' : 'auto');
          setMessages((prev) => { const copy = [...prev]; copy[assistantIndex] = { ...copy[assistantIndex], content: result.text || '—', mode: result.mode, sources: result.sources || [], tool: result.tool, web: result.web, confidence: result.confidence, steps: result.steps || [], streaming: false }; return copy; });
        } catch (fallback) { setMessages((prev) => { const copy = [...prev]; copy[assistantIndex] = { ...copy[assistantIndex], content: `تعذر تنفيذ الطلب محلياً: ${msg(fallback)}`, streaming: false }; return copy; }); }
      }
    } finally { abortRef.current = null; setBusy(false); }
  };
  const keyDown = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } };
  const attach = async (e) => { const file = e.target.files?.[0]; e.target.value = ''; if (!file) return; let content = ''; const textLike = /^(text\/)|\.(md|markdown|txt|json|jsonl|csv|py|js|jsx|ts|tsx|yaml|yml|html|htm)$/i.test(file.type || '') || /\.(md|markdown|txt|json|jsonl|csv|py|js|jsx|ts|tsx|yaml|yml|html|htm)$/i.test(file.name); if (textLike && file.size <= 300000) { try { content = await file.text(); } catch (_) {} } setAttachment({ name: file.name, size: file.size, content }); textarea.current?.focus(); };
  const action = (label) => { if (label === 'تدريب النموذج') return onOpenTraining(); if (label === 'تحليل الملفات') return onGo('files'); if (label === 'البحث في الويب') return onGo('web'); setInput(label === 'كتابة وتطوير' ? 'ساعدني في كتابة وتحسين الكود الخاص بالمشروع مع فحص الأخطاء.' : 'حلّل هذه المهمة خطوة بخطوة ثم تحقق من النتيجة قبل اعتمادها.'); textarea.current?.focus(); };
  const copy = async (text) => { try { await navigator.clipboard.writeText(text); } catch (_) {} };
  const feedback = async (m, accepted) => { const idx = messages.indexOf(m); if (idx < 0) return; try { await api.feedback({ user_text: messages[idx - 1]?.content || '', assistant_text: m.content, accepted }); if (!accepted) { const corrected = window.prompt('اكتب التصحيح الصحيح. سيُحفظ كعينة معتمدة للجيل القادم بعد مراجعتك:'); if (corrected?.trim()) await api.correct({ user_text: messages[idx - 1]?.content || '', bad_output: m.content, corrected_output: corrected.trim(), component: 'desktop-chat', reason: 'thumbs_down_verified_correction', source: 'user' }); } setMessages((prev) => prev.map((x) => x === m ? { ...x, feedback: accepted ? 'up' : 'down' } : x)); } catch (_) {} };
  const remember = async (m) => { try { await api.saveMemory({ type: 'semantic', key: `chat_${Date.now()}`, content: m.content.slice(0, 4000), source: 'chat-action', confidence: .9 }); } catch (_) {} };
  const train = async (m) => { if (!messages.length) return; const prior = messages[messages.indexOf(m) - 1]; if (!prior) return; try { const blob = new Blob([`User:\n${prior.content}\n\nAssistant:\n${m.content}\n`], { type: 'text/markdown' }); const file = new File([blob], `ALI-chat-${Date.now()}.md`, { type: 'text/markdown' }); const path = window.electronAPI?.saveTempFile ? await window.electronAPI.saveTempFile(file.name, await blob.text()) : ''; if (path) { await api.trainingIngest([path]); } } catch (_) {} };
  return <main className="centerPanel">
    <div className="sessionBar"><button className="primaryBtn" onClick={newChat}><Plus size={14}/>محادثة جديدة</button><button className="softBtn" onClick={() => setShowHistory(v=>!v)}><History size={14}/>المحادثات السابقة</button><span className="sessionMeta">{conversationId ? 'جلسة محفوظة' : 'جلسة جديدة'} · {computeMode} · {model}</span>{showHistory && <div className="historyMenu">{conversations.length ? conversations.map(c => <div className="historyItem" key={c.id}><button className="historyOpen" onClick={() => loadChat(c.id)}><MessageCircle size={13}/><span>{c.title}</span></button><button className="historyAction" title="إعادة تسمية" onClick={() => renameChat(c)}>✎</button><button className="historyAction danger" title="حذف" onClick={() => deleteChat(c)}>×</button></div>) : <div className="empty compact">لا توجد محادثات محفوظة.</div>}</div>}</div>
    <div className="tabbar"><Tab title="المحادثة" icon={MessageCircle} active/><Tab title="المشاريع" icon={BriefcaseBusiness} onClick={() => onGo('projects')}/><Tab title="الملفات" icon={FileText} onClick={() => onGo('files')}/><Tab title="الذاكرة" icon={Brain} onClick={() => onGo('memory')}/><Tab title="الأدوات" icon={Wrench} onClick={() => onGo('tools')}/><Tab title="المزيد" icon={MoreHorizontal} onClick={() => onGo('settings')}/></div>
    <div className="chatArea" ref={area}>
      {messages.length === 0 && <div className="welcome"><Logo/><h1>مرحباً بك في ALI</h1><p>مساعدك الذكي المتكامل على جهازك المحلي</p><div className="quickRow">{QUICK_ACTIONS.map(([id, label, Icon]) => <button key={label} onClick={() => action(label)}><Icon size={15}/>{label}</button>)}</div><div className="welcomeHint"><Lock size={13}/> يعمل محلياً أولاً مع ذاكرة وRAG وأدوات وتنفيذ اختياري للويب.</div></div>}
      {messages.map((m, i) => <Message key={`${m.time}-${i}`} message={m} onFeedback={feedback} onCopy={copy} onRemember={remember} onTrain={train}/>)}
      {busy && messages.at(-1)?.streaming && !messages.at(-1)?.content && <div className="typing"><span/><span/><span/> ALI يحلل الطلب ويتحقق من النتيجة…</div>}
    </div>
    <div className="composer"><div className="composerTools"><button title="إرفاق ملف" onClick={() => document.getElementById('chatFile').click()}><Paperclip size={18}/></button><button title="فتح مركز التدريب" onClick={onOpenTraining}><Gauge size={18}/></button><button title="فتح الطرفية" onClick={() => onGo('tools')}><TerminalSquare size={18}/></button><button title="البحث عبر الإنترنت داخل المحادثة" onClick={() => { setInput((v) => v ? `${v}\n\nابحث عبر الإنترنت وتحقق من المصادر قبل الإجابة.` : 'ابحث عبر الإنترنت وتحقق من المصادر قبل الإجابة: '); textarea.current?.focus(); }}><Globe2 size={18}/></button><input id="chatFile" type="file" hidden accept=".md,.markdown,.txt,.json,.jsonl,.csv,.pdf,.docx,.html,.htm,.py,.js,.jsx,.ts,.tsx,.yaml,.yml" onChange={attach}/></div><div className="composerMain"><textarea dir="auto" spellCheck={true} ref={textarea} value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={keyDown} placeholder="اكتب سؤالك هنا…  Enter للإرسال · Shift+Enter لسطر جديد" rows={1}/>{attachment && <div className="attachmentChip"><Paperclip size={12}/>{attachment.name}<button onClick={() => setAttachment(null)} title="إزالة المرفق"><X size={11}/></button></div>}</div><button className={`sendButton ${busy ? 'stopMode' : ''}`} disabled={!busy && (!input.trim() && !attachment)} onClick={busy ? () => abortRef.current?.abort() : send} title={busy ? 'إيقاف إنشاء الإجابة' : 'إرسال'}>{busy ? <Square size={16}/> : <Send size={19}/>}</button></div>
  </main>;
}

function Tab({ title, icon: Icon, active = false, onClick }) { return <button className={`tab ${active ? 'active' : ''}`} onClick={onClick}><Icon size={15}/>{title}</button>; }

function ProjectsPage({ workspace, onSelect }) {
  const [git, setGit] = useState(''); const [info, setInfo] = useState(null); const [error, setError] = useState('');
  const refresh = async () => { try { const [g, f] = await Promise.all([api.git(), api.files('')]); setGit(g.output || g.error || 'Git غير متاح'); setInfo({ files: (f.entries || []).filter((x) => x.type === 'file').length, folders: (f.entries || []).filter((x) => x.type === 'directory').length }); setError(''); } catch (e) { setError(msg(e)); } };
  useEffect(() => { refresh(); }, [workspace]);
  return <PageShell title="المشاريع" sub="إدارة مساحة العمل والمهام وحالة Git" actions={<><button className="softBtn" onClick={onSelect}><FolderOpen size={15}/>فتح مجلد</button><button className="primaryBtn" onClick={refresh}><RefreshCw size={15}/>تحديث</button></>}>
    {error && <ErrorBox text={error}/>}<section className="heroCard"><div className="heroIcon"><Home/></div><div className="grow"><h3>{workspace?.split(/[\\/]/).pop() || 'ALI Project'}</h3><p>{workspace || 'لم يتم اختيار مساحة عمل بعد'}</p><div className="tags"><span>Local</span><span>Agent</span><span>Windows</span><span>{info?.files ?? '—'} ملف</span></div></div></section>
    <div className="twoCards"><section className="tableCard"><PanelTitle Icon={GitBranch} title="Git Status" action={<button className="iconButton" onClick={refresh}><RefreshCw size={14}/></button>}/><pre className="gitOutput">{git || 'جارٍ الفحص…'}</pre></section><section className="tableCard"><PanelTitle Icon={Activity} title="مؤشرات المشروع"/><InfoRow label="الملفات" value={info?.files ?? '—'}/><InfoRow label="المجلدات" value={info?.folders ?? '—'}/><InfoRow label="Workspace" value="نشط"/><InfoRow label="الأمان" value="Safe Path"/></section></div>
  </PageShell>;
}

function FilesPage({ workspace }) {
  const [items, setItems] = useState([]); const [path, setPath] = useState(''); const [editor, setEditor] = useState(''); const [editorPath, setEditorPath] = useState(''); const [dirty, setDirty] = useState(false); const [error, setError] = useState(''); const [query, setQuery] = useState('');
  const load = async (p = '') => { try { const r = await api.files(p); setItems(r.entries || []); setPath(p); setError(''); } catch (e) { setError(msg(e)); } };
  useEffect(() => { load(''); }, [workspace]);
  const open = async (item) => { if (item.type === 'directory') return load(item.path); try { const r = await api.readFile(item.path); setEditorPath(r.path); setEditor(r.content); setDirty(false); setError(''); } catch (e) { setError(msg(e)); } };
  const save = async () => { if (!editorPath) return; try { await api.writeFile(editorPath, editor); setDirty(false); setError('تم حفظ الملف بنجاح'); } catch (e) { setError(msg(e)); } };
  const create = async () => { const name = window.prompt('اسم الملف الجديد:', 'new_file.md'); if (!name) return; try { const target = path ? `${path}/${name}` : name; await api.createFile(target, ''); await load(path); await open({ type: 'file', path: target, name }); } catch (e) { setError(msg(e)); } };
  const remove = async () => { if (!editorPath || !window.confirm(`حذف ${editorPath}؟`)) return; try { await api.deleteFile(editorPath); setEditorPath(''); setEditor(''); setDirty(false); await load(path); } catch (e) { setError(msg(e)); } };
  const visible = items.filter((x) => x.name.toLowerCase().includes(query.toLowerCase())); const parent = path.split('/').slice(0, -1).join('/');
  return <PageShell title="الملفات" sub={workspace || 'مساحة العمل المحلية'} actions={<><div className="searchMini"><Search size={14}/><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="بحث…"/></div><button className="softBtn" onClick={create}><FilePlus2 size={15}/>ملف جديد</button><button className="primaryBtn" onClick={() => load(path)}><RefreshCw size={15}/>تحديث</button></>}>
    {error && <ErrorBox text={error}/>}<div className="fileWorkspace"><div className="fileTree">{path && <button className="backRow" onClick={() => load(parent)}>← المجلد الأعلى</button>}{visible.map((item) => <button className={`fileRow ${editorPath === item.path ? 'selected' : ''}`} key={item.path} onClick={() => open(item)}><div className="rowIcon">{item.type === 'directory' ? <FolderOpen size={15}/> : <FileText size={15}/>}</div><div><b>{item.name}</b><small>{item.type === 'directory' ? 'مجلد' : `${item.size ?? 0} bytes`}</small></div></button>)}{!visible.length && <div className="empty compact">لا توجد عناصر.</div>}</div><div className="editorPane"><div className="editorBar"><div className="editorTitle"><FileCode2 size={14}/><span>{editorPath || 'لم يتم فتح ملف'}</span>{dirty && <i title="تعديلات غير محفوظة"/>}</div><div className="editorActions"><button className="iconButton" onClick={() => navigator.clipboard.writeText(editor)} disabled={!editor}><Clipboard size={14}/></button><button className="iconButton dangerIcon" onClick={remove} disabled={!editorPath}><Trash2 size={14}/></button><button className="primaryBtn" onClick={save} disabled={!editorPath || !dirty}><Save size={14}/>حفظ</button></div></div><CodeEditor value={editor} onChange={(v) => { setEditor(v); setDirty(true); }} /></div></div>
  </PageShell>;
}

function CodeEditor({ value, onChange }) {
  const lines = Math.max(1, String(value || '').split('\n').length); return <div className="codeWrap"><div className="lineNumbers">{Array.from({ length: lines }, (_, i) => <span key={i}>{i + 1}</span>)}</div><textarea className="codeEditor" value={value} onChange={(e) => onChange(e.target.value)} spellCheck={false} placeholder="افتح ملفاً لعرض محتواه…" /></div>;
}

function MemoryPage() {
  const [tab, setTab] = useState('facts'); const [query, setQuery] = useState(''); const [rows, setRows] = useState([]); const [convs, setConvs] = useState([]); const [form, setForm] = useState({ type: 'user', key: '', content: '' }); const [error, setError] = useState('');
  const load = async () => { try { const r = await api.memory(query, tab === 'facts' ? '' : ''); setRows(r.memories || []); setConvs(r.conversations || []); setError(''); } catch (e) { setError(msg(e)); } };
  useEffect(() => { load(); }, [tab]);
  const add = async () => { if (!form.key.trim() || !form.content.trim()) return; try { await api.saveMemory(form); setForm({ type: 'user', key: '', content: '' }); await load(); } catch (e) { setError(msg(e)); } };
  const remove = async (id) => { try { await api.deleteMemory(id); await load(); } catch (e) { setError(msg(e)); } };
  return <PageShell title="الذاكرة" sub="معلومات المستخدم والمحادثات المحفوظة منفصلة عن أوزان النموذج" actions={<><div className="searchMini"><Search size={14}/><input value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && load()} placeholder="ابحث في الذاكرة…"/></div><button className="primaryBtn" onClick={load}><RefreshCw size={14}/>تحديث</button></>}>
    {error && <ErrorBox text={error}/>}<div className="memoryTabs"><button className={tab === 'facts' ? 'active' : ''} onClick={() => setTab('facts')}>المعلومات</button><button className={tab === 'conversations' ? 'active' : ''} onClick={() => setTab('conversations')}>المحادثات</button></div>{tab === 'facts' ? <><section className="formCard"><div className="formGrid"><select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}><option value="user">user</option><option value="project">project</option><option value="semantic">semantic</option><option value="long_term">long_term</option><option value="episodic">episodic</option></select><input value={form.key} onChange={(e) => setForm({ ...form, key: e.target.value })} placeholder="المفتاح (مثال: language)"/><input className="growInput" value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} placeholder="المعلومة التي تريد أن يتذكرها ALI"/><button className="primaryBtn" onClick={add}><Plus size={15}/>إضافة</button></div></section><div className="tableCard">{rows.length ? rows.map((r) => <div className="listRow" key={r.id}><div className="rowIcon"><Brain size={15}/></div><div className="grow"><b>{r.key}</b><small>{r.content}</small><code>{r.type} · {r.source} · ثقة {(Number(r.confidence || 0) * 100).toFixed(0)}%</code></div><button className="iconButton dangerIcon" onClick={() => remove(r.id)}><Trash2 size={14}/></button></div>) : <div className="empty">لا توجد معلومات محفوظة.</div>}</div></> : <div className="tableCard">{convs.length ? convs.map((r) => <div className="convRow" key={r.id}><div className="convQ"><b>سؤال</b><span>{r.user_text}</span></div><div className="convA"><b>ALI</b><span>{r.assistant_text}</span></div><small>Quality {(Number(r.quality || 0) * 100).toFixed(0)}% · {r.source}</small></div>) : <div className="empty">لا توجد محادثات محفوظة.</div>}</div>}
  </PageShell>;
}

function ImprovementPage() {
  const [data, setData] = useState({ incidents: [], corrections: [], stats: {} });
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const load = useCallback(async () => { try { const r = await api.learningErrors(200); setData({ incidents: r.incidents || [], corrections: r.corrections || [], stats: r.stats || {} }); } catch (e) { setMessage(msg(e)); } }, []);
  useEffect(() => { load(); }, [load]);
  const correct = async (incident) => {
    const corrected = window.prompt('اكتب الإجابة/التصحيح الموثوق. سيتم حفظه للتدريب في الجيل القادم:', '');
    if (!corrected?.trim()) return;
    const userText = incident.user_text || window.prompt('ما سؤال المستخدم الذي تسبب بالمشكلة؟', '') || '';
    if (!userText.trim()) return;
    setBusy(true);
    try { await api.correct({ user_text: userText, bad_output: incident.bad_output || '', corrected_output: corrected.trim(), component: incident.component || 'chat', reason: 'verified_from_improvement_center', source: 'user' }); setMessage('تم حفظ التصحيح كبيانات معتمدة للجيل القادم.'); await load(); } catch (e) { setMessage(msg(e)); } finally { setBusy(false); }
  };
  return <PageShell title="التعلم من الأخطاء" sub="كل خطأ يصبح حادثة قابلة للمراجعة، والتصحيح المعتمد يتحول إلى عينة جاهزة للجيل التالي" actions={<button className="primaryBtn" onClick={load} disabled={busy}><RefreshCw size={14}/>تحديث</button>}>
    {message && <div className="noticeCard"><ShieldCheck size={17}/><div><b>{message}</b><p>التصحيحات لا تدخل الأوزان تلقائياً؛ تُجمع ضمن Delta الجيل التالي بعد بوابة التدريب والتحقق.</p></div></div>}
    <div className="trainStats"><Stat icon={ShieldCheck} label="حوادث محفوظة" value={Object.values(data.stats?.incidents || {}).reduce((a,b)=>a+Number(b||0),0)} sub="Incident ledger"/><Stat icon={CheckCircle2} label="تصحيحات معتمدة" value={Number(data.stats?.approved_corrections || 0)} sub="جاهزة للتدريب"/><Stat icon={Layers3} label="المصدر" value="Error Learning" sub="Persistent local"/><Stat icon={GitBranch} label="المصير" value="Next Gen" sub="Cumulative delta"/></div>
    <section className="tableCard"><PanelTitle Icon={ShieldCheck} title="الحوادث التي تحتاج مراجعة" pill={data.incidents.length ? `${data.incidents.length} حادثة` : 'لا توجد'}/>{data.incidents.length ? data.incidents.map((r) => <div className="improvementRow" key={r.id}><div className="rowIcon"><X size={14}/></div><div className="grow"><b>{r.component || 'chat'} · {r.status || 'open'}</b><small>{r.user_text || 'بدون سؤال محفوظ'}</small><p>{r.bad_output}</p><code>{r.reason || 'quality issue'}</code></div><button className="softBtn" onClick={() => correct(r)} disabled={busy}><Check size={13}/>إضافة تصحيح</button></div>) : <div className="empty">لا توجد حوادث مفتوحة حاليًا.</div>}</section>
    <section className="tableCard"><PanelTitle Icon={CheckCircle2} title="التصحيحات المعتمدة"/><div className="correctionList">{data.corrections.length ? data.corrections.slice().reverse().map((r) => <div className="correctionRow" key={r.sample_id}><div className="correctionHead"><span><CheckCircle2 size={13}/>معتمد</span><code>{String(r.sample_id || '').slice(0,16)}</code></div><div className="correctionQ"><b>السؤال</b><p>{r.user_text}</p></div><div className="correctionA"><b>التصحيح</b><p>{r.corrected_output}</p></div></div>) : <div className="empty">لا توجد تصحيحات معتمدة.</div>}</div></section>
  </PageShell>;
}

function ToolsPage({ workspace }) { return <PageShell title="الأدوات" sub="Terminal حقيقي عبر Windows ConPTY مع جلسة محلية" actions={<button className="softBtn" onClick={() => window.electronAPI?.terminal?.kill?.()}><Square size={14}/>إيقاف الطرفية</button>}><section className="terminalCard fullTerminal"><div className="terminalHeader"><div><TerminalSquare size={15}/><span>PowerShell / ConPTY</span></div><code>{workspace}</code></div><TerminalPanel workspace={workspace}/></section></PageShell>; }

function TerminalPanel({ workspace }) {
  const host = useRef(null); const termRef = useRef(null);
  useEffect(() => { if (!host.current) return; const term = new XTerminal({ cursorBlink: true, fontSize: 12, fontFamily: 'Cascadia Mono, Consolas, monospace', theme: { background: '#071220', foreground: '#dfe9f6', cursor: '#78a9ff', selectionBackground: '#244c83' }, scrollback: 8000 }); const fit = new FitAddon(); term.loadAddon(fit); term.open(host.current); term.write(`\r\n\x1b[36mALI Terminal\x1b[0m — ${workspace}\r\n`); fit.fit(); window.electronAPI?.terminal?.start?.(); const off = window.electronAPI?.terminal?.onData?.((d) => term.write(d)); const resize = () => { fit.fit(); window.electronAPI?.terminal?.resize?.(term.cols, term.rows); }; const obs = new ResizeObserver(resize); obs.observe(host.current); term.onData((d) => window.electronAPI?.terminal?.write?.(d)); resize(); termRef.current = term; return () => { obs.disconnect(); off?.(); window.electronAPI?.terminal?.kill?.(); term.dispose(); termRef.current = null; }; }, [workspace]);
  return <div className="terminalHost" ref={host}/>;
}

function WebPage() {
  const [query, setQuery] = useState(''); const [local, setLocal] = useState([]); const [web, setWeb] = useState([]); const [allow, setAllow] = useState(false); const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  useEffect(() => { api.settings().then((r) => setAllow(Boolean(r.allow_internet))).catch(() => {}); }, []);
  const search = async () => { if (!query.trim()) return; setBusy(true); setError(''); try { const l = await api.search(query); setLocal(l.results || []); if (allow) { const w = await api.webSearch(query); setWeb(w.results || []); } else setWeb([]); } catch (e) { setError(msg(e)); } finally { setBusy(false); } };
  const toggle = async () => { try { const next = !allow; await api.saveSettings({ allow_internet: next }); setAllow(next); } catch (e) { setError(msg(e)); } };
  return <PageShell title="البحث والويب" sub="ابدأ بالمصادر المحلية؛ فعّل الإنترنت عند الحاجة" actions={<label className="switchLine"><input type="checkbox" checked={allow} onChange={toggle}/><span/>السماح بالبحث الخارجي</label>}>
    {error && <ErrorBox text={error}/>}<div className="searchBoxLarge"><Search size={19}/><input value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && search()} placeholder="اكتب موضوع البحث…"/><button className="primaryBtn" onClick={search} disabled={busy}>{busy ? <Loader2 className="spin" size={15}/> : <Search size={15}/>}بحث</button></div>
    <div className="searchColumns"><section className="tableCard"><PanelTitle Icon={BookOpen} title="المعرفة المحلية"/><Results items={local} empty="لا توجد نتائج محلية."/></section><section className="tableCard"><PanelTitle Icon={Globe2} title="نتائج الويب" pill={allow ? 'مفعل' : 'متوقف'} ok={allow}/><Results items={web} empty={allow ? 'لا توجد نتائج ويب.' : 'فعّل البحث الخارجي من الأعلى.'}/></section></div>
  </PageShell>;
}

function Results({ items, empty }) { return items.length ? <div className="results">{items.map((r, i) => <div className="resultRow" key={`${r.path || r.url || ''}-${i}`}><div className="rowIcon"><FileText size={15}/></div><div className="grow"><b>{r.title || r.path || r.url || 'Result'}</b><small>{r.snippet || r.text?.slice(0, 220) || r.source || ''}</small>{r.url && <a href={r.url} onClick={(e) => { e.preventDefault(); window.electronAPI?.openExternal?.(r.url); }}><ExternalLink size={12}/>فتح المصدر</a>}</div></div>)}</div> : <div className="empty">{empty}</div>; }

function TrainingPage({ computeMode = 'Auto (Smart)' }) {
  const [autoTrain, setAutoTrain] = useState(() => localStorage.getItem('ali.autoTrain') !== '0');
  const [status, setStatus] = useState({ status: { state: 'idle', progress: 0 }, pending: [], versions: [] });
  const [busy, setBusy] = useState(false);
  const [drag, setDrag] = useState(false);
  const [message, setMessage] = useState('');
  const [events, setEvents] = useState([]);
  const input = useRef(null);

  const load = useCallback(async () => {
    try {
      const s = await api.training();
      setStatus(s);
      if (s.status?.run_id) {
        const ev = await api.trainingEvents(s.status.run_id, 120);
        setEvents(ev.events || []);
      } else {
        setEvents([]);
      }
    } catch (e) { setMessage(msg(e)); }
  }, []);

  useEffect(() => {
    load();
    const t = setInterval(load, 900);
    return () => clearInterval(t);
  }, [load]);

  const ingestPaths = async (paths, fileCount = paths?.length || 0) => {
    if (!paths?.length) {
      throw new Error('لم تصل أي مسارات ملفات إلى ALI Runtime. استخدم زر «اختيار الملفات» من داخل Electron أو أعد تشغيل التطبيق من START.bat.');
    }
    setBusy(true);
    setMessage(`تم تحديد ${fileCount || paths.length} ملفاً. جارٍ التحقق والاستيراد إلى ALI Runtime…`);
    try {
      const r = await api.trainingIngest(paths);
      const results = Array.isArray(r.results) ? r.results : [];
      const accepted = results.filter((x) => x.ok && x.status === 'validated').length;
      const duplicates = results.filter((x) => x.status === 'duplicate').length;
      const rejected = results.filter((x) => x.status === 'rejected').length;
      const rag = results.filter((x) => x.ok && x.status === 'rag_only').length;
      const samples = results.reduce((n, x) => n + (Number(x.sample_count) || 0), 0);
      if (!results.length) throw new Error('وصل الطلب إلى Runtime لكن لم تُرجع خدمة الاستيراد أي نتيجة. راجع تشغيل Electron/Backend ثم أعد المحاولة.');
      setMessage(`اكتمل الاستيراد: ${accepted} مقبول · ${samples} عينة تدريب · ${rag} RAG فقط · ${duplicates} مكرر · ${rejected} مرفوض.`);
      if (autoTrain && accepted > 0) {
        const started = await api.trainingStart(true, computeMode === 'GPU' ? 'gpu' : computeMode === 'CPU' ? 'cpu' : 'auto');
        if (started.status === 'started') {
          setMessage(`بدأت دورة ${started.generation} تلقائياً من ${started.base_version}. تمت إضافة ${samples} عينة جديدة إلى الدورة.`);
        } else {
          setMessage(`تم حفظ ${accepted} ملفاً، لكن لم يبدأ التدريب: ${started.reason || started.status || 'سبب غير معروف'}`);
        }
      } else if (accepted > 0) {
        setMessage(`تم حفظ ${accepted} ملفاً و${samples} عينة. التدريب التلقائي ${autoTrain ? 'مفعل' : 'متوقف'}؛ راقب بطاقة التقدم أو اضغط «بدء التدريب».`);
      }
      await load();
    } catch (e) {
      setMessage(`فشل الاستيراد: ${msg(e)}`);
      throw e;
    } finally { setBusy(false); }
  };

  const ingest = async (files) => {
    const list = [...(files || [])];
    if (!list.length || busy) return;
    try {
      // Electron's webUtils normally provides the real path for drag/drop. When a
      // packaged/older renderer does not expose it, persist the dropped bytes via
      // the main process so the backend still receives actual local paths.
      const direct = list.map((f) => window.electronAPI?.getFilePath?.(f) || f?.path || '').filter(Boolean);
      if (direct.length === list.length) return await ingestPaths(direct, list.length);
      if (window.electronAPI?.saveTrainingFiles) {
        const payload = await Promise.all(list.map(async (f) => ({ name: f.name, type: f.type || '', data: await f.arrayBuffer() })));
        const saved = await window.electronAPI.saveTrainingFiles(payload);
        if (saved?.paths?.length) return await ingestPaths(saved.paths, list.length);
      }
      throw new Error('تعذر الوصول إلى الملفات المسحوبة. سيتم فتح اختيار ملفات Windows بدلاً من ذلك.');
    } catch (e) {
      setMessage(`لم يتم استيراد الملفات: ${msg(e)}`);
    }
  };

  const pick = async () => {
    if (busy) return;
    try {
      const native = await window.electronAPI?.selectTrainingFiles?.();
      if (native?.paths?.length) await ingestPaths(native.paths, native.paths.length);
      else if (!native) throw new Error('واجهة اختيار ملفات Windows غير متاحة. شغّل ALI Studio من Electron وليس من متصفح عادي.');
      else setMessage('لم يتم اختيار ملفات.');
    } catch (e) { setMessage(`تعذر اختيار ملفات التدريب: ${msg(e)}`); }
  };

  const start = async () => {
    setBusy(true); setMessage('جاري بدء دورة التعلم…');
    try {
      const r = await api.trainingStart(true, computeMode === 'GPU' ? 'gpu' : computeMode === 'CPU' ? 'cpu' : 'auto');
      setMessage(r.status === 'started' ? `بدأ ${r.generation} اعتماداً على ${r.base_version}.` : `${r.status || 'blocked'} · ${r.reason || ''}`);
      await load();
    } catch (e) { setMessage(msg(e)); }
    finally { setBusy(false); }
  };

  const cancel = async () => {
    try { await api.trainingCancel(); setMessage('تم إرسال طلب الإيقاف الآمن.'); await load(); }
    catch (e) { setMessage(msg(e)); }
  };

  const setAuto = (value) => { setAutoTrain(value); localStorage.setItem('ali.autoTrain', value ? '1' : '0'); };
  const learn = status.status || {};
  const pct = Math.max(0, Math.min(100, Math.round((Number(learn.progress) || 0) * 100)));
  const remainingSteps = learn.total_steps ? Math.max(0, Number(learn.total_steps) - Number(learn.step || 0)) : null;
  const eta = Number.isFinite(learn.eta_sec) && learn.eta_sec != null ? `${Math.max(0, Math.ceil(learn.eta_sec))}ث` : '—';
  const elapsed = Number.isFinite(learn.elapsed_sec) ? `${Math.floor(Number(learn.elapsed_sec) / 60)}د ${Math.floor(Number(learn.elapsed_sec) % 60)}ث` : '—';

  return <PageShell title="مركز التدريب التراكمي" sub="سحب → تحقق → RAG فوراً → Dataset → LoRA → تقييم → إصدار جديد" actions={<>
    <label className="autoToggle"><input type="checkbox" checked={autoTrain} onChange={(e) => setAuto(e.target.checked)}/><span>تدريب تلقائي</span></label>
    <button className="softBtn" onClick={load} disabled={busy}><RefreshCw size={14}/>تحديث</button>
    {learn.state === 'running' ? <button className="dangerBtn" onClick={cancel}><Square size={14}/>إيقاف آمن</button> : <button className="primaryBtn" onClick={start} disabled={busy || !(status.pending || []).length}><Play size={14}/>بدء التدريب</button>}
  </>}>
    {message && <div className={`noticeCard ${learn.state === 'failed' ? 'errorNotice' : ''}`}><Info size={17}/><div><b>{message}</b><p>الاستيراد الناجح لا يساوي تدريباً ناجحاً: الأوزان لا تتغير إلا بعد دورة تدريب وتقييم وترقية.</p></div></div>}

    <div className="trainGrid">
      <section className={`dropZone ${drag ? 'dragging' : ''} ${busy ? 'disabledDrop' : ''}`} onDragOver={(e) => { e.preventDefault(); if (!busy) setDrag(true); }} onDragLeave={() => setDrag(false)} onDrop={(e) => { e.preventDefault(); setDrag(false); ingest([...e.dataTransfer.files]); }} onClick={pick}>
        <input ref={input} type="file" multiple hidden accept=".md,.markdown,.txt,.json,.jsonl,.csv,.pdf,.docx,.html,.htm,.py,.yaml,.yml" onChange={(e) => { ingest([...e.target.files]); e.target.value = ''; }}/>
        <div className="dropIcon"><UploadCloud size={29}/></div>
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
