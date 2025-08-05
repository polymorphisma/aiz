## 🔧 **Project Summary: AIZ – The AI CLI Navigator**

### **1. Concept**

**AIZ** is a context-aware, AI-powered command-line assistant that turns natural language instructions into safe, executable shell commands. It dynamically reads local help documentation from CLI tools to ensure accuracy, version-compatibility, and privacy.

---

### **2. Problem**

Modern developers rely on dozens of CLI tools, each with their own flags, options, and subcommands. Remembering syntax is inefficient, and switching to Google or StackOverflow:

* Breaks focus and flow
* Often returns outdated answers
* Creates a productivity bottleneck

---

### **3. Solution**

**AIZ** bridges the gap between user intent and precise CLI usage:

* It **scrapes the real-time `--help` output** of any CLI tool (and subcommands).
* An **LLM interprets user input** and generates the correct command.
* A **confirmation step** ensures commands are safe to run.

**Example:**

```bash
aiz git squash the last 3 commits  
# Suggests: git rebase -i HEAD~3  
# Prompts: Run this? [Y/n]
```

---

### **4. Key Features**

#### ✅ Natural Language Interface

Just type what you want to do:

```bash
aiz docker run redis in background, map port 6379
```

#### 🔍 Dynamic Help Scraper

Fetches live, tool-specific help docs from your installed CLI version:

* `git --help`
* `docker run --help`
* `poetry add --help`, etc.

#### 🤖 Hybrid AI Engine

* **Default Mode:** Fully offline using local LLMs (e.g., Phi-3, Gemma via [Ollama](https://ollama.com/)).
* **Optional Power Mode:** Use OpenAI/Gemini/Anthropic via API key for higher-quality completions.

#### 🛡️ Secure by Design

* Every command is previewed.
* **User must confirm** before execution (`[Y/n]` prompt).
* No auto-run, no surprises.

#### 🧠 Always Version-Compatible

By using local `--help`, aiz always matches the tool version on your system—unlike online tutorials that may be outdated.

---

## 🚀 Updated Project Plan

### 🔸 **Phase 1: Foundation (v0.1 – v0.2)**

* [x] Build CLI scaffold using **Typer** (`aiz <tool> <query>`)
* [x] Parse tool and query from CLI input
* [ ] Add subprocess logic to run `<tool> --help` and capture output
* [ ] Handle subcommands (`aiz docker run ...` → fetch `docker run --help`)

### 🔸 **Phase 2: AI Integration (v0.3 – v0.4)**

* [ ] Install and configure **Ollama** with a local LLM (e.g., phi3\:mini)
* [ ] Create prompt template using:

  * Help text
  * User objective
  * System instruction (`"You are a CLI expert..."`)
* [ ] Send prompt to local Ollama server
* [ ] Display generated command and request `[Y/n]` confirmation
* [ ] If confirmed, run via `subprocess`

### 🔸 **Phase 3: Feature Polish (v1.0)**

* [ ] Smart context fetching for multi-level commands (e.g., `docker compose logs`)
* [ ] Add caching for frequently used tools
* [ ] Add fallback error messages if parsing fails
* [ ] Clean CLI output formatting (colors, indentation)

### 🔸 **Phase 4: Extensions (v1.1+)**

* [ ] **Shell Alias Integration:** Enable `?? git ...` or `az ...` shortcuts in `.bashrc`/`.zshrc`
* [ ] **Cloud LLM Option:** Add config for OpenAI/Gemini via API key
* [ ] **Multi-step Command Support:** Handle workflows like `find + xargs + zip`
* [ ] **Auto-Update Cache:** Re-scrape help text if version changes

---

## 📦 Tech Stack Overview

| Component     | Choice          | Purpose                           |
| ------------- | --------------- | --------------------------------- |
| Language      | Python          | Core application logic            |
| CLI Framework | Typer or Click  | Clean CLI parsing and UX          |
| AI Runtime    | Ollama          | Local LLM hosting and serving     |
| Models        | Phi-3, Gemma 2B | Small, efficient instruction LLMs |
| Execution     | Subprocess      | Command execution & help scraping |

---

## 💡 Why AIZ Matters

AIZ is more than a productivity tool—it's a safer, smarter way to interact with the command line. By turning intent into action with local AI and real-time documentation, it transforms how developers work at the terminal.
