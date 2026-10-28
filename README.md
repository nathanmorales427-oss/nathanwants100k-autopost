# @nathanwants100k autopost

One "post in a post" carousel every day at 6:00 PM (Quito time), posted by GitHub Actions through Instagram's official
API (free). Claude fills `queue/` once a week (see PRODUCER.md). This repo is public on purpose: Instagram downloads the
slide images from it. It holds only the post images, captions and code. The Instagram key is a GitHub secret
(`IG_TOKEN`), never in the files.

- **Veto a post:** delete its folder in `queue/` (GitHub app or website) before 6 PM that day.
- **Posted:** moved to `posted/<date>/` with the Instagram media id.
- **TikTok:** each post also has `tiktok/` (1080x1920) slides to post by hand.
- **Test without posting:** Actions → "Post today's carousel" → Run workflow (dry run is ticked by default).
- **Key expires every 60 days:** make a new one in the Meta developer dashboard and replace the `IG_TOKEN` secret.

Fonts: Inter (SIL Open Font License, fonts/OFL.txt).
