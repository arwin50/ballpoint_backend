# 🧰 Setting Up Chocolatey and FFmpeg on Windows

This guide helps you install [Chocolatey](https://chocolatey.org/) (a Windows package manager) and [FFmpeg](https://ffmpeg.org/) (a powerful multimedia toolkit) for projects that need audio/video processing, such as Whisper.

---

## ✅ Step 1: Install Chocolatey

Chocolatey lets you install software from the command line with a single command.

1. Open **PowerShell as Administrator**:

   - Click **Start**
   - Search for **PowerShell**
   - Right-click → **Run as Administrator**

2. Paste the following command into the PowerShell window:

   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; `
   [System.Net.ServicePointManager]::SecurityProtocol = `
   [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
   iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

   ```

3. After installation, verify Chocolatey:

   ```powershell
   choco --version
   ```

## ✅ Step 2: Install FFmpeg

Now that Chocolatey is installed, installing FFmpeg is easy.

1. In the same Administrator PowerShell window, run:

   ```powershell
   choco install ffmpeg -y

   ```

2. Once done, check that FFmpeg is installed to see FFmpeg version information printed:

   ```powershell
   ffmpeg -version
   ```

## ✅ Final Step: Restart Your Environment

After installation:

- Restart any open terminals, editors (like VS Code), or development servers.
- Make sure ffmpeg works by running it in a new terminal.
