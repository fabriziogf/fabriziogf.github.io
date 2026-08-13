/**
 * The project list, shared by /projects/ and the homepage's "Now building" cell.
 *
 * Order is newest first — the homepage shows the first four, so a new project
 * added at the top surfaces there automatically.
 */

export interface ProjectLink {
  label: string;
  href: string;
  external?: boolean;
}

export interface Project {
  tag: string;
  tagColor: string;
  dot: string;
  status: string;
  title: string;
  /** full card copy on /projects/ */
  desc: string;
  /** one-liner for the homepage cell */
  blurb: string;
  stack: string;
  links: ProjectLink[];
  /** where the homepage entry points; defaults to the projects page */
  homeHref?: string;
}

export const projects: Project[] = [
  {
    tag: 'Personal Finance',
    // --other (slate). Deliberately not --bike: the green --bike-ink is what the
    // "Active" status pill uses, so a tag in that color reads as a status — the
    // same reason the Triathlon tag avoids --run.
    tagColor: 'var(--other-ink)',
    dot: 'var(--other)',
    status: 'In Progress',
    title: 'Financial Advisor',
    desc: 'A self-hosted advisor that holds the full picture — accounts, goals, risk capacity, benefits — and reasons about what to do next. Read-only by architecture, not by policy: it has no write path to any institution. Every figure comes from deterministic, unit-tested code; the model only explains and prioritizes.',
    blurb: 'Goal-aware money guidance, read-only by architecture',
    stack: 'Python · FastAPI · SQLite · SimpleFIN',
    links: [
      {
        label: 'View code →',
        href: 'https://github.com/fabriziogf/financial-advisor',
        external: true,
      },
    ],
  },
  {
    tag: 'GenAI',
    tagColor: 'var(--strength-ink)',
    dot: 'var(--strength)',
    status: 'In Progress',
    title: 'noteKB',
    desc: 'Turns photographs of handwritten notes into structured knowledge, merged into a version-controlled markdown knowledge base with a human review gate.',
    blurb: 'Handwritten notes into a version-controlled knowledge base',
    stack: 'Python · Anthropic SDK · uv · GitHub',
    links: [{ label: 'View code →', href: 'https://github.com/fabriziogf/noteKB', external: true }],
  },
  {
    tag: 'Sports Analytics',
    tagColor: 'var(--swim-ink)',
    dot: 'var(--swim)',
    status: 'Active',
    title: 'Fantasy Football Draft Assistant',
    desc: 'A draft-day assistant that builds my own player projections from nflverse history, turns them into value (VOR and VONA), and recommends the best pick in real time based on who is already gone and what my roster needs. Every recommendation explains its reasoning.',
    blurb: 'Value-based pick recommendations, live on the clock',
    stack: 'Python · FastAPI · React · nflverse',
    links: [
      { label: 'Read the writeup →', href: '/Fantasy_football_draft_assistant/' },
      { label: 'View code →', href: 'https://github.com/fabriziogf/fantasy-football-draft', external: true },
    ],
  },
  {
    tag: 'GenAI',
    tagColor: 'var(--strength-ink)',
    dot: 'var(--strength)',
    status: 'Active',
    title: 'Job Hunting Agent',
    desc: 'An AI agent that helps a candidate run a full job search end-to-end — resume, cover letter, networking, interview prep, application tracking, and offer negotiation — with advice grounded in a concrete playbook rather than generic LLM intuition.',
    blurb: 'An AI agent that runs a full job search end-to-end',
    stack: 'Python · Anthropic SDK · Claude Code',
    links: [
      { label: 'Read the writeup →', href: '/Job_hunting_agent_technical_implementation/' },
      { label: 'View code →', href: 'https://github.com/fabriziogf/job-hunt-assistant', external: true },
    ],
  },
  {
    tag: 'Sports Analytics',
    tagColor: 'var(--swim-ink)',
    dot: 'var(--swim)',
    status: 'Active',
    title: 'World Cup 2026 Prediction Model',
    desc: 'Monte Carlo tournament simulator built on Dixon-Coles and Elo ratings. Backtested across 2014–2022 World Cups with Brier score and calibration analysis.',
    blurb: 'Monte Carlo tournament simulator on Dixon-Coles and Elo',
    stack: 'Python · Monte Carlo · Dixon-Coles',
    links: [
      { label: 'Read the writeup →', href: '/World_Cup_prediction_model_part10/' },
      { label: 'View code →', href: 'https://github.com/fabriziogf/world_cup_model', external: true },
    ],
  },
  {
    tag: 'Triathlon',
    // --strava, matching the Workout Hours calendar. Deliberately not --run:
    // the amber --run-ink is what the "In Progress" status pill uses, and a
    // tag in that color reads as a status. The label takes the darkened -ink
    // variant for contrast; the dot keeps the true brand orange.
    tagColor: 'var(--strava-ink)',
    dot: 'var(--strava)',
    status: 'Active',
    title: 'Training Dashboard',
    desc: 'Live 7-day rolling window of swim, bike, run, and strength training. Activity data is pulled from Strava daily, with fitness metrics (CTL, ATL, TSB) and training load (TSS) from TrainingPeaks. Shows session-level detail, 12-month trends, and personal records.',
    blurb: 'Live Strava + TrainingPeaks pipeline, updated daily',
    stack: 'Python · Astro · Strava API · TrainingPeaks API',
    links: [
      { label: 'Read the writeup →', href: '/Training_dashboard_update/' },
      { label: 'View dashboard →', href: '/training/' },
    ],
    homeHref: '/training/',
  },
];
