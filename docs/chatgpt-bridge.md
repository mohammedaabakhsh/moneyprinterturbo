# ChatGPT to MoneyPrinterTurbo via GitHub Actions

This fork has a no-server integration path. ChatGPT uses your already connected GitHub app to create a new branch and a JSON request file. A GitHub Actions runner then uses the actual MoneyPrinterTurbo CLI to create an MP4 and stores it in the workflow's downloadable artifacts.

No OpenAI API is necessary because ChatGPT writes the script and sends it in the request. This integration cannot make the MoneyPrinterTurbo WebUI run natively inside ChatGPT.

## One-time setup

Open the Actions tab of this fork and enable workflows if GitHub asks you to enable Actions for a fork.

For the free slide-based demo, no media API key is necessary. GitHub Actions runner time and access to Edge TTS are necessary.

For real stock footage, create a free Pexels API key and store it under repository Settings > Secrets and variables > Actions > New repository secret. Name it PEXELS_API_KEY.

## Video request from ChatGPT

1. Ask ChatGPT to create a video, and instruct it to use this repository.
2. ChatGPT writes the Arabic or English video script and scene headings.
3. ChatGPT uses GitHub create_branch (base_ref main) with a unique branch name starting with video-requests/. For example: video-requests/jeddah-demo-1.
4. ChatGPT uses GitHub create_file in that branch to create exactly one request file at the repository root named video-request.json. The JSON object must include title and script, and optional source, aspect, language, scenes and terms.
5. The push starts the workflow in the branch. The Actions run produces an MP4 artifact and displays a download link in the job summary.
6. ChatGPT can read the workflow run's status with the connected GitHub tool.

Example content of video-request.json:

    {
      "title": "جولة في جدة",
      "script": "جدة مدينة ساحلية تجمع التراث والبحر. نبدأ رحلتنا من الكورنيش، ثم نتعرف على أحيائها التاريخية.",
      "source": "slides",
      "language": "ar-SA",
      "aspect": "9:16",
      "scenes": ["أهلًا بكم في جدة", "على ساحل البحر الأحمر", "تاريخ وثقافة"]
    }

Valid aspect ratios: 9:16, 16:9 and 1:1. Languages: ar-SA and en-US. Up to six scene headings. Two source modes:

- slides: creates illustrated text slides with audio narration and MPT editing. It does NOT create real cinematic AI footage. No media API key needed.
- pexels: actual stock footage from Pexels; requires a repository secret PEXELS_API_KEY and a terms list of up to eight English search phrases, for example ["Jeddah waterfront", "Saudi Arabia coastline"].

The workflow uploads video.mp4 as an artifact retained for seven days. All video generation and assembly happens on GitHub's runner; GitHub does not host a permanent web service.

## Privacy, cost, and reliability

This repository is PUBLIC. Branches, commits and video-request.json are publicly readable. Do not submit sensitive prompts or private information. Secrets must be stored in GitHub Secrets, never in JSON requests or Git history.

Any failure caused by GitHub runner limits, timeouts, Edge TTS availability, font rendering or provider APIs is shown in the Actions logs. Do not claim that a video was made until the Actions run finishes successfully and uploads its MP4.

For a fully private, always-on, authenticated API directly attached to a dedicated ChatGPT plugin, deploy MoneyPrinterTurbo on a separate backend. This GitHub Actions bridge is the serverless first stage.
