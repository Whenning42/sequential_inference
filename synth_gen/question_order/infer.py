import json
import os
from typing import Optional

import tqdm
from openai import OpenAI

import synth_gen.question_order.left_right_prompting as left_right_prompting

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def infer(prompts: list[str]) -> str:
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompts,
        max_tokens=30,
        temperature=0.0,
    )
    return [c.text.strip() for c in response.choices]


def get_value(response: str) -> Optional[int]:
    a = response.strip()
    a = a.strip()
    a = a.strip(".")
    try:
        return int(a)
    except ValueError:
        return None


ds = left_right_prompting.generate_ds(n=800)
print(len(ds))

datapoints = []
BS = 20
for i in tqdm.tqdm(range(len(ds) // BS)):
    batch = ds[BS * i : BS * (i + 1)]
    prompts = [b.prompt for b in batch]
    responses = infer(prompts)
    for question, response in zip(batch, responses):
        value = get_value(response)
        if value is None:
            print("WARNING: failed to adhere desired output format: ", response)
        datapoint = {
            "prompt": question.prompt,
            "response": response,
            "value": value,
            "gt_answer": question.answer,
            "question_def": question.__dict__,
        }
        datapoints.append(datapoint)

with open("gpt3.5-turbo-instruct.json", "w") as f:
    f.write(json.dumps(datapoints, indent=2))
