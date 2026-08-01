/**
 * GitHub contribution calendar, fetched at build time.
 *
 * Source is the public (unauthenticated) fragment GitHub serves at
 * /users/<login>/contributions — the same markup the profile page renders.
 * Each day is a <td> carrying data-date and data-level (0-4); the exact count
 * lives only in the matching <tool-tip> prose, so we parse both and join on
 * the cell id.
 *
 * Undocumented endpoint: if the markup ever changes, or the fetch fails, this
 * returns null and the caller skips the section rather than failing the build.
 */

export interface ContribDay {
  date: string;
  /** 0-4, GitHub's own intensity bucket */
  level: number;
  count: number;
  /** column index, 0 = oldest week */
  week: number;
  /** row index, 0 = Sunday */
  weekday: number;
}

export interface Contributions {
  days: ContribDay[];
  weeks: number;
  total: number;
  start: string;
  end: string;
}

const DAY_RE = /<td[^>]*class="ContributionCalendar-day"[^>]*>/g;
const TIP_RE = /<tool-tip[^>]*for="(contribution-day-component-[\d-]+)"[^>]*>([^<]*)<\/tool-tip>/g;

const attr = (tag: string, name: string) => tag.match(new RegExp(`${name}="([^"]*)"`))?.[1];

export async function loadContributions(login: string): Promise<Contributions | null> {
  let html: string;
  try {
    const res = await fetch(`https://github.com/users/${login}/contributions`, {
      headers: { 'user-agent': 'fabriziogf.github.io build' },
      signal: AbortSignal.timeout(10_000),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    html = await res.text();
  } catch (err) {
    console.warn(`[github] contribution calendar unavailable: ${err}`);
    return null;
  }

  // cell id -> exact count, from the screen-reader tooltip text
  const counts = new Map<string, number>();
  for (const [, id, text] of html.matchAll(TIP_RE)) {
    counts.set(id, Number(text.trim().match(/^([\d,]+)/)?.[1].replace(/,/g, '') ?? 0));
  }

  const days: ContribDay[] = [];
  for (const [tag] of html.matchAll(DAY_RE)) {
    const date = attr(tag, 'data-date');
    const id = attr(tag, 'id');
    if (!date || !id) continue;
    days.push({
      date,
      level: Number(attr(tag, 'data-level') ?? 0),
      count: counts.get(id) ?? 0,
      week: Number(attr(tag, 'data-ix') ?? 0),
      weekday: new Date(`${date}T00:00:00Z`).getUTCDay(),
    });
  }

  if (!days.length) {
    console.warn('[github] contribution calendar markup returned no days');
    return null;
  }

  days.sort((a, b) => a.date.localeCompare(b.date));

  return {
    days,
    weeks: Math.max(...days.map((d) => d.week)) + 1,
    total: Number(
      html.match(/([\d,]+)\s*\n?\s*contributions?\s*\n?\s*in the last year/)?.[1].replace(/,/g, '') ??
        days.reduce((a, d) => a + d.count, 0)
    ),
    start: days[0].date,
    end: days[days.length - 1].date,
  };
}
