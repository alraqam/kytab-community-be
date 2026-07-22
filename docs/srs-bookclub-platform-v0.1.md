# Software Requirements Specification

**Product:** Social reading platform with private book clubs (working name TBD — referred to below as "the Platform")

| | |
|---|---|
| **Version** | 0.1 — Draft for review |
| **Date** | 13 July 2026 |
| **Product owner** | Furkat |
| **Standard** | Adapted from ISO/IEC/IEEE 29148:2018 |
| **Priority notation** | M = Must (MVP-blocking) · S = Should (high-value, v1.x) · C = Could (later) |

**Contents:** 1. Introduction · 2. Overall Description · 3. Functional Requirements · 4. External Interfaces · 5. Non-Functional Requirements · 6. Data Requirements · 7. Release Plan · 8. Acceptance Criteria (samples) · 9. Open Questions · Appendix A. Permissions Matrix

---

## 1. Introduction

### 1.1 Purpose

This document specifies the functional and non-functional requirements for the Platform, a social cataloging and reading-community product positioned as a modern alternative to Goodreads, with **private book clubs** as its core differentiator. It is intended for the founding team, engineers, designers, QA, and technical reviewers (contractors, due-diligence). Requirements are identified, prioritized (MoSCoW), and written to be independently testable.

### 1.2 Product vision and scope

Readers maintain a personal library (shelves, ratings, reviews, reading progress) and create or join book clubs that are private by default. Clubs read on a shared schedule, and discussions are **spoiler-safe**: posts are bound to reading milestones and hidden from members who have not yet reached that point in the book.

**In scope for v1.0**

- Responsive web application (installable PWA)
- Personal library: shelves, statuses, half-star ratings, reviews, progress tracking
- Book catalog fed by external metadata APIs plus community-submitted titles (librarian-curated)
- Private clubs: membership and roles, scheduled reads with milestones, spoiler-gated discussions, polls, events
- Social layer: follow, activity feed, public club directory
- Notifications (in-app, email), Goodreads data import, moderation and administration

**Explicit non-goals for v1.0** (architecture must not preclude them)

- Native iOS/Android apps — planned for v2 on top of the public API; PWA covers mobile in v1
- In-app e-book reading or file hosting — legal/licensing complexity; the Platform tracks reading, it does not host books
- Book sales, affiliate links, ads — differentiator vs. Goodreads; monetization deferred (see §9)
- Author marketing tools (giveaways, ads, promoted reviews) — separate initiative
- Real-time chat/voice in clubs — v1 discussions are asynchronous; live video handled via external meeting links in Events
- Federation (ActivityPub) — revisit after product-market fit

### 1.3 Definitions and abbreviations

| Term | Meaning |
|---|---|
| Work | An abstract book (e.g., a novel) independent of format, publisher, or translation |
| Edition | A concrete published version of a Work (specific ISBN, language, format, cover) |
| Exclusive status | One of: Want to Read, Currently Reading, Read, Did Not Finish — at most one per user per Work |
| Shelf | A named user collection; custom shelves act as non-exclusive labels/tags |
| DNF | Did Not Finish |
| Club | A group of members reading and discussing together, with its own privacy tier and roles |
| Club read | A Work selected by a club, with a start date and a schedule |
| Milestone | A segment of a club read (chapter/page boundary plus target date) used to pace reading and gate discussion |
| Spoiler gate | Mechanism that hides milestone-bound content from members whose declared progress is earlier than that milestone |
| Librarian | Trusted community role that curates the catalog (approves submissions, merges duplicates) |
| MAU / WAU | Monthly / weekly active users |
| RBAC | Role-based access control |
| ICS | iCalendar file format (RFC 5545) |

### 1.4 References

- ISO/IEC/IEEE 29148:2018 — Requirements engineering
- Open Library APIs (bibliographic data and covers) — primary metadata source
- Google Books API — secondary metadata source
- WCAG 2.1 Level AA — accessibility target
- GDPR (EU 2016/679) and applicable local data-protection law in launch markets
- OWASP Application Security Verification Standard (ASVS) 4.x — security baseline
- RFC 5545 (iCalendar) — event export

