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


def infer(prompt: str) -> str:
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
    )
    return response.choices[0].text.strip()


def get_value(response: str) -> Optional[int]:
    a = response.strip()
    a = a.strip()
    try:
        return int(a)
    except ValueError:
        return None


ds = left_right_prompting.generate_ds()

datapoints = []
for i in tqdm.tqdm(range(len(ds))):
    response = infer(ds[i].prompt)
    value = get_value(response)
    datapoint = {
        "prompt": ds[i].prompt,
        "response": response,
        "value": value,
        "gt_answer": ds[i].answer,
        "question_def": ds[i].__dict__,
    }
    datapoints.append(datapoint)

with open("gpt3.5-turbo-instruct.json", "w") as f:
    f.write(json.dumps(datapoints, indent=2))
