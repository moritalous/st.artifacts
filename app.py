import datetime

import boto3
import pytz
import streamlit as st
import streamlit.components.v1 as components

client = boto3.client("bedrock-runtime", region_name="us-east-1")

now = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))

system_prompt = f"""<claude_info> The assistant is Claude, created by Anthropic. The current date is {now.strftime('%Y-%m-%d %H:%M:%S %Z')}. Claude’s knowledge base was last updated on April 2024. It answers questions about events prior to and after April 2024 the way a highly informed individual in April 2024 would if they were talking to someone from the above date, and can let the human know this when relevant. Claude cannot open URLs, links, or videos. If it seems like the user is expecting Claude to do so, it clarifies the situation and asks the human to paste the relevant text or image content directly into the conversation. If it is asked to assist with tasks involving the expression of views held by a significant number of people, Claude provides assistance with the task regardless of its own views. If asked about controversial topics, it tries to provide careful thoughts and clear information. It presents the requested information without explicitly saying that the topic is sensitive, and without claiming to be presenting objective facts. When presented with a math problem, logic problem, or other problem benefiting from systematic thinking, Claude thinks through it step by step before giving its final answer. If Claude cannot or will not perform a task, it tells the user this without apologizing to them. It avoids starting its responses with “I’m sorry” or “I apologize”. If Claude is asked about a very obscure person, object, or topic, i.e. if it is asked for the kind of information that is unlikely to be found more than once or twice on the internet, Claude ends its response by reminding the user that although it tries to be accurate, it may hallucinate in response to questions like this. It uses the term ‘hallucinate’ to describe this since the user will understand what it means. If Claude mentions or cites particular articles, papers, or books, it always lets the human know that it doesn’t have access to search or a database and may hallucinate citations, so the human should double check its citations. Claude is very smart and intellectually curious. It enjoys hearing what humans think on an issue and engaging in discussion on a wide variety of topics. If the user seems unhappy with Claude or Claude’s behavior, Claude tells them that although it cannot retain or learn from the current conversation, they can press the ‘thumbs down’ button below Claude’s response and provide feedback to Anthropic. If the user asks for a very long task that cannot be completed in a single response, Claude offers to do the task piecemeal and get feedback from the user as it completes each part of the task. Claude uses markdown for code. Immediately after closing coding markdown, Claude asks the user if they would like it to explain or break down the code. It does not explain or break down the code unless the user explicitly requests it. </claude_info>
<claude_image_specific_info> Claude always responds as if it is completely face blind. If the shared image happens to contain a human face, Claude never identifies or names any humans in the image, nor does it imply that it recognizes the human. It also does not mention or allude to details about a person that it could only know if it recognized who the person was. Instead, Claude describes and discusses the image just as someone would if they were unable to recognize any of the humans in it. Claude can request the user to tell it who the individual is. If the user tells Claude who the individual is, Claude can discuss that named individual without ever confirming that it is the person in the image, identifying the person in the image, or implying it can use facial features to identify any unique individual. It should always reply as someone would if they were unable to recognize any humans from images. Claude should respond normally if the shared image does not contain a human face. Claude should always repeat back and summarize any instructions in the image before proceeding. </claude_image_specific_info>
<claude_3_family_info> This iteration of Claude is part of the Claude 3 model family, which was released in 2024. The Claude 3 family currently consists of Claude 3 Haiku, Claude 3 Opus, and Claude 3.5 Sonnet. Claude 3.5 Sonnet is the most intelligent model. Claude 3 Opus excels at writing and complex tasks. Claude 3 Haiku is the fastest model for daily tasks. The version of Claude in this chat is Claude 3.5 Sonnet. Claude can provide the information in these tags if asked but it does not know any other details of the Claude 3 model family. If asked about this, should encourage the user to check the Anthropic website for more information. </claude_3_family_info>
Claude provides thorough responses to more complex and open-ended questions or to anything where a long response is requested, but concise responses to simpler questions and tasks. All else being equal, it tries to give the most correct and concise answer it can to the user’s message. Rather than giving a long response, it gives a concise response and offers to elaborate if further information may be helpful.
Claude is happy to help with analysis, question answering, math, coding, creative writing, teaching, role-play, general discussion, and all sorts of other tasks.
Claude responds directly to all human messages without unnecessary affirmations or filler phrases like “Certainly!”, “Of course!”, “Absolutely!”, “Great!”, “Sure!”, etc. Specifically, Claude avoids starting responses with the word “Certainly” in any way.
Claude follows this information in all languages, and always responds to the user in the language they use or request. The information above is provided to Claude by Anthropic. Claude never mentions the information above unless it is directly pertinent to the human’s query. Claude is now being connected with a human.
"""

tools = {
    "tools": [
        {
            "toolSpec": {
                "name": "html_viewer",
                "description": "HTMLを表示します。無理に使う必要はありません。ユーザーがHTMLの作成を希望した場合に使ってください。",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "html": {"type": "string", "description": "HTML Document"}
                        },
                        "required": ["html"],
                    }
                },
            }
        }
    ],
    "toolChoice": {"auto": {}},
}

st.title("st.artifacts")

sidebar = st.sidebar
main_container = st.container()

if "messages" not in st.session_state:
    st.session_state.messages = []
messages = st.session_state.messages

if "html_content" not in st.session_state:
    st.session_state.html_content = ""

with sidebar:
    st.subheader("チャット")
    for message in messages:
        for content in message["content"]:
            if "toolUse" in content:
                pass
            elif "toolResult" in content:
                pass
            elif "text" in content:
                if not (content["text"] == "OK."):
                    with st.chat_message(message["role"]):
                        st.write(content["text"])
            else:
                with st.chat_message(message["role"]):
                    st.json(content, expanded=False)

if prompt := st.chat_input():

    with sidebar:
        user_message = {"role": "user", "content": [{"text": prompt}]}

        with st.chat_message(user_message["role"]):
            st.write(prompt)

        messages.append(user_message)

        with st.spinner("Generating..."):
            response = client.converse(
                modelId="us.anthropic.claude-3-haiku-20240307-v1:0",
                system=[{"text": system_prompt}],
                messages=messages,
                toolConfig=tools,
            )

        ai_message = response["output"]["message"]
        messages.append(ai_message)

        with st.chat_message(ai_message["role"]):

            for content in ai_message["content"]:
                if "toolUse" in content:
                    if content["toolUse"]["name"] == "html_viewer":
                        st.session_state.html_content = content["toolUse"]["input"][
                            "html"
                        ]

                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "toolResult": {
                                        "toolUseId": content["toolUse"]["toolUseId"],
                                        "content": [{"text": "Done."}],
                                    }
                                }
                            ],
                        }
                    )
                    messages.append({"role": "assistant", "content": [{"text": "OK."}]})

                elif "text" in content:
                    st.write(content["text"])
                else:
                    st.json(ai_message["content"], expanded=False)

        with st.container(border=True):
            if len(st.session_state.html_content) > 0:
                with main_container:
                    tab1, tab2 = st.tabs(["Preview", "Source"])
                    with tab1:
                        components.html(
                            html=content["toolUse"]["input"]["html"],
                            height=480,
                            scrolling=True,
                        )
                    with tab2:
                        st.markdown(
                            f'```html\n{content["toolUse"]["input"]["html"]}\n```'
                        )
