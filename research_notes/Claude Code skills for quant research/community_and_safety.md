# Community-recommended Claude Code skills for data science / quant / statistics, and third-party skill safety

Research date: 2026-10-09. All web sources were read with WebSearch/WebFetch only; nothing was installed or executed. Star counts and install counts are as reported by each source on its date and were not independently verified unless noted. Search did not surface any Hacker News, Reddit, X/Twitter, Instagram or YouTube threads directly (queries aimed at news.ycombinator.com and Reddit returned only blogs and vendor pages), so "community" evidence below is from blogs, vendor articles, registries and GitHub pages.

## Q1. Which data/stats/research skill repos are repeatedly recommended, and by whom?

### Takeaway
The one third-party repo that every data/science/finance roundup recommends is K-Dense-AI's scientific skills collection (now `K-Dense-AI/scientific-agent-skills`, formerly `claude-scientific-skills`), which has statsmodels, PyMC, scikit-learn, time-series, Polars and EDA skills. It has the clearest evidence of real use (about 48k stars in Oct 2026, up from about 8k in Feb 2026). Other repos are recommended once or twice each. Quant-specific backtesting skills exist, but they are tiny and have no evidence of real use.

### Cited Findings
**K-Dense-AI scientific skills (most repeated recommendation)**
- Snyk's "Top 8 Claude Skills for Finance and Quantitative Developers" (Stephen Thoemmes, 2026-02-18) ranks `K-Dense-AI/claude-scientific-skills` #1. It cites coverage of data analysis, time series (ARIMA, GARCH), statistical modelling, ML and visualization, 140 skills, 8,241 stars, MIT, and a requirement for Python 3.12+ and `uv` — [Snyk](https://snyk.io/articles/top-claude-skills-finance-quantitative-developers/)
- AI Builder Club's "Claude Code for Data Scientists: the dataviz Skill + 35 More" (author "Shirley", published 2026-06-11, updated 2026-08-26) lists `K-Dense-AI/scientific-agent-skills` with 34K stars and 163 skills — [AI Builder Club](https://www.aibuilderclub.com/blog/claude-code-for-data-scientists-skills-guide)
- An aggregator listed 31.9k stars, last updated 2026-07-28 — [vibeindex / search summary](https://vibeindex.ai/marketplaces/K-Dense-AI/claude-scientific-skills)
- The GitHub page (fetched 2026-10-09) says "Claude Scientific Skills is now Scientific Agent Skills" and gives the repo as `K-Dense-AI/scientific-agent-skills` with about 48.2k stars and 177 skills. Skills relevant to this project include statsmodels, scikit-learn, PyMC, Statistical Analysis workflows, aeon and TimesFM (time series), Polars, Dask, Vaex, Exploratory Data Analysis, and database lookups including FRED, SEC EDGAR and U.S. Treasury Fiscal Data. It has no dedicated finance-analysis skill. The repo is MIT, but per-skill licences may differ. Some skills bundle `scripts/`, and many call external services (PubChem, ChEMBL, NCBI, Exa, and others). Installing the skill files does not install their dependencies — [GitHub K-Dense-AI](https://github.com/K-Dense-AI/claude-scientific-skills)
- Install routes listed on the page are `npx skills add K-Dense-AI/scientific-agent-skills`, `gh skill install ...` (with optional version pinning), and a manual clone into `~/.agents/skills/` or `.agents/skills/`. An older listing gives `/plugin marketplace add K-Dense-AI/claude-scientific-skills` — [GitHub K-Dense-AI](https://github.com/K-Dense-AI/claude-scientific-skills); [search summary of skillselion/vibeindex listings](https://skillselion.com/plugin/K-Dense-AI/claude-scientific-skills)
- K-Dense says every skill is scanned with the Cisco AI Defense Skill Scanner and the results are published in a security report. It recommends installing only the skills you need, reading each SKILL.md, and running the scanner locally, and it notes that a clean scan does not guarantee a skill is safe — [GitHub K-Dense-AI](https://github.com/K-Dense-AI/claude-scientific-skills)
- Unofficial mirrors and forks exist, for example `kellsaro/k-dense-ai-claude-scientific-skills` and `DenDen047/claude-scientific-skills`. Use the official org — [search results](https://github.com/kellsaro/k-dense-ai-claude-scientific-skills)
- K-Dense also sells a commercial "K-Dense Web" co-scientist platform, so the open repo doubles as marketing for it — [vibeindex / search summary](https://vibeindex.ai/collection/k-dense-ai/claude-scientific-skills)

**Other data-science repos recommended (each in one or two roundups)**
- AI Builder Club (Jun/Aug 2026) lists the following, with stars or skills.sh-style install counts where the article gave them — [AI Builder Club](https://www.aibuilderclub.com/blog/claude-code-for-data-scientists-skills-guide):
  - `anthropics/skills`: 171K stars
  - `davila7/claude-code-templates`: scientific Python and scikit-learn, 30K stars
  - `anthropics/knowledge-work-plugins`: dashboard builder 591 installs, plus `sql-queries`
  - `openai/skills` jupyter-notebook: 2.4K installs
  - `shubhamsaboo/awesome-llm-apps` visualization-expert: 2.9K installs
  - `mindrally/skills` analytics-data-analysis: 551 installs
  - `borghei/claude-skills` data-analyst: 368 installs
  - `motherduckdb/agent-skills`: 17 DuckDB skills, official from the vendor
  - `dbt-labs/dbt-agent-skills`: official dbt
  - `tvhahn/matplotlib-skill`
  - `wshobson/agents` ml-pipeline-workflow
  - `VoltAgent/awesome-agent-skills`: a directory of 1,424+ skills
  - It also names a built-in `dataviz` skill bundled with Claude Code.
- Snyk (Feb 2026) adds the following — [Snyk](https://snyk.io/articles/top-claude-skills-finance-quantitative-developers/):
  - `anthropics/claude-cookbooks` creating-financial-models skill: DCF and Monte Carlo, 32,682 stars
  - `quant-sentiment-ai/claude-equity-research`: 290 stars, labelled "educational use only"
  - `jeremylongshore/claude-code-plugins-plus-skills`: backtesting and risk among 1,537 skills, 1,312 stars
  - `tfriedel/claude-office-skills`: 244 stars
  - `liangdabiao/claude-data-analysis`: six sub-agents incl. QA and hypothesis generation, 318 stars
  - `coffeefuelbump/csv-data-summarizer-claude-skill`: 229 stars
  - `VoltAgent/awesome-agent-skills`: catalog including a quant-analyst agent for VaR, drawdown and walk-forward testing, 6,532 stars
- Registry listings (claudemarketplaces.com, claudskills.com) surface the following. These are listings, not endorsements — [claudemarketplaces data-scientist](https://claudemarketplaces.com/skills/sickn33/antigravity-awesome-skills/data-scientist); [claudemarketplaces statistics-math](https://claudemarketplaces.com/skills/pluginagentmarketplace/custom-plugin-data-engineer/statistics-math); [claudskills K-Dense statistical-analysis](https://claudskills.com/skills/statistical-analysis--skills-k-dense-ai/); [claudemarketplaces data-science category](https://claudemarketplaces.com/skills/category/data-science):
  - `sickn33/antigravity-awesome-skills` data-scientist: A/B tests, causal inference, PyMC3, SHAP
  - `pluginagentmarketplace/custom-plugin-data-engineer` statistics-math: SciPy and statsmodels, warns about p-hacking
  - K-Dense statistical-analysis: test selection, assumption checks, power analysis
  - a data-science category of 583+ skills

**Quant / backtesting-specific skills (small, little or no usage evidence)**
- `Jimmy7892/quant-research-skill` is a five-phase "honest backtesting" workflow (Frame, Simulate, Map, Correct, Decide) with gates. It refuses to report a single argmax parameter set and covers deflated Sharpe, walk-forward, PBO and effective sample size. It bundles 4 Python scripts (`region_pool.py`, `effective_n.py`, `selection_bias.py`, `sizing.py`) and is MIT-licensed. It had **7 stars, 0 forks**, and installs via `claude plugin marketplace add Jimmy7892/quant-research-skill`. The author also wrote the ManifoldBT engine used in its examples — [GitHub Jimmy7892](https://github.com/Jimmy7892/quant-research-skill)
- `shakeebshaan/claude-code-quant-skills` includes a `/backtest-review` skill that audits look-ahead bias, survivorship bias, overfitting, costs and regime dependence. It installs by copying into `~/.claude/skills/`. No usage data was found — [GitHub shakeebshaan (search snippet)](https://github.com/shakeebshaan/claude-code-quant-skills)
- `omer-metin/skills-for-antigravity` quantitative-research covers backtesting, alpha, factor models and stat-arb — [claudemarketplaces](https://claudemarketplaces.com/skills/omer-metin/skills-for-antigravity/quantitative-research)
- `VoltAgent/awesome-claude-code-subagents` quant-analyst is a subagent, not a skill — [GitHub VoltAgent](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/07-specialized-domains/quant-analyst.md)
- A Substack guide warns that "most publicly available skills don't just fail to help. They actively hurt - adding tokens, adding latency" — [corpwaters Substack (search snippet)](https://corpwaters.substack.com/p/the-ultimate-guide-to-claude-code)
- An Analytics Insight "Top Claude AI skills for data scientists in 2026" list was found in search but not read — [Analytics Insight](https://www.analyticsinsight.net/amp/story/artificial-intelligence/top-claude-ai-skills-for-data-scientists-in-2026)

### Inferences
- Star counts for K-Dense conflict across sources (8.2k Feb → 31.9k Jul → 34k Aug → 48.2k Oct 2026). This is consistent with fast growth across snapshots rather than an error, and it is the strongest "real usage" signal of any data/stats repo found. No source provides usage data beyond stars and skills.sh-style install counts.
- The quant/backtesting skills match this project's standards closely: no look-ahead, walk-forward, multiple-testing correction. But each has single-digit to unknown stars and no independent review. They are better read as reference material than installed, and their checklists largely duplicate the controls the repo already enforces (BH screen, walk-forward, variants log).
- K-Dense's documented install paths (`.agents/skills/`, `~/.agents/skills/`) are not among the skill locations Claude Code documents (`.claude/skills/`). A project install for Claude Code would need the specific skill folders copied into `.claude/skills/` (see Q4).
- None of the roundups compares skills head-to-head on quality. "Best" is popularity plus author reputation, not measured benefit.

### Gaps
- No HN, Reddit, X/Twitter, Instagram or YouTube posts were retrieved. Searches aimed at them returned none, so I cannot report what those communities recommend.
- No independent benchmark of whether any data/stats skill improves analysis quality.
- Not verified: the content of the shakeebshaan and omer-metin skills, and current star counts for most repos other than K-Dense, anthropics/skills and knowledge-work-plugins.

## Q2. What official Anthropic skills/plugins exist for data analysis?

### Takeaway
Anthropic ships three relevant first-party sources:
- `anthropics/knowledge-work-plugins`, which has a **data** plugin (SQL, visualization, statistical analysis, dashboards, validation) and a **finance** plugin (accounting/close-oriented, not quant).
- `anthropics/financial-services-plugins`, aimed at IB, equity research, PE and wealth management, with partner data plugins such as LSEG and S&P.
- `anthropics/skills`, which has document skills plus examples and is labelled demonstration/educational.

None of them is designed for quantitative time-series research. The data plugin's `statistical-analysis` and `validate-data` skills are the closest fit.

### Cited Findings
- `anthropics/knowledge-work-plugins` holds 11 plugins for Cowork, also compatible with Claude Code, including **data** ("Querying, visualization, statistical analysis, dashboards, validation"; connectors Snowflake, Databricks, BigQuery, Definite, Hex, Amplitude, Jira) and **finance** (journal entries, reconciliation, financial statements, variance analysis, close, audit support). It has 28.2k stars, Apache-2.0. Install with `claude plugin marketplace add anthropics/knowledge-work-plugins` then `claude plugin install data@knowledge-work-plugins` — [GitHub anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins)
- AI Builder Club cites the knowledge-work `interactive-dashboard-builder` (591 installs) and `sql-queries` (5 SQL dialects) skills — [AI Builder Club](https://www.aibuilderclub.com/blog/claude-code-for-data-scientists-skills-guide)
- `anthropics/financial-services-plugins`: you add the marketplace, install the core `financial-analysis` plugin first, then `investment-banking`, `equity-research`, `private-equity` and `wealth-management`. It is built for Cowork and compatible with Claude Code. A third-party guide adds that there are partner plugins for LSEG and S&P Global; its counts may be stale — [ecosyste.ms listing](https://awesome.ecosyste.ms/projects/github.com%2Fanthropics%2Ffinancial-services-plugins); [Medium guide (third-party)](https://medium.com/@marcos.magri/claude-for-financial-services-a-practical-no-fluff-guide-89e3d98b72aa)
- `anthropics/skills` has 180.2k stars. Install with `/plugin marketplace add anthropics/skills` then `/plugin install document-skills@anthropic-agent-skills` or `example-skills@anthropic-agent-skills`. The README disclaimer reads: "These skills are provided for demonstration and educational purposes only ... Always test skills thoroughly in your own environment before relying on them for critical tasks." The docx/pdf/pptx/xlsx skills are source-available, not open source; many others are Apache 2.0 — [GitHub anthropics/skills](https://github.com/anthropics/skills)
- `anthropics/claude-cookbooks` contains a `creating-financial-models` custom skill (DCF, sensitivity analysis, Monte Carlo, Excel output) — [Snyk](https://snyk.io/articles/top-claude-skills-finance-quantitative-developers/)
- Official marketplace names are reserved and accepted only when sourced from `github.com/anthropics/`. They include `claude-plugins-official`, `anthropic-agent-skills`, `knowledge-work-plugins`, `financial-services-plugins`, `claude-for-financial-services` and `life-sciences`. Community-tier names are `claude-community`, `claude-plugins-community` and `healthcare` — [Claude Code docs: Plugin security](https://code.claude.com/docs/en/plugins/security); [Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference)
- Auto-update is on by default for official marketplaces **except** `knowledge-work-plugins` and `first-party-plugins`, and off by default for community and third-party marketplaces — [Claude Code docs: Install plugins](https://code.claude.com/docs/en/plugins/install)
- The Anthropic engineering post "Equipping agents for the real world with Agent Skills" (Barry Zhang, Keith Lazuka, Mahesh Murag; 2025-10-16, updated 2025-12-18 when Agent Skills became an open standard) explains progressive disclosure: name and description are preloaded, the full SKILL.md is read when relevant, and linked files are read on demand. It also explains that bundled scripts run as tools without being loaded into context — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### Inferences
- In this cloud environment the knowledge-work `data:*` skills (`data:statistical-analysis`, `data:validate-data`, `data:explore-data`, and others) and `finance:*` skills already appear in the available-skills list. They seem to come through the claude.ai account or org rather than from the repo. This is an observation of the current session, not a documented guarantee.
- The official finance plugins centre on corporate finance and accounting (DCF, close, reconciliation). They are not built for time-series or relative-value futures research. The data plugin's statistics and validation skills are general-purpose and would need to be checked against this repo's stricter standards: walk-forward only, bootstrap CIs, variants logging.

### Gaps
- I did not enumerate the exact skill files in the knowledge-work `data/` folder from the repo itself. The list above comes from this session's skill listing and secondary sources.
- I did not read the financial-services-plugins README directly. Plugin names come from search summaries.

## Q3. What incidents or audits of malicious or low-quality skills have been reported?

### Takeaway
2026 saw several large audits and at least one mass-malware campaign, concentrated on open registries (ClawHub/OpenClaw especially):
- Koi's ClawHavoc: 341, later 824 malicious skills.
- Snyk: 76 confirmed malicious among 3,984 skills, and 13.4% with critical issues.
- ESET: about 0.3% (1 in 300) of about 900k skills directly malicious.
- SkillCloak (HKUST) showed that existing scanners can be evaded more than 90% of the time.

Curated or top-ranked lists such as the skills.sh top 100 showed far fewer problems. Malice can sit purely in markdown prose or in bundled files, so neither scanners nor a clean-looking SKILL.md are sufficient.

### Cited Findings
- **Snyk, "Exploring the Threat Landscape of Agent Skills" (2026-02-05):**
  - 3,984 skills analysed from clawhub.ai and the skills.sh top 100.
  - 76 confirmed malicious skill identities (credential theft, backdoors, exfiltration), at least 8 still installable at publication.
  - 13.4% (534) had at least one Critical issue; 36.82% (1,467) had lower-severity issues.
  - All confirmed malicious skills triggered malicious-code and suspicious-download detectors, and 91% also used prompt injection.
  - Unverifiable remote dependencies appeared in 21% of malicious samples.
  - One actor generated 40+ malicious skills. A "heartbeat" skill re-downloaded its own instructions on every run.
  - The skills.sh top 100 showed negligible Critical findings.
  - Recommendations: review code and scripts, distrust popularity as a safety signal, use Snyk Agent Scan / mcp-scan as well as manual review.
  - [Snyk Research](https://research.snyk.io/blog/agent-skills-threat-landscape/)
- Snyk's later finance roundup restates ToxicSkills figures inconsistently ("prompt injection in 36%", "1,467 malicious payloads", "13% critical"). The 1,467 figure in the original is the count of lower-severity findings, so treat the roundup's numbers as garbled and use the original — [Snyk finance article](https://snyk.io/articles/top-claude-skills-finance-quantitative-developers/); contradicted by [Snyk Research](https://research.snyk.io/blog/agent-skills-threat-landscape/)
- **Koi Security "ClawHavoc" (2026-02-03, updated 2026-02-16):**
  - 341 malicious skills among 2,857 on ClawHub; 335 delivered the Atomic Stealer macOS infostealer through fake "Prerequisites" sections (password-protected ZIPs, obfuscated shell scripts).
  - Some skills had reverse shells or credential exfiltration, for example `better-polymarket`.
  - By the 02-16 update ClawHub had grown to 10,700+ skills and the count had grown to 824 malicious.
  - Koi released the "Clawdex" scanner.
  - [Koi blog](https://koi.ai/blog/clawhavoc-341-malicious-clawedbot-skills-found-by-the-bot-they-were-targeting); [The Hacker News](https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html?hl=en)
- Antiy CERT counts at least 1,184 malicious skills historically on ClawHub — [Antiy](https://www.antiy.net/p/clawhavoc-analysis-of-large-scale-poisoning-campaign-targeting-the-openclaw-skill-market-for-ai-agents/)
- **ESET H1 2026 Threat Report (reported 2026-07-13):** about 900,000 skills analysed; about 25,000 (2.8%) suspicious and more than 3,000 (about 0.3%, "1 in 300") directly malicious. Techniques: malicious instructions hidden in READMEs and docs the agent reads, hidden local scripts that harvest credentials, and exploitation of install-time trust. The report recommends treating skills as third-party software under inventory and review — [Expert Insights](https://expertinsights.com/news/1-in-300-ai-agent-skills-is-directly-malicious-eset-research-finds)
- **SkillCloak, HKUST (arXiv 2607.02357; reported 2026-07-09):**
  - "Packing" (payload moved into a directory the scanner skips) evaded every tested scanner more than 90% of the time.
  - Token rewriting evaded more than 80% of most static scanners, and a hybrid rule+LLM scanner was evaded 96% of the time.
  - Cloaked skills still worked.
  - The countermeasure SkillDetonate (sandboxed behavioural detonation) reported 97% detection on synthetic attacks at about 2% false positives, and 87% on real malicious skills.
  - [Help Net Security](https://www.helpnetsecurity.com/2026/07/09/malicious-ai-agent-skills-scan/); [CSA research note](https://labs.cloudsecurityalliance.org/research/csa-research-note-skillcloak-agent-skill-evasion-20260706-cs/)
- A July 2026 arXiv preprint (2606.23416) scanned about 134k skills across three marketplaces. It flagged 258 on Lobehub, 101 on ClawHub and 0 on skills.sh, of which 83 and 48 were human-confirmed — [arXiv 2606.23416 (search summary)](https://arxiv.org/pdf/2606.23416)
- Another study's flag rates differed by marketplace: 46.8% ClawHub, 23% skills.sh, 6% SkillsDirectory. The authors note this may reflect false positives, and a separate paper argues that malicious rates may be overstated — [arXiv 2603.16572](https://arxiv.org/html/2603.16572v1)
- **Proof-of-concept attacks specific to Claude skills:**
  - Cato CTRL showed a legitimate-looking Claude skill running a MedusaLocker ransomware test while showing clean approval prompts. It was disclosed to Anthropic on 2025-10-30 and published 2025-12-02 — [Cato Networks](https://catonetworks.com/blog/cato-ctrl-weaponizing-claude-skills-with-medusalocker)
  - Secure Trajectories hid white-on-white instructions in a PDF referenced by an otherwise clean SKILL.md — [Secure Trajectories](https://securetrajectories.substack.com/p/claude-skill-hijack-invisible-sentence)
  - These two were seen as search snippets only; the full pages were not read.
- OWASP's Agentic Skills Top 10 lists "AST01 — Malicious Skills" (credential stealers, reverse shells or backdoors hidden in markdown prose; skills run with the host agent's permissions) — [OWASP AST01](https://owasp.org/www-project-agentic-skills-top-10/ast01.html) (search snippet)
- A SkillsDirectory scan (Sept 2026) of 103,619 public skills reported 86.2% clean. This is a vendor scan with its own methodology limits — [SkillsDirectory](https://skillsdirectory.com/blog/claude-skills-security-report) (search snippet)

### Inferences
- The documented mass campaigns targeted OpenClaw's ClawHub, not Anthropic's marketplaces. But the attack surface is the same for Claude Code skills (SKILL.md instructions plus bundled scripts, often crossposted), and Snyk names Claude Code users as targets of a 30+ skill campaign.
- Finance and crypto themes appear among the lures (Polymarket skills, exchange API keys, wallet keys). That is directly relevant to a repo holding Alpaca paper credentials in environment variables.
- Since scanners can be evaded and malice can be pure prose, manual reading of every file, a pinned commit, and minimal permissions matter more than any scanner badge.

### Gaps
- No incident was found of a malicious skill in Anthropic's own official or community marketplaces.
- Snyk's "ToxicSkills" branding and the exact Snyk count of Claude Code-targeted malicious skills were not confirmed from a primary page; the Snyk page I read refers to an OpenSourceMalware report of 30+ skills.
- The Cato, Secure Trajectories, OWASP and SkillsDirectory pages were seen only as search snippets.

## Q4. What is the recommended way to vet and pin a third-party skill, and how do you install one into a single project repo so cloud sessions pick it up?

### Takeaway
Anthropic's guidance is to install only from trusted sources and to read every file (SKILL.md, scripts, hooks, `.mcp.json`, `bin/`, and the `allowed-tools` frontmatter) before use. Plugins should be pinned to a full 40-character commit `sha` (or a tag via `#ref`), with auto-update left off for third-party marketplaces.

**For cloud sessions the only reliable route is to commit the reviewed skill folder into the repo's `.claude/skills/<name>/`.** Cloud sessions load committed `.claude/skills/`, but they do **not** install plugins or marketplaces declared in the repo's `.claude/settings.json` (`enabledPlugins` and `extraKnownMarketplaces`).

### Cited Findings
**Security model**
- "A Claude Code plugin you install can execute arbitrary code on your machine with your user privileges." Hooks, monitors, MCP/LSP servers and mod processes run **outside** the sandbox with full user permissions. A plugin's `bin/` is added to the Bash PATH. Skills, commands and agents enter context as instructions. With auto-update on, "the files you reviewed can change on disk" — [Claude Code docs: Plugin security and trust](https://code.claude.com/docs/en/plugins/security)
- Anthropic's install warning: "Anthropic does not control what MCP servers, files, or other software are included in plugins and cannot verify that they will work as intended or that they won't change." A marketplace's name "tells you who publishes the catalog, not what each plugin in it does," so review every plugin, whatever the marketplace — [Plugin security and trust](https://code.claude.com/docs/en/plugins/security)
- The community catalog (`claude-community`) pins nearly every entry to a commit SHA, and Claude Code refuses to install a different commit — [Plugin security and trust](https://code.claude.com/docs/en/plugins/security)
- Anthropic engineering blog: "malicious skills may introduce vulnerabilities in the environment where they're used"; "We recommend installing skills only from trusted sources"; "When installing a skill from a less-trusted source, thoroughly audit it before use". Audit bundled files, code dependencies, images and scripts, and watch for instructions to connect to untrusted external network sources — [Anthropic Engineering, 2025-10-16](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

**Skills docs: security-relevant behaviour**
- `allowed-tools` pre-approves tools for the invoking turn and "applies even in untrusted folders. Workspace trust does not gate it, even in `-p` runs. Review the `allowed-tools` of any skill checked into a repository before running Claude Code there." It is not a restriction; other tools remain callable — [Claude Code docs: Skills](https://code.claude.com/docs/en/skills)
- Injected shell commands (`` !`cmd` ``) run when a skill renders. They are checked against permission rules, and a deny aborts. `disableSkillShellExecution` turns them off, and `allowManagedPermissionRulesOnly` (v2.1.282+) makes Claude Code ignore `allowed-tools` in project and personal skills. `Skill(name)` deny rules block a specific skill — [Claude Code docs: Skills](https://code.claude.com/docs/en/skills)

**Vetting steps (official)**
- Run `claude plugin marketplace list` to see the source.
- Read the `/plugin` details pane ("Will install").
- Read `hooks/hooks.json`, `.mcp.json` and every file in `bin/`.
- Clone the plugin and run `claude --plugin-dir <dir> plugin details <name>` for a component inventory without starting a session. After install, `claude plugin details <name>` inventories the cached copy.
- [Plugin security and trust](https://code.claude.com/docs/en/plugins/security)

**Vetting steps (third-party)**
- Snyk: read SKILL.md and all scripts, scrutinize `allowed-tools` (Bash especially), keep proprietary data and brokerage API keys away from untrusted skills, and "Treat skills the way you would treat any third-party code" — [Snyk finance article](https://snyk.io/articles/top-claude-skills-finance-quantitative-developers/)
- Snyk research: avoid skills with remote instruction loading or auto-update, and use a scanner as well as manual review — [Snyk Research](https://research.snyk.io/blog/agent-skills-threat-landscape/)

**Pinning**
- Marketplace add: `/plugin marketplace add owner/repo#ref` (for example `your-org/plugins#v1.2.0`); git URLs also take `#ref` — [Install plugins](https://code.claude.com/docs/en/plugins/install)
- The marketplace-source table also accepts `owner/repo@ref` — [Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference)
- Plugin entries using the `github`, `url` or `git-subdir` source take `ref` (branch or tag) and `sha` (a full 40-character lowercase commit). If both are set, `sha` is checked out. `archive` sources take a `sha256` digest, and a mismatch refuses the install — [Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference)
- Example (sha shortened here; a real pin needs all 40 characters): `{"name":"formatter","source":{"source":"github","repo":"your-org/formatter","ref":"v2.0.0","sha":"a1b2c3d4…"}}` — [Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference)
- A self-hosted marketplace can therefore wrap a third-party plugin and pin it to a reviewed commit — [Create a marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- Auto-update is off by default for third-party and community marketplaces, and can be toggled per marketplace in the `/plugin` Marketplaces tab — [Install plugins](https://code.claude.com/docs/en/plugins/install)

**Scopes and project install**
- Skill locations: personal `~/.claude/skills/<name>/SKILL.md` ("not Cowork or cloud sessions"), project `.claude/skills/<name>/SKILL.md`, nested `<subdir>/.claude/skills/`, and plugin `<plugin>/skills/<name>/`. "Commit `.claude/skills/` to version control and everyone who works in the repository gets the skill. Cloud sessions also load project skills committed to the cloned repository." Precedence for the same name is enterprise > personal > project; plugin skills are namespaced — [Claude Code docs: Skills](https://code.claude.com/docs/en/skills)
- Plugin install scopes:
  - user: `~/.claude/settings.json` `enabledPlugins`
  - project: `.claude/settings.json`, committed. This enables the plugin but does not download it; each collaborator runs `claude plugin install <name>@<marketplace> --scope project`.
  - local: `.claude/settings.local.json`
  - [Install plugins](https://code.claude.com/docs/en/plugins/install)
- Cloud sessions: "has no plugin browser and doesn't load the plugins you installed on your own machine or the ones your repository's `.claude/settings.json` turns on" — [Install plugins](https://code.claude.com/docs/en/plugins/install)
- The cloud environments "What carries over" table says:
  - The repo's `.claude/skills/`, `.claude/agents/`, `.claude/commands/` and `CLAUDE.md`: **Yes**.
  - Hooks and permissions in `.claude/settings.json`: Yes, in a single-repo session.
  - "Plugins and marketplaces declared in your repo's `.claude/settings.json`": **No** ("A cloud session doesn't install the plugins a repository turns on under `enabledPlugins` ... `extraKnownMarketplaces`").
  - User `~/.claude/skills/`: No ("Commit them to the repo's `.claude/` directory instead. Cloud sessions automatically load skills you enable on claude.ai").
  - [Claude Code docs: Cloud environments](https://code.claude.com/docs/en/cloud-environments)
- Org-wide plugins reach cloud sessions only through server-managed settings — [Install plugins](https://code.claude.com/docs/en/plugins/install); [Cloud environments](https://code.claude.com/docs/en/cloud-environments)
- `/plugin` is not available in cloud sessions — [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)
- A SessionStart hook in the repo's `.claude/settings.json` runs in both local and cloud sessions, and `$CLAUDE_CODE_REMOTE == "true"` detects cloud. The documented example uses it to install dependencies — [Cloud environments](https://code.claude.com/docs/en/cloud-environments)
- Conflict: the docs say claude.ai-enabled skills load into cloud sessions automatically, but a July 2026 user issue report says they did not in fresh web sessions — [claudeissues.com #75261](https://claudeissues.com/issue/75261-skills-enabled-on-claude-ai-are-not-loaded-into-claude-code-web-cloud-sessions) (unverified single report); contradicted by [Cloud environments docs](https://code.claude.com/docs/en/cloud-environments)

### Inferences
Recommended procedure for this repo, combining the docs above:
1. Pick one specific skill folder, not a whole 177-skill collection.
2. Clone the upstream repo at a specific commit and record the full SHA.
3. Read SKILL.md, every reference file and every script, and check `allowed-tools` and any `` !`cmd` `` injections, network calls or remote-instruction loading.
4. Copy only that folder into `.claude/skills/<name>/`.
5. Record the upstream URL, commit SHA, licence and reason in `docs/decisions.md`, as the repo's CLAUDE.md requires for new dependencies.
6. Commit it. Cloud sessions will then load it from the clone.

Updates then become explicit, reviewed diffs.

Other points:
- Installing a plugin via project `.claude/settings.json` gives no benefit for cloud sessions. The docs say it is ignored there. A SessionStart hook could run `claude plugin install` in cloud, but that is not a documented pattern and it would fetch code at session start. That breaks the "pin and review" property unless the plugin is pinned by `sha` in a self-controlled marketplace.
- Committed project skills with `allowed-tools` are honoured even in untrusted folders, so a vendored skill should carry no `allowed-tools`, or a narrowly scoped one. Skills that call external APIs would conflict with this repo's source and terms rules, and with the rule not to call MCP connectors from autonomous runs.

### Gaps
- No documented, supported way to have a cloud session install a marketplace plugin from repo settings, other than org server-managed settings.
- I did not verify whether the K-Dense `gh skill install` "version pinning" pins to a commit SHA or to a tag.