---

## 2. Overall Description

### 2.1 Product perspective

The Platform is a greenfield SaaS product built on three pillars: (1) the personal library, (2) clubs, (3) discovery. Related products: Goodreads (incumbent; dated UX, public API retired in 2020), The StoryGraph (stats-led), Fable and Bookclubs (club-led), BookWyrm (federated, niche). The Platform's wedge is the combination of privacy-first clubs, progress-gated spoiler-safe discussion, and first-class support for regional-language catalogs (e.g., Uzbek and Russian titles) that global metadata sources cover poorly.

### 2.2 Major product functions (summary)

| Area | Summary | Detailed in |
|---|---|---|
| Accounts and profiles | Registration, sign-in, privacy controls, data export/erasure | §3.1, §3.2 |
| Catalog | Work/Edition model, search, external metadata, community submissions | §3.3 |
| Library | Shelves, statuses, ratings, reviews, progress, Goodreads import | §3.4–3.6 |
| Clubs | Creation, invitations, roles, schedules, spoiler-gated discussion, polls, events | §3.7 |
| Social and discovery | Follow, feed, club directory, recommendations | §3.8 |
| Notifications | In-app, email, push; per-club preferences and digests | §3.9 |
| Trust and safety | Reporting, moderation queues, audit logs | §3.10 |
| Administration | Admin console, metrics, librarian queue | §3.11 |

### 2.3 User classes

| Class | Description | Notes |
|---|---|---|
| Guest | Unauthenticated visitor | Can view public book pages, public profiles, and the public club directory only |
| Reader | Registered user | Core persona; manages library, joins clubs |
| Club owner | Reader who created a club (or received ownership) | Exactly one per club; full club control |
| Club moderator | Reader granted moderation rights within a club | Manages content, members, schedule |
| Librarian | Trusted community curator | Catalog editing rights; appointed by platform admins |
| Platform moderator | Staff handling reports and enforcement | Cross-platform scope |
| Platform admin | Staff with full administrative access | Configuration, roles, operations |

### 2.4 Operating environment

- Client: evergreen browsers (last two major versions of Chrome, Safari, Firefox, Edge), responsive from 360 px width, installable PWA on iOS/Android
- Server: Linux containers behind a load balancer; horizontally scalable stateless application tier
- Data: relational database as the primary store; object storage for images; cache layer for sessions, feeds, and rate limiting

### 2.5 Design and implementation constraints

| ID | Constraint |
|---|---|
| CON-01 | The Goodreads public API is retired; no live Goodreads integration is possible. Migration is supported only via the user's own Goodreads CSV export (FR-SHF-06) |
| CON-02 | Book metadata relies on Open Library (primary) and Google Books (secondary); their rate limits and content/cover licensing terms apply and must be respected |
| CON-03 | GDPR-grade privacy (consent, export, erasure) is required from day one, not retrofitted |
| CON-04 | This SRS is implementation-agnostic. Anticipated environment for planning purposes: Laravel or Node.js API, React front end, PostgreSQL, Redis, S3-compatible storage, Docker-based deployment — noted, not mandated |
| CON-05 | All text handling is UTF-8; Latin and Cyrillic scripts (including Uzbek Latin with special characters) must render and search correctly throughout |
| CON-06 | Private and secret club content must be excluded from search-engine indexing at the infrastructure level (authentication plus noindex), not merely by UI omission |

### 2.6 Assumptions and dependencies

- Users are reachable by email; email is the account recovery channel
- External metadata APIs remain available on free or affordable tiers; catalog degrades gracefully to community submissions if a source is unavailable
- Launch locales are assumed to be English, Russian, and Uzbek (to be confirmed — see §9); the i18n architecture must support adding locales without code changes
- Sizing basis: roughly 20,000 MAU in year one, with 10× headroom (see NFR-SCL)
- Minimum user age 16 by default, configurable per jurisdiction; no accounts under 13 in any market

