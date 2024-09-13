from langchain_openai import ChatOpenAI

from app.llm.chain import GeneralChain
from app.llm.prompt_templates import LLMEvaluationTemplate
from app.config import settings


def evaluate(query: str, output: str) -> str:
    evaluation_template = LLMEvaluationTemplate()
    prompt_template = evaluation_template.create_template()

    model = ChatOpenAI(model=settings.OPENAI_MODEL_ID, api_key=settings.OPENAI_API_KEY)
    chain = GeneralChain.get_chain(
        llm=model, output_key="evaluation", template=prompt_template
    )

    response = chain.invoke({"query": query, "output": output})

    return response["evaluation"]
