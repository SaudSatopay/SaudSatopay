<!-- ============================== HEADER ============================== -->
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:7aa2f7,50:bb9af7,100:7dcfff&height=230&section=header&text=Saud%20Satopay&fontSize=64&fontColor=ffffff&animation=twinkling&fontAlignY=36&desc=AI%2FML%20Engineer%20%C2%B7%20Data%20%E2%86%92%20Model%20%E2%86%92%20API%20%E2%86%92%20Interface&descAlignY=57&descSize=20" width="100%" alt="Saud Satopay — AI/ML Engineer" />

<a href="https://github.com/SaudSatopay">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1200&color=7AA2F7&center=true&vCenter=true&width=720&lines=Hybrid+RAG+%C2%B7+on-device+vision+%C2%B7+risk+engines;50%C2%B5s+decisions+%C2%B7+700k+signals%2Fsec+per+core;100%25+Hit%403+retrieval+%E2%80%94+fully+offline;Upstream+patches%3A+libheif+%C2%B7+assimp+%C2%B7+libavif;NIRMAN+2026+Winner+%F0%9F%8F%86" alt="What I build" />
</a>

<br/>

<a href="https://saudsatopay.netlify.app/"><img src="https://img.shields.io/badge/Portfolio-00C7B7?style=for-the-badge&logo=netlify&logoColor=white" alt="Portfolio" /></a>
<a href="https://www.linkedin.com/in/saud-satopay"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
<a href="mailto:satopaysaud@gmail.com"><img src="https://img.shields.io/badge/Email-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Email" /></a>
<a href="https://www.instagram.com/saudd02"><img src="https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram" /></a>

<br/><br/>

<img src="https://komarev.com/ghpvc/?username=SaudSatopay&label=Profile%20views&color=7aa2f7&style=for-the-badge" alt="Profile views" />

</div>

<!-- ============================== ABOUT ============================== -->
## `$ whoami`

I'm **Saud** — an AI/ML engineer who likes hard, load-bearing problems: retrieval that can't hallucinate, risk engines that can't miss, vision that runs where there's no internet. Most of what's below started as a hackathon sprint and got hardened into a system — eval harness, ablations, latency budget and all.

