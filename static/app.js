// Root App — auth gate, router, AppCtx provider, iOS frame.

const App = () => {
  const [user, setUser] = React.useState(undefined);   // undefined = loading
  const [route, setRoute] = React.useState('home');
  const [navStack, setNavStack] = React.useState([]);
  const [currentArticleId, setCurrentArticleId] = React.useState(null);
  const [bookmarks, setBookmarks] = React.useState(new Set());
  const [searchQuery, setSearchQuery] = React.useState('');
  const [pendingAi, setPendingAi] = React.useState(null);
  const [toastMsg, setToastMsg] = React.useState(null);
  const [unreadCount, setUnreadCount] = React.useState(0);

  // ── boot: load session ──
  React.useEffect(() => {
    API.me()
      .then(u => { setUser(u); if (u) { loadInitialState(); detectLocation(); } })
      .catch(() => setUser(null));
  }, []);

  // ── real location: browser geolocation → reverse geocode → ward label ──
  const detectLocation = () => {
    const cached = localStorage.getItem('samachar_loc');
    if (cached) setUser(u => (u ? { ...u, ward: cached } : u));
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(async (pos) => {
      try {
        const { latitude, longitude } = pos.coords;
        const r = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=jsonv2&zoom=14` +
          `&lat=${latitude}&lon=${longitude}&accept-language=ne`,
          { headers: { Accept: 'application/json' } });
        const d = await r.json();
        const a = d.address || {};
        const local  = a.suburb || a.neighbourhood || a.village || a.town ||
                       a.city_district || a.municipality || a.city || a.county || '';
        const region = a.city || a.county || a.state_district || a.state || '';
        const label = [...new Set([local, region].filter(Boolean))].join(', ') ||
                      (d.display_name ? d.display_name.split(',').slice(0, 2).join(',').trim() : '');
        if (label) {
          localStorage.setItem('samachar_loc', label);
          setUser(u => (u ? { ...u, ward: label } : u));
        }
      } catch (e) { /* keep existing ward */ }
    }, () => {}, { enableHighAccuracy: false, timeout: 8000, maximumAge: 600000 });
  };

  // ── apply theme + accent from user prefs ──
  React.useEffect(() => {
    if (!user) return;
    document.documentElement.dataset.theme = user.theme;
    document.documentElement.style.setProperty('--accent', user.accent);
  }, [user?.theme, user?.accent]);

  const loadInitialState = async () => {
    try {
      const [bm, notifs] = await Promise.all([API.bookmarks(), API.notifications()]);
      setBookmarks(new Set(bm.map(a => a.id)));
      setUnreadCount(notifs.filter(n => !n.is_read).length);
    } catch (e) { /* not authed */ }
  };

  const refreshUser = async () => {
    const u = await API.me();
    setUser(u);
  };

  const refreshUnreadCount = async () => {
    const notifs = await API.notifications();
    setUnreadCount(notifs.filter(n => !n.is_read).length);
  };

  const toast = (m) => {
    setToastMsg(m);
    setTimeout(() => setToastMsg(null), 2200);
  };

  const go = (r) => {
    if (r === 'back') {
      if (navStack.length === 0) { setRoute('home'); return; }
      const prev = navStack[navStack.length - 1];
      setNavStack(s => s.slice(0, -1));
      setRoute(prev);
      return;
    }
    setNavStack(s => [...s, route]);
    setRoute(r);
  };

  const openArticle = (id) => {
    setCurrentArticleId(id);
    setNavStack(s => [...s, route]);
    setRoute('article');
  };

  const toggleBookmark = async (id) => {
    const { saved } = await API.toggleBookmark(id);
    const next = new Set(bookmarks);
    saved ? next.add(id) : next.delete(id);
    setBookmarks(next);
    toast(saved ? 'Saved' : 'Removed');
  };

  // ─── loading state ───
  if (user === undefined) {
    return (
      <IOSDevice width={402} height={874}>
        <LoadingScreen msg="Booting samachar" />
      </IOSDevice>
    );
  }

  // ─── login gate ───
  if (!user) {
    return (
      <IOSDevice width={402} height={874}>
        <div className="app">
          <LoginScreen onLogin={(u) => { setUser(u); loadInitialState(); detectLocation(); }} />
        </div>
      </IOSDevice>
    );
  }

  // ─── onboarding gate ───
  if (!user.onboarded) {
    return (
      <AppCtx.Provider value={{
        user, setUser, refreshUser, toast,
        bookmarks, toggleBookmark, openArticle,
        searchQuery, setSearchQuery, pendingAi, setPendingAi,
        currentArticleId, unreadCount, refreshUnreadCount,
      }}>
        <IOSDevice width={402} height={874} dark={user.theme === 'dark'}>
          <div className="app">
            <OnboardingScreen onComplete={() => { setRoute('home'); }} />
          </div>
        </IOSDevice>
        <Toast message={toastMsg} />
      </AppCtx.Provider>
    );
  }

  // ─── main app ───
  const screens = {
    home: HomeScreen,
    article: ArticleScreen,
    discover: DiscoverScreen,
    premium: PremiumScreen,
    profile: ProfileScreen,
    notifications: NotificationsScreen,
    bookmarks: BookmarksScreen,
    search: SearchResultsScreen,
    ai: AiChatScreen,
    settings: SettingsScreen,
  };
  const Screen = screens[route] || HomeScreen;

  const showTabs = ['home','discover','premium','profile'].includes(route);
  const currentTab = showTabs ? route : null;

  return (
    <AppCtx.Provider value={{
      user, setUser, refreshUser, toast,
      bookmarks, toggleBookmark, openArticle,
      searchQuery, setSearchQuery, pendingAi, setPendingAi,
      currentArticleId, unreadCount, refreshUnreadCount,
    }}>
      <IOSDevice width={402} height={874} dark={user.theme === 'dark'}>
        <div className="app" data-density={user.density}>
          <Screen go={go} />
          {showTabs && <TabBar current={currentTab} onChange={go} />}
        </div>
      </IOSDevice>
      <Toast message={toastMsg} />
    </AppCtx.Provider>
  );
};

// Density styles
const densityStyle = document.createElement('style');
densityStyle.textContent = `
  [data-density="compact"] .card-row { padding: 14px 20px; }
  [data-density="compact"] .h-headline { font-size: 19px !important; }
  [data-density="compact"] .h-title { font-size: 15.5px !important; }
  [data-density="roomy"] .card-row { padding: 24px 20px; }
  [data-density="roomy"] .h-headline { font-size: 24px !important; }
`;
document.head.appendChild(densityStyle);

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