---

## 3. Functional Requirements

Requirements use the form "The system shall …" and are individually testable. Priorities: **M** = Must, **S** = Should, **C** = Could.

### 3.1 Accounts and authentication (FR-ACC)

| ID | P | Requirement |
|---|---|---|
| FR-ACC-01 | M | The system shall allow registration with email and password, requiring email verification before the account is fully active |
| FR-ACC-02 | M | The system shall support sign-in, sign-out, and concurrent sessions across devices, and shall let users view and revoke active sessions |
| FR-ACC-03 | S | The system shall support OAuth sign-in with Google and Apple, linking to an existing account when the verified email matches |
| FR-ACC-04 | M | The system shall support password reset via a single-use, time-limited email link |
| FR-ACC-05 | C | The system shall support optional TOTP two-factor authentication with recovery codes |
| FR-ACC-06 | M | Each account shall have an immutable internal ID and a unique public username; usernames are changeable at most once per 30 days |
| FR-ACC-07 | M | Account deletion shall apply a 30-day soft-delete grace period (account hidden, sign-in restores), after which erasure proceeds per NFR-PRV |
| FR-ACC-08 | M | The system shall provide a self-service data export: a machine-readable archive (JSON plus CSV) of the user's library, reviews, progress, and club posts |
| FR-ACC-09 | M | Authentication endpoints shall be rate-limited with progressive lockout on repeated failures |

### 3.2 Profiles (FR-PRO)

| ID | P | Requirement |
|---|---|---|
| FR-PRO-01 | M | Users shall have a profile with display name, avatar, bio, favorite genres, and optional links |
| FR-PRO-02 | M | Profile visibility shall be configurable: Public, Followers only, or Private |
| FR-PRO-03 | M | A profile shall display the user's shelves, reviews, activity, and reading stats, subject to profile visibility and per-shelf privacy (FR-SHF-03) |
| FR-PRO-04 | S | Users shall be able to set an annual reading goal, displayed on the profile with progress |
| FR-PRO-05 | M | Users shall be able to block another user; a blocked user cannot follow, mention, or invite the blocking user, and each party's content is hidden from the other's feeds |

### 3.3 Book catalog (FR-CAT)

| ID | P | Requirement |
|---|---|---|
| FR-CAT-01 | M | The catalog shall use a Work/Edition model: ratings, reviews, and shelf placements aggregate at the Work level while recording the specific Edition where known |
| FR-CAT-02 | M | Each book page shall display cover, title, author(s), description, publication details, series, genres, average rating with distribution, and reviews |
| FR-CAT-03 | M | Catalog search shall match title, author, ISBN, and series; be tolerant of diacritics and minor typos; and handle Latin and Cyrillic input equally |
| FR-CAT-04 | M | On search misses or explicit lookup, the system shall fetch metadata from Open Library first and Google Books as fallback, deduplicating by ISBN and title-author heuristics before creating records |
| FR-CAT-05 | M | Users shall be able to submit a book not in the catalog (title, author, language; ISBN and cover optional); the submission enters a librarian review queue but is immediately usable on the submitter's shelves, flagged "pending verification" |
| FR-CAT-06 | M | Librarians shall be able to approve or reject submissions, edit metadata, merge duplicate Works, combine Editions under a Work, and manage author and series records |
| FR-CAT-07 | S | The system shall provide author pages (bio, bibliography) and series pages with reading order |
| FR-CAT-08 | S | The system shall maintain a curated genre taxonomy plus free-form user tags derived from custom shelf names |
| FR-CAT-09 | C | Users shall be able to select their preferred Edition per book, reflected in page counts used for progress |

### 3.4 Shelves and reading statuses (FR-SHF)

