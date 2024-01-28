# Measure GPT-2 medium's (350M) performance on the SeqInfer task.

from tqdm import tqdm
from transformers import GPT2Model, GPT2Tokenizer

import synth_gen.gen


def build_ds():
    ds = synth_gen.gen.generate_ds(100000)
    questions = set()
    ds_by_depth = {q.depth: [] for q in ds}
    for q in ds:
        if q.prompt in questions:
            continue
        questions.add(q.prompt)
        ds_by_depth[q.depth].append(q)

    for depth, qs in ds_by_depth.items():
        print(depth, len(qs))

    sampled_ds = (
        ds_by_depth[1]
        + ds_by_depth[2]
        + ds_by_depth[3][:490]
        + ds_by_depth[4][:490]
        + ds_by_depth[5]
    )
    return sampled_ds


def run_exp():
    # Load dataset
    full_ds = build_ds()

    # Load model
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2-medium")
    model = GPT2Model.from_pretrained("gpt2-medium")

    # Run inference
    bs = 4
    for i in tqdm(range(len(full_ds) // bs)):
        qs = full_ds[i * bs : (i + 1) * bs]
        prompts = [q.prompt for q in qs]
        input = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True)
        output = model(**input)
        print(output)
        break


if __name__ == "__main__":
    run_exp()
