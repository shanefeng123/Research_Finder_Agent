# Research Finder Agent

## About

This is a simple agentic workflow that searches for research papers based on your research 
interests and your specified topic.

The design is relatively simple. The agent first asks the user for their research interests and the topic they want to search for. 
Then, it searches the topic on arXiv. It then filters the results based on the user's research interests and retrieves the relevant papers.
Finally, it summarizes the results and sends them to the user through email.

There are two reasons why I want to build this agentic tool: to get myself familiar with implementing agentic workflows and to have a tool that can help me find relevant research papers more efficiently.

## Usage

### Install

I highly recommend you to check out the [`uv`](https://docs.astral.sh/uv/) python package manager for installing and managing
dependencies for project like this one, which is more for experimenting and prototyping. It is extremely fast and easy to use.

After you install [`uv`](https://docs.astral.sh/uv/), run the following command in the root directory of this project to install the dependencies:

```bash
uv sync
```

That's all you need to do.

### Config
To run this project, you need to have an [OpenAI API key](https://platform.openai.com), a [SendGrid API key](https://www.twilio.com/en-us/sendgrid), and an email address for sending out the email.
Create a `.env` file in the root directory of the project and add the following lines to it:
```
OPENAI_API_KEY=your_openai_api_key
SENDGRID_API_KEY=your_sendgrid_api_key
MY_EMAIL_ADDRESS=your_email_address
```

Note: To use the SendGrid service, you need to verify your send email address.


### Run
To run the agent, simply run the following command:

```bash
uv run main.py
```

It will ask you for your research interests, the topic you want to search about, how many papers you wish to receive, 
the source of the search (only supporting arXiv for now), the similarity comparison method (only supporting LLM for now), and the email address you want to receive the results. 
After you provide all the information, it will start searching for relevant papers, filtering papers based on your research interest,
and send the results to your email.

## Future Work
This is a very basic implementation of an agentic workflow, just to test and showcase the capabilities of agentic tools. 
There are many ways to improve and expand this project, such as:
- Adding more sources for searching papers, such as Semantic Scholar, Google Scholar (They don't have an API, which is another story)
, etc.
- Adding filtering methods, such as using embedding similarity, etc.
- Adding memory management, such as saving the search history, etc.