| ID | P | Requirement |
|---|---|---|
| FR-SHF-01 | M | The system shall provide four default exclusive statuses: Want to Read, Currently Reading, Read, and Did Not Finish |
| FR-SHF-02 | M | Users shall be able to create unlimited custom shelves that act as non-exclusive labels alongside the exclusive status |
| FR-SHF-03 | M | Privacy shall be settable per shelf: Public, Followers only, or Private |
| FR-SHF-04 | S | The system shall record multiple start/finish date pairs per book to support re-reads, all visible in reading history |
| FR-SHF-05 | M | Shelf views shall support sorting (date added, date read, title, author, rating) and filtering (status, tag, year) |
| FR-SHF-06 | M | The system shall import a Goodreads CSV export, mapping shelves, exclusive statuses, ratings, reviews, and read dates; unmatched rows shall produce a report with one-click submission to the catalog queue (FR-CAT-05) |
| FR-SHF-07 | C | The system shall support bulk shelf operations (move, tag, delete) on multi-selected books |

### 3.5 Ratings and reviews (FR-REV)

| ID | P | Requirement |
|---|---|---|
| FR-REV-01 | M | Ratings shall use a half-star scale from 0.5 to 5.0 |
| FR-REV-02 | M | Users shall be able to rate without reviewing and review without rating |
| FR-REV-03 | M | Reviews shall support basic formatting and editing; edited reviews display an "edited" marker |
| FR-REV-04 | M | Reviews shall support inline spoiler tags and a whole-review spoiler flag; flagged content is collapsed for other users until explicitly revealed |
| FR-REV-05 | M | Users shall be able to like and comment on reviews; comments are reportable (FR-MOD-01) |
| FR-REV-06 | M | Review lists shall be sortable (newest, most liked) and filterable by star rating |
| FR-REV-07 | C | The review editor shall autosave drafts |

### 3.6 Reading progress and stats (FR-PRG)

| ID | P | Requirement |
|---|---|---|
| FR-PRG-01 | M | Users shall be able to log progress on Currently Reading books by page number or percentage |
| FR-PRG-02 | M | A progress update may include a note; visibility of updates follows the book's shelf privacy |
| FR-PRG-03 | M | Marking a book finished shall prompt for rating/review and move it to Read with a finish date |
| FR-PRG-04 | S | The system shall provide a yearly reading challenge (target count) with progress and past-year history |
| FR-PRG-05 | S | The system shall provide personal stats: books and pages per month/year, genre split, average rating, longest and shortest reads |
| FR-PRG-06 | C | The system shall estimate reading pace and project a finish date for current reads |

### 3.7 Clubs (FR-CLB) — core differentiator

A club has a privacy tier, roles, an optional current read with a milestone schedule, discussions, polls, and events. The defining feature is the **spoiler gate** (FR-CLB-13): discussion content is bound to milestones and withheld from members who have not reached them.

