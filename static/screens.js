// samachar.ai — All screens.
// Nepali AI summaries · Local area news · Topic search · Pro features

// ───────────────────────── LOGIN / SIGNUP ─────────────────────────
const LoginScreen = ({ onLogin }) => {
  const [mode, setMode] = React.useState('login');
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [name, setName] = React.useState('');
  const [busy, setBusy] = React.useState(false);
  const [err, setErr] = React.useState(null);
  const [showPw, setShowPw] = React.useState(false);

  const submit = async () => {
    setErr(null);
    if (mode === 'login') {
      if (!email.trim() || !password) { setErr('इमेल र पासवर्ड आवश्यक छ।'); return; }
      setBusy(true);
      try {
        const user = await API.login({ email: email.trim(), password });
        onLogin(user);
      } catch (e) { setErr(e.body?.error || e.message); setBusy(false); }
    } else {
      if (!name.trim()) { setErr('नाम आवश्यक छ।'); return; }
      if (!email.trim()) { setErr('इमेल आवश्यक छ।'); return; }
      if (password.length < 6) { setErr('पासवर्ड कम्तीमा ६ अक्षरको हुनुपर्छ।'); return; }
      setBusy(true);
      try {
        const user = await API.signup({ name: name.trim(), email: email.trim(), password });
        onLogin(user);
      } catch (e) { setErr(e.body?.error || e.message); setBusy(false); }
    }
  };
  const onKey = e => e.key === 'Enter' && submit();

  return (
    <div className="scrollable" style={{ padding: '40px 28px' }}>
      <div className="brand" style={{ fontSize: 30, marginBottom: 4 }}>
        samachar<span style={{ color: 'var(--accent)' }}>.</span>
        <span className="brand-sub" style={{ fontSize: 10 }}>AI · NP</span>
      </div>
      <div className="meta" style={{ marginBottom: 28 }}>नेपाली समाचार, AI विश्लेषण सहित</div>

      <div style={{ display: 'flex', padding: 3, background: 'var(--bg-sunk)', borderRadius: 12, marginBottom: 26 }}>
        {[{ id: 'login', l: 'साइन इन' }, { id: 'signup', l: 'नयाँ खाता' }].map(opt => (
          <div key={opt.id} onClick={() => { setMode(opt.id); setErr(null); }}
            style={{ flex: 1, padding: '10px 12px', borderRadius: 9, textAlign: 'center', cursor: 'pointer',
              background: mode === opt.id ? 'var(--bg-elev)' : 'transparent',
              fontWeight: mode === opt.id ? 700 : 400, fontSize: 13,
              color: mode === opt.id ? 'var(--ink-1)' : 'var(--ink-3)',
              fontFamily: 'var(--serif)' }}>
            {opt.l}
          </div>
        ))}
      </div>

      <div className="h-display" style={{ fontSize: 28, marginBottom: 22 }}>
        {mode === 'login'
          ? <>स्वागत छ<span style={{ color: 'var(--accent)' }}>।</span></>
          : <>खाता बनाउनुहोस्<span style={{ color: 'var(--accent)' }}>।</span></>}
      </div>

      {mode === 'signup' && (
        <>
          <label className="meta" style={{ display: 'block', marginBottom: 5 }}>तपाईंको नाम</label>
          <input className="input-field" placeholder="जस्तै: Ramesh Thapa" autoFocus
            value={name} onChange={e => setName(e.target.value)} onKeyDown={onKey}
            style={{ marginBottom: 14 }} />
        </>
      )}

      <label className="meta" style={{ display: 'block', marginBottom: 5 }}>इमेल</label>
      <input className="input-field" type="email" placeholder="you@example.com"
        value={email} onChange={e => setEmail(e.target.value)} onKeyDown={onKey}
        style={{ marginBottom: 14 }} autoFocus={mode === 'login'} />

      <label className="meta" style={{ display: 'block', marginBottom: 5 }}>पासवर्ड</label>
      <div style={{ position: 'relative', marginBottom: 22 }}>
        <input className="input-field" type={showPw ? 'text' : 'password'}
          placeholder={mode === 'signup' ? 'कम्तीमा ६ अक्षर' : '••••••••'}
          value={password} onChange={e => setPassword(e.target.value)} onKeyDown={onKey}
          style={{ width: '100%', paddingRight: 50 }} />
        <span onClick={() => setShowPw(!showPw)}
          style={{ position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)',
            cursor: 'pointer', fontSize: 10, color: 'var(--ink-3)', fontFamily: 'var(--mono)' }}>
          {showPw ? 'HIDE' : 'SHOW'}
        </span>
      </div>

      {err && (
        <div style={{ padding: '10px 14px', background: 'var(--accent-soft)', color: 'var(--accent)',
          borderRadius: 10, marginBottom: 14, fontSize: 13 }}>{err}</div>
      )}

      <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '14px 16px' }}
        onClick={submit} disabled={busy}>
        {busy
          ? <><span className="loader" style={{ borderTopColor: 'var(--bg-elev)' }} /> प्रक्रिया हुँदैछ…</>
          : <>{mode === 'login' ? 'साइन इन' : 'खाता बनाउनुहोस्'} <Icon name="arrow-right" size={15} /></>}
      </button>

      <div style={{ marginTop: 36, paddingTop: 24, borderTop: '1px solid var(--rule)' }}>
        <div className="eyebrow" style={{ marginBottom: 12 }}>के पाउनुहुन्छ</div>
        {[
          { k: '८+', v: 'नेपाली समाचार स्रोतहरू — हर ३० मिनेटमा स्वतः अपडेट' },
          { k: 'AI', v: 'Samachar AI द्वारा नेपालीमा सारांश र विश्लेषण' },
          { k: 'पक्षपात', v: 'प्रत्येक समाचारको पक्षपात मिटर — वाम देखि दायाँ' },
          { k: 'स्थानीय', v: 'आफ्नो ठेगाना राखेर स्थानीय समाचार खोज्नुहोस्' },
        ].map((row, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'baseline', gap: 14, marginBottom: 10 }}>
            <div className="serif" style={{ fontSize: 15, fontWeight: 700, minWidth: 50, color: 'var(--accent)' }}>{row.k}</div>
            <div style={{ fontSize: 12.5, color: 'var(--ink-2)' }}>{row.v}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
window.LoginScreen = LoginScreen;

// ───────────────────── ONBOARDING ─────────────────────
const OnboardingScreen = ({ onComplete }) => {
  const ctx = useApp();
  const [step, setStep] = React.useState(0);
  const [selected, setSelected] = React.useState(new Set(['t1', 't3']));
  const [chosenLang, setChosenLang] = React.useState('np');
  const [topics, setTopics] = React.useState([]);

  React.useEffect(() => { API.topics().then(setTopics); }, []);

  const toggle = id => {
    const next = new Set(selected);
    next.has(id) ? next.delete(id) : next.add(id);
    setSelected(next);
  };

  const finish = async () => {
    await API.updateTopics([...selected]);
    await API.updatePrefs({ language: chosenLang, onboarded: 1 });
    await ctx.refreshUser();
    onComplete();
  };

  return (
    <div className="scrollable" style={{ padding: '20px 24px 40px' }}>
      <div style={{ display: 'flex', gap: 6, marginTop: 24, marginBottom: 32 }}>
        {[0, 1, 2].map(i => (
          <div key={i} style={{ height: 3, flex: i === step ? 2 : 1, borderRadius: 2, transition: '.3s',
            background: i <= step ? 'var(--ink-1)' : 'var(--rule)' }} />
        ))}
      </div>
      <div className="eyebrow" style={{ marginBottom: 10 }}>चरण {step + 1} / ३</div>

      {step === 0 && (
        <>
          <div className="h-display" style={{ fontSize: 32, marginBottom: 14 }}>
            नेपाली समाचार,<br />
            <span style={{ color: 'var(--ink-3)' }}>बुझेर पढ्नुहोस्</span><span style={{ color: 'var(--accent)' }}>।</span>
          </div>
          <div style={{ padding: 16, border: '1px solid var(--rule)', borderRadius: 14, background: 'var(--bg-elev)', marginBottom: 24 }}>
            {[
              { dot: 'var(--accent)', text: 'Samachar AI ले नेपालीमा सारांश र विश्लेषण गर्छ' },
              { dot: 'var(--info)', text: '८ प्रमुख नेपाली स्रोतबाट हर ३० मिनेटमा समाचार आउँछ' },
              { dot: 'var(--verify)', text: 'प्रत्येक समाचारको पक्षपात मिटर र तथ्य जाँच' },
              { dot: 'var(--warn)', text: 'आफ्नो ठेगाना राखेर स्थानीय खबर खोज्नुहोस्' },
            ].map((r, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '6px 0' }}>
                <span style={{ width: 7, height: 7, borderRadius: 999, background: r.dot, flexShrink: 0 }} />
                <span style={{ fontSize: 13, color: 'var(--ink-2)' }}>{r.text}</span>
              </div>
            ))}
          </div>
          <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '14px 16px' }}
            onClick={() => setStep(1)}>अगाडि बढ्नुहोस् <Icon name="arrow-right" size={16} /></button>
          <div style={{ textAlign: 'center', marginTop: 14 }}>
            <span onClick={finish} style={{ fontSize: 12, color: 'var(--ink-3)', cursor: 'pointer', textDecoration: 'underline' }}>
              छोड्नुहोस्
            </span>
          </div>
        </>
      )}

      {step === 1 && (
        <>
          <div className="h-display" style={{ fontSize: 26, marginBottom: 10 }}>आफ्नो विषय छान्नुहोस्</div>
          <div className="body" style={{ fontSize: 13, marginBottom: 20 }}>
            यी विषयहरूले तपाईंको फिड निर्धारण गर्छन् — जुनसुकै बेला परिवर्तन गर्न सकिन्छ।
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 22 }}>
            {topics.map(t => {
              const on = selected.has(t.id);
              return (
                <div key={t.id} onClick={() => toggle(t.id)} style={{
                  padding: 14, borderRadius: 12, cursor: 'pointer',
                  border: `1px solid ${on ? 'var(--ink-1)' : 'var(--rule)'}`,
                  background: on ? 'var(--ink-1)' : 'var(--bg-elev)',
                  color: on ? 'var(--bg-elev)' : 'var(--ink-1)',
                  display: 'flex', flexDirection: 'column', gap: 8, minHeight: 90,
                }}>
                  <Icon name={t.icon} size={20} />
                  <div style={{ marginTop: 'auto' }}>
                    <div className="serif" style={{ fontSize: 14, fontWeight: 600 }}>{t.name}</div>
                    <div style={{ fontSize: 11, opacity: on ? 0.6 : 0.5, marginTop: 2 }}>{t.sub}</div>
                  </div>
                </div>
              );
            })}
          </div>
          <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '14px 16px' }}
            onClick={() => setStep(2)} disabled={selected.size === 0}>
            {selected.size} विषय छानिए <Icon name="arrow-right" size={16} />
          </button>
        </>
      )}

      {step === 2 && (
        <>
          <div className="h-display" style={{ fontSize: 26, marginBottom: 10 }}>भाषा छान्नुहोस्</div>
          <div className="body" style={{ fontSize: 13, marginBottom: 22 }}>
            AI सारांश र विश्लेषण कुन भाषामा पाउन चाहनुहुन्छ?
          </div>
          <div style={{ display: 'flex', gap: 8, marginBottom: 28 }}>
            {[{ v: 'np', l: 'नेपाली', s: 'AI जवाफ देवनागरीमा' }, { v: 'en', l: 'English', s: 'AI answers in English' }].map(l => (
              <div key={l.v} onClick={() => setChosenLang(l.v)}
                style={{ flex: 1, padding: '16px 12px', borderRadius: 12, textAlign: 'center', cursor: 'pointer',
                  border: `1.5px solid ${chosenLang === l.v ? 'var(--ink-1)' : 'var(--rule)'}`,
                  background: chosenLang === l.v ? 'var(--ink-1)' : 'var(--bg-elev)',
                  color: chosenLang === l.v ? 'var(--bg-elev)' : 'var(--ink-1)' }}>
                <div className="serif" style={{ fontSize: 18, fontWeight: 700 }}>{l.l}</div>
                <div style={{ fontSize: 11, opacity: 0.6, marginTop: 4 }}>{l.s}</div>
              </div>
            ))}
          </div>
          <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '14px 16px' }} onClick={finish}>
            मेरो फिड खोल्नुहोस् <Icon name="arrow-right" size={16} />
          </button>
        </>
      )}
    </div>
  );
};
window.OnboardingScreen = OnboardingScreen;

