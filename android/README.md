# samachar.ai — Android app

Native Android (Kotlin · Jetpack Compose) news reader for Nepal.

- **Auth** — Firebase Authentication (email/password + anonymous guest)
- **Data** — Cloud Firestore (articles, comments, bookmarks, notifications, AI history)
- **AI chat** — Google Gemini 1.5 Flash (`gemini-1.5-flash`)
- **Push** — Firebase Cloud Messaging (FCM)
- **UI** — Material 3, custom editorial-press theme (light + dark)

```
android/
├── settings.gradle.kts
├── build.gradle.kts                  Root Gradle (Kotlin DSL)
├── gradle.properties
├── gradle/wrapper/gradle-wrapper.properties
└── app/
    ├── build.gradle.kts              Module Gradle + dependencies
    ├── google-services.json          Already populated from your project
    ├── proguard-rules.pro
    └── src/main/
        ├── AndroidManifest.xml
        ├── java/samachar/ai/
        │   ├── SamacharApplication.kt          Init Firebase + notif channel
        │   ├── MainActivity.kt                 Compose entry + theming
        │   ├── data/
        │   │   ├── model/Models.kt             Article, UserProfile, Comment, ...
        │   │   └── repository/
        │   │       ├── AuthRepository.kt       Firebase Auth + profile doc
        │   │       ├── ArticleRepository.kt    Firestore article queries
        │   │       ├── BookmarkRepository.kt   Per-user bookmark subcollection
        │   │       ├── CommentRepository.kt    Comments + reactions
        │   │       ├── NotificationRepository.kt
        │   │       └── AiRepository.kt         Gemini wrapper + rule fallback
        │   ├── viewmodel/AppViewModel.kt       Single source of truth
        │   ├── ui/
        │   │   ├── theme/                      Editorial palette + typography
        │   │   ├── components/                 TopBar, TabBar, NewsCard, ...
        │   │   ├── navigation/AppNavGraph.kt   Routes + auth gates
        │   │   └── screens/                    10 screens
        │   └── util/SamacharMessagingService.kt    FCM handler
        └── res/                                Strings, themes, launcher icon
```

## One-time setup (15 min)

### 1. Tools

Install **Android Studio Iguana** or newer with:
- Android SDK Platform 34
- Android SDK Build-Tools 34.0.0
- JDK 17 (bundled with Android Studio)

### 2. Firebase console (project `samachar-ai-224bf`)

Open <https://console.firebase.google.com/project/samachar-ai-224bf> and:

- **Build → Authentication → Sign-in method**:
  - Enable **Email/Password**
  - Enable **Anonymous** (for guest login)
- **Build → Firestore Database → Create database**:
  - Mode: **Start in production** (we'll set rules below)
  - Region: **asia-south1** (Mumbai — lowest latency to Nepal)
- **Build → Firestore Database → Rules**:
  - Paste the contents of `../firestore-seed/firestore.rules`
  - Click **Publish**

### 3. Seed Firestore with articles + trends + notifications

```bash
cd ../firestore-seed
pip install firebase-admin
# Project Settings → Service Accounts → "Generate new private key"
# Save the downloaded JSON as service-account.json (next to seed_firestore.py)
python seed_firestore.py
```

You should see `[seeded] 10 articles · 7 trends · 5 notifications`.

### 4. Verify your SHA-1 for Firebase Auth (optional, for Google sign-in)

```bash
cd android
./gradlew signingReport       # or gradlew.bat signingReport on Windows
```

Copy the **SHA-1** from the `:app debug` variant and paste it in
Firebase Console → Project Settings → Your apps → Add fingerprint.

### 5. Build the wrapper (first time only)

Android Studio will offer to do this automatically when you open the project.
If you want to do it manually:

```bash
cd android
# If you don't have gradle installed, just open in Android Studio — it'll download.
gradle wrapper --gradle-version 8.7
```

### 6. Run

In Android Studio: **File → Open** → select the `android/` folder.
Wait for Gradle sync, then click **Run** (▶) with an emulator or device attached.

CLI alternative:

```bash
cd android
./gradlew installDebug         # builds + installs to attached device
# or
./gradlew assembleDebug        # produces app/build/outputs/apk/debug/app-debug.apk
```

## First-run flow

1. **Login** — Sign up with email/password (or tap "Continue as guest")
2. **Onboarding** — Pick 2-3 topics → choose language
3. **Home** — Tabs filter by tag; lead article is full-bleed; voice-brief and Pro teaser are inline
4. **Article** — Drop-cap body, AI brief, bias meter, comments (post + vote)
5. **Discover** — Trending list, AI suggestions
6. **AI** — Real Gemini chat, sources extracted from response
7. **Premium** — Toggle pro plan → AI quota becomes ∞
8. **Profile / Settings** — Theme, accent, density, language all persist to Firestore

## How the AI tab uses Gemini

`AiRepository.ask()` builds a Nepal-specific system prompt and calls
`GenerativeModel("gemini-1.5-flash").generateContent(...)` with your key from
`BuildConfig.GEMINI_API_KEY`. The response text is split on `SOURCES:` to
extract citations. On any error (rate-limit, offline) it falls back to a
keyword rule table so the chat still feels responsive.

To swap models — edit `AiRepository.kt`:

```kotlin
modelName = "gemini-1.5-pro"        // higher quality, more cost
```

## "Local server" mode

If you want to run the Python REST backend in parallel (e.g. for
non-Firebase testing), see `../backend/README.md` — it's a separate
self-contained Flask + SQLite app that the frontend at `../static/index.html`
talks to. The Android app does **not** depend on it — Android talks
directly to Firebase + Gemini.

## Build verification checklist

After Gradle sync, check the **Problems** panel. Common first-time fixes:

| If you see | Fix |
| --- | --- |
| "google-services.json not found" | It's in `app/` — sync Gradle again |
| "minSdk 24 is below 26" warning | Ignore — adaptive icons fall back fine |
| Gemini SDK Kotlin metadata version | Set `kotlinOptions { jvmTarget = "17" }` (already done) |
| Firestore permission denied | Re-paste rules from `firestore.rules` |

## File counts

```
27 Kotlin source files
 5 XML resource files
 4 Gradle / config files
 1 google-services.json
```

## Troubleshooting Gemini

If AI replies say "Error" or "I don't have a confident answer":

1. The key in `app/build.gradle.kts` is the default. Override locally by adding
   to `~/.gradle/gradle.properties` (per-user, never committed):
   ```
   GEMINI_API_KEY=your_actual_key
   ```
2. Make sure the Gemini API is enabled in **Google Cloud Console** for project
   `850095434966` (the project number tied to your Gemini key — separate from
   Firebase's `samachar-ai-224bf`).
3. Check Logcat for `AiRepository` errors — quota/billing issues surface there.
