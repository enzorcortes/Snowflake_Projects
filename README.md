# ❄️ Snowflake Projects ❄️

Welcome! Here you will find insightful and creative ways to interpret data using a powerful AI-powered software used in many data analytical environments around the workforce known as ❄️ [Snowflake](https://www.snowflake.com/en/).

# Projects

## 💵 Ask the US Economy

A conversational AI agent that answers plain-English questions about the US economy — powered entirely by Snowflake. The dataset can be found for free within the Snowflake Marketplace as *SNOWFLAKE_PUBLIC_DATA_FREE. PUBLIC_DATA_FREE. FINANCIAL_ECONOMIC_INDICATORS_TIMESERIES*.

> *"It's a recession when your neighbor loses his job; it's a depression when you lose your own." — Harry S. Truman*

## 📓❕Notebook Notes
A step-by-step notebook with SQL, Snowpark, Dynamic Tables, Cortex Analyst, and Streamlit App UI has been generated and submitted in this repo as a PDF for your convenience if you want to recreate it yourself. This notebook was generated via Codex Work after an incohesive documentation effort was done from a combination of .txt files and VS Code. The reference notebook can be found [here](https://github.com/enzorcortes/Snowflake_Projects/blob/main/askuseconomy/Snowflake%20-%20Ask%20US%20Economy%20Notebook.pdf).
## Step 2.1
- If on a MacBook, like I was, make sure [Homebrew](https://downloads.install.guide/suym-brew/Set-Up-Your-Mac-with-Homebrew.dmg?utm_source=home&utm_medium=hero_cta&utm_campaign=suym-brew_setup) or [Xcode Command Line Tools](https://downloads.install.guide/suym-cli/Set-Up-Your-Mac-for-the-Command-Line.dmg?utm_source=home&utm_medium=hero_cta&utm_campaign=suym-cli_setup) (you need the uv) and [Python for Mac](https://downloads.install.guide/suym-python/Set-Up-Your-Mac-for-Python.dmg?utm_source=home&utm_medium=hero_cta&utm_campaign=suym-python_setup) are downloaded. This must be done BEFORE installing Snowpack in your local terminal. I found help via the [Mac Install Guide](https://mac.install.guide)
- If on a Mac, instead of typing *pip install "snowflake-snowpark-python[pandas]" snowflake-connector-python*, you must type *pip3 install "snowflake-snowpark-python[pandas]" snowflake-connector-python* as the BASH is in zsh and has different formatting
## Step 2.2
- To replace <your-account> for the connection_params, you must navigate within Snowflake to your Account Details > Config File > copy and paste the account = "_______-_______" (alphanumeric, 14 character code, 7 characters separated by a dash). This must be repeated for <your-username>, labeled user = "______" in the Config File (same place as the account).
- The password is tricky as it requires either MFA (multi-factor authentication) or a temporary generated token via Settings > Authentication > Programmatic Access Tokens > Generate Token. Copy and paste the given token (you may receive an email alerting you of this action, do not be alarmed) to the <your-password> line.