| ID | P | Requirement |
|---|---|---|
| FR-CLB-01 | M | Users shall be able to create a club with name, description, cover image, genre tags, language, and privacy tier |
| FR-CLB-02 | M | Privacy tiers: **Public** (listed in the directory; anyone may join), **Private** (listed; join by approval or invite), **Secret** (unlisted; invite only). Default is Private |
| FR-CLB-03 | M | Roles: one Owner (transferable), any number of Moderators, Members. Permissions follow Appendix A and are enforced server-side on every request |
| FR-CLB-04 | M | Invitations shall be supported via revocable expiring links (default 14 days), in-app invites by username, and email invites; before joining, an invitee sees only name, description, member count, and current book |
| FR-CLB-05 | M | Private clubs shall support join requests with moderator approve/decline; an optional application question may be configured (C) |
| FR-CLB-06 | M | Moderators shall be able to remove members and ban them (ban blocks rejoining via any invite path) |
| FR-CLB-07 | M | The club home shall show current read(s), schedule, latest discussions, pinned posts, and upcoming events |
| FR-CLB-08 | M | Moderators shall set a current read from the catalog with a start date; the system shall support up to three concurrent reads per club (S) |
| FR-CLB-09 | M | A reading schedule shall consist of ordered milestones, each with a label, a boundary (chapter range and/or page or percentage), and a target date; schedule edits notify members |
| FR-CLB-10 | S | A schedule assistant shall auto-split a book into milestones given a date range and the edition's page count |
| FR-CLB-11 | M | Each member shall have a per-club progress marker (highest milestone reached), set manually; when the member's personal progress on the same Work is ahead, the system offers one-tap sync (S) |
| FR-CLB-12 | M | Every book-discussion thread and post shall be bound to a milestone or to "Finished" |
| FR-CLB-13 | M | **Spoiler gate:** content bound to a milestone beyond the viewer's club progress shall be hidden by default (title visible, body withheld). The API shall exclude gated bodies from default responses; the body is delivered only on an explicit per-item reveal action, which does not change the member's progress marker |
| FR-CLB-14 | M | Each club shall have a general discussion area not bound to any read, never spoiler-gated |
| FR-CLB-15 | M | Posts shall support text with basic formatting, reactions, single-level replies, edit (with marker) and delete; moderators may pin, lock, and remove posts; image attachments (S) |
| FR-CLB-16 | S | Moderators shall be able to attach discussion prompts to milestones, surfaced to each member upon reaching that milestone |
| FR-CLB-17 | M | Clubs shall support next-read polls: members nominate books from the catalog, one vote per member, a deadline, and result announcement; auto-set winner as next read (S); ranked-choice voting (C) |
| FR-CLB-18 | M | Clubs shall support events with title, description, start/end time, location or meeting URL, and RSVP (yes/no/maybe); times are stored with timezone and rendered in each member's local time; ICS download provided. Automated reminders (S); recurring events (C) |
| FR-CLB-19 | S | Clubs shall keep a history of completed reads (book, dates, linked discussions, originating poll) |
| FR-CLB-20 | M | Members may leave at any time; their posts remain attributed. Account deletion anonymizes their club posts ("former member") per NFR-PRV-02 |
| FR-CLB-21 | M | **Privacy guarantee:** Private and Secret club content shall never appear in public pages, internal search results for non-members, activity feeds outside the club, notification previews to non-members, recommendation signals, or search-engine indexes; membership of Secret clubs is itself non-discoverable |
| FR-CLB-22 | S | Members shall have per-club notification settings, including a digest-only mode |
| FR-CLB-23 | C | Clubs shall have a default member cap (e.g., 150) with a platform-configurable ceiling, reserved as a future premium lever |

### 3.8 Social and discovery (FR-SOC)

| ID | P | Requirement |
|---|---|---|
| FR-SOC-01 | M | Users shall be able to follow other users (asymmetric); follower and following lists respect profile privacy |
| FR-SOC-02 | M | The home feed shall combine followed users' visible activity with summaries from the user's clubs |
| FR-SOC-03 | M | A club directory shall list Public and Private clubs with search and filters (genre, language, size); Secret clubs never appear |
| FR-SOC-04 | S | The system shall generate book recommendations from the user's shelves and ratings using content-based signals; private-club data is excluded (FR-CLB-21) |
| FR-SOC-05 | C | Book pages shall show a "readers also enjoyed" section |
| FR-SOC-06 | M | Every feed item shall respect the strictest applicable privacy setting of its source object |

### 3.9 Notifications (FR-NTF)

| ID | P | Requirement |
|---|---|---|
| FR-NTF-01 | M | The system shall provide an in-app notification center with read/unread state |
| FR-NTF-02 | M | Email notifications shall cover high-value events: club invite, join approval, mention, event reminder, poll opening/closing, milestone date reached |
| FR-NTF-03 | S | The system shall support web push for installed PWA users |
| FR-NTF-04 | M | Preferences shall be granular per category and per club, with a global mute |
| FR-NTF-05 | S | Users shall be able to opt into a daily or weekly digest consolidating club activity |

### 3.10 Trust, safety, and moderation (FR-MOD)

