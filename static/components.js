// Reusable UI primitives + iOS device frame + Toast + AppCtx context.

const AppCtx = React.createContext(null);
window.AppCtx = AppCtx;
const useApp = () => React.useContext(AppCtx);
window.useApp = useApp;

// ─────────────── iOS Device Frame ───────────────
function IOSStatusBar({ dark = false, time = '9:41' }) {
  const c = dark ? '#fff' : '#000';
  return (
    <div style={{
      display: 'flex', gap: 154, alignItems: 'center', justifyContent: 'center',
      padding: '21px 24px 19px', boxSizing: 'border-box',
      position: 'relative', zIndex: 20, width: '100%',
    }}>
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <span style={{
          fontFamily: '-apple-system, "SF Pro", system-ui', fontWeight: 590,
          fontSize: 17, lineHeight: '22px', color: c,
        }}>{time}</span>
      </div>
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7 }}>
        <svg width="19" height="12" viewBox="0 0 19 12">
          <rect x="0" y="7.5" width="3.2" height="4.5" rx="0.7" fill={c}/>
          <rect x="4.8" y="5" width="3.2" height="7" rx="0.7" fill={c}/>
          <rect x="9.6" y="2.5" width="3.2" height="9.5" rx="0.7" fill={c}/>
          <rect x="14.4" y="0" width="3.2" height="12" rx="0.7" fill={c}/>
        </svg>
        <svg width="27" height="13" viewBox="0 0 27 13">
          <rect x="0.5" y="0.5" width="23" height="12" rx="3.5" stroke={c} strokeOpacity="0.35" fill="none"/>
          <rect x="2" y="2" width="20" height="9" rx="2" fill={c}/>
        </svg>
      </div>
    </div>
  );
}

function IOSDevice({ children, width = 402, height = 874, dark = false }) {
  return (
    <div style={{
      width, height, borderRadius: 48, overflow: 'hidden',
      position: 'relative', background: dark ? '#000' : '#F2F2F7',
      boxShadow: '0 40px 80px rgba(0,0,0,0.18), 0 0 0 1px rgba(0,0,0,0.12)',
    }}>
      <div style={{
        position: 'absolute', top: 11, left: '50%', transform: 'translateX(-50%)',
        width: 126, height: 37, borderRadius: 24, background: '#000', zIndex: 50,
      }} />
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, zIndex: 10 }}>
        <IOSStatusBar dark={dark} />
      </div>
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, overflow: 'hidden' }}>{children}</div>
      </div>
      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0, zIndex: 60,
        height: 34, display: 'flex', justifyContent: 'center', alignItems: 'flex-end',
        paddingBottom: 8, pointerEvents: 'none',
      }}>
        <div style={{
          width: 139, height: 5, borderRadius: 100,
          background: dark ? 'rgba(255,255,255,0.7)' : 'rgba(0,0,0,0.25)',
        }} />
      </div>
    </div>
  );
}
window.IOSDevice = IOSDevice;

// ─────────────── UI primitives ───────────────
const Pill = ({ children, on, onClick }) => (
  <div className="pill" data-on={!!on} onClick={onClick}>{children}</div>
);

const MetaLine = ({ items }) => (
  <div className="card-meta-line">
    {items.map((it, i) => (
      <React.Fragment key={i}>
        {i > 0 && <span className="sep" />}
        <span style={it.color ? { color: it.color, fontWeight: 600 } : {}}>{it.text}</span>
      </React.Fragment>
    ))}
  </div>
);

const BiasMeter = ({ position = 50, size = 'sm' }) => (
  <div style={{ marginTop: 4 }}>
    <div className="bias-track" style={{ height: size === 'lg' ? 6 : 4 }}>
      <div className="bias-pin" style={{ left: `${position}%`, height: size === 'lg' ? 14 : 10, top: size === 'lg' ? -4 : -3 }} />
    </div>
    {size === 'lg' && (
      <div className="meta" style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6 }}>
        <span>Left</span><span>Center</span><span>Right</span>
      </div>
    )}
  </div>
);

const SectionHeader = ({ eyebrow, title, action, onAction }) => (
  <div className="section-hd">
    <div>
      <div className="eyebrow">{eyebrow}</div>
      {title && <div className="serif" style={{ fontSize: 20, fontWeight: 600, marginTop: 4, color: 'var(--ink-1)' }}>{title}</div>}
    </div>
    {action && <div onClick={onAction} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, fontWeight: 600, color: 'var(--ink-1)', cursor: 'pointer' }}>{action}<Icon name="arrow-right" size={14}/></div>}
  </div>
);

const TopBar = ({ onNotif, onProfile, ward, unread, streak = 24 }) => (
  <div>
    <div className="topbar">
      <div className="brand">
        samachar<span style={{ color: 'var(--accent)' }}>.</span>
        <span className="brand-sub">AI · NP</span>
      </div>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <div className="iconbtn" onClick={onNotif} title="Notifications">
          <Icon name="bell" size={16} />
          {unread > 0 && <div className="badge-dot" />}
        </div>
        <div className="iconbtn" onClick={onProfile} title="Profile">
          <Icon name="user" size={16} />
        </div>
      </div>
    </div>
    <div style={{ padding: '0 20px 8px', display: 'flex', alignItems: 'center', gap: 10 }}>
      <Icon name="pin" size={13} color="var(--ink-3)" />
      <span className="meta" style={{ color: 'var(--ink-2)' }}>{ward}</span>
      <div style={{ flex: 1, height: 1, background: 'var(--rule)' }} />
      <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
        <Icon name="flame" size={13} color="var(--accent)" />
        <span className="meta" style={{ color: 'var(--ink-1)' }}>{streak} DAY</span>
      </div>
    </div>
  </div>
);

