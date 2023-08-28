from __future__ import annotations

import json
from typing import (
    Any,
    Literal,
    Mapping,
    NotRequired,
    Sequence,
    TypeAlias,
    TypedDict,
)

import openai

from apply_gpt.utils import Json


class OpenaiTyping:
    class Message:
        class System(TypedDict):
            role: Literal["system"]
            content: str

        class User(TypedDict):
            role: Literal["user"]
            content: str

    class Function:
        class Parameters:
            class Object(TypedDict):
                type: Literal["object"]
                properties: Mapping[str, OpenaiTyping.Function.Parameters.Any]
                required: Sequence[str]
                description: NotRequired[str]

            class Array(TypedDict):
                type: Literal["array"]
                items: OpenaiTyping.Function.Parameters.Any
                description: NotRequired[str]

            class Number(TypedDict):
                type: Literal["number"]
                description: NotRequired[str]

            class String(TypedDict):
                type: Literal["string"]
                enum: NotRequired[Sequence[str]]
                description: NotRequired[str]

            Any: TypeAlias = Object | Array | Number | String

        class Signature(TypedDict):
            name: str
            parameters: OpenaiTyping.Function.Parameters.Any

        class Call(TypedDict):
            name: str


class OpenaiModule:
    """
    Low level wrapper of direct calls to OpenAI's python module.
    """

    def __init__(self, api_key: str, model: str) -> None:
        openai.api_key = api_key
        self._model = model

    def chat_completion_create(
        self,
        messages: tuple[OpenaiTyping.Message.System, OpenaiTyping.Message.User],
        functions: Sequence[OpenaiTyping.Function.Signature],
        function_call: OpenaiTyping.Function.Call,
        temperature: float,
    ) -> Any:
        return openai.ChatCompletion.create(
            model=self._model,
            messages=messages,
            functions=functions,
            function_call=function_call,
            temperature=temperature,
        )


# Ref: https://blog.simonfarshid.com/native-json-output-from-gpt-4
class OpenaiJsonGenerator:
    """
    Generates a JSON object with an OpenAI API call.
    """

    def __init__(self, openai_module: OpenaiModule) -> None:
        self._openai_module = openai_module

    def generate(
        self,
        system_message: str,
        user_message: str,
        name: str,
        schema: Schema,
    ) -> Json:
        """
        Generate a JSON object with an OpenAI API call.

        :param system_message: the message instructing GPT how to behave
        :param user_message: the message requesting the generation of the object
        :param name: the name of the type of generated object in snake_case
        :param schema: the JSON schema of the generated object
        """
        function_name = f"generate_{name}"
        completion = self._openai_module.chat_completion_create(
            messages=(
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ),
            functions=[{"name": function_name, "parameters": schema}],
            function_call={"name": function_name},
            temperature=0.0,
        )
        generated_json_str: str = completion.choices[0].message.function_call.arguments
        generated_json: Json = json.loads(generated_json_str)
        return generated_json

    Schema: TypeAlias = OpenaiTyping.Function.Parameters.Any