| ID | P | Requirement |
|---|---|---|
| FR-MOD-01 | M | Users shall be able to report content, users, and clubs with a categorized reason and optional free text |
| FR-MOD-02 | M | Platform moderators shall have a queue to review reports and take actions: remove content, warn, suspend, ban; reporters are notified of resolution |
| FR-MOD-03 | M | Club moderation is independent: club moderators handle in-club content, with an escalation path to platform moderation; platform staff can act inside any club when handling a report |
| FR-MOD-04 | S | The system shall apply automated spam/abuse throttles (link limits and posting caps for new accounts, burst rate limits) |
| FR-MOD-05 | M | All moderation and administrative actions shall be recorded in an immutable audit log |
| FR-MOD-06 | M | Terms of Service, Privacy Policy, and Community Guidelines shall be versioned, with consent captured at signup and re-consent on material change |

### 3.11 Administration (FR-ADM)

| ID | P | Requirement |
|---|---|---|
| FR-ADM-01 | M | An admin console shall provide user lookup and account actions, content tools, the reports queue, and librarian-queue oversight |
| FR-ADM-02 | M | The console shall show operational metrics: signups, MAU/WAU, retention cohorts, club counts and activity, catalog growth |
| FR-ADM-03 | S | The system shall support feature flags for staged rollouts |
| FR-ADM-04 | C | Admins shall be able to publish in-product announcements or banners |

---

## 4. External Interface Requirements

### 4.1 User interface

- Responsive layout from 360 px to 1920 px; primary flows optimized mobile-first
- WCAG 2.1 AA compliance (see NFR-USE); full keyboard navigability of core flows
- All user-facing strings externalized for localization; no hard-coded copy
- Every zero-data view (empty shelf, new club, no notifications) shall have a designed empty state with a next action
- Dark mode (S)

### 4.2 Software interfaces

| Interface | Purpose | Notes |
|---|---|---|
| Open Library API | Primary bibliographic metadata and covers | Respect rate limits and cover licensing (CON-02) |
| Google Books API | Secondary metadata fallback | API key management; quota monitoring |
| Transactional email provider | Verification, resets, notifications, digests | SPF/DKIM/DMARC configured; suppression-list handling |
| Object storage (S3 API) | Covers, avatars, club images, post attachments | Private objects served via signed, time-limited URLs (NFR-SEC-06) |
| OAuth providers (Google, Apple) | Federated sign-in (FR-ACC-03) | — |
| Web Push | PWA notifications (FR-NTF-03) | VAPID keys |
| ICS generation | Club event export (FR-CLB-18) | RFC 5545 |

There is no Goodreads interface: migration is file-based only (CON-01).

### 4.3 Platform API

- All client functionality shall be served by a versioned JSON API (v1); no privileged client-only paths — authorization lives entirely server-side
- A documented public/partner API for future mobile apps (S); outbound webhooks (C)

---

## 5. Non-Functional Requirements

### 5.1 Performance (NFR-PRF)

| ID | Requirement |
|---|---|
| NFR-PRF-01 | Core read endpoints (book page, shelf, club home) shall respond within 300 ms at p95 under nominal load |
| NFR-PRF-02 | Catalog search shall return within 700 ms at p95, including external-lookup fallback deferral (external fetches happen asynchronously after local results render) |
| NFR-PRF-03 | Largest Contentful Paint shall be under 2.5 s at p75 on a mid-range mobile device over 4G |
| NFR-PRF-04 | Rating aggregates may be eventually consistent, converging within 60 seconds |

### 5.2 Scalability (NFR-SCL)

| ID | Requirement |
|---|---|
| NFR-SCL-01 | The system shall be designed for 100,000 registered users / 20,000 MAU with 10× headroom without re-architecture |
| NFR-SCL-02 | The application tier shall be stateless and horizontally scalable; images served via CDN |

### 5.3 Security (NFR-SEC)

