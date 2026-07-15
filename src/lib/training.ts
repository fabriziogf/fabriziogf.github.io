import fs from 'node:fs';
import yaml from 'js-yaml';

export type SportKey = 'swim' | 'bike' | 'run' | 'strength' | 'other';

export interface SportTotals {
  sessions: number;
  hours: number;
  distance_km: number;
  tss: number;
}

export interface DailyEntry {
  date: string;
  swim: { tss: number; hours: number };
  bike: { tss: number; hours: number };
  run: { tss: number; hours: number };
  strength: { tss: number; hours: number };
}

export interface MonthlyEntry {
  month: string;
  swim: { tss: number; hours: number };
  bike: { tss: number; hours: number };
  run: { tss: number; hours: number };
  strength: { tss: number; hours: number };
}

export interface Workout {
  date: string;
  sport: SportKey;
  title: string;
  hours: number;
  distance_km: number;
  tss: number;
  hr_avg?: number;
  power_avg?: number;
  strava_id?: number;
}

export interface PrEntry {
  label: string;
  unit?: string;
  all_time?: number | string;
  all_time_date?: string;
  all_time_workout?: string;
  this_year?: number | string;
  this_year_date?: string;
  this_year_workout?: string;
}

export interface TrainingData {
  generated_at: string;
  window_start: string;
  window_end: string;
  fitness: { ctl: number; atl: number; tsb: number };
  totals: Record<'swim' | 'bike' | 'run' | 'strength', SportTotals>;
  daily: DailyEntry[];
  workouts: Workout[];
  monthly: MonthlyEntry[];
  ctl_trend: { month: string; ctl: number; atl: number; tsb: number }[];
  prs: {
    bike: Record<string, PrEntry>;
    run: Record<string, PrEntry>;
  };
}

// The daily updater (scripts/update_training_data.py) keeps writing this
// exact file; a push to main triggers a rebuild, so build-time reads stay fresh.
const DATA_PATH = new URL('../../_data/training_data.yml', import.meta.url);

export function loadTrainingData(): TrainingData {
  return yaml.load(fs.readFileSync(DATA_PATH, 'utf8')) as TrainingData;
}

export const SPORT_COLORS: Record<SportKey, string> = {
  swim: '#4fc3f7',
  bike: '#81c784',
  run: '#ffb74d',
  strength: '#ce93d8',
  other: '#90a4ae',
};

export const SPORT_LABELS: Record<SportKey, string> = {
  swim: 'Swim',
  bike: 'Bike',
  run: 'Run',
  strength: 'Strength',
  other: 'Other',
};
