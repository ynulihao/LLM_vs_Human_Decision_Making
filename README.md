# 🧠 LLM vs Human Decision Making



> **Research Implementation**: *Large Language Models are Near-Optimal Decision-Makers with a Non-Human Learning Behavior*

This repository contains the implementation for comparing decision-making behaviors between Large Language Models (LLMs) and humans across three fundamental dimensions: **uncertainty**, **risk**, and **set-shifting**.

## 📋 Abstract

Human decision-making belongs to the foundation of our society and civilization, but we are on the verge of a future where much of it will be delegated to artificial intelligence. The arrival of Large Language Models (LLMs) has transformed the nature and scope of AI-supported decision-making; however, the process by which they learn to make decisions, compared to humans, remains poorly understood. In this study, we examined the decision-making behavior of five leading LLMs across three core dimensions of real-world decision-making: uncertainty, risk, and set-shifting. Using three well-established experimental psychology tasks designed to probe these dimensions, we benchmarked LLMs against 360 newly recruited human participants. Across all tasks, LLMs often outperformed humans, approaching near-optimal performance. Moreover, the processes underlying their decisions diverged fundamentally from those of humans. On the one hand, our finding demonstrates the ability of LLMs to manage uncertainty, calibrate risk, and adapt to changes. On the other hand, this disparity highlights the risks of relying on them as substitutes for human judgment, calling for further inquiry.


## 🧪 Experimental Tasks

### 1. 🎰 Iowa Gambling Task
Decision-making under **uncertainty**


### 2. 🎲 Cambridge Gambling Task  
Decision-making under **risk**.

### 3. 🃏 Wisconsin Card Sort Test
Decision-making under **set-shifting**. 


## ✨ Features

- 🤖 **Multi-LLM Support**: Integration with OpenAI, Anthropic, Google, and Ollama
- 👥 **Human & AI Participants**: Seamless comparison between human and LLM decision-making
- 📊 **Comprehensive Analytics**: Detailed data collection and analysis tools
- 🎨 **Modern UI**: Clean, responsive web interface built with oTree
- ⚡ **High Performance**: Concurrent processing with configurable worker pools

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- API keys for LLM providers (OpenAI, Anthropic, etc.)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/LLM_vs_Human_Decision_Making.git
   cd LLM_vs_Human_Decision_Making
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements_base.txt
   ```

3. **Configure environment**
   
   Create a `.ENV` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   GOOGLE_API_KEY=your_google_key_here
   ```

### Running the Experiments

**🖥️ Standard Mode (Human Participants)**
```bash
./run_otree.sh
```

**🤖 Bot Mode (LLM Participants)**
```bash
./run_otree_with_bot.sh task_name
```

**🧹 Cleanup Processes**
```bash
./run_clean_otree_process.sh
```

Access the interface at `http://localhost:8000`

## 📁 Project Structure

```
LLM_vs_Human_Decision_Making/
├── 🎰 iowa_gambling_task/          # Iowa Gambling Task implementation
├── 🎲 cambridge_gambling_task/     # Cambridge Gambling Task implementation  
├── 🃏 wisconsin_card_sort_test_task/ # Wisconsin Card Sort Test implementation
├── 📝 info_collector/              # Participant data collection
├── 🤖 LLM_utils/                   # LLM integration utilities
├── 🛠️ otree_utils/                 # oTree framework utilities
├── 🎨 _templates/                  # HTML templates
├── 📊 _static/                     # Static assets (CSS, JS, images)
├── ⚙️ settings.py                  # Main configuration
├── 📋 settings_sessions.py         # Session configurations
└── 📚 requirements_base.txt        # Python dependencies
```

## ⚙️ Configuration

### Session Settings

Edit `settings_sessions.py` to customize experimental parameters:

```python
# Example configuration for Iowa Gambling Task
dict(
    name='iowa_gambling_task',
    num_demo_participants=30,
    init_money=2000.0,
    card_rewards=[100, 100, 50, 50],
    use_language_model=True,
    language_model='gpt-4o',
    temperature=1.0,
    total_interactions=80,
    # ... more parameters
)
```

### Supported LLM Models

The system supports a wide range of LLM providers and models:

- **OpenAI**: `gpt-4o`, `gpt-o4-mini`
- **Claude**: `claude-3-5-sonnet`
- **Gemini**: `gemini-1.5-pro`
- **DeepSeek**: `Deepseek-r1`

For the complete list of supported models, see [`LLM_utils/llm/__init__.py`](LLM_utils/llm/__init__.py)

## 📊 Data Collection

The system automatically collects:
- **Decision sequences** and response times
- **Learning curves** and adaptation patterns  
- **Risk preferences** and betting behaviors
- **Cognitive flexibility** metrics
- **LLM reasoning** processes and confidence scores


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with the [oTree](https://www.otree.org/) framework
- Inspired by classic experimental psychology paradigms
- Thanks to all human participants

