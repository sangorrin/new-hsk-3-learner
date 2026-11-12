# New-HSK-3-Learner

A static, bilingual study app for learners of the New HSK 3.0 course.

## Features

- Lesson-based study for lessons 1–18.
- Five modes: Hanzi, Words, Phrases, Grammar, and Flashcards.
- Search across Chinese text, pinyin, English meanings, and lesson content.
- Text-to-speech pronunciation using the browser Speech Synthesis API.
- Local favorites and study progress with `localStorage`.
- HanziVG-first stroke-order rendering with a compatible fallback when data is unavailable.
- Responsive interface for desktop and mobile browsers.
- Static deployment to GitHub Pages.

The generated course data is bundled with the application, so a fresh clone can run without any source workbook files.

## Development

Requirements: Node.js 24 LTS and npm.

```bash
npm install
npm run dev
```

The development server runs at <http://localhost:3000>.

## Validation and build

```bash
npm run lint
npm run build
```

## GitHub Pages

The workflow in `.github/workflows/deploy.yml` builds and deploys the `dist` directory when changes are pushed to `main` or `master`.

In the repository settings, configure GitHub Pages to use **GitHub Actions** as the deployment source.

## Licensing

- Application code: [MIT License](./LICENSE).
- Hanzi stroke data: HanziVG/KanjiVG-compatible sources retain their respective CC BY-SA 3.0 requirements.
- Course workbook content remains subject to its original educational/content rights.