// ──────────────────────── HOME ────────────────────────
const HomeScreen = ({ go }) => {
  const ctx = useApp();
  const [tab, setTab] = React.useState('foryou');
  const [articles, setArticles] = React.useState(null);
  const [playing, setPlaying] = React.useState(false);
  const [scanStatus, setScanStatus] = React.useState(null);
  const [newBanner, setNewBanner] = React.useState(null);
  const [scanning, setScanning] = React.useState(false);
  const esRef = React.useRef(null);

  const filters = ['foryou', 'nepal', 'politics', 'business', 'tech', 'sports', 'climate', 'health'];
  const filterLabels = {
    foryou: 'सबैका लागि', nepal: 'नेपाल', politics: 'राजनीति',
    business: 'व्यापार', tech: 'प्रविधि', sports: 'खेलकुद', climate: 'वातावरण', health: 'स्वास्थ्य',
  };

  const loadArticles = React.useCallback(() => {
    setArticles(null);
    const param = tab === 'foryou' ? {} : { tag: tab };
    API.articles(param).then(setArticles).catch(() => setArticles([]));
  }, [tab]);

  React.useEffect(() => { loadArticles(); }, [loadArticles]);

  React.useEffect(() => {
    API.scanStatus().then(setScanStatus).catch(() => {});
  }, []);

  // SSE live feed
  React.useEffect(() => {
    if (esRef.current) esRef.current.close();
    const es = API.liveFeed(
      () => setNewBanner(b => ({ count: (b?.count || 0) + 1 })),
      (data) => {
        setScanStatus(s => ({ ...s, ...data }));
        if (data.new_articles > 0)
          setNewBanner({ count: data.new_articles, fromScan: true });
      }
    );
    esRef.current = es;
    return () => es.close();
  }, []);

  const triggerScan = async () => {
    if (scanning || scanStatus?.running) return;
    setScanning(true);
    try {
      await API.triggerScan();
      ctx.toast('स्क्यान सुरु भयो…');
      setTimeout(() => API.scanStatus().then(setScanStatus), 2000);
    } catch (e) { ctx.toast(e.message); }
    finally { setScanning(false); }
  };

  const dismissBanner = () => { setNewBanner(null); loadArticles(); };

  if (articles === null) return (
    <>
      <TopBar onNotif={() => go('notifications')} onProfile={() => go('profile')}
        ward={ctx.user.ward} unread={ctx.unreadCount} />
      <LoadingScreen msg="समाचार लोड हुँदैछ…" />
    </>
  );

  const lead = articles[0];
  const lastScan = scanStatus?.last_run_human;
  const isRunning = scanStatus?.running;

  return (
    <>
      <TopBar onNotif={() => go('notifications')} onProfile={() => go('profile')}
        ward={ctx.user.ward} unread={ctx.unreadCount} />
      <SearchBar onClick={() => go('search')} hint="खोज्नुहोस् वा AI सोध्नुहोस्…" />

      {/* New stories banner */}
      {newBanner && (
        <div onClick={dismissBanner} style={{
          margin: '0 16px 8px', padding: '10px 14px', background: 'var(--ink-1)',
          color: 'var(--bg-elev)', borderRadius: 10,
          display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer',
        }}>
          <span className="dot pulse" style={{ background: 'var(--bg-elev)' }} />
          <span style={{ flex: 1, fontSize: 12.5, fontWeight: 600, fontFamily: 'var(--serif)' }}>
            {newBanner.count} नयाँ समाचार आयो — ताजा गर्न थिच्नुहोस्
          </span>
          <Icon name="refresh-cw" size={13} />
        </div>
      )}

      {/* Date bar + scan control */}
      <div style={{ padding: '8px 20px 12px', borderTop: '1px solid var(--rule)', borderBottom: '1px solid var(--rule)',
        display: 'flex', alignItems: 'center', gap: 10 }}>
        <div className="serif" style={{ fontSize: 13, fontWeight: 700, letterSpacing: '0.03em' }}>
          {new Date().toLocaleDateString('ne-NP', { weekday: 'long', day: 'numeric', month: 'long' }).toUpperCase()}
        </div>
        <div style={{ flex: 1 }} />
        {/* Scan button */}
        <button onClick={triggerScan} disabled={scanning || isRunning}
          style={{ display: 'flex', alignItems: 'center', gap: 5, padding: '5px 10px', borderRadius: 999,
            background: isRunning ? 'var(--warn-soft)' : 'var(--bg-elev)',
            border: `1px solid ${isRunning ? 'var(--warn)' : 'var(--rule)'}`,
            cursor: (scanning || isRunning) ? 'not-allowed' : 'pointer',
            color: isRunning ? 'var(--warn)' : 'var(--ink-2)' }}>
          <span className="dot" style={{ background: isRunning ? 'var(--warn)' : 'var(--verify)',
            animation: isRunning ? 'pulse 1s infinite' : 'none' }} />
          <span className="meta" style={{ fontSize: 10 }}>
            {isRunning ? 'स्क्यानिङ…' : scanning ? 'सुरु हुँदैछ…' : lastScan ? `अपडेट ${lastScan}` : 'स्क्यान'}
          </span>
          {!isRunning && !scanning && <Icon name="refresh-cw" size={11} color="var(--ink-3)" />}
        </button>
      </div>

      {/* Filter tabs */}
      <div className="pill-row" style={{ paddingTop: 12 }}>
        {filters.map(f => (
          <Pill key={f} on={tab === f} onClick={() => setTab(f)}>{filterLabels[f]}</Pill>
        ))}
      </div>

      <div className="scrollable" style={{ paddingBottom: 20 }}>
        {/* Morning brief card */}
        {lead && (
          <div style={{ margin: '0 16px 4px', padding: '14px 16px', background: 'var(--ink-1)',
            borderRadius: 14, display: 'flex', alignItems: 'center', gap: 14, color: 'var(--bg-elev)' }}>
            <div onClick={() => setPlaying(!playing)} style={{ width: 42, height: 42, borderRadius: 999,
              background: 'var(--bg-elev)', color: 'var(--ink-1)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', flexShrink: 0 }}>
              <Icon name={playing ? 'pause' : 'play'} size={16} color="var(--ink-1)" />
            </div>
            <div style={{ flex: 1 }}>
              <div className="eyebrow" style={{ color: 'rgba(255,255,255,0.5)', fontSize: 9 }}>आजको सारांश</div>
              <div className="serif" style={{ fontSize: 14, fontWeight: 600, marginTop: 2 }}>
                आजको मुख्य ५ समाचार · ५ मिनेट
              </div>
            </div>
            {playing && <div className="wave">{[0,1,2,3,4].map(i=><i key={i} style={{animationDelay:`${i*.15}s`,background:'var(--bg-elev)'}}/>)}</div>}
            {!playing && <span className="tag" style={{ background: 'rgba(255,255,255,.12)', color: 'rgba(255,255,255,.7)' }}>PRO</span>}
          </div>
        )}

        {articles.length === 0 && (
          <div style={{ padding: '60px 24px', textAlign: 'center' }}>
            <Icon name="refresh-cw" size={28} color="var(--ink-4)" />
            <div className="serif" style={{ fontSize: 17, fontWeight: 600, marginTop: 14 }}>
              यस फिल्टरमा समाचार छैन
            </div>
            <div className="body" style={{ marginTop: 8, marginBottom: 18 }}>
              स्क्यान बटन थिचेर ताजा समाचार ल्याउनुहोस्।
            </div>
            <button className="btn btn-ghost" onClick={() => setTab('foryou')}>सबै समाचार हेर्नुहोस्</button>
          </div>
        )}

        {lead && <NewsCard article={lead} variant="lead" />}

        {tab === 'foryou' && lead && (
          <>
            {/* Scan info strip */}
            {scanStatus && scanStatus.scraped_articles > 15 && (
              <div style={{ margin: '0 16px 4px', padding: '10px 14px', border: '1px solid var(--rule)',
                borderRadius: 10, background: 'var(--bg-elev)', display: 'flex', alignItems: 'center', gap: 10 }}>
                <Icon name="rss" size={13} color="var(--verify)" />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--verify)' }}>
                    {scanStatus.scraped_articles} समाचार सङ्कलित
                  </div>
                  <div className="meta" style={{ marginTop: 1 }}>
                    {(scanStatus.sources_ok || []).length} स्रोत ठीक · {lastScan || 'कहिल्यै चलेन'} मा अपडेट
                  </div>
                </div>
              </div>
            )}

            <SectionHeader eyebrow="ब्यापार र बजार" />
            {articles.filter(a => a.tag === 'business').slice(0, 2).map(a => <NewsCard key={a.id} article={a} />)}
            {articles.filter(a => a.tag === 'business').length === 0 &&
              articles.filter(a => a.tag === 'nepal').slice(1, 3).map(a => <NewsCard key={a.id} article={a} />)}

            {ctx.user.plan === 'free' && (
              <div onClick={() => go('premium')} style={{ margin: '14px 16px', padding: 18,
                border: '1.5px solid var(--ink-1)', borderRadius: 14, cursor: 'pointer', background: 'var(--bg-elev)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                  <Icon name="sparkles" size={14} />
                  <span className="eyebrow" style={{ fontWeight: 700 }}>SAMACHAR PRO</span>
                  <span style={{ marginLeft: 'auto' }} className="meta">{ctx.user.ai_quota}/१० AI बाँकी</span>
                </div>
                <div className="serif" style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>
                  असीमित AI च्याट — रू ७९/महिना।
                </div>
                <div className="body" style={{ fontSize: 12.5 }}>
                  नेपालको जुनसुकै समाचारबारे सोध्नुहोस्। Samachar AI ले नेपालीमा विश्लेषण गर्छ।
                </div>
              </div>
            )}

            <SectionHeader eyebrow="राजनीति" />
            {articles.filter(a => a.tag === 'politics').slice(0, 2).map(a => <NewsCard key={a.id} article={a} />)}

            <SectionHeader eyebrow="अन्य समाचार" />
            {articles.slice(4).map(a => <NewsCard key={a.id} article={a} />)}
          </>
        )}

        {tab !== 'foryou' && articles.slice(1).map(a => <NewsCard key={a.id} article={a} />)}

        <div style={{ padding: '28px 20px 40px', textAlign: 'center', borderTop: '1px solid var(--rule)' }}>
          <div className="serif" style={{ fontSize: 15, fontStyle: 'italic', color: 'var(--ink-3)' }}>
            अहिलेका लागि यति नै।
          </div>
          {lastScan && <div className="meta" style={{ marginTop: 6 }}>अन्तिम स्क्यान: {lastScan}</div>}
        </div>
      </div>
    </>
  );
};
window.HomeScreen = HomeScreen;

// ─────────────────────── ARTICLE ───────────────────────
const ArticleScreen = ({ go }) => {
  const ctx = useApp();
  const [a, setA] = React.useState(null);
  const [comments, setComments] = React.useState([]);
  const [reply, setReply] = React.useState('');
  const [showFacts, setShowFacts] = React.useState(false);
  const lang = ctx.user?.language || 'np';

  React.useEffect(() => {
    if (!ctx.currentArticleId) return;
    setA(null);
    API.article(ctx.currentArticleId).then(setA);
    API.comments(ctx.currentArticleId).then(setComments);
  }, [ctx.currentArticleId]);

  if (!a) return <LoadingScreen msg="समाचार लोड हुँदैछ…" />;

  const title = (lang === 'np' && a.title_np) ? a.title_np : a.title;
  const bm = ctx.bookmarks.has(a.id);
  const biasColor = a.bias < 35 ? 'var(--info)' : a.bias > 65 ? 'var(--accent)' : 'var(--verify)';
  const biasNp = {
    'Center': 'तटस्थ', 'Center-Left': 'मध्य-वाम', 'Center-Right': 'मध्य-दायाँ',
    'Left-Center': 'वाम-मध्य', 'Pro-Market': 'बजार-समर्थक', 'Pro-Govt': 'सरकार-समर्थक',
  };

  const submitComment = async () => {
    if (!reply.trim()) return;
    try {
      const c = await API.postComment(a.id, reply.trim());
      setComments([c, ...comments]); setReply('');
      ctx.toast('टिप्पणी पोस्ट भयो');
    } catch (e) { ctx.toast(e.message); }
  };

  const vote = async (cid, currentVote, newVote) => {
    const v = currentVote === newVote ? 0 : newVote;
    try {
      const updated = await API.voteComment(cid, v);
      setComments(comments.map(c => c.id === cid ? { ...updated, my_vote: v || null } : c));
    } catch (e) { ctx.toast(e.message); }
  };

  const share = () => {
    if (navigator.share) navigator.share({ title: a.title, text: a.dek, url: a.source_url || '' }).catch(() => {});
    else { try { navigator.clipboard.writeText(a.title); ctx.toast('शीर्षक कपी भयो'); } catch (e) {} }
  };

  return (
    <div className="scrollable">
      {/* Header */}
      <div style={{ padding: '8px 20px 12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div onClick={() => go('back')} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
          <Icon name="arrow-left" size={16} /><span style={{ fontSize: 12.5, fontWeight: 600 }}>फिर्ता</span>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          <div className="iconbtn" style={{ width: 34, height: 34, color: bm ? 'var(--accent)' : 'var(--ink-1)' }}
            onClick={() => ctx.toggleBookmark(a.id)}><Icon name="bookmark" size={14} /></div>
          <div className="iconbtn" style={{ width: 34, height: 34 }} onClick={share}><Icon name="share" size={14} /></div>
        </div>
      </div>

      <div style={{ padding: '0 20px 18px' }}>
        {/* Category + source dot */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          {a.source_color && <span style={{ width: 8, height: 8, borderRadius: 999, background: a.source_color }} />}
          <span className="eyebrow">{a.category}</span>
        </div>

        <div className="h-display" style={{ fontSize: 26, marginBottom: 14 }}>{title}</div>
        <div style={{ fontSize: 15, fontStyle: 'italic', color: 'var(--ink-2)', fontFamily: 'var(--serif)',
          lineHeight: 1.5, marginBottom: 18 }}>{a.dek}</div>

        {/* Source meta */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 0',
          borderTop: '1px solid var(--rule)', borderBottom: '1px solid var(--rule)' }}>
          <div style={{ width: 32, height: 32, borderRadius: 999, background: a.source_color || 'var(--bg-sunk)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 11, fontWeight: 700, color: '#fff', fontFamily: 'var(--serif)' }}>
            {a.source.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 12.5, fontWeight: 600 }}>{a.source}</div>
            <div className="meta">{a.time_label}</div>
          </div>
          {a.source_url && (
            <a href={a.source_url} target="_blank" rel="noopener noreferrer"
              style={{ fontSize: 10.5, color: 'var(--info)', textDecoration: 'none', fontFamily: 'var(--mono)' }}>
              स्रोत ↗
            </a>
          )}
        </div>
      </div>

      {/* Image */}
      {a.img_url
        ? <img src={a.img_url} alt="" style={{ width: '100%', height: 200, objectFit: 'cover', marginBottom: 20 }}
            onError={e => { e.target.style.display = 'none'; }} />
        : <div className="ph" style={{ height: 180, marginBottom: 20 }}>
            <div className="ph-label">{a.source}</div>
          </div>}

      {/* AI Key Points (Nepali) */}
      {a.key_points && a.key_points.length > 0 && (
        <div style={{ margin: '0 20px 22px', padding: '18px 0',
          borderTop: '2px solid var(--ink-1)', borderBottom: '2px solid var(--ink-1)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 14 }}>
            <Icon name="sparkles" size={14} />
            <span className="eyebrow" style={{ fontWeight: 700 }}>AI सारांश · Samachar AI</span>
            <span style={{ marginLeft: 'auto', fontFamily: 'var(--mono)', fontSize: 10,
              color: ctx.user.plan === 'pro' ? 'var(--verify)' : 'var(--ink-3)' }}>
              {ctx.user.plan === 'pro' ? 'PRO ∞' : `${ctx.user.ai_quota}/१०`}
            </span>
          </div>
          <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
            {a.key_points.map((kp, i) => (
              <li key={i} style={{ display: 'flex', gap: 12, padding: '8px 0',
                borderBottom: i < a.key_points.length - 1 ? '1px dashed var(--rule)' : 'none' }}>
                <div className="mono" style={{ fontSize: 10, color: 'var(--ink-4)', minWidth: 18, paddingTop: 2 }}>
                  {String(i + 1).padStart(2, '0')}
                </div>
                <div style={{ fontSize: 14, color: 'var(--ink-1)', lineHeight: 1.55, fontFamily: 'var(--serif)' }}>{kp}</div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Why it matters */}
      {a.why_matters && (
        <div style={{ margin: '0 20px 22px', padding: 16, border: '1px solid var(--rule)',
          borderRadius: 12, background: 'var(--bg-elev)' }}>
          <div className="eyebrow" style={{ color: 'var(--verify)', marginBottom: 8 }}>
            तपाईंलाई किन महत्त्वपूर्ण
          </div>
          <div style={{ fontSize: 14, lineHeight: 1.6, fontFamily: 'var(--serif)' }}>{a.why_matters}</div>
        </div>
      )}

      {/* Body paragraphs */}
      <div style={{ padding: '0 20px' }}>
        {(a.body || []).map((p, i) => (
          <p key={i} className="serif" style={{ fontSize: 16, lineHeight: 1.7, margin: '0 0 18px' }}>
            {i === 0 && (
              <span style={{ fontSize: 46, float: 'left', lineHeight: 0.85,
                marginRight: 8, marginTop: 6, color: 'var(--accent)', fontWeight: 700 }}>{p[0]}</span>
            )}
            {i === 0 ? p.slice(1) : p}
          </p>
        ))}
      </div>

      {/* Bias meter */}
      {a.bias !== null && a.bias !== undefined && (
        <div style={{ margin: '0 20px 22px', padding: 18, border: '1px solid var(--rule)',
          borderRadius: 14, background: 'var(--bg-elev)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <div className="eyebrow">पक्षपात विश्लेषण</div>
            <span style={{ fontSize: 12, fontWeight: 700, color: biasColor }}>
              {biasNp[a.bias_label] || a.bias_label || 'तटस्थ'}
            </span>
          </div>
          <BiasMeter position={a.bias} size="lg" />
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
            <span className="meta">वाम</span>
            <span className="meta">तटस्थ</span>
            <span className="meta">दायाँ</span>
          </div>
          {ctx.user.plan !== 'pro' && (
            <div onClick={() => go('premium')} style={{ marginTop: 12, padding: '10px 12px',
              background: 'var(--bg-sunk)', borderRadius: 8, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Icon name="chart" size={13} color="var(--ink-3)" />
              <span style={{ fontSize: 12, color: 'var(--ink-2)' }}>Pro: सबै स्रोतको तुलनात्मक विश्लेषण हेर्नुहोस्</span>
              <Icon name="chevron-right" size={12} color="var(--ink-3)" />
            </div>
          )}
        </div>
      )}

      {/* Source verification */}
      <div style={{ margin: '0 20px 22px' }}>
        <div onClick={() => setShowFacts(!showFacts)} style={{ padding: 14,
          border: '1px solid var(--verify)', borderRadius: 12,
          display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer', background: 'var(--verify-soft)' }}>
          <Icon name="shield-check" size={17} color="var(--verify)" />
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--verify)' }}>
              प्रकाशित स्रोत — {a.source}
            </div>
            <div className="meta" style={{ color: 'var(--verify)', opacity: .7 }}>मूल लिङ्क हेर्न थिच्नुहोस्</div>
          </div>
          <Icon name="chevron-down" size={13} color="var(--verify)"
            style={{ transform: showFacts ? 'rotate(180deg)' : 'none', transition: '.2s' }} />
        </div>
        {showFacts && a.source_url && (
          <div style={{ padding: '12px 14px', border: '1px solid var(--rule)', borderTop: 'none',
            borderRadius: '0 0 12px 12px', background: 'var(--bg-elev)' }}>
            <a href={a.source_url} target="_blank" rel="noopener noreferrer"
              style={{ fontSize: 12, color: 'var(--info)', wordBreak: 'break-all' }}>{a.source_url}</a>
          </div>
        )}
      </div>

      {/* Action buttons */}
      <div style={{ margin: '0 20px 22px', display: 'flex', gap: 8 }}>
        <button className="btn btn-ghost" style={{ flex: 1, justifyContent: 'center' }} onClick={share}>
          <Icon name="share" size={13} /> साझा
        </button>
        <button className="btn btn-ghost" style={{ flex: 1, justifyContent: 'center' }}
          onClick={() => ctx.toggleBookmark(a.id)}>
          <Icon name="bookmark" size={13} /> {bm ? 'सेभ भयो' : 'सेभ'}
        </button>
        <button className="btn btn-primary" style={{ flex: 1, justifyContent: 'center' }} onClick={() => go('ai')}>
          <Icon name="sparkles" size={13} /> AI सोध्नुहोस्
        </button>
      </div>

      {/* Comments */}
      <SectionHeader eyebrow={`टिप्पणीहरू · ${comments.length}`} />
      <div style={{ padding: '0 20px 14px' }}>
        <div style={{ padding: '12px 14px', border: '1px solid var(--rule)', borderRadius: 12,
          background: 'var(--bg-elev)', display: 'flex', gap: 10, marginBottom: 14 }}>
          <input value={reply} onChange={e => setReply(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && submitComment()}
            placeholder="आफ्नो विचार लेख्नुहोस्…"
            style={{ flex: 1, border: 'none', outline: 'none', background: 'transparent', fontSize: 13, color: 'var(--ink-1)' }} />
          <Icon name="send" size={15} color={reply.trim() ? 'var(--ink-1)' : 'var(--ink-4)'}
            style={{ cursor: 'pointer' }} onClick={submitComment} />
        </div>
        {comments.length === 0 ? (
          <div style={{ padding: '20px', textAlign: 'center' }}>
            <div className="serif" style={{ fontSize: 14, fontStyle: 'italic', color: 'var(--ink-3)' }}>
              पहिलो टिप्पणी गर्नुहोस्।
            </div>
          </div>
        ) : comments.map((c, i) => (
          <div key={c.id} style={{ padding: '14px 0', borderTop: i === 0 ? '1px solid var(--ink-1)' : '1px solid var(--rule)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
              <div style={{ width: 28, height: 28, borderRadius: 999, background: 'var(--bg-sunk)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontFamily: 'var(--serif)', fontSize: 11, fontWeight: 700 }}>{c.initials}</div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 12.5, fontWeight: 600 }}>{c.name}</div>
                <div className="meta">{c.place}</div>
              </div>
              {c.verified ? <Icon name="check-circle" size={14} color="var(--verify)" /> : null}
            </div>
            <div className="serif" style={{ fontSize: 14, lineHeight: 1.55, marginBottom: 8 }}>{c.text}</div>
            <div style={{ display: 'flex', gap: 14 }}>
              <div onClick={() => vote(c.id, c.my_vote, 1)}
                style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11.5, cursor: 'pointer',
                  color: c.my_vote === 1 ? 'var(--verify)' : 'var(--ink-3)' }}>
                <Icon name="thumb-up" size={13} /> {c.likes}
              </div>
              <div onClick={() => vote(c.id, c.my_vote, -1)}
                style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11.5, cursor: 'pointer',
                  color: c.my_vote === -1 ? 'var(--accent)' : 'var(--ink-3)' }}>
                <Icon name="thumb-down" size={13} /> {c.dislikes}
              </div>
            </div>
          </div>
        ))}
      </div>
      <div style={{ height: 40 }} />
    </div>
  );
};
window.ArticleScreen = ArticleScreen;

// ───────────────────── DISCOVER ─────────────────────
const DiscoverScreen = ({ go }) => {
  const ctx = useApp();
  const [trends, setTrends] = React.useState([]);
  const [sources, setSources] = React.useState([]);
  const [aiQ, setAiQ] = React.useState('');

  // Local area news state
  const [localAddr, setLocalAddr] = React.useState('');
  const [localResult, setLocalResult] = React.useState(null);
  const [localBusy, setLocalBusy] = React.useState(false);

  React.useEffect(() => {
    API.trends().then(setTrends);
    API.sources().then(setSources).catch(() => {});
  }, []);

  const askAi = q => { if (!q.trim()) return; ctx.setPendingAi(q); go('ai'); };
  const doSearch = q => { ctx.setSearchQuery(q); go('search'); };

  const searchLocal = async () => {
    if (!localAddr.trim()) return;
    setLocalBusy(true);
    setLocalResult(null);
    try {
      const res = await API.localNews(localAddr.trim());
      setLocalResult(res);
    } catch (e) {
      setLocalResult({ error: e.message, articles: [], location: localAddr });
    } finally { setLocalBusy(false); }
  };

  const heatColor = { hot: 'var(--accent)', breaking: 'var(--warn)', rising: 'var(--verify)', new: 'var(--info)' };
  const heatNp = { hot: 'तातो', breaking: 'ब्रेकिङ', rising: 'बढ्दो', new: 'नयाँ' };

  const suggested = [
    'NEPSE आज कति बढ्यो?',
    'नेपालको संघीय बजेटको सारांश',
    'मनसुनले कहाँ कहाँ असर गर्‍यो?',
    'नेपाल क्रिकेट टिमको अवस्था के छ?',
    'नेपालमा सुनको मूल्य कति छ?',
  ];

  return (
    <>
      <div className="topbar">
        <div className="serif" style={{ fontSize: 22, fontWeight: 700 }}>खोज्नुहोस्</div>
        <div className="iconbtn" onClick={() => go('settings')}><Icon name="settings" size={14} /></div>
      </div>

      {/* AI Ask bar */}
      <div style={{ margin: '0 16px 10px', padding: '14px 16px', background: 'var(--ink-1)',
        borderRadius: 14, display: 'flex', alignItems: 'center', gap: 10, color: 'var(--bg-elev)' }}>
        <Icon name="sparkles" size={16} />
        <input value={aiQ} onChange={e => setAiQ(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && askAi(aiQ)}
          placeholder="AI लाई नेपालीमा सोध्नुहोस्…"
          style={{ flex: 1, background: 'transparent', border: 'none', outline: 'none',
            color: 'var(--bg-elev)', fontSize: 13.5 }} />
        <div onClick={() => askAi(aiQ)} style={{ cursor: 'pointer', opacity: aiQ ? 1 : 0.5 }}>
          <Icon name="send" size={16} />
        </div>
      </div>

      {/* Text search bar */}
      <div onClick={() => doSearch(aiQ || '')}
        style={{ margin: '0 16px 14px', padding: '12px 14px', background: 'var(--bg-elev)',
          border: '1px solid var(--rule)', borderRadius: 14, display: 'flex', alignItems: 'center',
          gap: 10, cursor: 'pointer' }}>
        <Icon name="search" size={15} color="var(--ink-3)" />
        <span style={{ flex: 1, color: 'var(--ink-3)', fontSize: 13 }}>समाचार खोज्नुहोस्…</span>
        <span className="meta">↵</span>
      </div>

      <div className="scrollable">
        {/* ── LOCAL AREA NEWS ── */}
        <SectionHeader eyebrow="स्थानीय समाचार" title="आफ्नो ठेगाना खोज्नुहोस्" />
        <div style={{ padding: '0 16px 8px' }}>
          <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
            <input className="input-field" style={{ flex: 1, marginBottom: 0 }}
              placeholder="जस्तै: बानेश्वर, पोखरा-१६, बुटवल…"
              value={localAddr} onChange={e => setLocalAddr(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && searchLocal()} />
            <button className="btn btn-primary" style={{ padding: '10px 16px', borderRadius: 12 }}
              onClick={searchLocal} disabled={localBusy || !localAddr.trim()}>
              {localBusy ? <span className="loader" style={{ borderTopColor: 'var(--bg-elev)' }} /> : 'खोज'}
            </button>
          </div>

          {/* Local result */}
          {localResult && (
            <div style={{ border: '1px solid var(--rule)', borderRadius: 14, overflow: 'hidden', marginBottom: 8 }}>
              {/* AI summary */}
              {localResult.ai_summary && (
                <div style={{ padding: '14px 16px', background: 'var(--bg-elev)', borderBottom: '1px solid var(--rule)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 10 }}>
                    <Icon name="sparkles" size={13} />
                    <span className="eyebrow">{localResult.location} · AI सारांश</span>
                  </div>
                  <div className="serif" style={{ fontSize: 14, lineHeight: 1.6, color: 'var(--ink-1)' }}>
                    {localResult.ai_summary.answer}
                  </div>
                  {localResult.ai_summary.sources?.length > 0 && (
                    <div style={{ marginTop: 10, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      {localResult.ai_summary.sources.map((s, i) => (
                        <span key={i} className="tag">{s}</span>
                      ))}
                    </div>
                  )}
                </div>
              )}
              {/* Articles */}
              {localResult.articles?.length > 0 ? (
                localResult.articles.slice(0, 5).map(a => <NewsCard key={a.id} article={a} />)
              ) : (
                <div style={{ padding: '20px 16px', textAlign: 'center' }}>
                  <div className="meta">"{localResult.location}" सम्बन्धी समाचार फेला परेन।</div>
                  <div style={{ marginTop: 8 }}>
                    <span onClick={() => askAi(`${localResult.location} मा के भइरहेको छ?`)}
                      style={{ fontSize: 12, color: 'var(--info)', cursor: 'pointer', textDecoration: 'underline' }}>
                      AI लाई सोध्नुहोस् →
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Quick location chips */}
          {!localResult && (
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {['काठमाडौं', 'पोखरा', 'बुटवल', 'विराटनगर', 'धनगढी', 'हेटौँडा'].map(loc => (
                <span key={loc} onClick={() => { setLocalAddr(loc); setTimeout(searchLocal, 100); }}
                  className="pill" style={{ fontSize: 12 }}>{loc}</span>
              ))}
            </div>
          )}
        </div>

        {/* ── TRENDING ── */}
        <SectionHeader eyebrow="ट्रेन्डिङ · नेपाल" />
        <div style={{ padding: '0 16px 18px' }}>
          {trends.length === 0 && (
            <div className="meta" style={{ padding: '10px 4px' }}>पहिलो स्क्यान पछि ट्रेन्ड अपडेट हुन्छ।</div>
          )}
          {trends.map((t, i) => (
            <div key={t.rank} onClick={() => doSearch(t.title)}
              style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '14px 0',
                borderTop: i === 0 ? '1px solid var(--ink-1)' : '1px solid var(--rule)', cursor: 'pointer' }}>
              <div className="serif" style={{ fontSize: 24, fontWeight: 700, minWidth: 30, color: 'var(--ink-3)' }}>
                {String(t.rank).padStart(2, '0')}
              </div>
              <div style={{ flex: 1 }}>
                <div className="serif" style={{ fontSize: 15, fontWeight: 600 }}>{t.title}</div>
                <div className="meta" style={{ marginTop: 2 }}>{t.sub}</div>
              </div>
              <span className="tag" style={{ background: 'transparent',
                color: heatColor[t.heat], border: `1px solid ${heatColor[t.heat]}` }}>
                {heatNp[t.heat] || t.heat}
              </span>
            </div>
          ))}
        </div>

        {/* ── AI SUGGESTIONS ── */}
        <SectionHeader eyebrow="AI सँग सोध्नुहोस्" />
        <div style={{ padding: '0 16px 14px', display: 'flex', flexDirection: 'column', gap: 8 }}>
          {suggested.map((qq, i) => (
            <div key={i} onClick={() => askAi(qq)} style={{ padding: '13px 15px', background: 'var(--bg-elev)',
              border: '1px solid var(--rule)', borderRadius: 12,
              display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}>
              <span className="serif" style={{ fontSize: 14 }}>{qq}</span>
              <Icon name="arrow-up-right" size={13} color="var(--ink-3)" />
            </div>
          ))}
        </div>

        {/* ── NEWS SOURCES ── */}
        {sources.length > 0 && (
          <>
            <SectionHeader eyebrow="समाचार स्रोतहरू" title="हाम्रा स्रोतहरू" />
            <div style={{ padding: '0 16px 30px', display: 'flex', flexDirection: 'column', gap: 6 }}>
              {sources.map(s => (
                <div key={s.id} style={{ padding: '12px 14px', background: 'var(--bg-elev)',
                  border: '1px solid var(--rule)', borderRadius: 12,
                  display: 'flex', alignItems: 'center', gap: 12 }}>
                  <span style={{ width: 10, height: 10, borderRadius: 999, background: s.color, flexShrink: 0 }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13.5, fontWeight: 600 }}>{s.name}</div>
                    <div className="meta" style={{ marginTop: 1 }}>{s.bias_label} · नेपाली</div>
                  </div>
                  <div>
                    <div style={{ width: 48, height: 4, background: 'var(--bg-sunk)', borderRadius: 2, overflow: 'hidden' }}>
                      <div style={{ width: `${s.bias}%`, height: '100%', borderRadius: 2,
                        background: s.bias < 40 ? 'var(--info)' : s.bias > 60 ? 'var(--accent)' : 'var(--verify)' }} />
                    </div>
                    <div className="mono" style={{ fontSize: 9, marginTop: 2, textAlign: 'right', color: 'var(--ink-3)' }}>
                      {s.bias}/१००
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </>
  );
};
window.DiscoverScreen = DiscoverScreen;

// ────────────────────── SEARCH ──────────────────────
const TOPIC_PILLS = [
  { id: '', label: 'सबै' },
  { id: 'POLITICS', label: 'राजनीति' },
  { id: 'BUSINESS', label: 'व्यापार' },
  { id: 'TECHNOLOGY', label: 'प्रविधि' },
  { id: 'SPORTS', label: 'खेलकुद' },
  { id: 'HEALTH', label: 'स्वास्थ्य' },
  { id: 'CLIMATE', label: 'वातावरण' },
  { id: 'AGRICULTURE', label: 'कृषि' },
];

const SearchResultsScreen = ({ go }) => {
  const ctx = useApp();
  const isPro = ctx.user?.plan === 'pro';
  const [q, setQ] = React.useState(ctx.searchQuery || '');
  const [activeTopic, setActiveTopic] = React.useState('');
  const [mode, setMode] = React.useState('archive'); // 'archive' | 'web'
  const [results, setResults] = React.useState([]);
  const [web, setWeb] = React.useState(null);  // { results, pro_required, message, total }
  const [busy, setBusy] = React.useState(false);
  const inputRef = React.useRef(null);

  React.useEffect(() => { inputRef.current?.focus(); }, []);

  // Local archive search
  React.useEffect(() => {
    if (mode !== 'archive') return;
    const t = setTimeout(async () => {
      setBusy(true);
      try {
        const params = {};
        if (q.trim()) params.q = q.trim();
        if (activeTopic) params.topic = activeTopic;
        if (!q.trim() && !activeTopic) params.limit = 40;
        const res = await API.articles(params);
        setResults(res);
      } finally { setBusy(false); }
    }, 300);
    return () => clearTimeout(t);
  }, [q, activeTopic, mode]);

  // Internet-wide web search (PRO) — detects romanized Nepali server-side
  React.useEffect(() => {
    if (mode !== 'web') return;
    if (!q.trim()) { setWeb(null); return; }
    const t = setTimeout(async () => {
      setBusy(true);
      try {
        const res = await API.searchWeb(q.trim());
        setWeb(res);
      } catch (e) {
        setWeb({ results: [], error: e.message });
      } finally { setBusy(false); }
    }, 450);
    return () => clearTimeout(t);
  }, [q, mode]);

  return (
    <>
      <div className="topbar" style={{ paddingBottom: 8 }}>
        <div onClick={() => go('back')} style={{ cursor: 'pointer' }}>
          <Icon name="arrow-left" size={16} />
        </div>
        <div style={{ flex: 1, margin: '0 10px', padding: '9px 14px', background: 'var(--bg-elev)',
          border: '1px solid var(--rule)', borderRadius: 12, display: 'flex', alignItems: 'center', gap: 9 }}>
          <Icon name="search" size={13} color="var(--ink-3)" />
          <input ref={inputRef} value={q} onChange={e => setQ(e.target.value)}
            placeholder="शब्द वा वाक्यांश खोज्नुहोस्…"
            style={{ flex: 1, border: 'none', outline: 'none', background: 'transparent', fontSize: 13.5 }} />
          {q && <Icon name="x" size={13} color="var(--ink-3)" onClick={() => setQ('')} style={{ cursor: 'pointer' }} />}
        </div>
      </div>

      {/* Search-scope toggle: our archive vs the whole internet (PRO) */}
      <div style={{ display: 'flex', gap: 8, padding: '2px 16px 8px' }}>
        <span className="pill" data-on={mode === 'archive'} onClick={() => setMode('archive')}
          style={{ fontSize: 12, display: 'inline-flex', alignItems: 'center', gap: 5, cursor: 'pointer' }}>
          <Icon name="search" size={11} /> हाम्रो संग्रह
        </span>
        <span className="pill" data-on={mode === 'web'} onClick={() => setMode('web')}
          style={{ fontSize: 12, display: 'inline-flex', alignItems: 'center', gap: 5, cursor: 'pointer' }}>
          <Icon name="globe" size={11} /> इन्टरनेटभरि
          {!isPro && <span style={{ fontSize: 9, fontWeight: 800, color: 'var(--accent)' }}>PRO</span>}
        </span>
      </div>

      {/* Topic filter pills — only for the local archive */}
      {mode === 'archive' && (
        <div className="pill-row" style={{ paddingTop: 0, paddingBottom: 10 }}>
          {TOPIC_PILLS.map(tp => (
            <Pill key={tp.id} on={activeTopic === tp.id} onClick={() => setActiveTopic(tp.id)}>
              {tp.label}
            </Pill>
          ))}
        </div>
      )}

      {/* ── Internet-wide web search results ── */}
      {mode === 'web' && (
        <div className="scrollable">
          <div style={{ padding: '6px 20px 10px' }} className="meta">
            {busy ? 'इन्टरनेटभरि खोजिँदैछ…'
              : !q.trim() ? 'कुनै पनि शब्द लेख्नुहोस् — इन्टरनेटभरिका नेपाली स्रोतहरूबाट खोज्छौं। (नेपाली रोमनमा पनि लेख्न सक्नुहुन्छ)'
              : web ? `${web.total ?? (web.results || []).length} परिणाम · "${q}"` : ''}
          </div>

          {/* Romanized → Devanagari hint */}
          {web && web.expanded && web.expanded.devanagari && (
            <div style={{ padding: '0 20px 8px' }}>
              <span className="tag" style={{ background: 'var(--bg-elev)' }}>
                खोजी: {web.expanded.devanagari}
              </span>
            </div>
          )}

          {(web?.results || []).map((r, i) => (
            <a key={i} href={r.url} target="_blank" rel="noopener noreferrer"
              style={{ display: 'block', padding: '13px 20px', borderBottom: '1px solid var(--rule)',
                textDecoration: 'none', color: 'inherit' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 5 }}>
                <Icon name="globe" size={11} color="var(--ink-3)" />
                <span className="eyebrow" style={{ fontSize: 9.5, color: 'var(--ink-3)' }}>
                  {r.source}{r.published ? ' · ' + (r.published || '').slice(0, 16) : ''}
                </span>
              </div>
              <div className="serif" style={{ fontSize: 15, fontWeight: 600, lineHeight: 1.35 }}>{r.title}</div>
              {r.snippet && (
                <div className="body" style={{ fontSize: 12.5, marginTop: 5, color: 'var(--ink-2)', lineHeight: 1.5 }}>
                  {r.snippet}
                </div>
              )}
            </a>
          ))}

          {/* PRO upsell when the server only returned a preview */}
          {web && web.pro_required && (
            <div style={{ margin: '16px 20px 30px', padding: 18, borderRadius: 14,
              border: '1px solid var(--accent)', background: 'var(--accent-soft)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <Icon name="globe" size={16} color="var(--accent)" />
                <span className="serif" style={{ fontSize: 15, fontWeight: 700, color: 'var(--accent)' }}>
                  इन्टरनेटभरि पूर्ण खोज — PRO
                </span>
              </div>
              <div className="body" style={{ fontSize: 13, lineHeight: 1.55, marginBottom: 12 }}>
                {web.message || 'इन्टरनेटभरि नेपाली समाचार खोज्न Samachar PRO चाहिन्छ।'}
              </div>
              <button className="btn btn-primary" onClick={() => go('premium')}>
                <Icon name="sparkles" size={13} /> PRO मा अपग्रेड गर्नुहोस्
              </button>
            </div>
          )}

          {!busy && q.trim() && web && (web.results || []).length === 0 && !web.pro_required && (
            <div style={{ padding: '40px 24px', textAlign: 'center' }}>
              <Icon name="globe" size={28} color="var(--ink-4)" />
              <div className="serif" style={{ fontSize: 16, fontWeight: 600, marginTop: 14 }}>
                इन्टरनेटमा केही फेला परेन।
              </div>
              <button className="btn btn-primary" style={{ marginTop: 16 }}
                onClick={() => { ctx.setPendingAi(q); go('ai'); }}>
                <Icon name="sparkles" size={13} /> AI लाई सोध्नुहोस्
              </button>
            </div>
          )}
        </div>
      )}

      {mode === 'archive' && <div className="scrollable">
        <div style={{ padding: '6px 20px 10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div className="meta">
            {busy ? 'खोजिँदैछ…' : `${results.length} परिणाम${q ? ` · "${q}"` : ''}${activeTopic ? ` · ${TOPIC_PILLS.find(p=>p.id===activeTopic)?.label}` : ''}`}
          </div>
        </div>

        {!busy && results.length === 0 && (
          <div style={{ padding: '40px 24px', textAlign: 'center' }}>
            <Icon name="search" size={28} color="var(--ink-4)" />
            <div className="serif" style={{ fontSize: 16, fontWeight: 600, marginTop: 14 }}>
              कुनै समाचार फेला परेन।
            </div>
            <div className="body" style={{ fontSize: 13, marginTop: 8, marginBottom: 18 }}>
              AI ले यो विषयमा विश्लेषण गर्न सक्छ।
            </div>
            {q && (
              <button className="btn btn-primary" onClick={() => { ctx.setPendingAi(q); go('ai'); }}>
                <Icon name="sparkles" size={13} /> AI लाई सोध्नुहोस्: "{q}"
              </button>
            )}
          </div>
        )}

        {results.map(a => <NewsCard key={a.id} article={a} />)}

        {/* Always-visible AI prompt */}
        {results.length > 0 && q && (
          <div style={{ padding: '16px 20px 30px' }}>
            <div onClick={() => { ctx.setPendingAi(q); go('ai'); }}
              style={{ padding: '13px 15px', border: '1px dashed var(--rule)', borderRadius: 12,
                display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer', background: 'var(--bg-elev)' }}>
              <Icon name="sparkles" size={14} color="var(--ink-3)" />
              <span style={{ flex: 1, fontSize: 13, color: 'var(--ink-2)' }}>
                "{q}" बारे AI विश्लेषण पाउनुहोस्
              </span>
              <Icon name="arrow-right" size={13} color="var(--ink-3)" />
            </div>
          </div>
        )}
      </div>}
    </>
  );
};
window.SearchResultsScreen = SearchResultsScreen;

// ───────────────────── AI CHAT ─────────────────────
const AiChatScreen = ({ go }) => {
  const ctx = useApp();
  const lang = ctx.user?.language || 'np';
  const [messages, setMessages] = React.useState([]);
  const [input, setInput] = React.useState('');
  const [typing, setTyping] = React.useState(false);
  const scrollRef = React.useRef(null);
  const sent = React.useRef(false);

  const send = async (text) => {
    const q = (text || input).trim();
    if (!q) return;
    setMessages(m => [...m, { role: 'user', text: q }]);
    setInput('');
    setTyping(true);
    try {
      const res = await API.askAi(q, lang);
      if (res.quota_exceeded) {
        setMessages(m => [...m, { role: 'system', text: res.message || 'दैनिक सीमा समाप्त भयो। Pro मा अपग्रेड गर्नुहोस्।' }]);
      } else {
        setMessages(m => [...m, { role: 'ai', text: res.answer, sources: res.sources, related: res.related }]);
        await ctx.refreshUser();
      }
    } catch (e) {
      if (e.status === 429) {
        setMessages(m => [...m, { role: 'system', text: e.body?.message || 'दैनिक AI सीमा समाप्त भयो। Pro मा अपग्रेड गर्नुहोस्।' }]);
      } else {
        setMessages(m => [...m, { role: 'system', text: 'त्रुटि: ' + e.message }]);
      }
    } finally { setTyping(false); }
  };

  React.useEffect(() => {
    if (ctx.pendingAi && !sent.current) {
      sent.current = true;
      const q = ctx.pendingAi;
      ctx.setPendingAi(null);
      send(q);
    }
  }, []);

  React.useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, typing]);

  const isPro = ctx.user?.plan === 'pro';
  const quota = ctx.user?.ai_quota ?? 0;

  const suggested = lang === 'np' ? [
    'NEPSE आज कति बढ्यो र किन?',
    'नेपालको संघीय बजेटको मुख्य कुराहरू के के छन्?',
    'मनसुनले नेपालमा कहाँ कहाँ असर गर्‍यो?',
    'नेपाल क्रिकेट टिमको ताजा अवस्था?',
    'नेपालमा सुन किन महँगो भइरहेको छ?',
  ] : [
    'Why is NEPSE rallying today?',
    'Summarise the federal budget key points',
    'What districts are flood-affected this monsoon?',
    'Latest on Nepal cricket team',
    'Why is gold price rising in Nepal?',
  ];

  return (
    <>
      <div className="topbar">
        <div onClick={() => go('back')} style={{ cursor: 'pointer' }}><Icon name="arrow-left" size={16} /></div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Icon name="sparkles" size={14} />
          <span className="serif" style={{ fontSize: 17, fontWeight: 700 }}>
            AI · Samachar AI
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {!isPro && quota <= 3 && (
            <span onClick={() => go('premium')}
              style={{ fontSize: 11, color: 'var(--accent)', cursor: 'pointer', fontWeight: 700 }}>UPGRADE</span>
          )}
          <span className="mono" style={{ fontSize: 11 }}>{isPro ? '∞' : `${quota}/१०`}</span>
        </div>
      </div>

      {/* Quota bar */}
      {!isPro && (
        <div style={{ height: 3, background: 'var(--bg-sunk)' }}>
          <div style={{ width: `${Math.min(100, quota * 10)}%`, height: '100%', transition: 'width .3s',
            background: quota <= 3 ? 'var(--accent)' : 'var(--verify)' }} />
        </div>
      )}

      {/* Language toggle */}
      <div style={{ display: 'flex', padding: '6px 16px', gap: 6 }}>
        {[{ v: 'np', l: 'नेपाली' }, { v: 'en', l: 'English' }].map(opt => (
          <span key={opt.v} onClick={() => ctx.setUser && API.updatePrefs({ language: opt.v }).then(() => ctx.refreshUser())}
            className="pill" data-on={lang === opt.v} style={{ fontSize: 11.5 }}>{opt.l}</span>
        ))}
        <span style={{ flex: 1 }} />
        <span className="meta" style={{ alignSelf: 'center' }}>AI जवाफको भाषा</span>
      </div>

      <div ref={scrollRef} className="scrollable" style={{ padding: '8px 16px 12px' }}>
        {messages.length === 0 && (
          <div style={{ padding: '12px 4px' }}>
            {/* Model info card */}
            <div style={{ padding: 16, border: '1px solid var(--rule)', borderRadius: 14,
              background: 'var(--bg-elev)', marginBottom: 18 }}>
              <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 8 }}>
                <div style={{ width: 36, height: 36, borderRadius: 10, background: 'var(--bg-sunk)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Icon name="sparkles" size={18} />
                </div>
                <div>
                  <div className="serif" style={{ fontSize: 15, fontWeight: 600 }}>Samachar AI</div>
                  <div className="meta">Samachar AI · नेपाली सहायक</div>
                </div>
              </div>
              <div style={{ fontSize: 13, color: 'var(--ink-2)', lineHeight: 1.55 }}>
                {lang === 'np'
                  ? 'नेपालको राजनीति, अर्थतन्त्र, खेलकुद, मनसुन, NEPSE जुनसुकै विषयमा सोध्नुहोस् — नेपालीमा उत्तर पाउनुहुन्छ।'
                  : 'Ask anything about Nepal — politics, economy, sports, monsoon, NEPSE. I answer using real headlines.'}
              </div>
            </div>
            <div className="eyebrow" style={{ marginBottom: 10 }}>
              {lang === 'np' ? 'सुझाव' : 'SUGGESTIONS'}
            </div>
            {suggested.map((qq, i) => (
              <div key={i} onClick={() => send(qq)} style={{ padding: '12px 14px', marginBottom: 8,
                border: '1px solid var(--rule)', borderRadius: 12, background: 'var(--bg-elev)',
                cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="serif" style={{ fontSize: 13.5 }}>{qq}</span>
                <Icon name="arrow-right" size={13} color="var(--ink-3)" />
              </div>
            ))}
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start', marginBottom: 14 }}>
            {m.role === 'ai' && (
              <div style={{ width: 28, height: 28, borderRadius: 999, background: 'var(--bg-sunk)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginRight: 8, marginTop: 4 }}>
                <Icon name="sparkles" size={13} />
              </div>
            )}
            <div style={{
              maxWidth: '82%', padding: '12px 14px', borderRadius: 16,
              background: m.role === 'user' ? 'var(--ink-1)' : m.role === 'system' ? 'var(--accent-soft)' : 'var(--bg-elev)',
              color: m.role === 'user' ? 'var(--bg-elev)' : m.role === 'system' ? 'var(--accent)' : 'var(--ink-1)',
              border: m.role === 'ai' ? '1px solid var(--rule)' : 'none',
              fontSize: 14, lineHeight: 1.6,
              fontFamily: m.role !== 'user' ? 'var(--serif)' : 'var(--sans)',
            }}>
              {m.role === 'ai' && (
                <div className="eyebrow" style={{ marginBottom: 7, color: 'var(--ink-3)', fontSize: 9.5 }}>
                  SAMACHAR AI · {m.sources?.length || 0} स्रोत
                </div>
              )}
              {m.text}
              {m.role === 'ai' && m.sources && m.sources.length > 0 && (
                <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px dashed var(--rule)',
                  display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {m.sources.map((s, j) => <span key={j} className="tag">{s}</span>)}
                </div>
              )}
              {m.role === 'ai' && m.related && m.related.length > 0 && (
                <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px dashed var(--rule)' }}>
                  <div className="eyebrow" style={{ marginBottom: 8, color: 'var(--ink-3)', fontSize: 9.5 }}>
                    इन्टरनेटका स्रोतहरू
                  </div>
                  {m.related.map((r, j) => (
                    <a key={j} href={r.url} target="_blank" rel="noopener noreferrer"
                      style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 10px', marginBottom: 6,
                        border: '1px solid var(--rule)', borderRadius: 10, background: 'var(--bg)',
                        textDecoration: 'none', color: 'var(--ink-1)' }}>
                      <Icon name="globe" size={12} color="var(--ink-3)" />
                      <span style={{ flex: 1, fontSize: 12.5, lineHeight: 1.4, fontFamily: 'var(--sans)' }}>
                        {r.title}
                        <span style={{ color: 'var(--ink-3)', fontSize: 11 }}> · {r.source}</span>
                      </span>
                      <Icon name="arrow-right" size={12} color="var(--ink-3)" />
                    </a>
                  ))}
                </div>
              )}
              {m.role === 'system' && (
                <div style={{ marginTop: 10 }}>
                  <span onClick={() => go('premium')}
                    style={{ fontSize: 12, fontWeight: 700, cursor: 'pointer', textDecoration: 'underline' }}>
                    Pro मा अपग्रेड गर्नुहोस् →
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}

        {typing && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <div style={{ width: 28, height: 28, borderRadius: 999, background: 'var(--bg-sunk)',
              display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Icon name="sparkles" size={13} />
            </div>
            <div style={{ padding: '14px 16px', borderRadius: 16, background: 'var(--bg-elev)', border: '1px solid var(--rule)' }}>
              <span className="wave"><i /><i style={{ animationDelay: '.15s' }} /><i style={{ animationDelay: '.3s' }} /></span>
            </div>
          </div>
        )}
      </div>

      <div style={{ padding: '8px 16px 14px', borderTop: '1px solid var(--rule)', background: 'var(--bg)' }}>
        <div style={{ display: 'flex', gap: 8, padding: '10px 14px', background: 'var(--bg-elev)',
          border: '1px solid var(--rule)', borderRadius: 16, alignItems: 'center' }}>
          <input value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !typing && send()}
            placeholder={lang === 'np' ? 'केही पनि सोध्नुहोस्…' : 'Ask anything about Nepal…'}
            style={{ flex: 1, border: 'none', outline: 'none', background: 'transparent', fontSize: 14 }} />
          <button className="btn btn-primary" style={{ padding: '8px 12px', borderRadius: 10 }}
            onClick={() => send()} disabled={!input.trim() || typing}>
            <Icon name="send" size={14} />
          </button>
        </div>
        {!isPro && (
          <div className="meta" style={{ textAlign: 'center', marginTop: 6 }}>
            {quota} प्रश्न बाँकी · <span onClick={() => go('premium')} style={{ color: 'var(--accent)', cursor: 'pointer' }}>Pro: असीमित</span>
          </div>
        )}
      </div>
    </>
  );
};
window.AiChatScreen = AiChatScreen;

// ──────────────────── BOOKMARKS ────────────────────
const BookmarksScreen = ({ go }) => {
  const [saved, setSaved] = React.useState(null);
  React.useEffect(() => { API.bookmarks().then(setSaved); }, []);

  return (
    <>
      <div className="topbar">
        <div onClick={() => go('back')} style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
          <Icon name="arrow-left" size={16} /><span style={{ fontSize: 12.5, fontWeight: 600 }}>फिर्ता</span>
        </div>
        <div className="serif" style={{ fontSize: 18, fontWeight: 700 }}>सेभ गरिएका</div>
        <span style={{ width: 50 }} />
      </div>
      <div className="scrollable" style={{ paddingBottom: 30 }}>
        {saved === null ? <LoadingScreen /> : saved.length === 0 ? (
          <div style={{ padding: '60px 24px', textAlign: 'center' }}>
            <Icon name="bookmark" size={32} color="var(--ink-4)" />
            <div className="serif" style={{ fontSize: 18, fontWeight: 600, marginTop: 14 }}>
              कुनै समाचार सेभ गरिएको छैन
            </div>
            <div className="body" style={{ fontSize: 13, marginTop: 8 }}>
              समाचारको बुकमार्क आइकन थिचेर सेभ गर्नुहोस्।
            </div>
          </div>
        ) : (
          <>
            <div style={{ padding: '12px 20px 4px' }} className="meta">{saved.length} सेभ गरिएका</div>
            {saved.map(a => <NewsCard key={a.id} article={a} />)}
          </>
        )}
      </div>
    </>
  );
};
window.BookmarksScreen = BookmarksScreen;

// ────────────────── NOTIFICATIONS ──────────────────
const NotificationsScreen = ({ go }) => {
  const ctx = useApp();
  const [notifs, setNotifs] = React.useState([]);
  React.useEffect(() => { API.notifications().then(setNotifs); }, []);

  const markAll = async () => {
    await API.markAllRead();
    setNotifs(notifs.map(n => ({ ...n, is_read: 1 })));
    ctx.refreshUnreadCount();
  };

  const tap = async (n) => {
    if (!n.is_read) {
      await API.markRead(n.id);
      setNotifs(notifs.map(x => x.id === n.id ? { ...x, is_read: 1 } : x));
      ctx.refreshUnreadCount();
    }
  };

  return (
    <>
      <div className="topbar">
        <div onClick={() => go('back')} style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
          <Icon name="arrow-left" size={16} /><span style={{ fontSize: 12.5, fontWeight: 600 }}>फिर्ता</span>
        </div>
        <div className="serif" style={{ fontSize: 18, fontWeight: 700 }}>सूचनाहरू</div>
        <span style={{ fontSize: 12, color: 'var(--ink-3)', cursor: 'pointer' }} onClick={markAll}>सबै पढियो</span>
      </div>
      <div className="scrollable" style={{ padding: '4px 20px 30px' }}>
        {notifs.length === 0 && (
          <div style={{ padding: '60px 24px', textAlign: 'center' }}>
            <Icon name="bell" size={28} color="var(--ink-4)" />
            <div className="serif" style={{ fontSize: 16, fontWeight: 600, marginTop: 14 }}>सबै पढिसक्नुभयो</div>
          </div>
        )}
        {notifs.map((n, i) => {
          const color = { live: 'var(--accent)', info: 'var(--info)', verify: 'var(--verify)', warn: 'var(--warn)' }[n.tone] || 'var(--ink-2)';
          return (
            <div key={n.id} onClick={() => tap(n)} style={{
              display: 'flex', gap: 14, padding: '16px 0', cursor: 'pointer',
              borderTop: i === 0 ? 'none' : '1px solid var(--rule)', opacity: n.is_read ? 0.6 : 1,
            }}>
              <div style={{ width: 36, height: 36, borderRadius: 999, background: 'var(--bg-elev)',
                border: `1px solid ${color}`, display: 'flex', alignItems: 'center', justifyContent: 'center', color }}>
                <Icon name={n.icon} size={15} />
              </div>
              <div style={{ flex: 1 }}>
                <div className="serif" style={{ fontSize: 14, fontWeight: 600 }}>{n.title}</div>
                <div className="meta" style={{ marginTop: 4 }}>{n.sub}</div>
              </div>
              {!n.is_read && <span className="dot" style={{ background: color, marginTop: 14 }} />}
            </div>
          );
        })}
      </div>
    </>
  );
};
window.NotificationsScreen = NotificationsScreen;

// ─────────────────────── PROFILE ───────────────────────
const ProfileScreen = ({ go }) => {
  const ctx = useApp();
  const [stats, setStats] = React.useState({ read: 0, saved: 0, ai_asks: 0 });
  const [scanStatus, setScanStatus] = React.useState(null);
  const [scanning, setScanning] = React.useState(false);

  React.useEffect(() => {
    API.stats().then(setStats);
    API.scanStatus().then(setScanStatus).catch(() => {});
  }, []);

  const initials = ctx.user.name.split(' ').map(p => p[0]).join('').slice(0, 2).toUpperCase();
  const avatarColor = ctx.user.avatar_color || ctx.user.accent || '#14171C';

  const logout = async () => {
    if (!confirm('साइन आउट गर्ने?')) return;
    await API.logout();
    ctx.setUser(null);
  };

  const triggerScan = async () => {
    setScanning(true);
    try {
      const res = await API.triggerScan();
      ctx.toast(res.message || 'स्क्यान सुरु भयो…');
      setTimeout(() => API.scanStatus().then(setScanStatus), 3000);
    } catch (e) { ctx.toast(e.message); }
    finally { setScanning(false); }
  };

  return (
    <>
      <div className="topbar">
        <div className="serif" style={{ fontSize: 22, fontWeight: 700 }}>प्रोफाइल</div>
        <div className="iconbtn" onClick={() => go('settings')}><Icon name="settings" size={14} /></div>
      </div>

      <div className="scrollable">
        {/* Avatar */}
        <div style={{ padding: '8px 20px 22px', display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{ width: 58, height: 58, borderRadius: 999, background: avatarColor, color: '#fff',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: 'var(--serif)', fontSize: 22, fontWeight: 700 }}>{initials}</div>
          <div style={{ flex: 1 }}>
            <div className="serif" style={{ fontSize: 18, fontWeight: 600 }}>{ctx.user.name}</div>
            {ctx.user.email && <div className="meta" style={{ marginTop: 2 }}>{ctx.user.email}</div>}
          </div>
          {ctx.user.streak_days > 1 && (
            <div style={{ textAlign: 'center', padding: '8px 12px', background: 'var(--accent-soft)', borderRadius: 12 }}>
              <div className="serif" style={{ fontSize: 22, fontWeight: 700, color: 'var(--accent)' }}>{ctx.user.streak_days}</div>
              <div className="meta" style={{ color: 'var(--accent)', fontSize: 9 }}>दिन</div>
            </div>
          )}
        </div>

        {/* Stats */}
        <div style={{ margin: '0 20px 18px', padding: '18px 20px', border: '1px solid var(--rule)',
          borderRadius: 14, background: 'var(--bg-elev)', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 4 }}>
          {[
            { n: stats.read, l: 'पढियो' },
            { n: stats.saved, l: 'सेभ' },
            { n: stats.ai_asks, l: 'AI' },
          ].map(s => (
            <div key={s.l} onClick={() => s.l === 'सेभ' && go('bookmarks')}
              style={{ cursor: s.l === 'सेभ' ? 'pointer' : 'default' }}>
              <div className="serif" style={{ fontSize: 28, fontWeight: 600 }}>{s.n}</div>
              <div className="meta">{s.l}</div>
            </div>
          ))}
        </div>

        {/* Plan */}
        <SectionHeader eyebrow="तपाईंको प्लान"
          title={ctx.user.plan === 'pro' ? 'Reader · Pro' : 'Reader · Free'}
          action="हेर्नुहोस्" onAction={() => go('premium')} />
        <div style={{ margin: '0 20px 14px', padding: 18, border: '1px solid var(--rule)',
          borderRadius: 14, background: 'var(--bg-elev)' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 8 }}>
            <div className="eyebrow">AI प्रयोग · आज</div>
            <span className="mono" style={{ fontSize: 12, fontWeight: 700 }}>
              {ctx.user.plan === 'pro' ? '∞' : `${ctx.user.ai_quota} / १०`}
            </span>
          </div>
          <div style={{ height: 5, background: 'var(--bg-sunk)', borderRadius: 3, marginBottom: 14, overflow: 'hidden' }}>
            <div style={{ width: ctx.user.plan === 'pro' ? '100%' : `${Math.min(100, ctx.user.ai_quota * 10)}%`,
              height: '100%', background: ctx.user.ai_quota <= 3 && ctx.user.plan !== 'pro' ? 'var(--accent)' : 'var(--ink-1)',
              borderRadius: 3, transition: 'width .3s' }} />
          </div>
          {ctx.user.plan !== 'pro' && (
            <div onClick={() => go('premium')} style={{ display: 'flex', alignItems: 'center', gap: 12,
              padding: '12px 14px', border: '1px solid var(--ink-1)', borderRadius: 10, cursor: 'pointer' }}>
              <Icon name="sparkles" size={16} />
              <div style={{ flex: 1 }}>
                <div className="serif" style={{ fontSize: 14, fontWeight: 600 }}>Pro: ७ दिन निःशुल्क</div>
                <div className="meta">रू ७९/महिना · जुनसुकै बेला रद्द गर्न सकिन्छ</div>
              </div>
              <Icon name="arrow-right" size={14} />
            </div>
          )}
        </div>

        {/* Scanner status */}
        {scanStatus && (
          <>
            <SectionHeader eyebrow="समाचार स्क्यानर" />
            <div style={{ margin: '0 20px 14px', padding: 16, border: '1px solid var(--rule)',
              borderRadius: 14, background: 'var(--bg-elev)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                <span className="dot" style={{ background: scanStatus.running ? 'var(--warn)' : 'var(--verify)',
                  animation: scanStatus.running ? 'pulse 1s infinite' : 'none' }} />
                <div style={{ flex: 1 }}>
                  <span style={{ fontSize: 13, fontWeight: 600 }}>
                    {scanStatus.running ? 'स्क्यानिङ हुँदैछ…' : `अन्तिम स्क्यान: ${scanStatus.last_run_human || 'कहिल्यै भएन'}`}
                  </span>
                </div>
                <span className="meta">{scanStatus.scraped_articles || 0} समाचार</span>
              </div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 12 }}>
                {(scanStatus.sources_ok || []).map(s => (
                  <span key={s} className="tag" style={{ background: 'var(--verify-soft)', color: 'var(--verify)' }}>✓ {s}</span>
                ))}
                {(scanStatus.sources_err || []).map(s => (
                  <span key={s} className="tag" style={{ background: 'var(--accent-soft)', color: 'var(--accent)' }}>✗ {s}</span>
                ))}
              </div>
              <button className="btn btn-ghost" style={{ width: '100%', justifyContent: 'center' }}
                onClick={triggerScan} disabled={scanning || scanStatus.running}>
                <Icon name="refresh-cw" size={13} />
                {scanning ? 'सुरु हुँदैछ…' : 'अहिले स्क्यान गर्नुहोस्'}
              </button>
            </div>
          </>
        )}

        {/* Library */}
        <SectionHeader eyebrow="मेरो पुस्तकालय" />
        <div style={{ margin: '0 20px 14px', border: '1px solid var(--rule)', borderRadius: 14, background: 'var(--bg-elev)' }}>
          {[
            { icon: 'bookmark', label: 'सेभ गरिएका समाचार', val: stats.saved, action: () => go('bookmarks') },
            { icon: 'sparkles', label: 'AI कुराकानी', val: stats.ai_asks, action: () => go('ai') },
            { icon: 'bell', label: 'सूचनाहरू', val: `${ctx.unreadCount} नयाँ`, action: () => go('notifications') },
            { icon: 'settings', label: 'सेटिङ', val: '', action: () => go('settings') },
          ].map((row, i, arr) => (
            <div key={row.label} onClick={row.action}
              style={{ padding: '14px 16px', display: 'flex', alignItems: 'center', gap: 14,
                borderBottom: i < arr.length - 1 ? '1px solid var(--rule)' : 'none', cursor: 'pointer' }}>
              <Icon name={row.icon} size={16} color="var(--ink-2)" />
              <span style={{ flex: 1, fontSize: 13.5 }}>{row.label}</span>
              <span className="meta">{row.val}</span>
              <Icon name="chevron-right" size={14} color="var(--ink-3)" />
            </div>
          ))}
        </div>

        <div style={{ padding: '6px 20px 30px' }}>
          <button className="btn btn-ghost" style={{ width: '100%', justifyContent: 'center', color: 'var(--accent)' }} onClick={logout}>
            <Icon name="log-out" size={14} /> साइन आउट
          </button>
        </div>
      </div>
    </>
  );
};
window.ProfileScreen = ProfileScreen;

// ─────────────────────── PREMIUM ───────────────────────
const PremiumScreen = ({ go }) => {
  const ctx = useApp();
  const [billing, setBilling] = React.useState('monthly');
  const [busy, setBusy] = React.useState(false);

  const subscribe = async () => {
    setBusy(true);
    try {
      await API.subscribe(ctx.user.plan === 'pro' ? 'free' : 'pro');
      await ctx.refreshUser();
      ctx.toast(ctx.user.plan === 'pro' ? 'रद्द भयो। म्याद सकिएसम्म Pro रहन्छ।' : 'Pro मा स्वागत!');
      go('profile');
    } finally { setBusy(false); }
  };

  const price = billing === 'monthly'
    ? { amt: 79, per: 'प्रति महिना', cta: 'Pro सुरु गर्नुहोस् · रू ७९/महिना' }
    : { amt: 799, per: 'प्रति वर्ष (रू ६६/महिना)', cta: 'Pro सुरु गर्नुहोस् · रू ७९९/वर्ष' };

  const features = [
    { icon: 'sparkles', name: 'असीमित AI च्याट', desc: 'Samachar AI ले नेपालीमा जुनसुकै समाचारबारे उत्तर दिन्छ। कुनै दैनिक सीमा छैन।' },
    { icon: 'chart', name: 'पूर्ण पक्षपात विश्लेषण', desc: 'OnlineKhabar, Ratopati, Setopati — एउटै घटनालाई कसले कसरी फ्रेम गर्‍यो।' },
    { icon: 'search', name: 'उन्नत खोज', desc: 'तारिख, प्रकाशक, जिल्ला र भावना अनुसार फिल्टर गर्नुहोस्।' },
    { icon: 'map-pin', name: 'गहिरो स्थानीय समाचार', desc: 'पालिका र वडा तहसम्मको विस्तृत स्थानीय कभरेज।' },
    { icon: 'bell', name: 'ब्रेकिङ अलर्ट', desc: 'महत्त्वपूर्ण समाचारमा SMS र WhatsApp सूचना।' },
  ];

  return (
    <>
      <div className="topbar">
        <div onClick={() => go('back')} style={{ cursor: 'pointer' }}><Icon name="arrow-left" size={16} /></div>
        <div className="serif" style={{ fontSize: 20, fontWeight: 700 }}>Pro</div>
        <span className="meta">{ctx.user.plan === 'pro' ? 'सक्रिय' : '७ दिन निःशुल्क'}</span>
      </div>

      <div className="scrollable">
        <div style={{ padding: '10px 20px 24px', borderBottom: '1px solid var(--rule)' }}>
          <div className="eyebrow" style={{ marginBottom: 12 }}>SAMACHAR PRO · गम्भीर पाठकका लागि</div>
          <div className="h-display" style={{ fontSize: 34, marginBottom: 12 }}>
            बढी जानकारी।<br />
            <span style={{ color: 'var(--ink-3)' }}>बेकार कुरा कम</span>
            <span style={{ color: 'var(--accent)' }}>।</span>
          </div>
          <div className="body" style={{ fontSize: 14 }}>
            Samachar AI, पूर्ण पक्षपात विश्लेषण, स्थानीय गहिरो कभरेज र ब्रेकिङ अलर्ट।
          </div>
        </div>

        <SectionHeader eyebrow="के पाउनुहुन्छ" title="Pro सुविधाहरू" />
        <div style={{ padding: '0 20px 8px' }}>
          {features.map((f, i) => (
            <div key={f.name} style={{ borderTop: i === 0 ? '2px solid var(--ink-1)' : '1px solid var(--rule)',
              padding: '16px 0', display: 'flex', gap: 14, alignItems: 'flex-start' }}>
              <div style={{ width: 40, height: 40, borderRadius: 10, background: 'var(--bg-sunk)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Icon name={f.icon} size={17} />
              </div>
              <div style={{ flex: 1 }}>
                <div className="serif" style={{ fontSize: 16, fontWeight: 600 }}>{f.name}</div>
                <div className="body" style={{ fontSize: 12.5, marginTop: 4 }}>{f.desc}</div>
              </div>
            </div>
          ))}
        </div>

        <SectionHeader eyebrow="प्लान छान्नुहोस्" />
        <div style={{ margin: '0 20px 16px' }}>
          <div style={{ display: 'flex', padding: 3, background: 'var(--bg-sunk)', borderRadius: 12, marginBottom: 14 }}>
            {[{ id: 'monthly', l: 'मासिक' }, { id: 'yearly', l: 'वार्षिक', save: '−१६%' }].map(opt => (
              <div key={opt.id} onClick={() => setBilling(opt.id)}
                style={{ flex: 1, padding: '10px 12px', borderRadius: 9, textAlign: 'center', cursor: 'pointer',
                  background: billing === opt.id ? 'var(--bg-elev)' : 'transparent',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
                <span style={{ fontSize: 13, fontWeight: 600,
                  color: billing === opt.id ? 'var(--ink-1)' : 'var(--ink-3)' }}>{opt.l}</span>
                {opt.save && <span className="tag" style={{ background: 'var(--accent-soft)', color: 'var(--accent)' }}>{opt.save}</span>}
              </div>
            ))}
          </div>

          <div style={{ padding: 20, border: '2px solid var(--ink-1)', borderRadius: 16, background: 'var(--bg-elev)' }}>
            <div className="eyebrow" style={{ color: 'var(--accent)', marginBottom: 6 }}>SAMACHAR PRO</div>
            <div className="serif" style={{ fontSize: 40, fontWeight: 700, lineHeight: 1 }}>रू {price.amt}</div>
            <div className="meta" style={{ marginTop: 4, marginBottom: 16 }}>{price.per}</div>
            <div style={{ height: 1, background: 'var(--rule)', marginBottom: 16 }} />
            {['असीमित AI च्याट', 'पूर्ण पक्षपात विश्लेषण', 'उन्नत खोज', 'स्थानीय गहिरो कभरेज', 'ब्रेकिङ अलर्ट', 'विज्ञापन-मुक्त'].map(f => (
              <div key={f} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '5px 0' }}>
                <Icon name="check" size={13} color="var(--verify)" />
                <span style={{ fontSize: 13 }}>{f}</span>
              </div>
            ))}
            <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: 18, padding: '13px 16px' }}
              onClick={subscribe} disabled={busy}>
              {busy ? 'प्रक्रिया हुँदैछ…' : ctx.user.plan === 'pro' ? 'Free मा फर्कनुहोस्' : price.cta}
              {!busy && <Icon name="arrow-right" size={14} />}
            </button>
            <div className="meta" style={{ textAlign: 'center', marginTop: 10 }}>
              ७ दिन निःशुल्क · जुनसुकै बेला रद्द गर्न सकिन्छ
            </div>
          </div>
        </div>

        <div style={{ padding: '24px 20px 40px', textAlign: 'center', borderTop: '1px solid var(--rule)', marginTop: 16 }}>
          <div className="eyebrow">४२,००० + नेपाली पाठकहरूको विश्वास</div>
        </div>
      </div>
    </>
  );
};
window.PremiumScreen = PremiumScreen;

// ────────────────────── SETTINGS ──────────────────────
const SettingsScreen = ({ go }) => {
  const ctx = useApp();
  const [busy, setBusy] = React.useState(false);

  const update = async (k, v) => {
    setBusy(true);
    await API.updatePrefs({ [k]: v });
    await ctx.refreshUser();
    setBusy(false);
  };

  return (
    <>
      <div className="topbar">
        <div onClick={() => go('back')} style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
          <Icon name="arrow-left" size={16} /><span style={{ fontSize: 12.5, fontWeight: 600 }}>फिर्ता</span>
        </div>
        <div className="serif" style={{ fontSize: 18, fontWeight: 700 }}>सेटिङ</div>
        <span style={{ width: 50 }} />
      </div>

      <div className="scrollable" style={{ paddingBottom: 30 }}>
        <SectionHeader eyebrow="AI भाषा" />
        <div style={{ margin: '0 20px 14px', border: '1px solid var(--rule)', borderRadius: 14, background: 'var(--bg-elev)' }}>
          <div style={{ padding: '14px 16px', display: 'flex', alignItems: 'center' }}>
            <Icon name="language" size={16} color="var(--ink-2)" style={{ marginRight: 12 }} />
            <span style={{ flex: 1, fontSize: 13.5 }}>AI जवाफको भाषा</span>
            <div style={{ display: 'flex', gap: 4 }}>
              {[{ v: 'np', l: 'नेपाली' }, { v: 'en', l: 'English' }].map(opt => (
                <span key={opt.v} onClick={() => update('language', opt.v)}
                  className="pill" data-on={ctx.user.language === opt.v} style={{ fontSize: 11.5 }}>{opt.l}</span>
              ))}
            </div>
          </div>
        </div>

        <SectionHeader eyebrow="देखावट" />
        <div style={{ margin: '0 20px 14px', border: '1px solid var(--rule)', borderRadius: 14, background: 'var(--bg-elev)' }}>
          <div style={{ padding: '14px 16px', display: 'flex', alignItems: 'center', borderBottom: '1px solid var(--rule)' }}>
            <span style={{ flex: 1, fontSize: 13.5 }}>थिम</span>
            <div style={{ display: 'flex', gap: 4 }}>
              {[{ v: 'light', l: 'उज्यालो' }, { v: 'dark', l: 'अँध्यारो' }].map(t => (
                <span key={t.v} onClick={() => update('theme', t.v)}
                  className="pill" data-on={ctx.user.theme === t.v} style={{ fontSize: 11.5 }}>{t.l}</span>
              ))}
            </div>
          </div>
          <div style={{ padding: '14px 16px', display: 'flex', alignItems: 'center', borderBottom: '1px solid var(--rule)' }}>
            <span style={{ flex: 1, fontSize: 13.5 }}>घनत्व</span>
            <div style={{ display: 'flex', gap: 4 }}>
              {[{ v: 'compact', l: 'सघन' }, { v: 'comfortable', l: 'सामान्य' }, { v: 'roomy', l: 'फराकिलो' }].map(d => (
                <span key={d.v} onClick={() => update('density', d.v)}
                  className="pill" data-on={ctx.user.density === d.v} style={{ fontSize: 10.5 }}>{d.l}</span>
              ))}
            </div>
          </div>
          <div style={{ padding: '14px 16px', display: 'flex', alignItems: 'center' }}>
            <span style={{ flex: 1, fontSize: 13.5 }}>रङ</span>
            <div style={{ display: 'flex', gap: 6 }}>
              {['#C92A2A', '#1B3A5B', '#2D6A4F', '#8A5A1C', '#5B4B8A'].map(c => (
                <span key={c} onClick={() => update('accent', c)} style={{ width: 22, height: 22, borderRadius: 6,
                  background: c, cursor: 'pointer',
                  boxShadow: ctx.user.accent === c ? '0 0 0 2.5px var(--ink-1)' : 'none' }} />
              ))}
            </div>
          </div>
        </div>

        <SectionHeader eyebrow="खाता" />
        <div style={{ margin: '0 20px 14px', border: '1px solid var(--rule)', borderRadius: 14, background: 'var(--bg-elev)' }}>
          {ctx.user.email && (
            <div style={{ padding: '14px 16px', display: 'flex', alignItems: 'center', borderBottom: '1px solid var(--rule)' }}>
              <Icon name="mail" size={15} color="var(--ink-2)" style={{ marginRight: 12 }} />
              <span style={{ flex: 1, fontSize: 13.5 }}>इमेल</span>
              <span className="meta">{ctx.user.email}</span>
            </div>
          )}
          <div style={{ padding: '14px 16px', display: 'flex', alignItems: 'center' }}>
            <Icon name="sparkles" size={15} color="var(--ink-2)" style={{ marginRight: 12 }} />
            <span style={{ flex: 1, fontSize: 13.5 }}>प्लान</span>
            <span className="meta">{ctx.user.plan === 'pro' ? 'PRO' : 'FREE'}</span>
            <Icon name="chevron-right" size={13} color="var(--ink-3)"
              style={{ marginLeft: 8, cursor: 'pointer' }} onClick={() => go('premium')} />
          </div>
        </div>

        <div style={{ padding: '20px 20px 30px', textAlign: 'center' }}>
          <div className="meta">SAMACHAR.AI · v2.0 · Samachar AI · नेपाल</div>
        </div>
      </div>
    </>
  );
};
window.SettingsScreen = SettingsScreen;