- 🧠 **Applied AI** — hybrid RAG (dense + sparse + cross-encoder rerankers), deterministic risk engines, agentic tool-calling
- 👁️ **Vision at the edge** — TFLite / MobileFaceNet fully on-device, YOLOv8 in the loop
- 🔩 **The unglamorous parts** — eval harnesses, ablation studies, property-based tests, offline reproducibility
- 🛡️ **Upstream OSS** — memory-safety & validation patches merged into `libheif` and `assimp`, one in review at `libavif`
- 🏆 **NIRMAN 2026 Winner** — CrackWatch, an AI infrastructure-damage command center (₹75K prize)
- 🎓 B.Tech Computer Engineering ('27) · Thane, India · open to AI/ML roles & collabs

> **Data → Model → API → Interface** — I own the whole pipe.

<div align="center">
<br/>
<img src="https://raw.githubusercontent.com/SaudSatopay/SaudSatopay/main/assets/hero-terminal.svg" width="760" alt="Animated terminal running Saud's systems" />
</div>

<br/>

<div align="center"><img src="https://raw.githubusercontent.com/SaudSatopay/SaudSatopay/main/assets/divider.svg" width="92%" alt="" /></div>

<!-- ============================== FLAGSHIP ============================== -->
## `$ ls ./flagship-systems`

<table>
<tr>
<td width="50%" valign="top">

<h3><a href="https://github.com/SaudSatopay/trinetra">🛰️ trinetra</a></h3>
<p>Compound-risk intelligence for industrial safety. A <b>deterministic engine</b> fuses gas sensors, hot-work permits & CCTV into one risk score — LangGraph agents explain the decision, they never make it. Replayed against real disasters (Texas City '05, Jaipur '09), it fires minutes before any single sensor.</p>
<p>
<img src="https://img.shields.io/badge/p50-~50%C2%B5s-7aa2f7?style=flat-square&labelColor=1a1b27" alt="p50 ~50µs" />
<img src="https://img.shields.io/badge/throughput-~700k_tags%2Fs%2Fcore-bb9af7?style=flat-square&labelColor=1a1b27" alt="~700k tags/s/core" />
<img src="https://img.shields.io/badge/recall-100%25_(240_unseen)-9ece6a?style=flat-square&labelColor=1a1b27" alt="100% recall" />
</p>
<sub><code>Python</code> · <code>FastAPI</code> · <code>LangGraph</code> · <code>NetworkX</code> · <code>YOLOv8</code> · <code>Gemini</code></sub>

</td>
<td width="50%" valign="top">

<h3><a href="https://github.com/SaudSatopay/BIS-COMPASS">🧭 BIS-COMPASS</a></h3>
<p>Plain English in → <b>Bureau of Indian Standards codes</b> out. Four-stage hybrid retrieval: FAISS (bge-m3) + BM25 → reciprocal-rank fusion → cross-encoder rerank, with a whitelist guard so it <i>can't</i> hallucinate a standard. Auto-clamps to available VRAM, all the way down to CPU.</p>
<p>
<img src="https://img.shields.io/badge/Hit%403-100%25-7aa2f7?style=flat-square&labelColor=1a1b27" alt="Hit@3 100%" />
<img src="https://img.shields.io/badge/MRR%405-0.93-bb9af7?style=flat-square&labelColor=1a1b27" alt="MRR@5 0.93" />
<img src="https://img.shields.io/badge/latency-0.45%E2%80%930.85s-7dcfff?style=flat-square&labelColor=1a1b27" alt="sub-second latency" />
<img src="https://img.shields.io/badge/mode-offline--first-9ece6a?style=flat-square&labelColor=1a1b27" alt="offline-first" />
</p>
<sub><code>Python</code> · <code>FAISS</code> · <code>bge-m3</code> · <code>BM25</code> · <code>cross-encoder</code> · <code>FastAPI</code></sub>

</td>
</tr>
<tr>
<td width="50%" valign="top">

<h3><a href="https://github.com/SaudSatopay/Offline_Facial_Recognition_-_Liveness_Detection_System">🫥 Offline Face Recognition + Liveness</a></h3>
<p>Face recognition & liveness detection that works <b>where the internet doesn't</b>. MobileFaceNet on TensorFlow Lite, entirely on-device — built for remote sites with zero connectivity.</p>
<p>
<img src="https://img.shields.io/badge/accuracy-98.3%25-7aa2f7?style=flat-square&labelColor=1a1b27" alt="98.3% accuracy" />
<img src="https://img.shields.io/badge/connectivity-zero_required-9ece6a?style=flat-square&labelColor=1a1b27" alt="zero connectivity required" />
<img src="https://img.shields.io/badge/inference-on--device-bb9af7?style=flat-square&labelColor=1a1b27" alt="on-device inference" />
</p>
<sub><code>React Native</code> · <code>TensorFlow Lite</code> · <code>MobileFaceNet</code></sub>

</td>
<td width="50%" valign="top">

<h3><a href="https://github.com/SaudSatopay/CrackWatch-NirmanHackathon">🏆 CrackWatch</a></h3>
<p>AI command center for civic infrastructure — detects and triages structural damage from imagery, then routes it like an ops platform. Took home <b>NIRMAN 2026</b>. Since rebuilt AI-native on the Lemma SDK → <a href="https://github.com/SaudSatopay/crackwatch-lemma"><code>crackwatch-lemma</code></a>.</p>
<p>
<img src="https://img.shields.io/badge/NIRMAN_2026-Winner_%F0%9F%8F%86-e0af68?style=flat-square&labelColor=1a1b27" alt="NIRMAN 2026 Winner" />
<img src="https://img.shields.io/badge/prize-%E2%82%B975K-9ece6a?style=flat-square&labelColor=1a1b27" alt="₹75K prize" />
</p>
<sub><code>Vision AI</code> · <code>JavaScript</code> · <code>Lemma SDK</code></sub>

</td>
</tr>
<tr>
<td width="50%" valign="top">

<h3><a href="https://github.com/SaudSatopay/live-interview-assistant">🎙️ live-interview-assistant</a></h3>
<p>Real-time Q&A teleprompter: live voice capture → <b>Groq Whisper</b> transcription → <b>Gemini</b> answers, streamed to a glanceable overlay while you keep talking.</p>
<p>
<img src="https://img.shields.io/badge/pipeline-voice_%E2%86%92_answer-7dcfff?style=flat-square&labelColor=1a1b27" alt="voice to answer" />
<img src="https://img.shields.io/badge/mode-real--time-bb9af7?style=flat-square&labelColor=1a1b27" alt="real-time" />
</p>
<sub><code>Python</code> · <code>Groq Whisper</code> · <code>Gemini</code></sub>

</td>
<td width="50%" valign="top">

<h3><a href="https://github.com/SaudSatopay/sunpath-solar">🤖 Agentic builds</a></h3>
<p><a href="https://github.com/SaudSatopay/sunpath-solar"><b>sunpath-solar</b></a> — an agentic AI solar sales rep that qualifies, quotes and books surveys via tool-calling with generative UI. <a href="https://github.com/SaudSatopay/sbi-saarthi"><b>sbi-saarthi</b></a> — a multi-agent banking concierge, built for SBI Hackathon @ GFF 2026.</p>
<p>
<img src="https://img.shields.io/badge/agents-tool--calling-7aa2f7?style=flat-square&labelColor=1a1b27" alt="tool-calling" />
<img src="https://img.shields.io/badge/UI-generative-bb9af7?style=flat-square&labelColor=1a1b27" alt="generative UI" />
<img src="https://img.shields.io/badge/pattern-multi--agent-7dcfff?style=flat-square&labelColor=1a1b27" alt="multi-agent" />
</p>
<sub><code>TypeScript</code> · <code>Next.js</code> · <code>LLM orchestration</code></sub>

</td>
</tr>
</table>

<sub>**Also on the bench:** [FraudShield](https://claudy-coders.vercel.app) (fintech fraud detection) · [trader-performance-vs-market-sentiment](https://github.com/SaudSatopay/trader-performance-vs-market-sentiment) (211k-trade sentiment analysis) · [ride-a-go](https://github.com/SaudSatopay/ride-a-go) (Flutter group-riding app) · [WMS](https://github.com/SaudSatopay/WMS-Warehouse-Management-System) · [more →](https://github.com/SaudSatopay?tab=repositories)</sub>

<br/><br/>

<div align="center"><img src="https://raw.githubusercontent.com/SaudSatopay/SaudSatopay/main/assets/divider.svg" width="92%" alt="" /></div>

<!-- ============================== OPEN SOURCE ============================== -->
## `$ gh pr list --author @me`

Security-hardening patches in C/C++ libraries that ship inside browsers, games and image pipelines:

| | PR | What it hardens |
|:--|:--|:--|
| <img src="https://img.shields.io/badge/merged-a371f7?style=flat-square" alt="merged" /> | [strukturag/libheif **#1840**](https://github.com/strukturag/libheif/pull/1840) | Enforces security limits on `icef` unit allocation — no unbounded memory from crafted HEIF files |
| <img src="https://img.shields.io/badge/merged-a371f7?style=flat-square" alt="merged" /> | [assimp/assimp **#6705**](https://github.com/assimp/assimp/pull/6705) | Validates B3D chunk sizes against buffer & parent chunk — stops oversized allocations from malformed models |
| <img src="https://img.shields.io/badge/in_review-3fb950?style=flat-square" alt="in review" /> | [AOMediaCodec/libavif **#3272**](https://github.com/AOMediaCodec/libavif/pull/3272) | Adopts the `__counted_by` bounds-safety model on core data buffers |

<br/>

<div align="center"><img src="https://raw.githubusercontent.com/SaudSatopay/SaudSatopay/main/assets/divider.svg" width="92%" alt="" /></div>

<!-- ============================== STACK ============================== -->
## `$ cat tech-stack.txt`

**AI & systems**

<img src="https://skillicons.dev/icons?i=py,cpp,pytorch,tensorflow,opencv,sklearn,fastapi&theme=dark" alt="Python, C++, PyTorch, TensorFlow, OpenCV, scikit-learn, FastAPI" />

<img src="https://img.shields.io/badge/Hugging%20Face-FFD21E?style=flat-square&logo=huggingface&logoColor=black" alt="Hugging Face" /> <img src="https://img.shields.io/badge/FAISS-0467DF?style=flat-square&logo=meta&logoColor=white" alt="FAISS" /> <img src="https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square&logo=langchain&logoColor=white" alt="LangGraph" /> <img src="https://img.shields.io/badge/Gemini-8E75B2?style=flat-square&logo=googlegemini&logoColor=white" alt="Gemini" /> <img src="https://img.shields.io/badge/Groq-F55036?style=flat-square" alt="Groq" /> <img src="https://img.shields.io/badge/Whisper-74AA9C?style=flat-square&logo=openai&logoColor=white" alt="Whisper" /> <img src="https://img.shields.io/badge/pandas-150458?style=flat-square&logo=pandas&logoColor=white" alt="pandas" />

**Product & apps**

<img src="https://skillicons.dev/icons?i=ts,js,react,nextjs,tailwind,nodejs,flutter,dart,supabase,firebase&theme=dark" alt="TypeScript, JavaScript, React, Next.js, Tailwind, Node.js, Flutter, Dart, Supabase, Firebase" />

**Tools**

<img src="https://skillicons.dev/icons?i=git,github,githubactions,vscode,figma,vercel,netlify&theme=dark" alt="Git, GitHub, GitHub Actions, VS Code, Figma, Vercel, Netlify" />

<br/>

<div align="center"><img src="https://raw.githubusercontent.com/SaudSatopay/SaudSatopay/main/assets/divider.svg" width="92%" alt="" /></div>

<!-- ============================== STATS ============================== -->
## `$ gh stats`

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api?username=SaudSatopay&show_icons=true&theme=tokyonight&hide_border=true&include_all_commits=true&count_private=true&rank_icon=github" />
  <img height="165" src="https://github-readme-stats.vercel.app/api?username=SaudSatopay&show_icons=true&hide_border=true&include_all_commits=true&count_private=true&rank_icon=github&bg_color=ffffff&title_color=34548a&icon_color=5a4a78&text_color=343b58" alt="Saud's GitHub stats" />
</picture>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api/top-langs/?username=SaudSatopay&layout=compact&theme=tokyonight&hide_border=true&langs_count=10&hide=html,css,scss" />
  <img height="165" src="https://github-readme-stats.vercel.app/api/top-langs/?username=SaudSatopay&layout=compact&hide_border=true&langs_count=10&hide=html,css,scss&bg_color=ffffff&title_color=34548a&text_color=343b58" alt="Top languages" />
</picture>

<br/><br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://streak-stats.demolab.com/?user=SaudSatopay&theme=tokyonight&hide_border=true" />
  <img src="https://streak-stats.demolab.com/?user=SaudSatopay&hide_border=true&background=ffffff&ring=34548a&fire=f52a65&currStreakNum=343b58&sideNums=34548a&currStreakLabel=5a4a78&sideLabels=5a4a78&dates=9699a3&stroke=e6e9ef" alt="GitHub streak" />
</picture>

<br/><br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/SaudSatopay/SaudSatopay/output/profile-night-rainbow.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/SaudSatopay/SaudSatopay/output/profile-season-animate.svg" />
  <img src="https://raw.githubusercontent.com/SaudSatopay/SaudSatopay/output/profile-night-rainbow.svg" width="96%" alt="3D contribution graph" />
</picture>

<br/><br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-activity-graph.vercel.app/graph?username=SaudSatopay&theme=tokyo-night&hide_border=true&area=true&radius=8" />
  <img width="96%" src="https://github-readme-activity-graph.vercel.app/graph?username=SaudSatopay&hide_border=true&area=true&radius=8&bg_color=ffffff&color=343b58&line=34548a&point=5a4a78&area_color=dfe6f5" alt="Contribution activity graph" />
</picture>

<br/><br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/SaudSatopay/SaudSatopay/output/github-snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/SaudSatopay/SaudSatopay/output/github-snake.svg" />
  <img src="https://raw.githubusercontent.com/SaudSatopay/SaudSatopay/output/github-snake-dark.svg" alt="Contribution snake" />
</picture>

</div>

<!-- ============================== FOOTER ============================== -->
<div align="center">

<br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://quotes-github-readme.vercel.app/api?type=horizontal&theme=tokyonight" />
  <img src="https://quotes-github-readme.vercel.app/api?type=horizontal" alt="Random dev quote" />
</picture>

<sub>⭐ If something here is useful, a star says thanks. Interesting problem? <a href="mailto:satopaysaud@gmail.com">satopaysaud@gmail.com</a></sub>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:7aa2f7,50:bb9af7,100:7dcfff&height=110&section=footer" width="100%" alt="footer" />

</div>
