# 🚀 GitHub Profile Status Bar & Dynamic HUD System

> **A real-time, cyberpunk-styled HUD & telemetry status bar for your GitHub Profile README.**  
> Automatically refreshes developer metrics, 365-day contribution signals, streak data, active IDE, and coding status with **Dark & Light Mode** auto-switching!

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white" alt="Python 3.12">
  <img src="https://img.shields.io/badge/GitHub_Actions-Automated-2088FF?logo=github-actions&logoColor=white" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/Theme-Dark%20%7C%20Light%20Adaptive-00C49F" alt="Adaptive Themes">
  <img src="https://img.shields.io/badge/Template-One--Click%20Ready-ff69b4" alt="One-Click Ready">
</p>

---

## 📸 Live Preview

### 1. System Metrics
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Sachith-Gunarathna/GitHub-status-bar-system/main/assets/system-metrics-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Sachith-Gunarathna/GitHub-status-bar-system/main/assets/system-metrics-light.svg">
  <img width="100%" alt="GitHub System Metrics" src="https://raw.githubusercontent.com/Sachith-Gunarathna/GitHub-status-bar-system/main/assets/system-metrics-light.svg">
</picture>

### 2. Contribution Signal Graph
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Sachith-Gunarathna/GitHub-status-bar-system/main/assets/contribution-signal-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Sachith-Gunarathna/GitHub-status-bar-system/main/assets/contribution-signal-light.svg">
  <img width="100%" alt="Contribution Signal Graph" src="https://raw.githubusercontent.com/Sachith-Gunarathna/GitHub-status-bar-system/main/assets/contribution-signal-light.svg">
</picture>

### 3. Developer Signal & Live Heartbeat
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Sachith-Gunarathna/GitHub-status-bar-system/main/assets/dev-signal-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Sachith-Gunarathna/GitHub-status-bar-system/main/assets/dev-signal-light.svg">
  <img width="100%" alt="Dev Signal" src="https://raw.githubusercontent.com/Sachith-Gunarathna/GitHub-status-bar-system/main/assets/dev-signal-light.svg">
</picture>

---

## ⚡ Quick Setup: Add This to YOUR Profile (In 60 Seconds)

Anyone can set this up for their own GitHub profile in 4 simple steps:

### 1️⃣ Click "Use this template"
Click the green **[Use this template](https://github.com/Sachith-Gunarathna/GitHub-status-bar-system/generate)** button at the top of this repository (or **Fork** it) to create a copy under your account.

### 2️⃣ Enable Workflow Permissions
To allow GitHub Actions to commit your generated status SVGs:
1. In your new repository, go to **Settings** ➡️ **Actions** ➡️ **General**.
2. Scroll down to **Workflow permissions**.
3. Select **"Read and write permissions"** and click **Save**.

### 3️⃣ Run First Generation
1. Go to the **Actions** tab in your repository.
2. Select the **"Update GitHub HUD"** workflow from the left sidebar.
3. Click **"Run workflow"** ➡️ **"Run workflow"**.  
   *(The system automatically detects your GitHub username — no manual code changes required!)*

### 4️⃣ Add Snippets to your Profile README
Open your special Profile repository (`<YOUR_USERNAME>/<YOUR_USERNAME>`) and add the following snippets into your `README.md`.

> 💡 **Tip:** Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub username and repo name!

```html
<!-- GitHub System Metrics -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/main/assets/system-metrics-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/main/assets/system-metrics-light.svg">
  <img width="100%" alt="GitHub System Metrics" src="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/main/assets/system-metrics-light.svg">
</picture>

<!-- Contribution Signal Graph -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/main/assets/contribution-signal-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/main/assets/contribution-signal-light.svg">
  <img width="100%" alt="Contribution Signal Graph" src="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/main/assets/contribution-signal-light.svg">
</picture>

<!-- Dev Signal & Status -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/main/assets/dev-signal-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/main/assets/dev-signal-light.svg">
  <img width="100%" alt="Dev Signal" src="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/main/assets/dev-signal-light.svg">
</picture>
```

---

## 🎨 Optional Customization (`config.json`)

You can personalize the display, stack, and favorite tools by editing [config.json](config.json):

```json
{
  "github_username": "AUTO",               // Automatically detects repo owner if left as AUTO or default
  "display_name": "AUTO",                  // Your name / alias shown on the HUD
  "primary_stack": "JAVA",                 // Your main language / stack
  "active_ide": "INTELLIJ IDEA",           // Favorite IDE (VS Code, IntelliJ, NeoVim, etc.)
  "timezone": "Asia/Colombo",              // Your local timezone
  "footer_tools": [
    "VS CODE",
    "INTELLIJ IDEA",
    "ANDROID STUDIO",
    "JAVA-FIRST FULL-STACK WORKFLOW"
  ]
}
```

---

## 🛠️ How It Works

- **Auto-Detection:** GitHub Actions automatically provides `GITHUB_REPOSITORY_OWNER`, so anyone using this template gets their own metrics without having to rewrite python scripts.
- **REST & GraphQL API:** Fetches public repositories, stargazers count, followers, recent commit events, and 365-day contribution calendar.
- **Zero External Server Dependency:** Renders pure SVG images committed directly to your repository's `assets/` directory. 100% free forever using GitHub Actions.
- **Scheduled Updates:** Configured to refresh every 15 minutes via cron job (`*/15 * * * *`).

---

## ⭐ Support & Feedback

If you find this project useful, please consider giving it a **Star ⭐**! Feel free to fork, customize, and share it with the community.
