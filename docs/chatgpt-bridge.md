# ChatGPT ↔ MoneyPrinterTurbo

A lightweight GitHub Actions bridge for this fork. It uses the connected GitHub app in ChatGPT, the real MoneyPrinterTurbo CLI and GitHub's hosted runners. No OpenAI API key or extra always-on web server is needed. The finished video is attached as a GitHub Actions artifact, not embedded inside ChatGPT.

## Activate once

1. Open the repository Actions tab and enable workflows if GitHub asks you to enable Actions on a fork.
2. The default mode uses generated, animated title slides (not real scene generation), Edge TTS voice narration and video rendering. No content API key is required, but GitHub Actions minutes and network access are required.
3. Optional stock footage: add your free Pexels API key as repository secret PEXELS_API_KEY in Settings > Secrets and variables > Actions. Then request source pexels.

## Submit from ChatGPT

Ask ChatGPT to create a MoneyPrinterTurbo video and to use GitHub create_issue in repository mohammedaabakhsh/moneyprinterturbo.

The issue title MUST start with [MPT] and a space. The GitHub issue author MUST be the repository owner. The issue body MUST be plain JSON, NOT a code-fenced JSON block.

Example issue title: [MPT] جولة في جدة

Example issue body:

    {
      "title": "جولة في جدة",
      "script": "جدة مدينة ساحلية تجمع التراث والبحر. نبدأ رحلتنا من الكورنيش، ثم نتعرف على أحيائها التاريخية.",
      "source": "slides",
      "language": "ar-SA",
      "aspect": "9:16",
      "scenes": ["أهلًا بكم في جدة", "على ساحل البحر الأحمر", "تاريخ وثقافة"]
    }

For Pexels footage, use source "pexels" and provide up to eight English stock-search terms in an array named "terms", for example ["Jeddah waterfront", "Saudi Arabia coastline"]. Missing key will cause a clear failure. No paid video provider is used. The script is always prewritten by ChatGPT, so an OpenAI API key is unnecessary.

Available aspect ratios: 9:16, 16:9, 1:1. Languages: ar-SA or en-US. Six scene headings maximum.

## Results

The workflow reads and validates the issue body, uses MoneyPrinterTurbo to narrate and render the script, uploads video.mp4 as an artifact (7-day retention) and posts an artifact or error link as a comment on the issue. Open the Actions tab or issue comment to inspect progress and download.

## Safety and limitations

- This is a PUBLIC repository: issue titles, scripts and prompts are public. Do not include customer information, secrets, unpublished materials or private data.
- Only the repository owner can trigger video generation through Issues. All values are passed as program arguments, not shell commands.
- This route supports video production from prepared text and images/stock clips. It is NOT real text-to-video cinematic generation.
- GitHub-hosted runners and Edge TTS may fail or hit resource limits. A successful repository edit is not a verified end-to-end video render; make a test request after Actions is enabled.
- For private jobs, uploads, cinematic generation or a persistent ChatGPT-accessible video API, use a secure deployed backend and connect a custom plugin.
