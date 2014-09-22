drop table if exists totals;
create table totals (
  id integer primary key autoincrement,
  variable text not null default '',
  value text not null default '',
  tbb_v text not null default '',
  total integer,
  unique (variable, value, tbb_v)
);
PRAGMA journal_mode = WAL;