// Brand constants shared by the pages.

export const HEADLINE = 'Every day, a true story of what God did through ordinary, flawed people to shape the world.';

// MailerLite embedded-form action URL (see src/components/Signup.astro). Empty = signup not live yet.
export const MAILERLITE_ACTION = '';

// Cloudflare Web Analytics (free, cookieless). The token is public by design.
export const CF_ANALYTICS_TOKEN = 'f15c7169aefc45a6abc5c632e642ae7b';

// Sunrise mark (Logo marks canvas, approved Nov 12). Brand gold only, always flat.
export const MARK = `<svg class="sun" viewBox="0 0 200 140" fill="none" stroke="#E9C77B" stroke-width="5" stroke-linecap="round" aria-hidden="true"><line x1="125.7" y1="88.4" x2="163.4" y2="83.1"/><line x1="124.2" y1="82.4" x2="153.9" y2="70.6"/><line x1="121.2" y1="77.0" x2="163.6" y2="46.9"/><line x1="117.1" y1="72.4" x2="138.1" y2="48.2"/><line x1="111.9" y1="68.9" x2="135.8" y2="22.7"/><line x1="106.1" y1="66.7" x2="113.7" y2="35.6"/><line x1="100.0" y1="66.0" x2="100.0" y2="14.0"/><line x1="93.9" y1="66.7" x2="86.3" y2="35.6"/><line x1="88.1" y1="68.9" x2="64.2" y2="22.7"/><line x1="82.9" y1="72.4" x2="61.9" y2="48.2"/><line x1="78.8" y1="77.0" x2="36.4" y2="46.9"/><line x1="75.8" y1="82.4" x2="46.1" y2="70.6"/><line x1="74.3" y1="88.4" x2="36.6" y2="83.1"/><path d="M100 63 L103.6 75.4 L116 79 L103.6 82.6 L100 92 L96.4 82.6 L84 79 L96.4 75.4 Z" fill="#E9C77B" stroke="none"/><path d="M24 92 H176"/><path d="M50 105 H150"/><path d="M68 116 H132"/><path d="M86 127 H114"/></svg>`;

// Where Awestruck Today lives. Set a channel's url once its account exists; until then it shows without a link.
export const CHANNELS = [
  { group: 'now', name: 'Website', handle: 'awestrucktoday.org', note: "Every day's full story, with sources", icon: 'site', url: '/' },
  { group: 'now', name: 'Email', handle: 'Weekly digest', note: "The week's stories in your inbox", icon: 'email', url: null },
  { group: 'now', name: 'Substack', handle: 'Awestruck Today', note: 'Read and subscribe on Substack', icon: 'substack', url: null },
  { group: 'later', name: 'Instagram', handle: '@awestrucktoday', icon: 'instagram', url: null },
  { group: 'later', name: 'Facebook', handle: 'Awestruck Today', icon: 'facebook', url: null },
  { group: 'later', name: 'X', handle: '@awestrucktoday', icon: 'x', url: null },
  { group: 'later', name: 'TikTok', handle: '@awestrucktoday', icon: 'tiktok', url: null },
  { group: 'later', name: 'YouTube', handle: '@awestrucktoday', icon: 'youtube', url: null },
];
