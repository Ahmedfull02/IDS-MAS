# Distributed Network Incident Detection

### A Combined Approach using Multi-Agent Systems and Distributed Data Mining

This project, titled **"A Distributed Approach for Network Incident Detection,"** focuses on the design and implementation of an intelligent **Multi-Agent System (MAS)** capable of identifying network incidents in real-time.

By leveraging **Machine Learning (ML)** and **Deep Learning (DL)** models trained in a distributed environment, this system addresses the challenges posed by the continuous increase in network data volumes.

---

## 🎯 Project Objective

The primary goal is to move away from centralized detection limitations by exploiting **parallel resources**. This approach aims to significantly improve the detection process in three key areas:

1.  **Speed:** Faster processing through distributed computation.
2.  **Accuracy:** Enhanced detection capabilities using advanced ML/DL models.
3.  **Robustness:** Greater resilience and scalability in handling massive datasets.

---

## 🚀 Key Features

- **Real-Time Detection:** Identifies threats and anomalies as they occur within the network.
- **Distributed Architecture:** Combines Multi-Agent Systems (MAS) with Distributed Data Mining to decentralize processing.
- **Intelligent Analysis:** Utilizes state-of-the-art Machine Learning and Deep Learning algorithms.
- **Scalability:** Designed to handle high-volume data traffic by distributing tasks across multiple agents.

---

## 🏗️ The Approach

This project combines two powerful paradigms:

1.  **Multi-Agent Systems (MAS):** Autonomous agents interact to collect, preprocess, and analyze data across different network nodes.
2.  **Distributed Data Mining:** Instead of moving all data to a central location, knowledge is extracted locally, and only insights (or model parameters) are shared, reducing latency and bandwidth usage.

---

## 🛠️ Technology Stack

*   **Core:** Python
*   **Multi-Agent Framework:** SPADE (Smart Python Agent Development Environment) / JADE
*   **Machine Learning:** Scikit-learn, PyTorch tabnet-pytorch (Deep Learning architedcture)
*   **Data Processing:** Pandas, NumPy

---

# 📦 Installation Guide

This guide details how to set up the development environment and install the necessary dependencies for the **MAS (Monitoring Agent System)** project.

## Prerequisites

Before installing the requirements, ensure you have the following installed on your system:

- **Python 3.8** or higher
- **pip** (Python Package Installer)
- **Git**

You can verify your Python version by running:
```bash
python --version
# OR
python3 --version
```
### 1. Set Up a Virtual Environment
It is highly recommended to use a virtual environment to manage dependencies and avoid conflicts with your system-level Python packages.

* macOS / Linux :
Open your terminal and navigate to the project directory.
Create the virtual environment:
```bash
python3 -m venv .venv
```
Activate the environment:
```bash
source .venv/bin/activate
```
* Windows :
Open Command Prompt or PowerShell and navigate to the project directory.
Create the virtual environment:
```bash
python -m venv .venv
```
Activate the environment:
```bash
.venv\Scripts\activate
```
Once activated, your terminal prompt should show (.venv) at the beginning.
### 2. Install Dependencies
The project dependencies are listed in the requirements.txt file. Run the following command to install them:

```bash
pip install -r requirements.txt
```
### 3. Verify Installation
To ensure that all packages were installed correctly, you can list the installed packages:

```bash
pip list
```
