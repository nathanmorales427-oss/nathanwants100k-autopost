# Weekly producer: how the Claude routine makes next week's carousels

You are filling `queue/` with one carousel per day for the next 7 days (dates in Quito time, folder = `queue/YYYY-MM-DD`).
Nathan (@nathanwants100k, 19, investing + money history creator) approved fully automatic posting with a
veto window: every carousel must be good enough to post with NO human edit. Skip any date that already has a folder.

## The calendar (show per weekday)
| Mon | Tue | Wed | Thu | Fri | Sat | Sun |
|---|---|---|---|---|---|---|
| Money History | Money News | Money Basics | Money History | Money News | Value Story | Money History |
An anniversary beats the calendar: if a famous money event happened on that date (Black Tuesday Oct 29, Lehman Sep 15,
Nixon shock Aug 15...), make that day's post about it. Pick topics from TOPICS.md and move them to "Used" with the date.

## Hard rules (never break)
1. **Every number and date traces to a source** you actually opened this run (prefer primary: Federal Reserve History,
   BLS, Fed, SEC, Treasury, Britannica, AP/Reuters for news). List them in `post.json` "sources". If you can't verify a
   fact, cut it. Never invent a quote, number, date, name or result.
2. **Never about Nathan's own holdings, trades, stock picks, account balances or personal life.** No "buy X", no price
   targets, no predictions. Money News = what happened and why it matters, explained simply.
3. Any line about what Nathan does with money ends with "(not financial advice)" on that slide.
4. Photos: only public domain / CC (Wikimedia Commons, Library of Congress, government). Download from
   `upload.wikimedia.org` (md5 path: `/wikipedia/commons/thumb/<h0>/<h0h1>/<File_Name>/1280px-<File_Name>`; the Commons
   API rate-limits bursts). Credit every photo on its slide and in the caption ("Photo: <author/archive> / <license>").
   No identifiable private people, no AI images, no brand ads. 0-3 photos per carousel is fine.
5. Voice: Nathan's. Short plain sentences, first person where natural, no em dashes, no "Let's dive in", no "In
   conclusion", no hype words. Read like a smart 19-year-old texting a friend.

## Shape (6-9 slides)
1. Hook slide: the most surprising true number or fact + "Here's what happened." / "Here's why." (+ the best photo).
2. Strongest fact next (front-load).
3-N. One idea per slide, max ~45 words. Text-only slides are fine (they render bigger).
N-2. "Why I think about this at 19:" + the lesson in one or two lines (+ "(not financial advice)" if it's a money move).
N-1. **Saveable summary slide:** "The whole story in 4 lines:" then 3-4 short numbered takeaways (dates, numbers, the
     lesson). This is the slide people screenshot and save; it must stand alone.
N. One ending earned by the topic, NOT a generic line: a real question tied to the story ("Would you have sold?"),
   OR a specific save reason ("Save this for the next time..."), OR a specific person to send it to. Rotate them.

**One question per carousel.** Cut side stories (they become their own carousel). Date every study and estimate.

## Caption (caption field)
Line 1: the hook with the searchable topic words + 1 emoji (under 125 characters). Blank line. "Send this to the friend
who ..." Blank line. 2-3 short lines summarising. "New <Show> every day. Follow along 👇" + "@nathanwants100k". Photo
credits. "Source: ..." (1-2 main ones). "Not financial advice." Max 5 hashtags, topic first.

## Steps
1. `pip install pillow` then for each missing date: research, write `queue/<date>/post.json` (format: render.py
   docstring; photos in `queue/<date>/photos/`), run `python render.py queue/<date>`.
2. LOOK at every slide image you rendered. Fix anything cut off, misspelled or wrong, re-render.
3. `git add queue TOPICS.md && git commit -m "queue: <dates>" && git push`.
4. Final report: one line per date (show, hook, slide count, sources). Nathan vetoes by deleting a folder.