const SearchBar = ({ onClick, hint, placeholder = 'Search · खोज्नुहोस् · Ask AI…' }) => (
  <div onClick={onClick}
    style={{
      margin: '4px 20px 16px', padding: '12px 14px',
      background: 'var(--bg-elev)', border: '1px solid var(--rule)',
      borderRadius: 14, display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer',
    }}>
    <Icon name="search" size={16} color="var(--ink-3)" />
    <span style={{ flex: 1, color: 'var(--ink-3)', fontSize: 13, fontWeight: 500 }}>{placeholder}</span>
    {hint && <span className="tag tag-info">{hint}</span>}
  </div>
);

const TabBar = ({ current, onChange }) => {
  const tabs = [
    { id: 'home',    icon: 'home',    label: 'Today' },
    { id: 'discover',icon: 'compass', label: 'Discover' },
    { id: 'premium', icon: 'sparkles',label: 'Pro' },
    { id: 'profile', icon: 'user',    label: 'You' },
  ];
  return (
    <div className="tabbar">
      {tabs.map(t => (
        <div key={t.id} className="tab" data-on={current === t.id} onClick={() => onChange(t.id)}>
          <Icon name={t.icon} size={20} stroke={current === t.id ? 1.8 : 1.5} />
          <span>{t.label}</span>
        </div>
      ))}
    </div>
  );
};

const CardFoot = ({ a, bookmarked, onBookmark, onShare }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: 12, paddingTop: 2 }}>
    {a.verified ? (
      <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
        <Icon name="shield-check" size={12} color="var(--verify)" />
        <span className="meta" style={{ color: 'var(--verify)' }}>VERIFIED · {a.verified_count || 3}</span>
      </div>
    ) : null}
    {a.developing ? (
      <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
        <span className="dot pulse" style={{ background: 'var(--warn)' }} />
        <span className="meta" style={{ color: 'var(--warn)' }}>DEVELOPING</span>
      </div>
    ) : null}
    {a.bias !== null && a.bias !== undefined ? (
      <div style={{ flex: 1, maxWidth: 90 }}><BiasMeter position={a.bias} /></div>
    ) : null}
    <div style={{ marginLeft: 'auto', display: 'flex', gap: 14, color: 'var(--ink-3)', alignItems: 'center' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
        <Icon name="chat" size={13} />
        <span className="meta">{a.comments_count}</span>
      </div>
      <span onClick={onBookmark} style={{ cursor: 'pointer', display: 'inline-flex', color: bookmarked ? 'var(--accent)' : 'var(--ink-3)' }}>
        <Icon name="bookmark" size={13} />
      </span>
      <span onClick={onShare} style={{ cursor: 'pointer', display: 'inline-flex' }}>
        <Icon name="share" size={13} />
      </span>
    </div>
  </div>
);

const NewsCard = ({ article, variant = 'default' }) => {
  const ctx = useApp();
  const a = article;
  const bookmarked = ctx.bookmarks.has(a.id);
  const lang = ctx.user?.language || 'en';
  const title = (lang === 'np' && a.title_np) ? a.title_np : a.title;

  const open = () => ctx.openArticle(a.id);
  const toggleBm = async (e) => {
    e.stopPropagation();
    await ctx.toggleBookmark(a.id);
  };
  const share = (e) => {
    e.stopPropagation();
    if (navigator.share) navigator.share({ title: a.title, text: a.dek }).catch(()=>{});
    else { try { navigator.clipboard.writeText(a.title); ctx.toast('Title copied'); } catch(e){} }
  };

  if (variant === 'lead') {
    return (
      <div className="card-row" style={{ paddingTop: 8 }} onClick={open}>
        <div className="ph" style={{ aspectRatio: '16/10', borderRadius: 8 }}>
          <div className="ph-label">{a.img_label}</div>
        </div>
        <MetaLine items={[
          { text: a.category, color: 'var(--ink-1)' },
          { text: a.source },
          { text: a.time_label },
        ]} />
        <div className="h-headline" style={{ fontSize: 22, color: 'var(--ink-1)' }}>{title}</div>
        <div className="body" style={{ fontSize: 13.5 }}>{a.dek}</div>
        <CardFoot a={a} bookmarked={bookmarked} onBookmark={toggleBm} onShare={share} />
      </div>
    );
  }
  return (
    <div className="card-row" onClick={open}>
      <div style={{ display: 'flex', gap: 14 }}>
        <div style={{ flex: 1 }}>
          <MetaLine items={[
            { text: a.category, color: 'var(--ink-1)' },
            { text: a.source },
            { text: a.time_label },
          ]} />
          <div className="h-title" style={{ fontSize: 17, marginTop: 6, marginBottom: 6, color: 'var(--ink-1)' }}>{title}</div>
          <div className="body" style={{ fontSize: 12.5, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{a.dek}</div>
        </div>
        <div className="ph" style={{ width: 92, height: 92, borderRadius: 8, flexShrink: 0 }}>
          {a.icon && (
            <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--ink-4)' }}>
              <Icon name={a.icon} size={26} stroke={1.4} />
            </div>
          )}
        </div>
      </div>
      <CardFoot a={a} bookmarked={bookmarked} onBookmark={toggleBm} onShare={share} />
    </div>
  );
};

const LoadingScreen = ({ msg = 'Loading…' }) => (
  <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 14 }}>
    <span className="loader"/>
    <div className="meta">{msg.toUpperCase()}</div>
  </div>
);

const Toast = ({ message }) => message ? <div className="toast">{message}</div> : null;

Object.assign(window, {
  Pill, MetaLine, BiasMeter, SectionHeader, TopBar, SearchBar, TabBar,
  CardFoot, NewsCard, LoadingScreen, Toast,
});
