from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

PROMPT_REPHRASE="""
Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {input}
Standalone Question:
"""

PROMPT_RAG="""
Answer any use questions based solely on the context below:

<context>
{context}
</context>
Messages Placeholder
{chat_history}
"""

class RagChatPrompts:

    @classmethod
    def create_rag_template(cls) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", PROMPT_RAG),
            MessagesPlaceholder(variable_name="chat_history"),  # Dynamic history placeholder
            ("human", "{input}")
        ])

    @classmethod
    def create_rephase_template(cls) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", PROMPT_REPHRASE),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "Follow Up Input: {input}\n\nStandalone Question:")
        ])