| ID | Requirement |
|---|---|
| NFR-SEC-01 | The application shall meet OWASP ASVS Level 2 |
| NFR-SEC-02 | Passwords hashed with Argon2id (or bcrypt at appropriate cost); all traffic over TLS 1.2+ |
| NFR-SEC-03 | Every object access (club, post, shelf, review) shall be authorized server-side per request; no reliance on client-side hiding — this is the enforcement backbone of FR-CLB-13 and FR-CLB-21 |
| NFR-SEC-04 | Automated tests shall cover IDOR/authorization cases for all privacy-critical endpoints and run in CI as a release gate |
| NFR-SEC-05 | Rate limiting on write and auth endpoints; dependency and container image scanning in CI |
| NFR-SEC-06 | Images belonging to Private/Secret clubs and private profiles shall be non-guessable and served via signed, expiring URLs |

### 5.4 Privacy and data protection (NFR-PRV)

| ID | Requirement |
|---|---|
| NFR-PRV-01 | The system shall honor GDPR rights: access, export (FR-ACC-08), rectification, and erasure |
| NFR-PRV-02 | Erasure shall complete within 30 days of the grace period ending; club posts are anonymized rather than deleted to preserve conversation integrity, with all personal identifiers removed |
| NFR-PRV-03 | Analytics shall be first-party and consent-based; no third-party advertising trackers |
| NFR-PRV-04 | Personal data locations and processors shall be documented (records of processing); backups encrypted at rest |

### 5.5 Availability and reliability (NFR-AVL)

| ID | Requirement |
|---|---|
| NFR-AVL-01 | Target availability 99.5% monthly for v1 |
| NFR-AVL-02 | Daily encrypted backups; RPO ≤ 24 h, RTO ≤ 4 h; restore procedure tested quarterly |

### 5.6 Usability and accessibility (NFR-USE)

| ID | Requirement |
|---|---|
| NFR-USE-01 | A new user shall be able to sign up and add their first book within 3 minutes without documentation |
| NFR-USE-02 | Club creation shall take no more than 5 steps to a shareable invite link |
| NFR-USE-03 | The application shall conform to WCAG 2.1 AA, including contrast, focus states, and screen-reader labels |
| NFR-USE-04 | Error messages shall state what happened and what the user can do next |

### 5.7 Localization (NFR-L10N)

| ID | Requirement |
|---|---|
| NFR-L10N-01 | Full i18n architecture (ICU message format, externalized strings, locale-aware dates/numbers); adding a locale requires no code changes |
| NFR-L10N-02 | Launch locales: English, Russian, Uzbek (Latin) — assumption to confirm (§9) |
| NFR-L10N-03 | All times stored in UTC with source timezone and rendered in the viewer's local timezone — mandatory for club events and milestone deadlines |
| NFR-L10N-04 | Catalog content (titles, authors, descriptions) supports any language independent of UI locale |

### 5.8 Maintainability and SEO (NFR-MNT)

| ID | Requirement |
|---|---|
| NFR-MNT-01 | CI/CD with a staging environment; automated test coverage of at least 70% on privacy, authorization, and club-logic modules |
| NFR-MNT-02 | Structured logging and error tracking with alerting on error-rate anomalies |
| NFR-MNT-03 | Public book, author, and Public-club pages shall be server-rendered and indexable; Private/Secret club pages return authentication challenges and noindex (CON-06) |

---

## 6. Data Requirements

### 6.1 Principal entities

| Group | Entities |
|---|---|
| Identity | User, Profile, Session, Follow, Block |
| Catalog | Work, Edition, Author, Series, Genre, Tag, LibrarianSubmission |
| Library | Shelf, ShelfItem, ReadingSession (start/finish pairs), Rating, Review, ReviewComment, ProgressUpdate, ReadingChallenge |
| Clubs | Club, ClubMember, Invite, JoinRequest, ClubRead, Milestone, MemberMilestoneProgress, Thread, Post, Reaction, Poll, PollOption, Vote, Event, RSVP |
| Platform | Notification, NotificationPreference, Report, ModerationAction, AuditLog, ConsentRecord |

### 6.2 Retention and lifecycle

