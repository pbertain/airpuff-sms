-- subscribers.sql
CREATE TABLE IF NOT EXISTS subscribers (
  phone_e164 TEXT PRIMARY KEY,
  status TEXT NOT NULL,              -- 'subscribed' | 'unsubscribed' | 'pending'
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  consent_ts TEXT,                   -- when they opted-in
  last_keyword TEXT                  -- last keyword we saw
);