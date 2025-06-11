# 🕷️ FINOS Spider: rulebook that creates the hymen

Welcome to the most useless project you'll run today! (Yes, that bar is incredibly low)

## 🎭 Prerequisites

First things first, you'll need:

- Python 3.12+ (because we're fancy like that)
- `uv` package manager (because pip is sooo 2023)
- A will to live (optional, but recommended)

## 🎪 Setup

1. Clone this repository (if you haven't figured that out already):

   ```bash
   git clone https://github.com/trust-kernel-dtcc/hymen
   cd hymen  # Yes, that's really the name. Don't ask questions.
   ```

2. Install dependencies (it's like Christmas, but for your computer):
   ```bash
   uv sync
   ```

## 🎪 Running the Spider

Now for the moment you've all been waiting for! Navigate to the scrapy directory and unleash the beast:

```bash
cd scrapy
uv run scrapy crawl finos -o finos.json
```

Congratulations! You're now scraping FINOS data like a pro. The spider will do its thing and output everything into `finos.json`. Magic! ✨

## 📝 Notes

- If something breaks, try turning off your laptop and beat your meat
- If that doesn't work, try sacrificing a rubber duck to the debugging gods
- Still no luck? Open an issue, and we'll pretend to look at it promptly

## 🚫 Disclaimer

This spider is trained to be ethical and won't steal your cookies (the browser kind, your actual cookies are fair game).

---

Made with ❤️ and an unhealthy amount of libido