- Soft-deleted accounts retained 30 days, then erased/anonymized (NFR-PRV-02)
- Invite links expire after 14 days by default; expired links are revocable history, not reusable
- Application logs retained 90 days; audit logs retained 2 years; backups retained 30 days
- Report records retained per legal requirements even after related content removal

---

## 7. Release Plan (MoSCoW roll-up)

| Phase | Contents | Exit criterion |
|---|---|---|
| Phase 1 — MVP | All **M** requirements: accounts, catalog with submissions, shelves and statuses, ratings/reviews, progress, Goodreads import, clubs with schedule + spoiler gate + polls + events, notifications (in-app, email), moderation, admin basics | A closed-beta club of 10+ members completes one full scheduled read end-to-end |
| Phase 2 — v1.x | **S** items: OAuth, stats, re-read history, schedule assistant, prompts, digests, push, recommendations, club history, concurrent reads | Retention and club-activation metrics justify Phase 3 |
| Phase 3 — v2 | **C** items, public API, native mobile apps, monetization experiments (e.g., club premium: higher caps, advanced polls) | — |

Every requirement ID in this document shall be mapped to a tracker issue for traceability.

---

## 8. Acceptance Criteria (samples)

**Spoiler gate (FR-CLB-13)**
- Given a member whose club progress is Milestone 2, when they open a thread bound to Milestone 3, then the post titles are visible but bodies are withheld, with a notice and a reveal control
- Given the same member taps Reveal on one post, then only that post's body is fetched and shown, and their progress marker remains Milestone 2
- Given a non-member requests any Secret-club resource by direct URL or API call, then the response is indistinguishable from "not found"

**Goodreads import (FR-SHF-06)**
- Given a valid Goodreads CSV export, when imported, then statuses, ratings, reviews, and read dates appear on the correct default shelves
- Given rows that match no catalog entry, then the user receives an unmatched-titles report with a one-click "submit to catalog" action per row

**Event timezones (FR-CLB-18)**
- Given an event created for 19:00 in the owner's timezone, when a member in a different timezone views it, then the time is shown in the member's local timezone, and the downloaded ICS opens correctly in their calendar

**Erasure (NFR-PRV-02)**
- Given a deleted account past the 30-day grace period, then its club posts remain readable but display an anonymized author, and no personal data of the user is retrievable via any endpoint or export

---

## 9. Open Questions

| # | Question | Owner | Blocking? |
|---|---|---|---|
| 1 | Confirm launch market(s) and locales — EN/RU/UZ assumed | Product | Before UI copy freeze |
| 2 | Monetization model (club premium vs. reader premium vs. none for v1) and any free-tier caps | Product | No — architecture keeps levers open (FR-CLB-23) |
| 3 | Is ranked-choice voting worth the complexity, or is single-vote enough for v1? | Product + Design | No |
| 4 | Licensing review of cover images from Open Library/Google Books and of user-uploaded covers | Legal | Before public launch |
| 5 | Moderation staffing model at launch (founder-led vs. outsourced first line) | Product | Before public launch |
| 6 | Native app timeline — determines how soon the public API (§4.3) must harden | Product + Engineering | No |
| 7 | Minimum-age policy per launch jurisdiction (16 default assumed) | Legal | Before public launch |

---

## Appendix A. Club permissions matrix

| Action | Owner | Moderator | Member |
|---|---|---|---|
| Edit club settings, privacy tier | ✔ | — | — |
| Transfer ownership, delete club | ✔ | — | — |
| Grant/revoke moderator role | ✔ | — | — |
| Invite members, approve join requests | ✔ | ✔ | link-share if enabled |
| Remove/ban members | ✔ | ✔ | — |
| Set current read, edit schedule | ✔ | ✔ | — |
| Create polls and events | ✔ | ✔ | nominate/vote/RSVP |
| Pin, lock, remove posts | ✔ | ✔ | own posts only |
| Post, react, reply | ✔ | ✔ | ✔ |
| Leave club | transfer first | ✔ | ✔ |

*End of document — SRS v0.1, 13 July 2026.*
