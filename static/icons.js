// Inline Lucide-style SVG icon component. Pure function of `name`.

const Icon = ({ name, size = 18, stroke = 1.6, color = 'currentColor', style = {} }) => {
  const s = { width: size, height: size, color, ...style };
  const common = {
    width: size, height: size, viewBox: '0 0 24 24', fill: 'none',
    stroke: 'currentColor', strokeWidth: stroke,
    strokeLinecap: 'round', strokeLinejoin: 'round',
  };
  switch (name) {
    case 'search': return <svg {...common} style={s}><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>;
    case 'bell': return <svg {...common} style={s}><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>;
    case 'pin': return <svg {...common} style={s}><path d="M12 22s7-7 7-12a7 7 0 1 0-14 0c0 5 7 12 7 12Z"/><circle cx="12" cy="10" r="2.5"/></svg>;
    case 'flame': return <svg {...common} style={s}><path d="M8.5 14.5A2.5 2.5 0 0 0 11 17a2.5 2.5 0 0 0 2.5-2.5c0-1.5-.5-2-1.25-3C11.5 10.5 11 10 11 9c0-1 1-2 2-2 2.5 0 4.5 2.5 4.5 5.5a6 6 0 0 1-12 0c0-1.5.5-3.5 2-5C8.5 6.5 9 8 9 9.5c0 1.5-.5 2-.5 3 0 1 .5 1.5 0 2Z"/></svg>;
    case 'play': return <svg {...common} style={s}><path d="M6 4v16l14-8L6 4Z" fill="currentColor"/></svg>;
    case 'pause': return <svg {...common} style={s}><rect x="6" y="4" width="4" height="16" fill="currentColor"/><rect x="14" y="4" width="4" height="16" fill="currentColor"/></svg>;
    case 'bookmark': return <svg {...common} style={s}><path d="M19 21V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v16l7-4 7 4Z"/></svg>;
    case 'share': return <svg {...common} style={s}><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/></svg>;
    case 'chat': return <svg {...common} style={s}><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5Z"/></svg>;
    case 'home': return <svg {...common} style={s}><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2h-4v-7h-6v7H5a2 2 0 0 1-2-2V9Z"/></svg>;
    case 'user': return <svg {...common} style={s}><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>;
    case 'compass': return <svg {...common} style={s}><circle cx="12" cy="12" r="9"/><path d="m15 9-2 5-5 2 2-5 5-2Z" fill="currentColor"/></svg>;
    case 'arrow-right': return <svg {...common} style={s}><path d="M5 12h14m-5-5 5 5-5 5"/></svg>;
    case 'arrow-left': return <svg {...common} style={s}><path d="M19 12H5m5 5-5-5 5-5"/></svg>;
    case 'arrow-up-right': return <svg {...common} style={s}><path d="M7 17 17 7M7 7h10v10"/></svg>;
    case 'chevron-right': return <svg {...common} style={s}><path d="m9 18 6-6-6-6"/></svg>;
    case 'chevron-down': return <svg {...common} style={s}><path d="m6 9 6 6 6-6"/></svg>;
    case 'check': return <svg {...common} style={s}><path d="m20 6-11 11-5-5"/></svg>;
    case 'shield-check': return <svg {...common} style={s}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/></svg>;
    case 'sparkle': return <svg {...common} style={s}><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/><circle cx="12" cy="12" r="2"/></svg>;
    case 'sparkles': return <svg {...common} style={s}><path d="M12 3 13.8 8.2 19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3ZM19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8L19 16ZM5 16l.6 1.7L7 18l-1.4.3L5 20l-.6-1.7L3 18l1.4-.3L5 16Z" fill="currentColor"/></svg>;
    case 'globe': return <svg {...common} style={s}><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a13 13 0 0 1 0 18M12 3a13 13 0 0 0 0 18"/></svg>;
    case 'whatsapp': return <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" style={s}><path d="M19.05 4.91A9.82 9.82 0 0 0 12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38a9.9 9.9 0 0 0 4.74 1.21h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.91-7.01Zm-7.01 15.24h-.01a8.23 8.23 0 0 1-4.19-1.15l-.3-.18-3.11.82.83-3.04-.2-.31a8.2 8.2 0 1 1 15.27-4.14c0 4.54-3.69 8.23-8.23 8.23Z"/></svg>;
    case 'send': return <svg {...common} style={s}><path d="m22 2-7 20-4-9-9-4 20-7Z"/></svg>;
    case 'settings': return <svg {...common} style={s}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h0a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v0a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z"/></svg>;
    case 'alert': return <svg {...common} style={s}><path d="M10.3 3.7 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.7a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/></svg>;
    case 'download': return <svg {...common} style={s}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>;
    case 'wifi-off': return <svg {...common} style={s}><path d="M2 2l20 20M8.5 16.5a5 5 0 0 1 7 0M2 8.8a16 16 0 0 1 4.2-2.8M5 12.6a10 10 0 0 1 5.2-2.6M19.5 8.8A16 16 0 0 0 12 4M22 12.6a10 10 0 0 0-3.3-2.3M12 20h.01"/></svg>;
    case 'thumb-up': return <svg {...common} style={s}><path d="M7 10v11h11a3 3 0 0 0 3-3l1-7a1 1 0 0 0-1-1h-5l1-4a2 2 0 0 0-2-2L9 9l-2 1ZM3 10h4v11H3Z"/></svg>;
    case 'thumb-down': return <svg {...common} style={s} transform="scale(1,-1)"><path d="M7 10v11h11a3 3 0 0 0 3-3l1-7a1 1 0 0 0-1-1h-5l1-4a2 2 0 0 0-2-2L9 9l-2 1ZM3 10h4v11H3Z"/></svg>;
    case 'chart': return <svg {...common} style={s}><path d="M3 21h18M5 21V9M10 21V5M15 21V13M20 21V8"/></svg>;
    case 'star': return <svg {...common} style={s}><path d="m12 2 3 7 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1 3-7Z"/></svg>;
    case 'plus': return <svg {...common} style={s}><path d="M12 5v14M5 12h14"/></svg>;
    case 'x': return <svg {...common} style={s}><path d="M18 6 6 18M6 6l12 12"/></svg>;
    case 'building': return <svg {...common} style={s}><path d="M3 21h18M5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16M9 7h.01M13 7h.01M9 11h.01M13 11h.01M9 15h.01M13 15h.01"/></svg>;
    case 'mountain': return <svg {...common} style={s}><path d="m3 21 7-12 5 8 3-4 3 8H3Z"/><circle cx="17" cy="6" r="2"/></svg>;
    case 'plant': return <svg {...common} style={s}><path d="M12 21V10M12 10c0-4 3-7 7-7-1 5-3 8-7 8ZM12 10c0-4-3-7-7-7 1 5 3 8 7 8Z"/></svg>;
    case 'water': return <svg {...common} style={s}><path d="M12 3s7 7 7 12a7 7 0 0 1-14 0c0-5 7-12 7-12Z"/></svg>;
    case 'language': return <svg {...common} style={s}><path d="M3 5h12M9 3v4M5 14a9 9 0 0 0 9 0M14 21l4-9 4 9M16 17h6"/></svg>;
    case 'check-circle': return <svg {...common} style={s}><circle cx="12" cy="12" r="9"/><path d="m9 12 2 2 4-4"/></svg>;
    case 'open-quote': return <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" style={s}><path d="M6 17c0-3 1-5 4-7L8 8c-4 2-6 5-6 9h4Zm9 0c0-3 1-5 4-7l-2-2c-4 2-6 5-6 9h4Z"/></svg>;
    case 'logout': return <svg {...common} style={s}><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/></svg>;
    default: return null;
  }
};

window.Icon = Icon;
