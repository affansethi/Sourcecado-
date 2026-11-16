-- Migration slice S08: MeetingEvidenceStore moves from meeting_evidence.db to Postgres.
-- Head schema of the SQLite store, plus user_id on every table and key.
-- Every text column is collate "C": bytewise, as SQLite compares text.
-- evidence_id is a hash of (provider, provider_id), so two users who see the
-- same meeting get the same evidence_id. The keys include user_id for that.

create table meeting_evidence (
    user_id uuid not null references auth.users(id) on delete cascade,
    evidence_id text collate "C" not null,
    provider text collate "C" not null,
    provider_id text collate "C" not null,
    title text collate "C" not null,
    starts_at text collate "C",
    ends_at text collate "C",
    participants_json text collate "C" not null,
    source_ref_json text collate "C" not null,
    notes text collate "C",
    status text collate "C" not null,
    person_id text collate "C",
    match_reason text collate "C",
    created_at text collate "C" not null,
    updated_at text collate "C" not null,
    primary key (user_id, evidence_id),
    unique (user_id, provider, provider_id)
);

create index meeting_evidence_user_person_idx
    on meeting_evidence (user_id, person_id);

-- YOUR TURN (block 1, piece 2): write the table `meeting_candidates`.
--
-- It records that one meeting may belong to one person. Write three things.
--
-- 1. The table, with these columns, in this order. None may be null.
--      user_id        the owner: a uuid that refers to auth.users(id),
--                     and the row goes when that user is deleted
--      evidence_id    text
--      person_id      text
--      status         text
--      match_reason   text
--      updated_at     text
--    Every text column sorts by bytes: add  collate "C"  after  text.
--    The primary key is (user_id, evidence_id, person_id).
--
-- 2. An index named meeting_candidates_user_person_idx
--    on (user_id, person_id).
--
-- 3. At the end of this file there is a second YOUR TURN line: switch on
--    row-level security for this table.
--
-- The table `meeting_evidence` above is a full example of the same rules.

-- Row-level security on, with no policy: the public API keys see no rows.
-- The backend connects as the table owner, so it is not affected.


-- YOUR TURN (block 1, piece 2): the same line for meeting_candidates.
create table meeting_candidates (
    user_id uuid not null references auth.users(id) on delete cascade,
    evidence_id text collate "C" not null,
    person_id text collate "C" not null,
    status text collate "C" not null,
    match_reason text collate "C" not null,
    updated_at text collate "C" not null,
    primary key (user_id, evidence_id, person_id)
);
create index meeting_candidates_user_person_idx
    on meeting_candidates (user_id, person_id);
alter table meeting_evidence enable row level security;
alter table meeting_candidates enable row level security;
